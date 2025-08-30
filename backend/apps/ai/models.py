from django.db import models

# Import conversation models
from .conversation.storage import ConversationModel

# Re-export for Django admin and migrations
__all__ = ['ConversationModel']
