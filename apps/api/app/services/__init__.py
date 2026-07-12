"""
Services layer for Synthesize.io API.

This module exports all service classes for business logic.
"""

from app.services.user_service import UserService, get_user_service
from app.services.auth_service import AuthService, get_auth_service
from app.services.organization_service import OrganizationService, get_organization_service
from app.services.dataset_service import DatasetService, get_dataset_service
from app.services.generation_service import GenerationService, get_generation_service
from app.services.subscription_service import SubscriptionService, get_subscription_service
from app.services.api_key_service import APIKeyService, get_api_key_service
from app.services.webhook_service import WebhookService, get_webhook_service

# Re-export existing services
from app.services.llm_service import LLMService
from app.services.data_factory import DataFactory


__all__ = [
    # Service classes
    "UserService",
    "AuthService",
    "OrganizationService",
    "DatasetService",
    "GenerationService",
    "SubscriptionService",
    "APIKeyService",
    "WebhookService",
    "LLMService",
    "DataFactory",
    
    # Factory functions
    "get_user_service",
    "get_auth_service",
    "get_organization_service",
    "get_dataset_service",
    "get_generation_service",
    "get_subscription_service",
    "get_api_key_service",
    "get_webhook_service",
]
