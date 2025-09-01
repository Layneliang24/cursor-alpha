from django.db import models

# Import conversation models
from .conversation.storage import ConversationModel

# Import config models
from .config_models import (
    AIProvider, APIKey, AIModel, PromptTemplate, ModelConfig, TokenUsage,
    FailoverStrategy, FailoverRule, FallbackAuditLog, UsageQuota, ProviderHealthStatus
)

# Import monitoring models
from .monitoring_models import (
    ServiceHealthRecord, PerformanceMetric, SystemAlert
)

# Re-export for Django admin and migrations
__all__ = [
    'ConversationModel',
    'AIProvider', 'APIKey', 'AIModel', 'PromptTemplate', 'ModelConfig', 'TokenUsage',
    'FailoverStrategy', 'FailoverRule', 'FallbackAuditLog', 'UsageQuota', 'ProviderHealthStatus',
    'ServiceHealthRecord', 'PerformanceMetric', 'SystemAlert'
]

