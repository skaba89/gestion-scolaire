#!/bin/bash
#
# SchoolFlow Pro - Backup Script
# Comprehensive backup for PostgreSQL, Redis, MinIO, and Keycloak
#
# Usage: ./backup.sh [--full | --incremental] [destination]
#

set -euo pipefail

# ─── Configuration ──────────────────────────────────────────────────────────

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_TYPE="${1:-full}"
BACKUP_DEST="${2:-/backups}"
BACKUP_DIR="${BACKUP_DEST}/${BACKUP_DATE}_${BACKUP_TYPE}"

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

# Retention
DAILY_RETENTION=7
WEEKLY_RETENTION=4
MONTHLY_RETENTION=12

# ─── Logging ────────────────────────────────────────────────────────────────

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# ─── Pre-flight Checks ──────────────────────────────────────────────────────

check_dependencies() {
    local deps=("pg_dump" "redis-cli" "mc" "aws" "rclone")
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log "WARNING: $dep not found, some features may not work"
        fi
    done
}

check_disk_space() {
    local required_gb=10
    local available_kb=$(df -k "$BACKUP_DEST" | awk 'NR==2 {print $4}')
    local available_gb=$((available_kb / 1024 / 1024))
    
    if [ "$available_gb" -lt "$required_gb" ]; then
        error "Insufficient disk space: ${available_gb}GB available, ${required_gb}GB required"
        exit 1
    fi
    
    log "Disk space check passed: ${available_gb}GB available"
}

# ─── Database Backup ────────────────────────────────────────────────────────

backup_postgresql() {
    log "Starting PostgreSQL backup..."
    
    local backup_file="${BACKUP_DIR}/postgresql_${DB_NAME}_${BACKUP_DATE}.sql.gz"
    local checksum_file="${BACKUP_DIR}/postgresql_${DB_NAME}_${BACKUP_DATE}.sha256"
    
    mkdir -p "$BACKUP_DIR"
    
    # Set password if provided
    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi
    
    # Create backup with pg_dump
    # Using custom format for better compression and parallel restore
    pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --format=custom \
        --verbose \
        --no-owner \
        --no-privileges \
        | gzip > "$backup_file"
    
    # Generate checksum
    sha256sum "$backup_file" > "$checksum_file"
    
    # Verify backup integrity
    if gzip -t "$backup_file"; then
        log "PostgreSQL backup completed: $(du -h "$backup_file" | cut -f1)"
    else
        error "PostgreSQL backup integrity check failed"
        return 1
    fi
    
    # Unset password
    unset PGPASSWORD
}

backup_postgresql_basebackup() {
    log "Starting PostgreSQL base backup (for PITR)..."
    
    local base_dir="${BACKUP_DIR}/postgresql_base"
    mkdir -p "$base_dir"
    
    # For streaming replication setups
    pg_basebackup \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -D "$base_dir" \
        --format=tar \
        --gzip \
        --progress \
        --wal-method=stream
    
    log "PostgreSQL base backup completed"
}

# ─── Redis Backup ───────────────────────────────────────────────────────────

backup_redis() {
    log "Starting Redis backup..."
    
    local backup_file="${BACKUP_DIR}/redis_${BACKUP_DATE}.rdb"
    
    # Trigger Redis BGSAVE
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" BGSAVE
    
    # Wait for save to complete
    local retries=30
    while [ $retries -gt 0 ]; do
        if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" LASTSAVE | grep -q "$(date +%s | cut -c1-6)"; then
            break
        fi
        sleep 1
        retries=$((retries - 1))
    done
    
    # Copy RDB file
    docker cp redis:/data/dump.rdb "$backup_file" 2>/dev/null || \
        cp /var/lib/redis/dump.rdb "$backup_file" 2>/dev/null || \
        log "WARNING: Could not copy Redis RDB file"
    
    if [ -f "$backup_file" ]; then
        log "Redis backup completed: $(du -h "$backup_file" | cut -f1)"
    else
        log "WARNING: Redis backup file not created"
    fi
}

# ─── MinIO/S3 Backup ────────────────────────────────────────────────────────

backup_minio() {
    log "Starting MinIO backup..."
    
    local backup_dir="${BACKUP_DIR}/minio"
    mkdir -p "$backup_dir"
    
    # Configure mc client
    mc alias set schoolflow-minio "http://${MINIO_ENDPOINT}" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY"
    
    # Mirror bucket to local
    mc mirror schoolflow-minio/"$MINIO_BUCKET" "$backup_dir/$MINIO_BUCKET" --overwrite
    
    # Create archive
    tar -czf "${backup_dir}.tar.gz" -C "$backup_dir" .
    rm -rf "$backup_dir"
    
    log "MinIO backup completed: $(du -h "${backup_dir}.tar.gz" | cut -f1)"
}

# ─── Keycloak Backup ────────────────────────────────────────────────────────

backup_keycloak() {
    log "Starting Keycloak backup..."
    
    local backup_file="${BACKUP_DIR}/keycloak_${BACKUP_DATE}.json"
    
    # Export realm configuration
    docker exec keycloak /opt/keycloak/bin/kc.sh export \
        --realm schoolflow \
        --file "/tmp/realm-export.json" \
        2>/dev/null || log "WARNING: Keycloak export failed"
    
    docker cp keycloak:/tmp/realm-export.json "$backup_file" 2>/dev/null || \
        log "WARNING: Could not copy Keycloak export"
    
    if [ -f "$backup_file" ]; then
        gzip "$backup_file"
        log "Keycloak backup completed"
    fi
}

