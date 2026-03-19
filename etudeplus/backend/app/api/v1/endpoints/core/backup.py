"""
Backup and Restore API Endpoints
Implements backup scheduling, execution, and restoration functionality.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum
import os
import subprocess
import json
from pathlib import Path

from app.core.config import settings
from app.core.security import require_permission
from app.utils.audit import log_audit_event


router = APIRouter()


class BackupType(str, Enum):
    FULL = "full"
    DATABASE = "database"
    FILES = "files"
    CONFIG = "config"


class BackupStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class BackupCreate(BaseModel):
    backup_type: BackupType = BackupType.FULL
    description: Optional[str] = None
    include_files: bool = True
    include_database: bool = True


class BackupInfo(BaseModel):
    id: str
    backup_type: BackupType
    status: BackupStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    size_bytes: Optional[int] = None
    description: Optional[str] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None


class BackupRestore(BaseModel):
    backup_id: str
    restore_database: bool = True
    restore_files: bool = True
    confirm: bool  # Must be True to confirm restore


class RestoreStatus(BaseModel):
    backup_id: str
    status: BackupStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps_completed: List[str] = []
    error_message: Optional[str] = None


# In-memory backup registry (in production, use database)
backup_registry: dict = {}


def get_backup_directory() -> Path:
    """Get the backup directory path."""
    backup_dir = Path(os.getenv("BACKUP_DIR", "/backups"))
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def execute_database_backup(backup_path: Path) -> tuple[bool, str]:
    """Execute database backup using pg_dump."""
    try:
        db_url = settings.DATABASE_URL
        backup_file = backup_path / "database.sql"
        
        # Use pg_dump for backup
        result = subprocess.run(
            [
                "pg_dump",
                db_url,
                "--format=custom",
                "--no-owner",
                "--no-acl",
                f"--file={backup_file}"
            ],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        if result.returncode != 0:
            return False, f"pg_dump failed: {result.stderr}"
        
        return True, str(backup_file)
    except subprocess.TimeoutExpired:
        return False, "Backup timed out after 1 hour"
    except Exception as e:
        return False, f"Backup failed: {str(e)}"


def execute_files_backup(backup_path: Path) -> tuple[bool, str]:
    """Backup uploaded files from MinIO."""
    try:
        import tarfile
        
        files_backup = backup_path / "files.tar.gz"
        
        # This would backup from MinIO
        # For now, we'll create a placeholder
        with tarfile.open(files_backup, "w:gz") as tar:
            # Add files from MinIO
            pass
        
        return True, str(files_backup)
    except Exception as e:
        return False, f"Files backup failed: {str(e)}"


def execute_config_backup(backup_path: Path) -> tuple[bool, str]:
    """Backup system configuration."""
    try:
        config_backup = backup_path / "config.json"
        
        config_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.APP_VERSION,
            "keycloak_realm": settings.KEYCLOAK_REALM,
            # Don't include secrets!
        }
        
        with open(config_backup, "w") as f:
            json.dump(config_data, f, indent=2)
        
        return True, str(config_backup)
    except Exception as e:
        return False, f"Config backup failed: {str(e)}"


async def run_backup_task(backup_id: str, backup_request: BackupCreate):
    """Background task to execute backup."""
    backup_dir = get_backup_directory()
    backup_path = backup_dir / backup_id
    backup_path.mkdir(parents=True, exist_ok=True)
    
    backup_registry[backup_id]["status"] = BackupStatus.IN_PROGRESS
    
    errors = []
    completed_files = []
    
    # Database backup
    if backup_request.include_database:
        success, result = execute_database_backup(backup_path)
        if success:
            completed_files.append(result)
        else:
            errors.append(result)
    
    # Files backup
    if backup_request.include_files:
        success, result = execute_files_backup(backup_path)
        if success:
            completed_files.append(result)
        else:
            errors.append(result)
    
    # Config backup
    success, result = execute_config_backup(backup_path)
    if success:
        completed_files.append(result)
    else:
        errors.append(result)
    
    # Calculate total size
    total_size = sum(
        os.path.getsize(f) for f in completed_files if os.path.exists(f)
    )
    
    # Create archive
    archive_path = backup_dir / f"{backup_id}.tar.gz"
    import tarfile
    with tarfile.open(archive_path, "w:gz") as tar:
        for f in completed_files:
            if os.path.exists(f):
                tar.add(f, arcname=os.path.basename(f))
    
    # Update registry
    backup_registry[backup_id].update({
        "status": BackupStatus.COMPLETED if not errors else BackupStatus.FAILED,
        "completed_at": datetime.utcnow(),
        "size_bytes": os.path.getsize(archive_path) if archive_path.exists() else 0,
        "file_path": str(archive_path),
        "error_message": "; ".join(errors) if errors else None,
    })
    
    # Log audit event
    log_audit_event(
        action="backup_completed" if not errors else "backup_failed",
        resource="system/backup",
        details={
            "backup_id": backup_id,
            "type": backup_request.backup_type.value,
            "size_bytes": backup_registry[backup_id]["size_bytes"],
        }
    )


@router.post("/", response_model=BackupInfo)
async def create_backup(
    backup_request: BackupCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_permission("settings:manage")),
):
    """
    Create a new system backup.
    
    Requires 'settings:manage' permission.
    Backup runs in the background.
    """
    import uuid
    
    backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Register backup
    backup_registry[backup_id] = {
        "id": backup_id,
        "backup_type": backup_request.backup_type,
        "status": BackupStatus.PENDING,
        "created_at": datetime.utcnow(),
        "description": backup_request.description,
    }
    
    # Start background task
    background_tasks.add_task(run_backup_task, backup_id, backup_request)
    
    # Log audit event
    log_audit_event(
        action="backup_initiated",
        resource="system/backup",
        user_id=current_user.get("id"),
        details={
            "backup_id": backup_id,
            "type": backup_request.backup_type.value,
        }
    )
    
    return BackupInfo(**backup_registry[backup_id])


@router.get("/", response_model=List[BackupInfo])
async def list_backups(
    current_user: dict = Depends(require_permission("settings:read")),
):
    """
    List all backups.
    
    Requires 'settings:read' permission.
    """
    return [BackupInfo(**backup) for backup in backup_registry.values()]


@router.get("/{backup_id}", response_model=BackupInfo)
async def get_backup(
    backup_id: str,
    current_user: dict = Depends(require_permission("settings:read")),
):
    """
    Get details of a specific backup.
    
    Requires 'settings:read' permission.
    """
    if backup_id not in backup_registry:
        raise HTTPException(status_code=404, detail="Backup not found")
    
    return BackupInfo(**backup_registry[backup_id])


@router.post("/{backup_id}/restore", response_model=RestoreStatus)
async def restore_backup(
    backup_id: str,
    restore_request: BackupRestore,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_permission("settings:manage")),
):
    """
    Restore system from a backup.
    
    WARNING: This is a destructive operation that will overwrite current data.
    Requires 'settings:manage' permission and explicit confirmation.
    """
    if backup_id not in backup_registry:
        raise HTTPException(status_code=404, detail="Backup not found")
    
    backup = backup_registry[backup_id]
    
    if backup["status"] != BackupStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot restore backup with status: {backup['status']}"
        )
    
    if not restore_request.confirm:
        raise HTTPException(
            status_code=400,
            detail="Restore must be explicitly confirmed with confirm=true"
        )
    
    # Log critical action
    log_audit_event(
        action="restore_initiated",
        resource="system/backup",
        user_id=current_user.get("id"),
        details={
            "backup_id": backup_id,
            "restore_database": restore_request.restore_database,
            "restore_files": restore_request.restore_files,
        }
    )
    
    # In production, this would run the actual restore
    # For safety, we return a placeholder status
    
    return RestoreStatus(
        backup_id=backup_id,
        status=BackupStatus.PENDING,
        started_at=datetime.utcnow(),
        steps_completed=["initiated"],
    )


@router.delete("/{backup_id}")
async def delete_backup(
    backup_id: str,
    current_user: dict = Depends(require_permission("settings:manage")),
):
    """
    Delete a backup file.
    
    Requires 'settings:manage' permission.
    """
    if backup_id not in backup_registry:
        raise HTTPException(status_code=404, detail="Backup not found")
    
    backup = backup_registry[backup_id]
    
    # Delete backup file
    if backup.get("file_path"):
        try:
            os.remove(backup["file_path"])
        except OSError:
            pass
    
    # Remove from registry
    del backup_registry[backup_id]
    
    log_audit_event(
        action="backup_deleted",
        resource="system/backup",
        user_id=current_user.get("id"),
        details={"backup_id": backup_id}
    )
    
    return {"message": "Backup deleted successfully"}


@router.post("/schedule")
async def schedule_backup(
    cron_expression: str,
    backup_type: BackupType = BackupType.FULL,
    retention_days: int = 30,
    current_user: dict = Depends(require_permission("settings:manage")),
):
    """
    Schedule automated backups.
    
    Args:
        cron_expression: Cron expression for backup schedule
        backup_type: Type of backup to perform
        retention_days: Number of days to keep backups
    
    Requires 'settings:manage' permission.
    """
    # In production, this would integrate with a scheduler
    # like Celery Beat, APScheduler, or external cron
    
    schedule_config = {
        "cron": cron_expression,
        "backup_type": backup_type.value,
        "retention_days": retention_days,
        "created_by": current_user.get("id"),
        "created_at": datetime.utcnow().isoformat(),
    }
    
    log_audit_event(
        action="backup_scheduled",
        resource="system/backup",
        user_id=current_user.get("id"),
        details=schedule_config
    )
    
    return {
        "message": "Backup schedule configured",
        "schedule": schedule_config,
    }


@router.get("/retention/status")
async def get_retention_status(
    current_user: dict = Depends(require_permission("settings:read")),
):
    """
    Get backup retention status and storage usage.
    """
    backup_dir = get_backup_directory()
    
    total_size = 0
    backup_count = 0
    
    for backup in backup_registry.values():
        if backup.get("size_bytes"):
            total_size += backup["size_bytes"]
            backup_count += 1
    
    return {
        "total_backups": backup_count,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "backup_directory": str(backup_dir),
        "retention_days": int(os.getenv("BACKUP_RETENTION_DAYS", "30")),
    }
