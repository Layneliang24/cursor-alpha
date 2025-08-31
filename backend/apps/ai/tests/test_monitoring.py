"""
监控功能测试
"""

import json
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from ..monitoring_models import (
    ServiceHealthRecord, PerformanceMetric, SystemAlert,
    ServiceHealthStatus
)
from ..config_models import AIProvider
from ..services.monitoring_service import MonitoringService, RealTimeMetrics, ServiceStatus

User = get_user_model()


class ServiceHealthRecordTest(TestCase):
    """服务健康记录模型测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = AIProvider.objects.create(
            provider_type='openai',
            display_name='OpenAI',
            is_active=True,
            created_by=self.user
        )
    
    def test_create_health_record(self):
        """测试创建健康记录"""
        record = ServiceHealthRecord.objects.create(
            service_name='test-service',
            provider=self.provider,
            status=ServiceHealthStatus.HEALTHY,
            is_healthy=True,
            response_time=0.5,
            check_type='health_check'
        )
        
        self.assertEqual(record.service_name, 'test-service')
        self.assertEqual(record.provider, self.provider)
        self.assertEqual(record.status, ServiceHealthStatus.HEALTHY)
        self.assertTrue(record.is_healthy)
        self.assertEqual(record.response_time, 0.5)
        self.assertEqual(record.check_type, 'health_check')
    
    def test_get_latest_status(self):
        """测试获取最新状态"""
        # 创建多个记录
        ServiceHealthRecord.objects.create(
            service_name='test-service',
            status=ServiceHealthStatus.UNHEALTHY,
            is_healthy=False,
            response_time=1.0
        )
        
        latest_record = ServiceHealthRecord.objects.create(
            service_name='test-service',
            status=ServiceHealthStatus.HEALTHY,
            is_healthy=True,
            response_time=0.3
        )
        
        # 获取最新状态
        result = ServiceHealthRecord.get_latest_status('test-service')
        self.assertEqual(result.id, latest_record.id)
        self.assertEqual(result.status, ServiceHealthStatus.HEALTHY)
    
    def test_get_uptime_percentage(self):
        """测试运行时间百分比计算"""
        base_time = timezone.now() - timedelta(hours=2)
        
        # 创建测试记录（80%健康）
        for i in range(10):
            is_healthy = i < 8  # 前8个健康，后2个不健康
            ServiceHealthRecord.objects.create(
                service_name='test-service',
                is_healthy=is_healthy,
                check_timestamp=base_time + timedelta(minutes=i * 10)
            )
        
        uptime = ServiceHealthRecord.get_uptime_percentage('test-service', hours=24)
        self.assertEqual(uptime, 80.0)
    
    def test_cleanup_old_records(self):
        """测试清理旧记录"""
        # 创建旧记录
        old_time = timezone.now() - timedelta(days=10)
        ServiceHealthRecord.objects.create(
            service_name='old-service',
            check_timestamp=old_time
        )
        
        # 创建新记录
        ServiceHealthRecord.objects.create(
            service_name='new-service'
        )
        
        # 清理7天前的记录
        deleted_count = ServiceHealthRecord.cleanup_old_records(days=7)
        
        self.assertEqual(deleted_count, 1)
        self.assertEqual(ServiceHealthRecord.objects.count(), 1)
        self.assertTrue(ServiceHealthRecord.objects.filter(service_name='new-service').exists())


class PerformanceMetricTest(TestCase):
    """性能指标模型测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = AIProvider.objects.create(
            provider_type='openai',
            display_name='OpenAI',
            is_active=True,
            created_by=self.user
        )
    
    def test_create_performance_metric(self):
        """测试创建性能指标"""
        period_start = timezone.now() - timedelta(hours=1)
        period_end = timezone.now()
        
        metric = PerformanceMetric.objects.create(
            service_name='test-service',
            provider=self.provider,
            period_start=period_start,
            period_end=period_end,
            total_requests=100,
            successful_requests=95,
            failed_requests=5,
            avg_response_time=0.5,
            total_input_tokens=1000,
            total_output_tokens=500
        )
        
        # 检查自动计算的字段
        self.assertAlmostEqual(metric.qps, 100 / 3600, places=6)  # 100请求/3600秒
        self.assertEqual(metric.error_rate, 5.0)  # 5/100 * 100%
        self.assertEqual(metric.success_rate, 95.0)  # 95/100 * 100%
    
    def test_get_service_summary(self):
        """测试服务性能摘要"""
        base_time = timezone.now() - timedelta(hours=2)
        
        # 创建测试指标
        for i in range(3):
            PerformanceMetric.objects.create(
                service_name='test-service',
                period_start=base_time + timedelta(hours=i),
                period_end=base_time + timedelta(hours=i+1),
                total_requests=50,
                successful_requests=45,
                failed_requests=5,
                avg_response_time=0.5 + i * 0.1,
                qps=50.0,
                error_rate=10.0,
                total_cost=1.0
            )
        
        summary = PerformanceMetric.get_service_summary('test-service', hours=24)
        
        self.assertEqual(summary['service_name'], 'test-service')
        self.assertEqual(summary['total_requests'], 150)  # 50 * 3
        self.assertEqual(summary['avg_qps'], 50.0)
        self.assertEqual(summary['avg_error_rate'], 10.0)
        self.assertEqual(summary['total_cost'], 3.0)  # 1.0 * 3
    
    def test_cleanup_old_metrics(self):
        """测试清理旧指标"""
        # 创建旧指标
        old_time = timezone.now() - timedelta(days=40)
        PerformanceMetric.objects.create(
            service_name='old-service',
            period_start=old_time,
            period_end=old_time + timedelta(hours=1),
            timestamp=old_time
        )
        
        # 创建新指标
        PerformanceMetric.objects.create(
            service_name='new-service',
            period_start=timezone.now() - timedelta(hours=1),
            period_end=timezone.now()
        )
        
        # 清理30天前的指标
        deleted_count = PerformanceMetric.cleanup_old_metrics(days=30)
        
        self.assertEqual(deleted_count, 1)
        self.assertEqual(PerformanceMetric.objects.count(), 1)
        self.assertTrue(PerformanceMetric.objects.filter(service_name='new-service').exists())


