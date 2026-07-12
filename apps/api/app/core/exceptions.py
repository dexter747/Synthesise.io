"""
Custom exceptions for Synthesize.io API.
"""
from typing import Any, Dict, Optional


class SynthesizeException(Exception):
    """Base exception for all Synthesize.io errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


# =============================================================================
# AUTHENTICATION ERRORS (401)
# =============================================================================

class AuthenticationError(SynthesizeException):
    """Authentication failed."""
    
    def __init__(self, message: str = "Authentication required", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class InvalidCredentialsError(AuthenticationError):
    """Invalid email or password."""
    
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(
            message=message,
            details={"hint": "Please check your credentials and try again"}
        )


class InvalidTokenError(AuthenticationError):
    """Invalid or expired token."""
    
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message=message)


class TokenExpiredError(AuthenticationError):
    """Token has expired."""
    
    def __init__(self):
        super().__init__(
            message="Token has expired",
            details={"hint": "Please refresh your token or log in again"}
        )


class SessionExpiredError(AuthenticationError):
    """Session has expired."""
    
    def __init__(self):
        super().__init__(
            message="Your session has expired",
            details={"hint": "Please log in again"}
        )


# =============================================================================
# AUTHORIZATION ERRORS (403)
# =============================================================================

class AuthorizationError(SynthesizeException):
    """User is not authorized to perform this action."""
    
    def __init__(self, message: str = "You are not authorized to perform this action"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403
        )


class InsufficientPermissionsError(AuthorizationError):
    """User lacks required permissions."""
    
    def __init__(self, required_permission: Optional[str] = None):
        message = "Insufficient permissions"
        details = {}
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(message=message)
        self.details = details


class SubscriptionRequiredError(AuthorizationError):
    """Action requires a higher subscription tier."""
    
    def __init__(self, required_tier: str, current_tier: str):
        super().__init__(
            message=f"This feature requires a {required_tier} subscription"
        )
        self.code = "SUBSCRIPTION_REQUIRED"
        self.details = {
            "required_tier": required_tier,
            "current_tier": current_tier,
            "upgrade_url": "/pricing"
        }


class QuotaExceededError(AuthorizationError):
    """User has exceeded their quota."""
    
    def __init__(self, quota_type: str, limit: int, used: int):
        super().__init__(
            message=f"You have exceeded your {quota_type} quota"
        )
        self.code = "QUOTA_EXCEEDED"
        self.details = {
            "quota_type": quota_type,
            "limit": limit,
            "used": used,
            "upgrade_url": "/pricing"
        }


class AccountSuspendedError(AuthorizationError):
    """User account has been suspended."""
    
    def __init__(self, reason: Optional[str] = None):
        super().__init__(
            message="Your account has been suspended"
        )
        self.code = "ACCOUNT_SUSPENDED"
        if reason:
            self.details["reason"] = reason


# =============================================================================
# NOT FOUND ERRORS (404)
# =============================================================================

class NotFoundError(SynthesizeException):
    """Requested resource was not found."""
    
    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with ID '{identifier}' not found"
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details={"resource": resource}
        )


class UserNotFoundError(NotFoundError):
    """User was not found."""
    
    def __init__(self, identifier: Optional[str] = None):
        super().__init__("User", identifier)


class DatasetNotFoundError(NotFoundError):
    """Dataset was not found."""
    
    def __init__(self, identifier: Optional[str] = None):
        super().__init__("Dataset", identifier)


class OrganizationNotFoundError(NotFoundError):
    """Organization was not found."""
    
    def __init__(self, identifier: Optional[str] = None):
        super().__init__("Organization", identifier)


class SubscriptionNotFoundError(NotFoundError):
    """Subscription was not found."""
    
    def __init__(self, identifier: Optional[str] = None):
        super().__init__("Subscription", identifier)


class JobNotFoundError(NotFoundError):
    """Generation job was not found."""
    
    def __init__(self, identifier: Optional[str] = None):
        super().__init__("Generation job", identifier)


# =============================================================================
# VALIDATION ERRORS (400)
# =============================================================================

class ValidationError(SynthesizeException):
    """Request validation failed."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        _details = details or {}
        if field:
            _details["field"] = field
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=_details
        )


