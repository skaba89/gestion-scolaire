#!/bin/bash
#
# SchoolFlow Pro - Restore Script
# Comprehensive restore for PostgreSQL, Redis, MinIO, and Keycloak
#
# Usage: ./restore.sh <backup_directory> [--component <postgres|redis|minio|keycloak|all>]
#

set -euo pipefail

# ─── Configuration ──────────────────────────────────────────────────────────

BACKUP_DIR="${1:-}"
COMPONENT="${3:-all}"
RESTORE_LOG="/var/log/schoolflow/restore_$(date +%Y%m%d_%H%M%S).log"

# Database
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-schoolflow}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-}"

# Redis
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

# MinIO
MINIO_ENDPOINT="${MINIO_ENDPOINT:-localhost:9000}"
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-minioadmin}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-minioadmin}"
MINIO_BUCKET="${MINIO_BUCKET:-schoolflow}"

# ─── Logging ────────────────────────────────────────────────────────────────

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$RESTORE_LOG"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2 | tee -a "$RESTORE_LOG"
}

# ─── Validation ─────────────────────────────────────────────────────────────

validate_backup_dir() {
    if [ -z "$BACKUP_DIR" ]; then
        error "Backup directory is required"
        echo "Usage: $0 <backup_directory> [--component <component>]"
        exit 1
    fi
    
    if [ ! -d "$BACKUP_DIR" ]; then
        error "Backup directory not found: $BACKUP_DIR"
        exit 1
    fi
    
    if [ ! -f "${BACKUP_DIR}/manifest.json" ]; then
        error "Invalid backup directory - manifest.json not found"
        exit 1
    fi
    
    log "Backup directory validated: $BACKUP_DIR"
}