class SystemAlertTest(TestCase):
    """系统告警模型测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = AIProvider.objects.create(
            provider_type='openai',
            display_name='OpenAI',
            is_active=True,
            created_by=self.user
        )
    
    def test_create_alert(self):
        """测试创建告警"""
        alert = SystemAlert.create_alert(
            alert_type='service_down',
            title='服务下线',
            message='OpenAI服务无法访问',
            level=SystemAlert.AlertLevel.CRITICAL,
            service_name='openai-service',
            provider=self.provider,
            error_code=500
        )
        
        self.assertEqual(alert.alert_type, 'service_down')
        self.assertEqual(alert.title, '服务下线')
        self.assertEqual(alert.level, SystemAlert.AlertLevel.CRITICAL)
        self.assertEqual(alert.service_name, 'openai-service')
        self.assertEqual(alert.provider, self.provider)
        self.assertEqual(alert.metadata['error_code'], 500)
    
    def test_resolve_alert(self):
        """测试解决告警"""
        alert = SystemAlert.create_alert(
            alert_type='test_alert',
            title='测试告警',
            message='这是一个测试告警'
        )
        
        # 解决告警
        alert.resolve('问题已修复')
        
        self.assertEqual(alert.status, SystemAlert.AlertStatus.RESOLVED)
        self.assertIsNotNone(alert.resolved_at)
        self.assertIn('解决说明: 问题已修复', alert.message)
    
    def test_acknowledge_alert(self):
        """测试确认告警"""
        alert = SystemAlert.create_alert(
            alert_type='test_alert',
            title='测试告警',
            message='这是一个测试告警'
        )
        
        # 确认告警
        alert.acknowledge(self.user)
        
        self.assertEqual(alert.status, SystemAlert.AlertStatus.ACKNOWLEDGED)
        self.assertEqual(alert.metadata['acknowledged_by'], self.user.username)
        self.assertIn('acknowledged_at', alert.metadata)
    
    def test_get_active_alerts(self):
        """测试获取活跃告警"""
        # 创建活跃告警
        SystemAlert.create_alert(
            alert_type='active_alert',
            title='活跃告警',
            message='这是一个活跃告警'
        )
        
        # 创建已解决告警
        resolved_alert = SystemAlert.create_alert(
            alert_type='resolved_alert',
            title='已解决告警',
            message='这是一个已解决告警'
        )
        resolved_alert.resolve()
        
        # 获取活跃告警
        active_alerts = SystemAlert.get_active_alerts()
        
        self.assertEqual(active_alerts.count(), 1)
        self.assertEqual(active_alerts.first().alert_type, 'active_alert')


class MonitoringServiceTest(TransactionTestCase):
    """监控服务测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = AIProvider.objects.create(
            provider_type='openai',
            display_name='OpenAI',
            is_active=True,
            created_by=self.user
        )
        
        self.monitoring_service = MonitoringService()
    
    def test_record_api_call(self):
        """测试记录API调用"""
        self.monitoring_service.record_api_call(
            service_name='test-service',
            success=True,
            response_time=0.5,
            input_tokens=100,
            output_tokens=50,
            cost=0.01
        )
        
        # 检查实时数据
        self.assertIn('test-service', self.monitoring_service._real_time_data)
        metrics = self.monitoring_service._real_time_data['test-service']
        self.assertEqual(metrics.total_requests, 1)
        self.assertEqual(metrics.failed_requests, 0)
        
        # 检查请求历史
        self.assertIn('test-service', self.monitoring_service._request_history)
        self.assertEqual(len(self.monitoring_service._request_history['test-service']), 1)
    
    def test_get_service_status(self):
        """测试获取服务状态"""
        # 模拟健康监控器中的服务
        from ..services.health_monitor import ServiceHealth, HealthStatus
        
        mock_health = ServiceHealth(
            service_name='test-service',
            status=HealthStatus.HEALTHY,
            is_healthy=True,
            response_time=0.5,
            last_check=timezone.now()
        )
        
        with patch.object(self.monitoring_service.health_monitor, 'get_health', return_value=mock_health):
            status = self.monitoring_service.get_service_status('test-service')
            
            self.assertIsNotNone(status)
            self.assertEqual(status.service_name, 'test-service')
            self.assertTrue(status.is_healthy)
            self.assertEqual(status.response_time, 0.5)
    
    def test_get_system_overview(self):
        """测试获取系统概览"""
        # 创建一些测试数据
        ServiceHealthRecord.objects.create(
            service_name='test-service',
            is_healthy=True,
            response_time=0.5
        )
        
        overview = self.monitoring_service.get_system_overview()
        
        self.assertIn('timestamp', overview)
        self.assertIn('health_summary', overview)
        self.assertIn('alerts', overview)
        self.assertIn('performance', overview)
        self.assertIn('services', overview)
    
    def test_cleanup_old_data(self):
        """测试数据清理"""
        # 创建旧数据
        old_time = timezone.now() - timedelta(days=10)
        ServiceHealthRecord.objects.create(
            service_name='old-service',
            check_timestamp=old_time
        )
        
        # 执行清理
        result = self.monitoring_service.cleanup_old_data(days=7)
        
        self.assertIn('health_records', result)
        self.assertGreaterEqual(result['health_records'], 1)


