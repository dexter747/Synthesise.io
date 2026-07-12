"""
Notification tasks - Email, webhooks, and all notification triggers
"""
from app.celery_app import celery_app
from typing import Dict, Any, Optional
import logging
import os
import smtplib
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

logger = logging.getLogger(__name__)

# Email configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@synthesize.io")
FROM_NAME = os.getenv("FROM_NAME", "Synthesize.io")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def _send_email_sync(to: str, subject: str, html_body: str, text_body: str = None) -> bool:
    """Synchronous email sending via SMTP"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = to
        
        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            if SMTP_USER and SMTP_PASSWORD:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, to, msg.as_string())
        
        logger.info(f"Email sent successfully to {to}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return False


def _get_base_email_template(content: str, title: str = "Synthesize.io") -> str:
    """Get base HTML email template"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ background: #ffffff; padding: 30px; border: 1px solid #e1e1e1; border-top: none; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; border: 1px solid #e1e1e1; border-top: none; border-radius: 0 0 8px 8px; }}
            .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 15px 0; }}
            .button:hover {{ background: #5a6fd6; }}
            .alert {{ padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .alert-success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }}
            .alert-warning {{ background: #fff3cd; border: 1px solid #ffeeba; color: #856404; }}
            .alert-danger {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }}
            .details {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .details table {{ width: 100%; border-collapse: collapse; }}
            .details td {{ padding: 8px 0; border-bottom: 1px solid #e1e1e1; }}
            .details td:first-child {{ font-weight: bold; width: 40%; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔮 Synthesize.io</h1>
            </div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                <p>© {datetime.utcnow().year} Synthesize.io - AI-Powered Synthetic Data Generation</p>
                <p>
                    <a href="{FRONTEND_URL}/dashboard">Dashboard</a> |
                    <a href="{FRONTEND_URL}/settings">Settings</a> |
                    <a href="{FRONTEND_URL}/help">Help</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """


# ============================================================================
# GENERIC EMAIL TASK
# ============================================================================

@celery_app.task(name="app.tasks.notifications.send_email")
def send_email(to: str, subject: str, body: str, template: str = None) -> Dict[str, Any]:
    """Send email notification"""
    logger.info(f"Sending email to {to}: {subject}")
    
    html_body = _get_base_email_template(body)
    success = _send_email_sync(to, subject, html_body, body)
    
    return {
        "status": "sent" if success else "failed",
        "to": to,
        "subject": subject
    }


# ============================================================================
# PAYMENT NOTIFICATION TASKS
# ============================================================================

@celery_app.task(name="app.tasks.notifications.send_payment_confirmation_email")
def send_payment_confirmation_email(user_id: str, invoice_id: str) -> Dict[str, Any]:
    """Send payment confirmation email with invoice details"""
    from app.core.database import SessionLocal
    from app.models import User, Invoice, Subscription, SubscriptionPlan
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not user or not invoice:
            return {"status": "failed", "error": "User or invoice not found"}
        
        subscription = db.query(Subscription).filter(
            Subscription.id == invoice.subscription_id
        ).first()
        
        plan = None
        if subscription:
            plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.id == subscription.plan_id
            ).first()
        
        plan_name = plan.name if plan else "Subscription"
        amount = invoice.total_cents / 100
        currency_symbol = "₹" if invoice.currency == "INR" else "$"
        
        content = f"""
        <h2>Payment Successful! 🎉</h2>
        <p>Dear {user.first_name or 'Customer'},</p>
        <p>Thank you for your payment. Your subscription has been activated.</p>
        
        <div class="alert alert-success">
            <strong>Transaction Complete</strong><br>
            Your payment has been processed successfully.
        </div>
        
        <div class="details">
            <h3>Order Details</h3>
            <table>
                <tr><td>Invoice Number</td><td>{invoice.invoice_number}</td></tr>
                <tr><td>Plan</td><td>{plan_name}</td></tr>
                <tr><td>Amount</td><td>{currency_symbol}{amount:.2f} {invoice.currency}</td></tr>
                <tr><td>Payment Date</td><td>{invoice.paid_at.strftime('%B %d, %Y') if invoice.paid_at else 'N/A'}</td></tr>
                <tr><td>Next Billing Date</td><td>{subscription.current_period_end.strftime('%B %d, %Y') if subscription else 'N/A'}</td></tr>
            </table>
        </div>
        
        <p style="text-align: center;">
            <a href="{FRONTEND_URL}/billing" class="button">View Billing History</a>
        </p>
        
        <p>If you have any questions, please don't hesitate to contact our support team.</p>
        <p>Best regards,<br>The Synthesize.io Team</p>
        """
        
        html_body = _get_base_email_template(content, "Payment Confirmation")
        success = _send_email_sync(
            user.email,
            f"Payment Confirmation - Invoice #{invoice.invoice_number}",
            html_body
        )
        
        return {"status": "sent" if success else "failed", "to": user.email}
    finally:
        db.close()


@celery_app.task(name="app.tasks.notifications.send_payment_failed_email")
def send_payment_failed_email(user_id: str, retry_attempt: int, next_retry_days: int) -> Dict[str, Any]:
    """Send payment failed notification with retry information"""
    from app.core.database import SessionLocal
    from app.models import User, Subscription, SubscriptionPlan
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "failed", "error": "User not found"}
        
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()
        
        plan = None
        if subscription:
            plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.id == subscription.plan_id
            ).first()
        
        plan_name = plan.name if plan else "your subscription"
        
        content = f"""
        <h2>Payment Failed ⚠️</h2>
        <p>Dear {user.first_name or 'Customer'},</p>
        <p>We were unable to process your payment for {plan_name}.</p>
        
        <div class="alert alert-warning">
            <strong>Action Required</strong><br>
            Please update your payment method to continue your subscription.
        </div>
        
        <div class="details">
            <h3>Retry Information</h3>
            <table>
                <tr><td>Retry Attempt</td><td>{retry_attempt} of 3</td></tr>
                <tr><td>Next Retry</td><td>In {next_retry_days} day(s)</td></tr>
                <tr><td>Subscription Status</td><td>Past Due</td></tr>
            </table>
        </div>
        
        <p>Your subscription features remain active during the retry period. To avoid service interruption, please:</p>
        <ul>
            <li>Ensure your payment method has sufficient funds</li>
            <li>Update your card if it has expired</li>
            <li>Contact your bank if payments are being blocked</li>
        </ul>
        
        <p style="text-align: center;">
            <a href="{FRONTEND_URL}/billing" class="button">Update Payment Method</a>
        </p>
        
        <p>If you have any questions, please contact our support team.</p>
        <p>Best regards,<br>The Synthesize.io Team</p>
        """
        
        html_body = _get_base_email_template(content, "Payment Failed")
        success = _send_email_sync(
            user.email,
            f"Payment Failed - Action Required (Attempt {retry_attempt}/3)",
            html_body
        )
        
        return {"status": "sent" if success else "failed", "to": user.email}
    finally:
        db.close()


@celery_app.task(name="app.tasks.notifications.send_renewal_failed_email")
def send_renewal_failed_email(user_id: str, grace_period_days: int) -> Dict[str, Any]:
    """Send subscription renewal failed notification with grace period info"""
    from app.core.database import SessionLocal
    from app.models import User, Subscription, SubscriptionPlan
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "failed", "error": "User not found"}
        
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()
        
        plan_name = "your subscription"
        if subscription:
            plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.id == subscription.plan_id
            ).first()
            if plan:
                plan_name = plan.name
        
        content = f"""
        <h2>Subscription Renewal Failed ⚠️</h2>
        <p>Dear {user.first_name or 'Customer'},</p>
        <p>We were unable to renew your {plan_name} subscription.</p>
        
        <div class="alert alert-danger">
            <strong>Grace Period Active</strong><br>
            You have {grace_period_days} days to update your payment method before your subscription is suspended.
        </div>
        
        <p>During the grace period:</p>
        <ul>
            <li>Your subscription features will remain active</li>
            <li>We will attempt to charge your payment method again</li>
            <li>You can manually retry the payment at any time</li>
        </ul>
        
        <p style="text-align: center;">
            <a href="{FRONTEND_URL}/billing" class="button">Update Payment Method</a>
        </p>
        
        <p>If you no longer wish to continue your subscription, no action is needed and it will expire after the grace period.</p>
        <p>Best regards,<br>The Synthesize.io Team</p>
        """
        
        html_body = _get_base_email_template(content, "Renewal Failed")
        success = _send_email_sync(
            user.email,
            f"Subscription Renewal Failed - {grace_period_days} Days Grace Period",
            html_body
        )
        
        return {"status": "sent" if success else "failed", "to": user.email}
    finally:
        db.close()


@celery_app.task(name="app.tasks.notifications.send_renewal_success_email")
def send_renewal_success_email(user_id: str, invoice_id: str) -> Dict[str, Any]:
    """Send subscription renewal success notification"""
    from app.core.database import SessionLocal
    from app.models import User, Invoice, Subscription, SubscriptionPlan
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not user or not invoice:
            return {"status": "failed", "error": "User or invoice not found"}
        
        subscription = db.query(Subscription).filter(
            Subscription.id == invoice.subscription_id
        ).first()
        
        plan = None
        if subscription:
            plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.id == subscription.plan_id
            ).first()
        
        plan_name = plan.name if plan else "Subscription"
        amount = invoice.total_cents / 100
        currency_symbol = "₹" if invoice.currency == "INR" else "$"
        
        content = f"""
        <h2>Subscription Renewed! 🎉</h2>
        <p>Dear {user.first_name or 'Customer'},</p>
        <p>Your {plan_name} subscription has been successfully renewed.</p>
        
        <div class="alert alert-success">
            <strong>Renewal Complete</strong><br>
            Your subscription is active until {subscription.current_period_end.strftime('%B %d, %Y') if subscription else 'N/A'}.
        </div>
        
        <div class="details">
            <h3>Renewal Details</h3>
            <table>
                <tr><td>Invoice Number</td><td>{invoice.invoice_number}</td></tr>
                <tr><td>Plan</td><td>{plan_name}</td></tr>
                <tr><td>Amount</td><td>{currency_symbol}{amount:.2f} {invoice.currency}</td></tr>
                <tr><td>Renewal Date</td><td>{invoice.paid_at.strftime('%B %d, %Y') if invoice.paid_at else 'N/A'}</td></tr>
                <tr><td>Next Billing Date</td><td>{subscription.current_period_end.strftime('%B %d, %Y') if subscription else 'N/A'}</td></tr>
            </table>
        </div>
        
        <p style="text-align: center;">
            <a href="{FRONTEND_URL}/dashboard" class="button">Go to Dashboard</a>
        </p>
        
        <p>Thank you for continuing with Synthesize.io!</p>
        <p>Best regards,<br>The Synthesize.io Team</p>
        """
        
        html_body = _get_base_email_template(content, "Subscription Renewed")
        success = _send_email_sync(
            user.email,
            f"Subscription Renewed - Invoice #{invoice.invoice_number}",
            html_body
        )
        
        return {"status": "sent" if success else "failed", "to": user.email}
    finally:
        db.close()


# ============================================================================
# USAGE NOTIFICATION TASKS
# ============================================================================

@celery_app.task(name="app.tasks.notifications.send_usage_warning_email")
def send_usage_warning_email(user_id: str, usage_type: str, percentage: int, limit: int, current: int) -> Dict[str, Any]:
    """Send usage warning notification (80%, 90%, 100%)"""
    from app.core.database import SessionLocal
    from app.models import User
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "failed", "error": "User not found"}
        
        alert_class = "alert-warning" if percentage < 100 else "alert-danger"
        alert_text = "Approaching Limit" if percentage < 100 else "Limit Reached"
        
        usage_labels = {
            "rows": "Data Rows",
            "storage": "Storage",
            "api_calls": "API Calls",
            "jobs": "Generation Jobs"
        }
        usage_label = usage_labels.get(usage_type, usage_type.replace("_", " ").title())
        
        content = f"""
        <h2>Usage Alert: {percentage}% {usage_label} Used</h2>
        <p>Dear {user.first_name or 'Customer'},</p>
        <p>You've used {percentage}% of your monthly {usage_label.lower()} quota.</p>
        
        <div class="alert {alert_class}">
            <strong>{alert_text}</strong><br>
            {"Your quota has been exceeded. Further operations may be limited." if percentage >= 100 else f"You're approaching your limit. Consider upgrading your plan."}
        </div>
        
        <div class="details">
            <h3>Usage Details</h3>
            <table>
                <tr><td>Current Usage</td><td>{current:,}</td></tr>
                <tr><td>Monthly Limit</td><td>{limit:,}</td></tr>
                <tr><td>Remaining</td><td>{max(0, limit - current):,}</td></tr>
                <tr><td>Usage Percentage</td><td>{percentage}%</td></tr>
            </table>
        </div>
        
        <p style="text-align: center;">
            <a href="{FRONTEND_URL}/pricing" class="button">Upgrade Plan</a>
            <a href="{FRONTEND_URL}/usage" class="button" style="background: #6c757d; margin-left: 10px;">View Usage</a>
        </p>
        
        <p>Best regards,<br>The Synthesize.io Team</p>
        """
        
        html_body = _get_base_email_template(content, "Usage Alert")
        success = _send_email_sync(
            user.email,
            f"Usage Alert: {percentage}% of {usage_label} Used",
            html_body
        )
        
        return {"status": "sent" if success else "failed", "to": user.email}
    finally:
        db.close()


# ============================================================================
# JOB NOTIFICATION TASKS
# ============================================================================

@celery_app.task(name="app.tasks.notifications.send_job_completion_email")
def send_job_completion_email(user_id: str, job_id: str, job_name: str, row_count: int, download_url: str) -> Dict[str, Any]:
    """Send job completion notification"""
    from app.core.database import SessionLocal
    from app.models import User
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "failed", "error": "User not found"}
        
        content = f"""
        <h2>Data Generation Complete! 🎉</h2>
        <p>Dear {user.first_name or 'Customer'},</p>
        <p>Your data generation job has completed successfully.</p>
        
        <div class="alert alert-success">
            <strong>Job Complete</strong><br>
            Your synthetic data is ready for download.
        </div>
        
        <div class="details">
            <h3>Job Details</h3>
            <table>
                <tr><td>Job Name</td><td>{job_name}</td></tr>
                <tr><td>Job ID</td><td>{job_id[:8]}...</td></tr>
                <tr><td>Rows Generated</td><td>{row_count:,}</td></tr>
                <tr><td>Status</td><td>Completed</td></tr>
            </table>
        </div>
        
        <p style="text-align: center;">
            <a href="{download_url}" class="button">Download Data</a>
            <a href="{FRONTEND_URL}/jobs/{job_id}" class="button" style="background: #6c757d; margin-left: 10px;">View Job Details</a>
        </p>
        
        <p>Best regards,<br>The Synthesize.io Team</p>
        """
        
        html_body = _get_base_email_template(content, "Job Complete")
        success = _send_email_sync(
            user.email,
            f"Data Generation Complete - {job_name}",
            html_body
        )
        
        return {"status": "sent" if success else "failed", "to": user.email}
    finally:
        db.close()


@celery_app.task(name="app.tasks.notifications.send_job_failed_email")
def send_job_failed_email(user_id: str, job_id: str, job_name: str, error_message: str) -> Dict[str, Any]:
    """Send job failure notification"""
    from app.core.database import SessionLocal
    from app.models import User
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "failed", "error": "User not found"}
        
        content = f"""
        <h2>Data Generation Failed ❌</h2>
        <p>Dear {user.first_name or 'Customer'},</p>
        <p>Unfortunately, your data generation job encountered an error.</p>
        
        <div class="alert alert-danger">
            <strong>Job Failed</strong><br>
            {error_message}
        </div>
        
        <div class="details">
            <h3>Job Details</h3>
            <table>
                <tr><td>Job Name</td><td>{job_name}</td></tr>
                <tr><td>Job ID</td><td>{job_id[:8]}...</td></tr>
                <tr><td>Status</td><td>Failed</td></tr>
            </table>
        </div>
        
        <p>You can try:</p>
        <ul>
            <li>Reviewing and simplifying your data schema</li>
            <li>Reducing the number of rows requested</li>
            <li>Checking for any unsupported data types</li>
        </ul>
        
        <p style="text-align: center;">
            <a href="{FRONTEND_URL}/jobs/{job_id}" class="button">View Job Details</a>
            <a href="{FRONTEND_URL}/help" class="button" style="background: #6c757d; margin-left: 10px;">Get Help</a>
        </p>
        
        <p>If the problem persists, please contact our support team.</p>
        <p>Best regards,<br>The Synthesize.io Team</p>
        """
        
        html_body = _get_base_email_template(content, "Job Failed")
        success = _send_email_sync(
            user.email,
            f"Data Generation Failed - {job_name}",
            html_body
        )
        
        return {"status": "sent" if success else "failed", "to": user.email}
    finally:
        db.close()


@celery_app.task(name="app.tasks.notifications.send_completion_notification")
def send_completion_notification(user_id: str, job_id: str, result: Dict[str, Any]) -> None:
    """Notify user when their generation job completes (legacy support)"""
    logger.info(f"Sending completion notification for job {job_id} to user {user_id}")
    
    if result.get("status") == "completed":
        send_job_completion_email.delay(
            user_id,
            job_id,
            result.get("name", "Data Generation Job"),
            result.get("row_count", 0),
            result.get("download_url", f"{FRONTEND_URL}/jobs/{job_id}")
        )
    elif result.get("status") == "failed":
        send_job_failed_email.delay(
            user_id,
            job_id,
            result.get("name", "Data Generation Job"),
            result.get("error", "An unexpected error occurred")
        )


# ============================================================================
# WEBHOOK TASKS
# ============================================================================

@celery_app.task(name="app.tasks.notifications.trigger_webhook")
def trigger_webhook(webhook_url: str, event: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Trigger webhook for events like job completion"""
    logger.info(f"Triggering webhook {webhook_url} for event {event}")
    
    try:
        import httpx
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                webhook_url,
                json={
                    "event": event,
                    "timestamp": datetime.utcnow().isoformat(),
                    "payload": payload
                },
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Synthesize.io-Webhook/1.0",
                    "X-Synthesize-Event": event
                }
            )
            response.raise_for_status()
            
            return {
                "status": "triggered",
                "webhook_url": webhook_url,
                "event": event,
                "response_code": response.status_code
            }
    except Exception as e:
        logger.error(f"Webhook trigger failed: {e}")
        return {
            "status": "failed",
            "webhook_url": webhook_url,
            "event": event,
            "error": str(e)
        }


# ============================================================================
# SUBSCRIPTION NOTIFICATION TASKS
# ============================================================================

@celery_app.task(name="app.tasks.notifications.send_subscription_activated_email")
def send_subscription_activated_email(user_id: str, plan_name: str) -> Dict[str, Any]:
    """Send subscription activation welcome email"""
    from app.core.database import SessionLocal
    from app.models import User
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "failed", "error": "User not found"}
        
        content = f"""
        <h2>Welcome to {plan_name}! 🚀</h2>
        <p>Dear {user.first_name or 'Customer'},</p>
        <p>Your {plan_name} subscription is now active! You have access to all the features included in your plan.</p>
        
        <div class="alert alert-success">
            <strong>Subscription Active</strong><br>
            You're all set to start generating synthetic data.
        </div>
        
        <h3>What's Next?</h3>
        <ul>
            <li><strong>Create Your First Dataset</strong> - Describe your data needs and let AI generate it</li>
            <li><strong>Explore Templates</strong> - Use pre-built schemas for common use cases</li>
            <li><strong>Set Up API Access</strong> - Integrate data generation into your workflow</li>
        </ul>
        
        <p style="text-align: center;">
            <a href="{FRONTEND_URL}/dashboard" class="button">Start Generating Data</a>
        </p>
        
        <p>If you have any questions, our support team is here to help.</p>
        <p>Best regards,<br>The Synthesize.io Team</p>
        """
        
        html_body = _get_base_email_template(content, f"Welcome to {plan_name}")
        success = _send_email_sync(
            user.email,
            f"Welcome to {plan_name} - Your Subscription is Active!",
            html_body
        )
        
        return {"status": "sent" if success else "failed", "to": user.email}
    finally:
        db.close()


@celery_app.task(name="app.tasks.notifications.send_subscription_expiring_email")
def send_subscription_expiring_email(user_id: str, days_remaining: int) -> Dict[str, Any]:
    """Send subscription expiring soon notification"""
    from app.core.database import SessionLocal
    from app.models import User, Subscription, SubscriptionPlan
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "failed", "error": "User not found"}
        
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()
        
        plan_name = "your subscription"
        if subscription:
            plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.id == subscription.plan_id
            ).first()
            if plan:
                plan_name = plan.name
        
        content = f"""
        <h2>Subscription Expiring Soon ⏰</h2>
        <p>Dear {user.first_name or 'Customer'},</p>
        <p>Your {plan_name} subscription will expire in {days_remaining} day(s).</p>
        
        <div class="alert alert-warning">
            <strong>Action Recommended</strong><br>
            Ensure your subscription renews to avoid service interruption.
        </div>
        
        <p>Your subscription will automatically renew if you have a valid payment method on file. If you'd like to make any changes:</p>
        <ul>
            <li>Update your payment method</li>
            <li>Change your subscription plan</li>
            <li>Cancel auto-renewal</li>
        </ul>
        
        <p style="text-align: center;">
            <a href="{FRONTEND_URL}/billing" class="button">Manage Subscription</a>
        </p>
        
        <p>Best regards,<br>The Synthesize.io Team</p>
        """
        
        html_body = _get_base_email_template(content, "Subscription Expiring")
        success = _send_email_sync(
            user.email,
            f"Subscription Expiring in {days_remaining} Day(s)",
            html_body
        )
        
        return {"status": "sent" if success else "failed", "to": user.email}
    finally:
        db.close()


@celery_app.task(name="app.tasks.notifications.send_subscription_cancelled_email")
def send_subscription_cancelled_email(user_id: str, end_date: str) -> Dict[str, Any]:
    """Send subscription cancellation confirmation"""
    from app.core.database import SessionLocal
    from app.models import User
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "failed", "error": "User not found"}
        
        content = f"""
        <h2>Subscription Cancelled</h2>
        <p>Dear {user.first_name or 'Customer'},</p>
        <p>Your subscription has been cancelled as requested.</p>
        
        <div class="details">
            <h3>What Happens Next</h3>
            <table>
                <tr><td>Access Until</td><td>{end_date}</td></tr>
                <tr><td>After Expiry</td><td>Account reverts to Free tier</td></tr>
            </table>
        </div>
        
        <p>You'll continue to have access to your paid features until {end_date}. After that, your account will automatically switch to the Free tier.</p>
        
        <p>We're sorry to see you go! If you change your mind, you can resubscribe at any time.</p>
        
        <p style="text-align: center;">
            <a href="{FRONTEND_URL}/pricing" class="button">Resubscribe</a>
        </p>
        
        <p>Best regards,<br>The Synthesize.io Team</p>
        """
        
        html_body = _get_base_email_template(content, "Subscription Cancelled")
        success = _send_email_sync(
            user.email,
            "Subscription Cancellation Confirmed",
            html_body
        )
        
        return {"status": "sent" if success else "failed", "to": user.email}
    finally:
        db.close()