verify_checksums() {
    log "Verifying backup checksums..."
    
    local failed=0
    for checksum_file in "${BACKUP_DIR}"/*.sha256; do
        if [ -f "$checksum_file" ]; then
            if ! sha256sum -c "$checksum_file" --quiet 2>/dev/null; then
                error "Checksum verification failed: $checksum_file"
                failed=1
            fi
        fi
    done
    
    if [ $failed -eq 1 ]; then
        error "Backup integrity check failed. Aborting restore."
        exit 1
    fi
    
    log "All checksums verified successfully"
}

confirm_restore() {
    log "============================================"
    log "WARNING: This will REPLACE existing data!"
    log "Backup: $BACKUP_DIR"
    log "Component: $COMPONENT"
    log "Database: $DB_NAME on $DB_HOST:$DB_PORT"
    log "============================================"
    
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log "Restore cancelled by user"
        exit 0
    fi
}

# ─── PostgreSQL Restore ─────────────────────────────────────────────────────

restore_postgresql() {
    log "Starting PostgreSQL restore..."
    
    local backup_file=$(ls "${BACKUP_DIR}"/postgresql_*.sql.gz 2>/dev/null | head -1)
    
    if [ -z "$backup_file" ]; then
        error "No PostgreSQL backup found"
        return 1
    fi
    
    # Set password if provided
    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi
    
    # Create temporary database for restore
    local temp_db="${DB_NAME}_restore_$(date +%s)"
    
    log "Creating temporary database: $temp_db"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $temp_db;"
    
    # Restore to temporary database
    log "Restoring to temporary database..."
    gunzip -c "$backup_file" | pg_restore \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$temp_db" \
        --no-owner \
        --no-privileges \
        --verbose \
        2>&1 | tee -a "$RESTORE_LOG"
    
    # Verify restore
    local table_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$temp_db" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
    log "Tables restored: $table_count"
    
    # Ask for confirmation to switch
    read -p "Restore complete. Switch $DB_NAME to restored version? (yes/no): " switch_confirm
    
    if [ "$switch_confirm" = "yes" ]; then
        log "Switching databases..."
        
        # Terminate existing connections
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres <<EOF
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS ${DB_NAME}_old;
ALTER DATABASE $DB_NAME RENAME TO ${DB_NAME}_old;
ALTER DATABASE $temp_db RENAME TO $DB_NAME;
EOF
        
        log "PostgreSQL restore completed successfully"
    else
        log "Database switch cancelled. Restored database available as: $temp_db"
    fi
    
    unset PGPASSWORD
}

restore_postgresql_pitr() {
    log "Starting PostgreSQL Point-in-Time Recovery..."
    
    local base_dir=$(ls -d "${BACKUP_DIR}"/postgresql_base 2>/dev/null | head -1)
    
    if [ -z "$base_dir" ]; then
        error "No base backup found for PITR"
        return 1
    fi
    
    # Stop PostgreSQL
    log "Stopping PostgreSQL..."
    docker stop postgres || systemctl stop postgresql
    
    # Clear existing data
    log "Clearing existing data directory..."
    rm -rf /var/lib/postgresql/data/*
    
    # Extract base backup
    log "Extracting base backup..."
    tar -xzf "${base_dir}/base.tar.gz" -C /var/lib/postgresql/data/
    
    # Configure recovery
    cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = 'cp /archive/%f %p'
recovery_target_time = '${RECOVERY_TARGET_TIME:-}'
recovery_target_action = 'promote'
EOF
    
    # Start PostgreSQL
    log "Starting PostgreSQL in recovery mode..."
    docker start postgres || systemctl start postgresql
    
    log "PITR restore initiated. Monitor logs for completion."
}

# ─── Redis Restore ───────────────────────────────────────────────────────────

restore_redis() {
    log "Starting Redis restore..."
    
    local backup_file=$(ls "${BACKUP_DIR}"/redis_*.rdb 2>/dev/null | head -1)
    
    if [ -z "$backup_file" ]; then
        log "No Redis backup found, skipping"
        return 0
    fi
    
    # Stop Redis
    log "Stopping Redis..."
    docker stop redis || systemctl stop redis
    
    # Copy RDB file
    log "Restoring RDB file..."
    docker cp "$backup_file" redis:/data/dump.rdb 2>/dev/null || \
        cp "$backup_file" /var/lib/redis/dump.rdb
    
    # Start Redis
    log "Starting Redis..."
    docker start redis || systemctl start redis
    
    # Verify
    sleep 2
    local key_count=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" DBSIZE | grep -o '[0-9]*')
    log "Redis restore completed. Keys restored: $key_count"
}

# ─── MinIO/S3 Restore ────────────────────────────────────────────────────────

restore_minio() {
    log "Starting MinIO restore..."
    
    local backup_file=$(ls "${BACKUP_DIR}"/minio_*.tar.gz 2>/dev/null | head -1)
    
    if [ -z "$backup_file" ]; then
        log "No MinIO backup found, skipping"
        return 0
    fi
    
    # Configure mc client
    mc alias set schoolflow-minio "http://${MINIO_ENDPOINT}" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY"
    
    # Extract backup
    local temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir"
    
    # Restore bucket
    log "Restoring bucket contents..."
    mc mirror "${temp_dir}/${MINIO_BUCKET}" schoolflow-minio/"$MINIO_BUCKET" --overwrite
    
    # Cleanup
    rm -rf "$temp_dir"
    
    log "MinIO restore completed"
}

# ─── Keycloak Restore ───────────────────────────────────────────────────────

restore_keycloak() {
    log "Starting Keycloak restore..."
    
    local backup_file=$(ls "${BACKUP_DIR}"/keycloak_*.json.gz 2>/dev/null | head -1)
    
    if [ -z "$backup_file" ]; then
        log "No Keycloak backup found, skipping"
        return 0
    fi
    
    # Extract
    gunzip -k "$backup_file"
    local realm_file="${backup_file%.gz}"
    
    # Import realm
    log "Importing realm configuration..."
    docker exec keycloak /opt/keycloak/bin/kc.sh import \
        --file "/tmp/realm-import.json" \
        --realm schoolflow \
        2>&1 | tee -a "$RESTORE_LOG"
    
    # Copy import file
    docker cp "$realm_file" keycloak:/tmp/realm-import.json
    
    # Cleanup
    rm -f "$realm_file"
    
    log "Keycloak restore completed"
}

# ─── Full System Restore ─────────────────────────────────────────────────────

restore_all() {
    log "Starting full system restore..."
    
    local start_time=$(date +%s)
    
    restore_postgresql
    restore_redis
    restore_minio
    restore_keycloak
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log "============================================"
    log "Full restore completed in ${duration}s"
    log "============================================"
    
    # Verification
    verify_restore
}

# ─── Verification ────────────────────────────────────────────────────────────

verify_restore() {
    log "Verifying restore..."
    
    local checks_passed=0
    local checks_total=4
    
    # Check PostgreSQL
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
        log "✓ PostgreSQL: Connected successfully"
        ((checks_passed++))
    else
        log "✗ PostgreSQL: Connection failed"
    fi
    
    # Check Redis
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" PING 2>&1 | grep -q PONG; then
        log "✓ Redis: Connected successfully"
        ((checks_passed++))
    else
        log "✗ Redis: Connection failed"
    fi
    
    # Check MinIO
    if mc ls schoolflow-minio/"$MINIO_BUCKET" >/dev/null 2>&1; then
        log "✓ MinIO: Bucket accessible"
        ((checks_passed++))
    else
        log "✗ MinIO: Bucket not accessible"
    fi
    
    # Check Keycloak
    if curl -s "http://localhost:8080/health" | grep -q "UP"; then
        log "✓ Keycloak: Healthy"
        ((checks_passed++))
    else
        log "✗ Keycloak: Not healthy"
    fi
    
    log "Verification: $checks_passed/$checks_total checks passed"
    
    if [ $checks_passed -eq $checks_total ]; then
        return 0
    else
        return 1
    fi
}

# ─── Main Execution ─────────────────────────────────────────────────────────

main() {
    mkdir -p "$(dirname "$RESTORE_LOG")"
    
    log "============================================"
    log "SchoolFlow Pro Restore Script"
    log "============================================"
    
    validate_backup_dir
    verify_checksums
    confirm_restore
    
    case "$COMPONENT" in
        postgres|postgresql)
            restore_postgresql
            ;;
        redis)
            restore_redis
            ;;
        minio)
            restore_minio
            ;;
        keycloak)
            restore_keycloak
            ;;
        all)
            restore_all
            ;;
        *)
            error "Unknown component: $COMPONENT"
            exit 1
            ;;
    esac
    
    log "Restore process completed"
}

# Run main
main "$@"