class MonitoringAPITest(APITestCase):
    """监控API测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
        self.provider = AIProvider.objects.create(
            provider_type='openai',
            display_name='OpenAI',
            is_active=True,
            created_by=self.user
        )
        
        # 创建测试数据
        ServiceHealthRecord.objects.create(
            service_name='test-service',
            provider=self.provider,
            status=ServiceHealthStatus.HEALTHY,
            is_healthy=True,
            response_time=0.5
        )
    
    def test_get_overview_unauthorized(self):
        """测试未授权访问概览"""
        response = self.client.get('/api/v1/ai/monitoring/overview/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_overview_authorized(self):
        """测试授权访问概览"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/ai/monitoring/overview/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('timestamp', data)
        self.assertIn('health_summary', data)
    
    def test_get_services(self):
        """测试获取服务列表"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/ai/monitoring/services/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('services', data)
        self.assertIn('total_services', data)
        self.assertIn('timestamp', data)
    
    def test_get_service_status(self):
        """测试获取特定服务状态"""
        self.client.force_authenticate(user=self.user)
        
        # 模拟服务状态
        with patch('apps.ai.services.monitoring_service.monitoring_service.get_service_status') as mock_get_status:
            mock_status = ServiceStatus(
                service_name='test-service',
                is_healthy=True,
                status='healthy',
                response_time=0.5
            )
            mock_get_status.return_value = mock_status
            
            response = self.client.get('/api/v1/ai/monitoring/test-service/service_status/')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            self.assertEqual(data['service_name'], 'test-service')
            self.assertTrue(data['is_healthy'])
    
    def test_get_service_history(self):
        """测试获取服务历史"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/ai/monitoring/test-service/service_history/?hours=24')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['service_name'], 'test-service')
        self.assertEqual(data['hours'], 24)
        self.assertIn('history', data)
    
    def test_get_alerts(self):
        """测试获取告警"""
        self.client.force_authenticate(user=self.user)
        
        # 创建测试告警
        SystemAlert.create_alert(
            alert_type='test_alert',
            title='测试告警',
            message='这是一个测试告警',
            service_name='test-service',
            provider=self.provider
        )
        
        response = self.client.get('/api/v1/ai/monitoring/alerts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('alerts', data)
        self.assertGreater(data['total_alerts'], 0)
    
    def test_health_check(self):
        """测试强制健康检查"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/api/v1/ai/monitoring/health_check/', {
            'service_name': 'test-service'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['message'], '健康检查完成')
        self.assertIn('result', data)
    
    def test_cleanup_data_unauthorized(self):
        """测试非管理员清理数据"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/api/v1/ai/monitoring/cleanup_data/', {
            'days': 7
        })
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_cleanup_data_authorized(self):
        """测试管理员清理数据"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post('/api/v1/ai/monitoring/cleanup_data/', {
            'days': 7
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('result', data)
    
    def test_metrics_summary(self):
        """测试获取指标摘要"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/ai/monitoring/metrics_summary/?hours=24')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['period_hours'], 24)
        self.assertIn('health_checks', data)
        self.assertIn('services', data)
        self.assertIn('alerts', data)


