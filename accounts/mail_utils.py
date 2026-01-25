import smtplib
import ssl
from email.message import EmailMessage
from django.conf import settings  # ADD THIS IMPORT


def send_otp_email(email, otp, purpose="registration"):
    """Send OTP email with HTML formatting"""
    
    # Get email credentials from Django settings
    gmail_user = settings.EMAIL_HOST_USER
    gmail_password = settings.EMAIL_HOST_PASSWORD
    
    if not gmail_user or not gmail_password:
        print("ERROR: Email credentials not configured in settings.py")
        return False
    
    msg = EmailMessage()
    msg["From"] = gmail_user
    msg["To"] = email

    if purpose == "registration":
        subject = "Verify Your Email - EdTube"
        color = "#667eea"
        title = "🔐 Email Verification"
        message = "Thank you for registering with EdTube! Use the OTP below to verify your email."
    elif purpose == "login":
        subject = "Login Verification - EdTube"
        color = "#48bb78"
        title = "🔐 Login Verification"
        message = "Use the OTP below to verify your login."
    elif purpose == "password_reset":
        subject = "Password Reset - EdTube"
        color = "#f5576c"
        title = "🔑 Password Reset"
        message = "Use the OTP below to reset your password."
    else:
        subject = "Verification Code - EdTube"
        color = "#667eea"
        title = "🔐 Verification Code"
        message = "Use the OTP below to verify your account."

    msg["Subject"] = subject

    html = f"""
    <html>
    <body style="font-family:Arial;background:#f4f4f4;padding:30px;">
        <div style="max-width:600px;margin:auto;background:#fff;border-radius:10px;padding:30px;box-shadow:0 4px 12px rgba(0,0,0,0.1);">
            <div style="text-align:center;margin-bottom:20px;">
                <h2 style="color:#667eea;margin:0;">EdTube</h2>
                <p style="color:#666;margin-top:5px;">Learning Platform</p>
            </div>
            
            <h3 style="color:#333;text-align:center">{title}</h3>
            <p style="color:#555;font-size:16px;line-height:1.6;text-align:center;">{message}</p>

            <div style="
                font-size:36px;
                letter-spacing:8px;
                font-weight:bold;
                color:{color};
                background:#f8f9fa;
                border:2px dashed {color};
                padding:25px;
                text-align:center;
                margin:30px 0;
                border-radius:8px;
                font-family:'Courier New', monospace;
            ">
                {otp}
            </div>

            <div style="background:#f8f9fa;padding:15px;border-radius:8px;margin:20px 0;">
                <p style="margin:0;color:#666;text-align:center;">
                    ⏰ This OTP is valid for <b style="color:{color}">15 minutes</b>
                </p>
            </div>

            <p style="color:#e53e3e;background:#fed7d7;padding:12px;border-radius:6px;text-align:center;font-weight:bold;">
                ⚠️ Do not share this code with anyone.
            </p>

            <hr style="border:none;border-top:1px solid #e2e8f0;margin:25px 0;">
            
            <div style="text-align:center;color:#718096;font-size:14px;">
                <p style="margin:0;">If you didn't request this, please ignore this email.</p>
                <p style="margin:5px 0 0 0;">Need help? Contact: {gmail_user}</p>
                <p style="margin:10px 0 0 0;">© 2026 EdTube. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg.add_alternative(html, subtype="html")

    try:
        # Try SMTP_SSL (port 465) first
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
        print(f"OTP email sent to {email}")
        return True
    except Exception as e:
        print(f"SMTP_SSL failed: {e}")
        
        # Try SMTP with TLS (port 587) as fallback
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(gmail_user, gmail_password)
                server.send_message(msg)
            print(f"OTP email sent to {email} (TLS fallback)")
            return True
        except Exception as e2:
            print(f"SMTP TLS also failed: {e2}")
            return False