class InvalidInputError(ValidationError):
    """Invalid input data."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message=message, field=field)


class DuplicateError(ValidationError):
    """Resource already exists."""
    
    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            message=f"{resource} with {field} '{value}' already exists",
            field=field,
            details={"resource": resource, "field": field}
        )
        self.code = "DUPLICATE_ERROR"
        self.status_code = 409


class EmailAlreadyExistsError(DuplicateError):
    """Email is already registered."""
    
    def __init__(self, email: str):
        super().__init__("User", "email", email)


class InvalidPasswordError(ValidationError):
    """Password does not meet requirements."""
    
    def __init__(self, message: str = "Password does not meet requirements"):
        super().__init__(
            message=message,
            field="password",
            details={
                "requirements": {
                    "min_length": 8,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_number": True,
                }
            }
        )


# =============================================================================
# RATE LIMITING ERRORS (429)
# =============================================================================

class RateLimitError(SynthesizeException):
    """Rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded. Please slow down.",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={
                "retry_after": retry_after,
                "hint": f"Please wait {retry_after} seconds before retrying"
            }
        )


# =============================================================================
# PAYMENT ERRORS (402)
# =============================================================================

class PaymentError(SynthesizeException):
    """Payment processing error."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="PAYMENT_ERROR",
            status_code=402,
            details=details
        )


class PaymentFailedError(PaymentError):
    """Payment transaction failed."""
    
    def __init__(self, reason: Optional[str] = None):
        message = "Payment failed"
        if reason:
            message = f"Payment failed: {reason}"
        super().__init__(message=message)


class InvalidPaymentMethodError(PaymentError):
    """Invalid payment method."""
    
    def __init__(self):
        super().__init__(message="Invalid or expired payment method")


# =============================================================================
# EXTERNAL SERVICE ERRORS (502, 503)
# =============================================================================

class ExternalServiceError(SynthesizeException):
    """External service error."""
    
    def __init__(self, service: str, message: str = "External service error"):
        super().__init__(
            message=f"{service}: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details={"service": service}
        )


class LLMServiceError(ExternalServiceError):
    """LLM (Claude) API error."""
    
    def __init__(self, message: str = "LLM service error"):
        super().__init__("LLM Service", message)


class PaymentGatewayError(ExternalServiceError):
    """Payment gateway error."""
    
    def __init__(self, gateway: str, message: str = "Payment gateway error"):
        super().__init__(f"Payment Gateway ({gateway})", message)


class ServiceUnavailableError(SynthesizeException):
    """Service temporarily unavailable."""
    
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(
            message=message,
            code="SERVICE_UNAVAILABLE",
            status_code=503,
            details={"hint": "Please try again later"}
        )


# =============================================================================
# GENERATION ERRORS
# =============================================================================

class GenerationError(SynthesizeException):
    """Data generation error."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="GENERATION_ERROR",
            status_code=500,
            details=details
        )


class SchemaExtractionError(GenerationError):
    """Failed to extract schema from description."""
    
    def __init__(self, message: str = "Could not extract schema from description"):
        super().__init__(
            message=message,
            details={"hint": "Please provide a clearer description of your data requirements"}
        )


class DataGenerationError(GenerationError):
    """Failed to generate data."""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Data generation failed: {reason}"
        )


class DatasetExpiredError(SynthesizeException):
    """Dataset has expired and is no longer available."""
    
    def __init__(self, dataset_id: str):
        super().__init__(
            message="Dataset has expired",
            code="DATASET_EXPIRED",
            status_code=410,
            details={"dataset_id": dataset_id, "hint": "Expired datasets are automatically deleted"}
        )