class RealTimeMetricsTest(TestCase):
    """实时指标测试"""
    
    def test_real_time_metrics_creation(self):
        """测试实时指标创建"""
        metrics = RealTimeMetrics(
            service_name='test-service',
            timestamp=timezone.now(),
            qps=10.5,
            avg_response_time=0.5,
            error_rate=2.0,
            total_requests=100
        )
        
        self.assertEqual(metrics.service_name, 'test-service')
        self.assertEqual(metrics.qps, 10.5)
        self.assertEqual(metrics.avg_response_time, 0.5)
        self.assertEqual(metrics.error_rate, 2.0)
        self.assertEqual(metrics.total_requests, 100)
    
    def test_to_dict_conversion(self):
        """测试转换为字典"""
        timestamp = timezone.now()
        metrics = RealTimeMetrics(
            service_name='test-service',
            timestamp=timestamp,
            qps=10.5
        )
        
        data = metrics.to_dict()
        
        self.assertEqual(data['service_name'], 'test-service')
        self.assertEqual(data['timestamp'], timestamp.isoformat())
        self.assertEqual(data['qps'], 10.5)


class ServiceStatusTest(TestCase):
    """服务状态测试"""
    
    def test_service_status_creation(self):
        """测试服务状态创建"""
        timestamp = timezone.now()
        metrics = RealTimeMetrics(
            service_name='test-service',
            timestamp=timestamp
        )
        
        status = ServiceStatus(
            service_name='test-service',
            provider_name='OpenAI',
            is_healthy=True,
            status='healthy',
            response_time=0.5,
            uptime_percentage=99.9,
            last_check=timestamp,
            metrics=metrics
        )
        
        self.assertEqual(status.service_name, 'test-service')
        self.assertEqual(status.provider_name, 'OpenAI')
        self.assertTrue(status.is_healthy)
        self.assertEqual(status.uptime_percentage, 99.9)
        self.assertIsNotNone(status.metrics)
    
    def test_to_dict_with_metrics(self):
        """测试包含指标的字典转换"""
        timestamp = timezone.now()
        metrics = RealTimeMetrics(
            service_name='test-service',
            timestamp=timestamp
        )
        
        status = ServiceStatus(
            service_name='test-service',
            is_healthy=True,
            last_check=timestamp,
            metrics=metrics
        )
        
        data = status.to_dict()
        
        self.assertEqual(data['service_name'], 'test-service')
        self.assertTrue(data['is_healthy'])
        self.assertEqual(data['last_check'], timestamp.isoformat())
        self.assertIn('metrics', data)
        self.assertEqual(data['metrics']['service_name'], 'test-service')

