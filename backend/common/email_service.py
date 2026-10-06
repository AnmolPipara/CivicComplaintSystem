"""
Email Notification Service for JanSewa Civic Complaint System.
Sends email notifications to citizens at key complaint lifecycle milestones:
1. Complaint Registered (Status: Pending)
2. Work In Progress (Status: Working)
3. Complaint Completed (Status: Resolved)
"""
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger("civic.email")

# In-memory record of sent emails for auditing and verification testing
SENT_EMAILS_LOG = []


def is_email_enabled() -> bool:
    return os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "true").lower() in ("true", "1", "yes")


def get_smtp_config() -> Dict[str, Any]:
    try:
        from dotenv import load_dotenv
        load_dotenv(override=False)
        load_dotenv(".env", override=False)
    except Exception:
        pass

    host = (os.getenv("SMTP_HOST") or "smtp.gmail.com").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    user = (os.getenv("SMTP_USER") or "anmolpipara@gmail.com").strip()
    password = (os.getenv("SMTP_PASSWORD") or "xbzs bzzd yadq jfoa").replace(" ", "").strip()
    from_email = (os.getenv("SMTP_FROM_EMAIL") or f"JanSewa Civic Support <{user}>").strip()
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "from_email": from_email,
        "use_tls": use_tls,
    }


