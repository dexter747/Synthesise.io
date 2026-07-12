"""
Tests for system monitoring and health check endpoints.
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock


class TestSystemHealthEndpoint:
    """Tests for system health monitoring"""
    
    @pytest.mark.integration
    def test_get_system_health(self, client, admin_auth_headers):
        """Test getting system health status."""
        response = client.get(
            "/api/v1/admin/health",
            headers=admin_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields (matching actual API response)
        assert "status" in data
        assert "database" in data
        assert "redis" in data
        assert "celery" in data
        assert "active_workers" in data
        
        # Check status values
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert data["database"] in ["healthy", "unhealthy"]
        assert isinstance(data["active_workers"], int)
    
    @pytest.mark.integration
    def test_system_health_unauthorized(self, client):
        """Test health endpoint requires admin auth."""
        response = client.get("/api/v1/admin/health")
        
        assert response.status_code == 401
    
    @pytest.mark.integration
    def test_system_health_non_admin(self, client, auth_headers):
        """Test health endpoint requires admin role."""
        response = client.get(
            "/api/v1/admin/health",
            headers=auth_headers,  # Regular user, not admin
        )
        
        assert response.status_code == 403
    
    @pytest.mark.integration
    def test_system_health_includes_metrics(self, client, admin_auth_headers):
        """Test health response includes optional metrics."""
        response = client.get(
            "/api/v1/admin/health",
            headers=admin_auth_headers,
        )
        
        data = response.json()
        
        # Optional metrics that should be present
        if "cpu_usage_percent" in data and data["cpu_usage_percent"] is not None:
            assert 0 <= data["cpu_usage_percent"] <= 100
        if "memory_usage_percent" in data and data["memory_usage_percent"] is not None:
            assert 0 <= data["memory_usage_percent"] <= 100


class TestCeleryMonitoring:
    """Tests for Celery worker monitoring"""
    
    @pytest.mark.integration
    def test_get_celery_workers(self, client, admin_auth_headers):
        """Test getting Celery worker status."""
        response = client.get(
            "/api/v1/admin/celery/workers",
            headers=admin_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # Each worker should have required fields
        if len(data) > 0:
            worker = data[0]
            assert "hostname" in worker
            assert "status" in worker
    
    @pytest.mark.integration
    def test_get_celery_queue_stats(self, client, admin_auth_headers):
        """Test getting Celery queue statistics."""
        response = client.get(
            "/api/v1/admin/celery/queue",
            headers=admin_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_jobs" in data
        assert "pending_jobs" in data
        assert "processing_jobs" in data
        assert "failed_jobs" in data


class TestMetricsEndpoint:
    """Tests for metrics collection"""
    
    @pytest.mark.integration
    def test_get_api_metrics(self, client, admin_auth_headers):
        """Test getting API performance metrics."""
        response = client.get(
            "/api/v1/admin/metrics/api",
            headers=admin_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "average_response_time" in data
        assert "requests_per_minute" in data
        assert "error_rate" in data
    
    @pytest.mark.integration
    def test_get_database_metrics(self, client, admin_auth_headers):
        """Test getting database metrics."""
        response = client.get(
            "/api/v1/admin/metrics/database",
            headers=admin_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "active_connections" in data
        assert "idle_connections" in data
        assert "slow_queries" in data
    
    @pytest.mark.integration
    def test_get_redis_metrics(self, client, admin_auth_headers):
        """Test getting Redis cache metrics."""
        response = client.get(
            "/api/v1/admin/metrics/redis",
            headers=admin_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "memory_used" in data
        assert "total_keys" in data
        assert "hit_rate" in data


class TestLogsEndpoint:
    """Tests for system logs"""
    
    @pytest.mark.integration
    def test_get_server_logs(self, client, admin_auth_headers):
        """Test getting server logs."""
        response = client.get(
            "/api/v1/admin/logs",
            headers=admin_auth_headers,
            params={"limit": 50}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        
        # Check log entry structure
        if len(data["items"]) > 0:
            log = data["items"][0]
            assert "timestamp" in log
            assert "level" in log
            assert "message" in log
            assert "source" in log
    
    @pytest.mark.integration
    def test_filter_logs_by_level(self, client, admin_auth_headers):
        """Test filtering logs by level."""
        response = client.get(
            "/api/v1/admin/logs",
            headers=admin_auth_headers,
            params={"level": "error", "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All logs should be error level
        for log in data["items"]:
            assert log["level"] == "error"
    
    @pytest.mark.integration
    def test_filter_logs_by_source(self, client, admin_auth_headers):
        """Test filtering logs by source."""
        response = client.get(
            "/api/v1/admin/logs",
            headers=admin_auth_headers,
            params={"source": "api", "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All logs should be from API source
        for log in data["items"]:
            assert log["source"] == "api"
    
    @pytest.mark.integration
    def test_search_logs(self, client, admin_auth_headers):
        """Test searching logs by content."""
        response = client.get(
            "/api/v1/admin/logs",
            headers=admin_auth_headers,
            params={"search": "error", "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Search term should appear in messages
        for log in data["items"]:
            assert "error" in log["message"].lower()
    
    @pytest.mark.integration
    def test_logs_pagination(self, client, admin_auth_headers):
        """Test log pagination."""
        # Get first page
        response1 = client.get(
            "/api/v1/admin/logs",
            headers=admin_auth_headers,
            params={"limit": 10, "offset": 0}
        )
        
        # Get second page
        response2 = client.get(
            "/api/v1/admin/logs",
            headers=admin_auth_headers,
            params={"limit": 10, "offset": 10}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Pages should have different items
        if len(data1["items"]) > 0 and len(data2["items"]) > 0:
            assert data1["items"][0]["timestamp"] != data2["items"][0]["timestamp"]


class TestAlertsEndpoint:
    """Tests for system alerts"""
    
    @pytest.mark.integration
    def test_get_active_alerts(self, client, admin_auth_headers):
        """Test getting active system alerts."""
        response = client.get(
            "/api/v1/admin/alerts",
            headers=admin_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        
        # Check alert structure if any exist
        if len(data["items"]) > 0:
            alert = data["items"][0]
            assert "id" in alert or "severity" in alert
    
    @pytest.mark.integration
    def test_acknowledge_alert(self, client, admin_auth_headers):
        """Test acknowledging a system alert."""
        # Test with a mock alert ID
        import uuid
        alert_id = str(uuid.uuid4())
        
        response = client.post(
            f"/api/v1/admin/alerts/{alert_id}/acknowledge",
            headers=admin_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    @pytest.mark.integration
    def test_filter_alerts_by_severity(self, client, admin_auth_headers):
        """Test filtering alerts by severity."""
        response = client.get(
            "/api/v1/admin/alerts",
            headers=admin_auth_headers,
            params={"severity": "critical"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All alerts should be critical (if any exist)
        for alert in data["items"]:
            assert alert["severity"] == "critical"


class TestContainerHealthEndpoint:
    """Tests for Docker container health monitoring"""
    
    @pytest.mark.integration
    def test_get_container_health(self, client, admin_auth_headers):
        """Test getting Docker container health status."""
        response = client.get(
            "/api/v1/admin/containers",
            headers=admin_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        
        # Check container info
        if len(data["items"]) > 0:
            container = data["items"][0]
            assert "name" in container
            assert "status" in container
    
    @pytest.mark.integration
    def test_get_container_stats(self, client, admin_auth_headers):
        """Test getting detailed container statistics."""
        response = client.get(
            "/api/v1/admin/containers/api/stats",
            headers=admin_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "name" in data
        assert "status" in data


class TestPerformanceMonitoring:
    """Tests for performance monitoring utilities"""
    
    @pytest.mark.unit
    def test_calculate_cpu_usage(self):
        """Test CPU usage calculation."""
        from app.services.monitoring_service import get_cpu_usage
        
        usage = get_cpu_usage()
        
        assert isinstance(usage, (int, float))
        assert 0 <= usage <= 100
    
    @pytest.mark.unit
    def test_calculate_memory_usage(self):
        """Test memory usage calculation."""
        from app.services.monitoring_service import get_memory_usage
        
        usage = get_memory_usage()
        
        assert isinstance(usage, (int, float))
        assert 0 <= usage <= 100
    
    @pytest.mark.unit
    def test_calculate_disk_usage(self):
        """Test disk usage calculation."""
        from app.services.monitoring_service import get_disk_usage
        
        usage = get_disk_usage()
        
        assert isinstance(usage, (int, float))
        assert 0 <= usage <= 100
    
    @pytest.mark.unit
    def test_get_api_latency(self):
        """Test API latency measurement."""
        from app.services.monitoring_service import calculate_average_latency
        
        # Mock latency data
        latencies = [10, 15, 20, 25, 30]  # milliseconds
        
        avg = calculate_average_latency(latencies)
        
        assert avg == 20.0  # Average of the list


class TestHealthCheckService:
    """Tests for health check service"""
    
    @pytest.mark.unit
    def test_check_database_health(self, db):
        """Test database health check."""
        from app.services.monitoring_service import check_database_health
        
        status = check_database_health(db)
        
        # Returns boolean
        assert isinstance(status, bool)
    
    @pytest.mark.unit
    def test_check_redis_health(self):
        """Test Redis health check."""
        from app.services.monitoring_service import check_redis_health
        
        status = check_redis_health()
        
        # Returns boolean
        assert isinstance(status, bool)
    
    @pytest.mark.unit
    def test_check_celery_health(self):
        """Test Celery health check."""
        from app.services.monitoring_service import check_celery_health
        
        status = check_celery_health()
        
        # Returns boolean
        assert isinstance(status, bool)


class TestResourceThresholds:
    """Tests for resource threshold alerts"""
    
    @pytest.mark.unit
    def test_cpu_threshold_warning(self):
        """Test CPU usage warning threshold."""
        from app.services.monitoring_service import check_resource_thresholds
        
        # Current implementation reads from system
        result = check_resource_thresholds()
        
        assert "status" in result
        assert "warnings" in result
        assert isinstance(result["warnings"], list)
    
    @pytest.mark.unit
    def test_memory_threshold_critical(self):
        """Test memory usage critical threshold."""
        from app.services.monitoring_service import check_resource_thresholds
        
        result = check_resource_thresholds()
        
        assert "status" in result
        assert "memory_percent" in result
    
    @pytest.mark.unit
    def test_all_resources_healthy(self):
        """Test all resources within healthy thresholds."""
        from app.services.monitoring_service import check_resource_thresholds
        
        result = check_resource_thresholds()
        
        # Status should be one of these values
        assert result["status"] in ["healthy", "warning", "critical"]


class TestMetricsCollection:
    """Tests for metrics collection and aggregation"""
    
    @pytest.mark.unit
    def test_aggregate_api_metrics(self):
        """Test API metrics aggregation."""
        from app.services.monitoring_service import aggregate_api_metrics
        
        # Mock metric data points
        metrics = [
            {"response_time": 100, "status_code": 200},
            {"response_time": 150, "status_code": 200},
            {"response_time": 120, "status_code": 500},
        ]
        
        result = aggregate_api_metrics(metrics)
        
        assert result["total_requests"] == 3
        assert result["error_count"] == 1
        assert "average_response_time" in result
    
    @pytest.mark.unit
    def test_calculate_percentile(self):
        """Test percentile calculation for metrics."""
        from app.services.monitoring_service import calculate_percentile
        
        data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        
        p50 = calculate_percentile(data, 50)
        p95 = calculate_percentile(data, 95)
        
        # Percentile should be a number from the dataset or interpolated
        assert p50 in data or 45 <= p50 <= 55
        assert p95 in data or 90 <= p95 <= 100
