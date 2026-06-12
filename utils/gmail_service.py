"""
Gmail Service — Send and read emails using SMTP/IMAP with App Passwords.
No Google Cloud project required. Users just need a Gmail App Password.

Setup: Google Account → Security → 2-Step Verification → App Passwords → Generate
"""
import smtplib
import imaplib
import email as email_lib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.mime.application import MIMEApplication
from typing import Optional


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993


def send_email(
    sender_email: str,
    app_password: str,
    to_email: str,
    subject: str,
    body: str,
    sender_name: str = "",
    reply_to_message_id: Optional[str] = None,
    attachment_bytes: Optional[bytes] = None,
    attachment_name: str = "Resume.pdf",
) -> Optional[str]:
    """
    Send an email via Gmail SMTP.
    Returns the Message-ID on success, None on failure.
    """
    try:
        msg = MIMEMultipart("mixed")
        
        alt_part = MIMEMultipart("alternative")
        msg.attach(alt_part)
        
        import email.utils
        msg_id = email.utils.make_msgid()
        msg["Message-ID"] = msg_id
        
        msg["From"] = formataddr((sender_name or sender_email, sender_email))
        msg["To"] = to_email
        msg["Subject"] = subject

        if reply_to_message_id:
            msg["In-Reply-To"] = reply_to_message_id
            msg["References"] = reply_to_message_id

        # Create both plain text and HTML versions
        plain_body = body
        html_body = body.replace("\n", "<br>")
        html_content = f"""
        <div style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
            {html_body}
        </div>
        """

        alt_part.attach(MIMEText(plain_body, "plain"))
        alt_part.attach(MIMEText(html_content, "html"))

        if attachment_bytes:
            part = MIMEApplication(attachment_bytes, Name=attachment_name)
            part['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
            msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, app_password)
            server.send_message(msg)

        return msg["Message-ID"]

    except smtplib.SMTPAuthenticationError:
        raise ValueError(
            "Gmail authentication failed. Check your email and App Password. "
            "Make sure 2-Step Verification is enabled and you're using an App Password, "
            "not your regular password."
        )
    except Exception as e:
        raise ValueError(f"Failed to send email: {str(e)}")


def fetch_replies(
    gmail_email: str,
    app_password: str,
    sent_subjects: list[str],
    since_days: int = 7,
) -> list[dict]:
    """
    Check Gmail inbox for replies to our cold emails.
    Matches by subject line (looking for Re: <original subject>).
    Returns list of reply dicts.
    """
    replies = []
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(gmail_email, app_password)
        mail.select("INBOX")

        # Search for recent emails
        from datetime import datetime, timedelta
        since_date = (datetime.now() - timedelta(days=since_days)).strftime("%d-%b-%Y")
        _, message_ids = mail.search(None, f'(SINCE "{since_date}")')

        if not message_ids[0]:
            mail.logout()
            return replies

        for msg_id in message_ids[0].split():
            _, msg_data = mail.fetch(msg_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email_lib.message_from_bytes(raw_email)

            subject = str(email_lib.header.decode_header(msg["Subject"])[0][0] or "")
            if isinstance(subject, bytes):
                subject = subject.decode("utf-8", errors="ignore")

            from_addr = msg["From"] or ""
            # Skip emails from ourselves
            if gmail_email.lower() in from_addr.lower():
                continue

            # Check if this is a reply to one of our sent emails
            clean_subject = subject.replace("Re: ", "").replace("RE: ", "").strip()
            is_reply = any(
                clean_subject.lower() == sent_subj.lower()
                for sent_subj in sent_subjects
            )

            if not is_reply:
                continue

            # Extract body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode("utf-8", errors="ignore")
                            break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="ignore")

            # Extract sender email
            sender = from_addr
            if "<" in sender and ">" in sender:
                sender = sender.split("<")[1].split(">")[0]

            in_reply_to = msg.get("In-Reply-To", "")
            message_id = msg.get("Message-ID", "")

            replies.append({
                "from_email": sender.strip(),
                "subject": subject,
                "body": body.strip(),
                "message_id": message_id,
                "in_reply_to": in_reply_to,
                "date": msg.get("Date", ""),
                "original_subject": clean_subject,
            })

        mail.logout()
    except imaplib.IMAP4.error as e:
        raise ValueError(f"IMAP login failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to fetch replies: {str(e)}")

    return replies


def test_connection(gmail_email: str, app_password: str) -> bool:
    """Test if the Gmail credentials are valid."""
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(gmail_email, app_password)
        return True
    except Exception:
        return False
