"""
Monitoring and Observability API Endpoints
Provides metrics, alerts, and system status for operations teams.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import psutil
import time
import redis
from app.core.config import settings
from app.core.security import require_permission


router = APIRouter()


class SystemStatus(BaseModel):
    status: str
    version: str
    uptime_seconds: float
    timestamp: datetime


class DatabaseStatus(BaseModel):
    connected: bool
    pool_size: int
    active_connections: int
    response_time_ms: Optional[float] =    database_size_mb: Optional[float]


class RedisStatus(BaseModel):
    connected: bool
    used_memory_mb: float
    total_keys: int
    connected_clients: int


class StorageStatus(BaseModel):
    connected: bool
    bucket_name: str
    total_objects: int
    total_size_mb: float


class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_io_bytes: int


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertRule(BaseModel):
    id: str
    name: str
    description: str
    severity: AlertSeverity
    metric: str
    threshold: float
    comparison: str  # "gt", "lt", "eq"
    enabled: bool
    last_triggered: Optional[datetime] = None


class AlertInstance(BaseModel):
    id: str
    rule_id: str
    severity: AlertSeverity
    message: str
    value: float
    threshold: float
    triggered_at: datetime
    acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


# Alert rules storage (in production, use database)
alert_rules: Dict[str, AlertRule] = {
    "high_cpu": AlertRule(
        id="high_cpu",
        name="High CPU Usage",
        description="Alert when CPU usage exceeds 80%",
        severity=AlertSeverity.WARNING,
        metric="cpu_percent",
        threshold=80.0,
        comparison="gt",
        enabled=True
    ),
    "high_memory": AlertRule(
        id="high_memory",
        name="High Memory Usage",
        description="Alert when memory usage exceeds 85%",
        severity=AlertSeverity.WARNING,
        metric="memory_percent",
        threshold=85.0,
        comparison="gt",
        enabled=True
    ),
    "disk_space_low": AlertRule(
        id="disk_space_low",
        name="Low Disk Space",
        description="Alert when disk usage exceeds 90%",
        severity=AlertSeverity.ERROR,
        metric="disk_percent",
        threshold=90.0,
        comparison="gt",
        enabled=True
    ),
    "database_connections_high": AlertRule(
        id="database_connections_high",
        name="High Database Connections",
        description="Alert when database connections exceed 80% of pool",
        severity=AlertSeverity.WARNING,
        metric="db_pool_usage_percent",
        threshold=80.0,
        comparison="gt",
        enabled=True
    ),
}

alert_instances: List[AlertInstance] = []
app_start_time = time.time()


@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """
    Get overall system status.
    """
    return SystemStatus(
        status="healthy",
        version=settings.APP_VERSION,
        uptime_seconds=time.time() - app_start_time,
        timestamp=datetime.utcnow()
    )


@router.get("/metrics", response_model=SystemMetrics)
async def get_system_metrics(
    current_user: dict = Depends(require_permission("dashboard:admin"))
):
    """
    Get real-time system metrics.
    """
    # CPU metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Memory metrics
    memory = psutil.virtual_memory()
    
    # Disk metrics
    disk = psutil.disk_usage('/')
    
    # Network I/O
    net_io = psutil.net_io_counters()
    network_io_bytes = net_io.bytes_sent + net_io.bytes_recv if net_io else 0
    
    return SystemMetrics(
        cpu_percent=cpu_percent,
        memory_percent=memory.percent,
        memory_used_mb=memory.used / (1024 * 1024),
        memory_total_mb=memory.total / (1024 * 1024),
        disk_percent=disk.percent,
        disk_used_gb=disk.used / (1024 * 1024 * 1024),
        disk_total_gb=disk.total / (1024 * 1024 * 1024),
        network_io_bytes=network_io_bytes
    )


@router.get("/database", response_model=DatabaseStatus)
async def get_database_status(
    current_user: dict = Depends(require_permission("dashboard:admin"))
):
    """
    Get database connection status.
    """
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        start_time = time.time()
        
        # Test connection
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        
        response_time = (time.time() - start_time) * 1000  # ms
        
        # Get connection pool info
        pool_size = settings.DATABASE_POOL_SIZE
        active_connections = 0  # Would need to query pg_stat_activity
        
        return DatabaseStatus(
            connected=True,
            pool_size=pool_size,
            active_connections=active_connections,
            response_time_ms=response_time
        )
    except Exception as e:
        return DatabaseStatus(
            connected=False,
            pool_size=settings.DATABASE_POOL_SIZE,
            active_connections=0,
            response_time_ms=None
        )


@router.get("/redis", response_model=RedisStatus)
async def get_redis_status(
    current_user: dict = Depends(require_permission("dashboard:admin"))
):
    """
    Get Redis connection status.
    """
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        
        info = redis_client.info()
        
        return RedisStatus(
            connected=True,
            used_memory_mb=float(info.get("used_memory", 0)) / (1024 * 1024),
            total_keys=redis_client.dbsize(),
            connected_clients=int(info.get("connected_clients", 0))
        )
    except Exception as e:
        return RedisStatus(
            connected=False,
            used_memory_mb=0,
            total_keys=0,
            connected_clients=0
        )


@router.get("/alerts/rules", response_model=List[AlertRule])
async def get_alert_rules(
    current_user: dict = Depends(require_permission("settings:read"))
):
    """
    Get all alert rules.
    """
    return list(alert_rules.values())


@router.put("/alerts/rules/{rule_id}")
async def update_alert_rule(
    rule_id: str,
    enabled: bool,
    threshold: Optional[float] = None,
    current_user: dict = Depends(require_permission("settings:manage"))
):
    """
    Update an alert rule.
    """
    if rule_id not in alert_rules:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    rule = alert_rules[rule_id]
    rule.enabled = enabled
    if threshold is not None:
        rule.threshold = threshold
    
    return rule


@router.get("/alerts/instances", response_model=List[AlertInstance])
async def get_alert_instances(
    acknowledged: Optional[bool] = None,
    severity: Optional[AlertSeverity] = None,
    limit: int = 50,
    current_user: dict = Depends(require_permission("dashboard:admin"))
):
    """
    Get alert instances (triggered alerts).
    """
    instances = alert_instances
    
    if acknowledged is not None:
        instances = [i for i in instances if i.acknowledged == acknowledged]
    
    if severity:
        instances = [i for i in instances if i.severity == severity]
    
    return instances[:limit]


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: dict = Depends(require_permission("dashboard:admin"))
):
    """
    Acknowledge an alert.
    """
    for instance in alert_instances:
        if instance.id == alert_id:
            instance.acknowledged = True
            instance.acknowledged_by = current_user.get("id")
            instance.acknowledged_at = datetime.utcnow()
            return instance
    
    raise HTTPException(status_code=404, detail="Alert not found")


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    current_user: dict = Depends(require_permission("dashboard:admin"))
):
    """
    Get a comprehensive dashboard summary for monitoring.
    """
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Check alerts
    active_alerts = len([a for a in alert_instances if not a.acknowledged])
    critical_alerts = len([a for a in alert_instances 
                         if not a.acknowledged and a.severity == AlertSeverity.CRITICAL])
    
    # Calculate health score
    health_score = 100
    if cpu_percent > 80:
        health_score -= 10
    if memory.percent > 85:
        health_score -= 15
    if disk.percent > 90:
        health_score -= 20
    health_score -= critical_alerts * 10
    health_score = max(0, health_score)
    
    return {
        "health_score": health_score,
        "status": "healthy" if health_score >= 70 else "degraded" if health_score >= 40 else "critical",
        "metrics": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent
        },
        "alerts": {
            "active": active_alerts,
            "critical": critical_alerts
        },
        "services": {
            "api": "healthy",
            "database": "healthy",  # Would check actual status
            "redis": "healthy",
            "storage": "healthy"
        }
    }


def check_alerts():
    """
    Background task to check metrics against alert rules.
    Should be run periodically.
    """
    try:
        # Get current metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
        }
        
        # Check each rule
        for rule_id, rule in alert_rules.items():
            if not rule.enabled:
                continue
            
            current_value = metrics.get(rule.metric, 0)
            
            # Check threshold
            triggered = False
            if rule.comparison == "gt" and current_value > rule.threshold:
                triggered = True
            elif rule.comparison == "lt" and current_value < rule.threshold:
                triggered = True
            elif rule.comparison == "eq" and current_value == rule.threshold:
                triggered = True
            
            if triggered:
                # Create alert instance
                alert = AlertInstance(
                    id=f"{rule_id}_{datetime.utcnow().isoformat()}",
                    rule_id=rule_id,
                    severity=rule.severity,
                    message=f"{rule.name}: {rule.metric}={current_value} (threshold: {rule.threshold})",
                    value=current_value,
                    threshold=rule.threshold,
                    triggered_at=datetime.utcnow(),
                    acknowledged=False
                )
                alert_instances.insert(0, alert)
                rule.last_triggered = datetime.utcnow()
        
        # Keep only last 100 alerts
        if len(alert_instances) > 100:
            alert_instances[:] = alert_instances[:100]
            
    except Exception as e:
        # Log error but don't crash
        pass