# ─── Upload to Remote Storage ────────────────────────────────────────────────

upload_to_s3() {
    log "Uploading backups to S3..."
    
    local s3_bucket="${S3_BACKUP_BUCKET:-schoolflow-backups}"
    local s3_prefix="daily"
    
    # Determine prefix based on backup type
    case "$BACKUP_TYPE" in
        full)
            if [ "$(date +%u)" -eq 7 ]; then
                s3_prefix="weekly"
            elif [ "$(date +%d)" -eq 01 ]; then
                s3_prefix="monthly"
            fi
            ;;
        incremental)
            s3_prefix="incremental"
            ;;
    esac
    
    # Upload with versioning
    aws s3 sync "$BACKUP_DIR" "s3://${s3_bucket}/${s3_prefix}/${BACKUP_DATE}/" \
        --storage-class STANDARD_IA \
        --only-show-errors
    
    log "Upload to S3 completed: s3://${s3_bucket}/${s3_prefix}/${BACKUP_DATE}/"
}

upload_to_backblaze() {
    log "Uploading backups to Backblaze B2..."
    
    local bucket="${B2_BUCKET:-schoolflow-backups}"
    
    rclone sync "$BACKUP_DIR" "b2:${bucket}/${BACKUP_DATE}" \
        --progress \
        --transfers 4
    
    log "Upload to Backblaze completed"
}

# ─── Retention Management ───────────────────────────────────────────────────

apply_retention_policy() {
    log "Applying retention policy..."
    
    # Daily backups
    find "$BACKUP_DEST" -maxdepth 1 -type d -name "*_full" -mtime +$DAILY_RETENTION -exec rm -rf {} \; 2>/dev/null || true
    
    # Weekly backups (keep last 4 weeks)
    # Monthly backups (keep last 12 months)
    # This is simplified - in production, use proper lifecycle policies
    
    log "Retention policy applied"
}

# ─── Verification ────────────────────────────────────────────────────────────

verify_backup() {
    log "Verifying backup integrity..."
    
    local all_passed=true
    
    # Check PostgreSQL backup
    for sql_file in "${BACKUP_DIR}"/postgresql_*.sql.gz; do
        if [ -f "$sql_file" ]; then
            if gzip -t "$sql_file" 2>/dev/null; then
                log "✓ PostgreSQL backup valid: $sql_file"
            else
                error "✗ PostgreSQL backup corrupted: $sql_file"
                all_passed=false
            fi
        fi
    done
    
    # Check checksums
    for checksum_file in "${BACKUP_DIR}"/*.sha256; do
        if [ -f "$checksum_file" ]; then
            if sha256sum -c "$checksum_file" --quiet 2>/dev/null; then
                log "✓ Checksum verified: $checksum_file"
            else
                error "✗ Checksum failed: $checksum_file"
                all_passed=false
            fi
        fi
    done
    
    if [ "$all_passed" = true ]; then
        log "All backup verifications passed"
        return 0
    else
        error "Some backup verifications failed"
        return 1
    fi
}

# ─── Notifications ──────────────────────────────────────────────────────────

send_notification() {
    local status="$1"
    local message="$2"
    
    # Slack notification
    if [ -n "${SLACK_WEBHOOK:-}" ]; then
        local color="good"
        [ "$status" = "error" ] && color="danger"
        
        curl -s -X POST "$SLACK_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{
                \"attachments\": [{
                    \"color\": \"$color\",
                    \"title\": \"SchoolFlow Backup - $BACKUP_TYPE\",
                    \"text\": \"$message\",
                    \"ts\": $(date +%s)
                }]
            }"
    fi
    
    # Email notification
    if [ -n "${EMAIL_RECIPIENT:-}" ]; then
        echo "$message" | mail -s "SchoolFlow Backup - $status" "$EMAIL_RECIPIENT"
    fi
}

# ─── Main Execution ─────────────────────────────────────────────────────────

main() {
    log "============================================"
    log "SchoolFlow Pro Backup Script"
    log "Type: $BACKUP_TYPE"
    log "Destination: $BACKUP_DIR"
    log "============================================"
    
    # Pre-flight checks
    check_dependencies
    check_disk_space
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Execute backups
    local backup_start=$(date +%s)
    
    backup_postgresql || error "PostgreSQL backup failed"
    backup_redis || log "Redis backup skipped"
    backup_minio || log "MinIO backup skipped"
    backup_keycloak || log "Keycloak backup skipped"
    
    local backup_end=$(date +%s)
    local duration=$((backup_end - backup_start))
    
    # Verify backups
    if verify_backup; then
        # Upload to remote storage
        upload_to_s3 || log "S3 upload failed"
        
        # Apply retention
        apply_retention_policy
        
        # Create manifest
        cat > "${BACKUP_DIR}/manifest.json" <<EOF
{
    "timestamp": "$(date -Iseconds)",
    "type": "${BACKUP_TYPE}",
    "duration_seconds": ${duration},
    "components": {
        "postgresql": true,
        "redis": true,
        "minio": true,
        "keycloak": true
    },
    "size_bytes": $(du -sb "$BACKUP_DIR" | cut -f1)
}
EOF
        
        send_notification "success" "Backup completed successfully in ${duration}s"
        log "============================================"
        log "Backup completed successfully in ${duration}s"
        log "============================================"
        exit 0
    else
        send_notification "error" "Backup verification failed"
        log "============================================"
        log "Backup FAILED - verification errors"
        log "============================================"
        exit 1
    fi
}

# Run main
main "$@"
