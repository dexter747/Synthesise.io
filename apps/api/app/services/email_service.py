"""
Email service for sending emails via SMTP.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_user = getattr(settings, 'SMTP_USER', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.from_email = getattr(settings, 'SMTP_FROM_EMAIL', 'noreply@synthesize.io')
        self.from_name = getattr(settings, 'SMTP_FROM_NAME', 'Synthesize.io')
        self.frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """Send an email."""
        # If SMTP is not configured, log the email instead
        if not self.smtp_user or not self.smtp_password:
            logger.warning(f"SMTP not configured. Email would be sent to {to_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body: {text_body or html_body}")
            return True
        
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email
            
            # Add text and HTML parts
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                message.attach(part1)
            
            part2 = MIMEText(html_body, 'html')
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_verification_email(self, email: str, token: str) -> bool:
        """Send email verification link."""
        verify_url = f"{self.frontend_url}/auth/verify-email?token={token}"
        
        subject = "Verify your email address"
        
        text_body = f"""
Hello,

Thank you for registering with Synthesize.io!

Please verify your email address by clicking the link below:

{verify_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
The Synthesize.io Team
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #14b8a6 0%, #10b981 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #14b8a6; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Synthesize.io!</h1>
        </div>
        <div class="content">
            <p>Thank you for registering with Synthesize.io!</p>
            <p>Please verify your email address by clicking the button below:</p>
            <a href="{verify_url}" class="button">Verify Email Address</a>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #14b8a6;">{verify_url}</p>
            <p style="margin-top: 30px; font-size: 14px; color: #666;">
                This link will expire in 24 hours.
            </p>
            <p style="font-size: 14px; color: #666;">
                If you didn't create an account, please ignore this email.
            </p>
        </div>
        <div class="footer">
            <p>&copy; 2025 Synthesize.io. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return self._send_email(email, subject, html_body, text_body)
    
    def send_password_reset_email(self, email: str, token: str) -> bool:
        """Send password reset link."""
        reset_url = f"{self.frontend_url}/auth/reset-password?token={token}"
        
        subject = "Reset your password"
        
        text_body = f"""
Hello,

We received a request to reset your password for your Synthesize.io account.

Click the link below to reset your password:

{reset_url}

This link will expire in 1 hour.

If you didn't request a password reset, please ignore this email and your password will remain unchanged.

Best regards,
The Synthesize.io Team
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #14b8a6 0%, #10b981 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #14b8a6; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Reset Your Password</h1>
        </div>
        <div class="content">
            <p>We received a request to reset your password for your Synthesize.io account.</p>
            <p>Click the button below to reset your password:</p>
            <a href="{reset_url}" class="button">Reset Password</a>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #14b8a6;">{reset_url}</p>
            <p style="margin-top: 30px; font-size: 14px; color: #666;">
                This link will expire in 1 hour.
            </p>
            <p style="font-size: 14px; color: #666;">
                If you didn't request a password reset, please ignore this email and your password will remain unchanged.
            </p>
        </div>
        <div class="footer">
            <p>&copy; 2025 Synthesize.io. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return self._send_email(email, subject, html_body, text_body)
    
    def send_welcome_email(self, email: str, first_name: Optional[str] = None) -> bool:
        """Send welcome email after email verification."""
        name = first_name or "there"
        
        subject = "Welcome to Synthesize.io!"
        
        text_body = f"""
Hello {name},

Welcome to Synthesize.io! We're excited to have you on board.

Your email has been verified and your account is now fully activated.

You can now:
- Create and manage synthetic datasets
- Access powerful AI features
- Integrate with your applications via API

Get started: {self.frontend_url}/dashboard

If you have any questions, feel free to reach out to our support team.

Best regards,
The Synthesize.io Team
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #14b8a6 0%, #10b981 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #14b8a6; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #666; }}
        .features {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .feature {{ margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Synthesize.io!</h1>
        </div>
        <div class="content">
            <p>Hello {name},</p>
            <p>Welcome to Synthesize.io! We're excited to have you on board.</p>
            <p>Your email has been verified and your account is now fully activated.</p>
            
            <div class="features">
                <h3>You can now:</h3>
                <div class="feature">✨ Create and manage synthetic datasets</div>
                <div class="feature">🤖 Access powerful AI features</div>
                <div class="feature">🔌 Integrate with your applications via API</div>
            </div>
            
            <a href="{self.frontend_url}/dashboard" class="button">Get Started</a>
            
            <p style="margin-top: 30px; font-size: 14px; color: #666;">
                If you have any questions, feel free to reach out to our support team.
            </p>
        </div>
        <div class="footer">
            <p>&copy; 2025 Synthesize.io. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return self._send_email(email, subject, html_body, text_body)


# Singleton instance
email_service = EmailService()