def generate_email_content(
    event_type: str,
    complaint_id: int,
    recipient_name: str,
    category_name: str,
    location: str,
    description: str,
    timestamp: Optional[datetime] = None
) -> tuple[str, str, str]:
    """
    Returns (subject, plain_text, html_body) for the given event type.
    event_type: 'registered', 'working', 'completed'
    """
    time_str = (timestamp or datetime.utcnow()).strftime("%B %d, %Y at %I:%M %p UTC")
    clean_desc = (description or "").strip()
    if len(clean_desc) > 160:
        clean_desc = clean_desc[:157] + "..."

    if event_type == "registered":
        subject = f"[JanSewa #{complaint_id}] Complaint Registered - {category_name}"
        status_label = "Pending Review"
        status_color = "#f59e0b"
        status_bg = "#fef3c7"
        headline = "Your complaint has been successfully registered"
        intro_text = (
            f"Dear {recipient_name},<br><br>"
            f"Thank you for reporting this issue. Your complaint <strong>#{complaint_id}</strong> "
            f"has been submitted to the municipal authority. Our system is assessing priority "
            f"and routing the issue to the appropriate department."
        )
        action_note = "Citizens within 25 km can view and upvote this issue to help prioritize community action."

    elif event_type == "working":
        subject = f"[JanSewa #{complaint_id}] Work Started - {category_name}"
        status_label = "In Progress"
        status_color = "#3b82f6"
        status_bg = "#dbeafe"
        headline = "Work has started on your complaint"
        intro_text = (
            f"Dear {recipient_name},<br><br>"
            f"Great news! A field team has been assigned and has <strong>started work</strong> on your complaint "
            f"<strong>#{complaint_id}</strong>. We are actively working toward resolution."
        )
        action_note = "Voting is now closed for this incident as active resolution has commenced."

    elif event_type == "completed":
        subject = f"[JanSewa #{complaint_id}] Complaint Resolved - {category_name}"
        status_label = "Resolved & Completed"
        status_color = "#10b981"
        status_bg = "#d1fae5"
        headline = "Your complaint has been resolved"
        intro_text = (
            f"Dear {recipient_name},<br><br>"
            f"We are pleased to inform you that complaint <strong>#{complaint_id}</strong> "
            f"has been marked as <strong>resolved and completed</strong>. "
            f"Thank you for helping keep our community clean, safe, and well-maintained!"
        )
        action_note = "You can log in to view the resolution updates and full activity history."

    else:
        subject = f"[JanSewa #{complaint_id}] Status Update: {event_type}"
        status_label = event_type.capitalize()
        status_color = "#6b7280"
        status_bg = "#f3f4f6"
        headline = f"Update on Complaint #{complaint_id}"
        intro_text = f"Dear {recipient_name},<br><br>The status of your complaint #{complaint_id} has been updated to {event_type}."
        action_note = ""

    # Plain text version
    plain_text = (
        f"{headline.upper()}\n\n"
        f"Complaint ID: #{complaint_id}\n"
        f"Category: {category_name}\n"
        f"Location: {location}\n"
        f"Status: {status_label}\n"
        f"Updated: {time_str}\n\n"
        f"Description:\n{clean_desc}\n\n"
        f"{action_note}\n\n"
        f"---\n"
        f"JanSewa Civic Support | Building Better Communities Together\n"
    )

    # Rich responsive HTML template
    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      margin: 0; padding: 0; background-color: #f8fafc; color: #1e293b;
    }}
    .container {{
      max-width: 600px; margin: 30px auto; background: #ffffff; border-radius: 12px;
      overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }}
    .header {{
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      padding: 28px 32px; text-align: left;
    }}
    .brand {{
      color: #38bdf8; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;
      display: inline-block; text-decoration: none;
    }}
    .brand span {{ color: #ffffff; }}
    .tagline {{
      color: #94a3b8; font-size: 13px; margin-top: 4px;
    }}
    .content {{
      padding: 32px;
    }}
    .headline {{
      font-size: 20px; font-weight: 700; color: #0f172a; margin-top: 0; margin-bottom: 12px;
    }}
    .intro {{
      font-size: 15px; line-height: 1.6; color: #475569; margin-bottom: 24px;
    }}
    .card {{
      background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;
      padding: 20px; margin-bottom: 24px;
    }}
    .card-row {{
      display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 14px;
    }}
    .card-label {{ color: #64748b; font-weight: 500; }}
    .card-value {{ color: #0f172a; font-weight: 600; text-align: right; }}
    .badge {{
      display: inline-block; padding: 4px 12px; border-radius: 9999px;
      font-size: 12px; font-weight: 600; color: {status_color}; background-color: {status_bg};
    }}
    .note {{
      font-size: 13px; color: #64748b; background: #f1f5f9; padding: 12px 16px;
      border-radius: 6px; border-left: 4px solid {status_color}; margin-bottom: 24px;
    }}
    .footer {{
      background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 20px 32px;
      text-align: center; font-size: 12px; color: #94a3b8;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="brand">Jan<span>Sewa</span></div>
      <div class="tagline">Civic Complaint & Community Prioritization System</div>
    </div>
    <div class="content">
      <div style="margin-bottom: 16px;">
        <span class="badge">{status_label}</span>
      </div>
      <h1 class="headline">{headline}</h1>
      <div class="intro">{intro_text}</div>

      <div class="card">
        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
          <tr>
            <td style="padding: 6px 0; color: #64748b; font-weight: 500;">Complaint ID</td>
            <td style="padding: 6px 0; color: #0f172a; font-weight: 600; text-align: right;">#{complaint_id}</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; color: #64748b; font-weight: 500;">Category</td>
            <td style="padding: 6px 0; color: #0f172a; font-weight: 600; text-align: right;">{category_name}</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; color: #64748b; font-weight: 500;">Location</td>
            <td style="padding: 6px 0; color: #0f172a; font-weight: 600; text-align: right;">{location}</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; color: #64748b; font-weight: 500;">Reported Description</td>
            <td style="padding: 6px 0; color: #334155; text-align: right; max-width: 300px;">{clean_desc}</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; color: #64748b; font-weight: 500;">Timestamp</td>
            <td style="padding: 6px 0; color: #64748b; text-align: right;">{time_str}</td>
          </tr>
        </table>
      </div>

      {f'<div class="note">{action_note}</div>' if action_note else ''}
    </div>
    <div class="footer">
      This is an automated notification from JanSewa Civic Portal.<br>
      Please do not reply directly to this email.
    </div>
  </div>
</body>
</html>
"""
    return subject, plain_text, html_body


def send_complaint_notification(
    event_type: str,
    complaint_id: int,
    recipient_email: str,
    recipient_name: str,
    category_name: str,
    location: str,
    description: str,
    timestamp: Optional[datetime] = None
) -> bool:
    """
    Sends an email notification to the citizen.
    If SMTP credentials are provided, delivers via SMTP.
    Otherwise logs the full message to logger and audit log.
    Never throws unhandled exceptions that could break request execution.
    """
    if not recipient_email or "@" not in recipient_email:
        logger.warning(f"Invalid or missing recipient email for complaint #{complaint_id}: '{recipient_email}'")
        return False

    if not is_email_enabled():
        logger.info(f"Email notifications disabled via config. Skipping email for #{complaint_id}")
        return False

    try:
        subject, plain_text, html_body = generate_email_content(
            event_type=event_type,
            complaint_id=complaint_id,
            recipient_name=recipient_name or "Citizen",
            category_name=category_name or "Civic Issue",
            location=location or "Reported Location",
            description=description or "",
            timestamp=timestamp
        )

        cfg = get_smtp_config()
        from_email = cfg["from_email"]
        smtp_host = (cfg["host"] or "").strip()
        smtp_user = (cfg["user"] or "").strip()
        smtp_pass = (cfg["password"] or "").replace(" ", "").strip()
        smtp_port = cfg["port"]

        is_smtp_ready = bool(smtp_host and smtp_user and smtp_pass)

        # Record in audit log
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "complaint_id": complaint_id,
            "recipient_email": recipient_email,
            "recipient_name": recipient_name,
            "subject": subject,
            "delivered_via": "smtp" if is_smtp_ready else "mock_logged",
        }
        SENT_EMAILS_LOG.append(audit_entry)
        # Keep log size bounded
        if len(SENT_EMAILS_LOG) > 500:
            SENT_EMAILS_LOG.pop(0)

        # Database audit log helper
        def _db_log(status_code_str, err_msg=None):
            try:
                from db.session import SessionLocal
                from sqlalchemy import text
                _s = SessionLocal()
                _s.execute(
                    text("INSERT INTO email_logs (event_type, complaint_id, recipient, status, error_detail, created_at) VALUES (:ev, :cid, :rcp, :st, :err, NOW())"),
                    {"ev": event_type, "cid": complaint_id, "rcp": recipient_email, "st": status_code_str, "err": str(err_msg or "")[:1000]}
                )
                _s.commit()
                _s.close()
            except Exception as _dbe:
                logger.warning(f"Failed to record email log in DB: {_dbe}")

        # Strategy 1: Resend HTTP API over Port 443 (Bypasses cloud firewall blocks on ports 25/465/587)
        resend_api_key = (os.getenv("RESEND_API_KEY") or "").strip()
        if resend_api_key:
            try:
                import httpx
                from_sender = os.getenv("RESEND_FROM_EMAIL", "JanSewa Civic Support <onboarding@resend.dev>")
                resend_payload = {
                    "from": from_sender,
                    "to": [recipient_email],
                    "subject": subject,
                    "html": html_body,
                    "text": plain_text,
                }
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(
                        "https://api.resend.com/emails",
                        headers={"Authorization": f"Bearer {resend_api_key}"},
                        json=resend_payload,
                    )
                    if resp.status_code in (200, 201):
                        logger.info(f"[EMAIL NOTIFICATION: SENT HTTP API] Event: {event_type} -> To: {recipient_email}")
                        audit_entry["delivered_via"] = "resend_http"
                        _db_log("DELIVERED_RESEND_HTTP", f"Status {resp.status_code}: {resp.text}")
                        return True
                    else:
                        err_msg = f"Resend HTTP API responded with {resp.status_code}: {resp.text}"
                        logger.warning(err_msg)
                        _db_log(f"FAILED_RESEND_{resp.status_code}", err_msg)
            except Exception as http_err:
                err_msg = f"HTTP Email API error: {http_err}, falling back to SMTP..."
                logger.warning(err_msg)
                _db_log("EXCEPTION_RESEND", err_msg)
        else:
            logger.info("RESEND_API_KEY not found in environment, using SMTP fallback")
            _db_log("NO_RESEND_KEY", "RESEND_API_KEY not configured")

        # Strategy 2: Standard SMTP (Works on local Docker, VPS, and paid cloud tiers)
        if is_smtp_ready:
            import email.utils
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = recipient_email
            msg["Date"] = email.utils.formatdate(localtime=True)
            msg_domain = smtp_user.split("@")[-1] if "@" in smtp_user else ("gmail.com" if "gmail" in smtp_host else "jansewa.gov")
            msg["Message-ID"] = email.utils.make_msgid(domain=msg_domain)
            msg["Reply-To"] = from_email

            msg.attach(MIMEText(plain_text, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            envelope_from = smtp_user if "@" in smtp_user else from_email

            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15) as server:
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(envelope_from, [recipient_email], msg.as_string())
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                    if cfg["use_tls"]:
                        server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(envelope_from, [recipient_email], msg.as_string())

            logger.info(f"[EMAIL NOTIFICATION: SENT SMTP] Event: {event_type} -> To: {recipient_email}, Subject: {subject}")
            _db_log("DELIVERED_SMTP", "Sent via SMTP")
            return True
        else:
            # Development / Mock mode
            logger.info(
                f"[EMAIL NOTIFICATION: MOCK DELIVERED] Event: {event_type} | To: {recipient_email} | Subject: {subject}"
            )
            _db_log("MOCK_DELIVERED", "Mock mode")
            return True

    except Exception as e:
        logger.error(f"Failed to send email notification for complaint #{complaint_id} to {recipient_email}: {e}")
        try:
            from db.session import SessionLocal
            from sqlalchemy import text
            _s = SessionLocal()
            _s.execute(
                text("INSERT INTO email_logs (event_type, complaint_id, recipient, status, error_detail, created_at) VALUES (:ev, :cid, :rcp, :st, :err, NOW())"),
                {"ev": event_type, "cid": complaint_id, "rcp": recipient_email, "st": "EXCEPTION_GLOBAL", "err": str(e)[:1000]}
            )
            _s.commit()
            _s.close()
        except Exception:
            pass
        return False

