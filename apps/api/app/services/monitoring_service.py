"""
Monitoring service for Synthesize.io API.

Provides system health, performance metrics, and resource monitoring.
"""
import psutil
from typing import Optional


def get_cpu_usage() -> float:
    """Get current CPU usage percentage."""
    try:
        return psutil.cpu_percent(interval=0.1)
    except Exception:
        return 0.0


def get_memory_usage() -> float:
    """Get current memory usage percentage."""
    try:
        return psutil.virtual_memory().percent
    except Exception:
        return 0.0


def get_disk_usage(path: str = '/') -> float:
    """Get disk usage percentage for specified path."""
    try:
        return psutil.disk_usage(path).percent
    except Exception:
        return 0.0


def get_api_latency() -> float:
    """Get average API latency in milliseconds."""
    # In production, this would read from metrics collection
    return 45.0


def check_database_health(db) -> bool:
    """Check if database connection is healthy."""
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def check_redis_health() -> bool:
    """Check if Redis connection is healthy."""
    try:
        import redis
        from app.core.config import settings
        client = redis.from_url(settings.REDIS_URL)
        client.ping()
        client.close()
        return True
    except Exception:
        return False


def check_celery_health() -> bool:
    """Check if Celery workers are available."""
    try:
        from app.celery_app import celery_app
        stats = celery_app.control.inspect().stats()
        return stats is not None and len(stats) > 0
    except Exception:
        return False


def check_resource_thresholds() -> dict:
    """Check if system resources are within acceptable thresholds."""
    cpu = get_cpu_usage()
    memory = get_memory_usage()
    disk = get_disk_usage()
    
    status = "healthy"
    warnings = []
    
    if cpu > 90:
        status = "critical"
        warnings.append("CPU usage critical")
    elif cpu > 70:
        if status != "critical":
            status = "warning"
        warnings.append("CPU usage high")
    
    if memory > 90:
        status = "critical"
        warnings.append("Memory usage critical")
    elif memory > 80:
        if status != "critical":
            status = "warning"
        warnings.append("Memory usage high")
    
    if disk > 90:
        status = "critical"
        warnings.append("Disk usage critical")
    elif disk > 80:
        if status != "critical":
            status = "warning"
        warnings.append("Disk usage high")
    
    return {
        "status": status,
        "cpu_percent": cpu,
        "memory_percent": memory,
        "disk_percent": disk,
        "warnings": warnings,
    }


def aggregate_api_metrics(metrics: list[dict]) -> dict:
    """Aggregate API metrics from a list of request metrics."""
    if not metrics:
        return {
            "total_requests": 0,
            "average_response_time": 0,
            "error_count": 0,
            "error_rate": 0,
        }
    
    total = len(metrics)
    errors = sum(1 for m in metrics if m.get("status_code", 200) >= 400)
    avg_time = sum(m.get("response_time", 0) for m in metrics) / total
    
    return {
        "total_requests": total,
        "average_response_time": avg_time,
        "error_count": errors,
        "error_rate": errors / total if total > 0 else 0,
    }


def calculate_percentile(values: list[float], percentile: int) -> float:
    """Calculate the specified percentile of a list of values."""
    if not values:
        return 0.0
    
    sorted_values = sorted(values)
    index = int(len(sorted_values) * percentile / 100)
    index = min(index, len(sorted_values) - 1)
    
    return sorted_values[index]


def calculate_average_latency(latencies: list[float]) -> float:
    """Calculate average latency from a list of latency values."""
    if not latencies:
        return 0.0
    return sum(latencies) / len(latencies)


def aggregate_metrics(metrics: list[dict]) -> dict:
    """Aggregate API metrics from a list of request metrics. Alias for aggregate_api_metrics."""
    return aggregate_api_metrics(metrics)
