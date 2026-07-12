"""
Email utilities for Synthesize.io API.
Handles email template rendering and sending.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict, Any
import logging

from app.core.config import settings


logger = logging.getLogger(__name__)


class EmailTemplate:
    """Email template definitions."""
    
    WELCOME = "welcome"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    QUOTA_WARNING = "quota_warning"
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_CANCELED = "subscription_canceled"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_FAILED = "payment_failed"
    INVOICE_READY = "invoice_ready"
    TEAM_INVITATION = "team_invitation"
    DATASET_DELETION_REMINDER = "dataset_deletion_reminder"
    DATASET_DELETED = "dataset_deleted"


# Email templates (in production, use proper template files)
EMAIL_TEMPLATES: Dict[str, Dict[str, str]] = {
    EmailTemplate.WELCOME: {
        "subject": "Welcome to Synthesize.io!",
        "html": """
            <h1>Welcome to Synthesize.io, {name}!</h1>
            <p>Thank you for joining us. We're excited to help you generate high-quality synthetic data.</p>
            <p>Get started by:</p>
            <ol>
                <li>Describing your data needs in natural language</li>
                <li>Reviewing the extracted schema</li>
                <li>Generating your dataset with one click</li>
            </ol>
            <p><a href="{app_url}/dashboard">Go to Dashboard</a></p>
            <p>If you have any questions, our support team is here to help.</p>
            <p>Best regards,<br>The Synthesize.io Team</p>
        """,
    },
    EmailTemplate.EMAIL_VERIFICATION: {
        "subject": "Verify your email address",
        "html": """
            <h1>Verify your email address</h1>
            <p>Hi {name},</p>
            <p>Please click the link below to verify your email address:</p>
            <p><a href="{verification_url}">Verify Email</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create an account with Synthesize.io, please ignore this email.</p>
            <p>Best regards,<br>The Synthesize.io Team</p>
        """,
    },
    EmailTemplate.PASSWORD_RESET: {
        "subject": "Reset your password",
        "html": """
            <h1>Reset your password</h1>
            <p>Hi {name},</p>
            <p>We received a request to reset your password. Click the link below to set a new password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request a password reset, please ignore this email or contact support if you're concerned.</p>
            <p>Best regards,<br>The Synthesize.io Team</p>
        """,
    },
    EmailTemplate.JOB_COMPLETED: {
        "subject": "Your dataset is ready!",
        "html": """
            <h1>Your dataset is ready!</h1>
            <p>Hi {name},</p>
            <p>Great news! Your dataset "{dataset_name}" has been generated successfully.</p>
            <p><strong>Details:</strong></p>
            <ul>
                <li>Rows: {row_count}</li>
                <li>Size: {file_size}</li>
                <li>Format: {format}</li>
            </ul>
            <p><a href="{download_url}">Download Dataset</a></p>
            <p>Your dataset will be available for {retention_days} days.</p>
            <p>Best regards,<br>The Synthesize.io Team</p>
        """,
    },
    EmailTemplate.JOB_FAILED: {
        "subject": "Dataset generation failed",
        "html": """
            <h1>Dataset generation failed</h1>
            <p>Hi {name},</p>
            <p>Unfortunately, we encountered an issue while generating your dataset.</p>
            <p><strong>Error:</strong> {error_message}</p>
            <p>Please try again or contact support if the issue persists.</p>
            <p><a href="{retry_url}">Try Again</a></p>
            <p>Best regards,<br>The Synthesize.io Team</p>
        """,
    },
    EmailTemplate.QUOTA_WARNING: {
        "subject": "Usage quota warning",
        "html": """
            <h1>You're approaching your usage limit</h1>
            <p>Hi {name},</p>
            <p>You've used {usage_percent}% of your monthly data quota.</p>
            <ul>
                <li>Used: {used}</li>
                <li>Limit: {limit}</li>
            </ul>
            <p>Consider upgrading your plan to avoid service interruption.</p>
            <p><a href="{upgrade_url}">Upgrade Plan</a></p>
            <p>Best regards,<br>The Synthesize.io Team</p>
        """,
    },
    EmailTemplate.PAYMENT_SUCCEEDED: {
        "subject": "Payment received - Thank you!",
        "html": """
            <h1>Payment received</h1>
            <p>Hi {name},</p>
            <p>We've received your payment of {amount}.</p>
            <p><strong>Details:</strong></p>
            <ul>
                <li>Amount: {amount}</li>
                <li>Plan: {plan_name}</li>
                <li>Date: {payment_date}</li>
            </ul>
            <p><a href="{invoice_url}">View Invoice</a></p>
            <p>Thank you for your continued support!</p>
            <p>Best regards,<br>The Synthesize.io Team</p>
        """,
    },
    EmailTemplate.TEAM_INVITATION: {
        "subject": "You've been invited to join {org_name}",
        "html": """
            <h1>Team Invitation</h1>
            <p>Hi,</p>
            <p>{inviter_name} has invited you to join <strong>{org_name}</strong> on Synthesize.io.</p>
            <p>Role: {role}</p>
            <p><a href="{invitation_url}">Accept Invitation</a></p>
            <p>This invitation will expire in 7 days.</p>
            <p>Best regards,<br>The Synthesize.io Team</p>
        """,
    },
    EmailTemplate.DATASET_DELETION_REMINDER: {
        "subject": "Your dataset will be deleted in {days_until_deletion} days",
        "html": """
            <h1>Dataset Deletion Reminder</h1>
            <p>Hi {user_name},</p>
            <p>Your dataset <strong>"{dataset_name}"</strong> will be automatically deleted on <strong>{deletion_date}</strong>.</p>
            <p>To keep your data, please download it before the deletion date.</p>
            <p><a href="{app_url}{download_url}" style="display: inline-block; background-color: #14b8a6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">Download Dataset</a></p>
            <p>After deletion, the dataset cannot be recovered.</p>
            <p>Best regards,<br>The Synthesize.io Team</p>
        """,
    },
    EmailTemplate.DATASET_DELETED: {
        "subject": "Your dataset has been deleted",
        "html": """
            <h1>Dataset Deleted</h1>
            <p>Hi {user_name},</p>
            <p>Your dataset <strong>"{dataset_name}"</strong> has been automatically deleted on {deleted_at}.</p>
            <p>Datasets are automatically deleted after 30 days to manage storage.</p>
            <p>You can always create new datasets from your dashboard.</p>
            <p><a href="{app_url}/dashboard" style="display: inline-block; background-color: #14b8a6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">Go to Dashboard</a></p>
            <p>Best regards,<br>The Synthesize.io Team</p>
        """,
    },
}


def render_email_template(template_name: str, context: Dict[str, Any]) -> tuple:
    """
    Render an email template with the given context.
    
    Args:
        template_name: Name of the template
        context: Template variables
    
    Returns:
        Tuple of (subject, html_body)
    """
    if template_name not in EMAIL_TEMPLATES:
        raise ValueError(f"Unknown email template: {template_name}")
    
    template = EMAIL_TEMPLATES[template_name]
    
    # Add default context
    default_context = {
        "app_url": "https://synthesize.io" if settings.ENVIRONMENT == "production" else "http://localhost:3000",
    }
    full_context = {**default_context, **context}
    
    subject = template["subject"].format(**full_context)
    html = template["html"].format(**full_context)
    
    return subject, html


async def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    from_email: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> bool:
    """
    Send an email.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML body content
        from_email: Sender email (default: settings.SMTP_FROM_EMAIL)
        reply_to: Reply-to address
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured, skipping email send")
        return False
    
    from_email = from_email or settings.SMTP_FROM_EMAIL
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        
        if reply_to:
            msg["Reply-To"] = reply_to
        
        # Attach HTML body
        html_part = MIMEText(html_body, "html")
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(from_email, [to_email], msg.as_string())
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


async def send_template_email(
    to_email: str,
    template_name: str,
    context: Dict[str, Any],
    from_email: Optional[str] = None,
) -> bool:
    """
    Send an email using a template.
    
    Args:
        to_email: Recipient email address
        template_name: Name of the email template
        context: Template variables
        from_email: Sender email (optional)
    
    Returns:
        True if sent successfully
    """
    subject, html_body = render_email_template(template_name, context)
    return await send_email(to_email, subject, html_body, from_email)


# Convenience functions for common emails
async def send_welcome_email(to_email: str, name: str) -> bool:
    """Send welcome email to new user."""
    return await send_template_email(
        to_email,
        EmailTemplate.WELCOME,
        {"name": name}
    )


async def send_verification_email(to_email: str, name: str, verification_url: str) -> bool:
    """Send email verification email."""
    return await send_template_email(
        to_email,
        EmailTemplate.EMAIL_VERIFICATION,
        {"name": name, "verification_url": verification_url}
    )


async def send_password_reset_email(to_email: str, name: str, reset_url: str) -> bool:
    """Send password reset email."""
    return await send_template_email(
        to_email,
        EmailTemplate.PASSWORD_RESET,
        {"name": name, "reset_url": reset_url}
    )


async def send_job_completed_email(
    to_email: str,
    name: str,
    dataset_name: str,
    row_count: int,
    file_size: str,
    format: str,
    download_url: str,
    retention_days: int,
) -> bool:
    """Send job completed notification."""
    return await send_template_email(
        to_email,
        EmailTemplate.JOB_COMPLETED,
        {
            "name": name,
            "dataset_name": dataset_name,
            "row_count": f"{row_count:,}",
            "file_size": file_size,
            "format": format.upper(),
            "download_url": download_url,
            "retention_days": retention_days,
        }
    )


async def send_team_invitation_email(
    to_email: str,
    org_name: str,
    inviter_name: str,
    role: str,
    invitation_url: str,
) -> bool:
    """Send team invitation email."""
    return await send_template_email(
        to_email,
        EmailTemplate.TEAM_INVITATION,
        {
            "org_name": org_name,
            "inviter_name": inviter_name,
            "role": role,
            "invitation_url": invitation_url,
        }
    )
