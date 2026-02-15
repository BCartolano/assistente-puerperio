# -*- coding: utf-8 -*-
import os
import smtplib
import ssl
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

try:
    import requests
except Exception:
    requests = None


def _render_fallback(subject, html, text):
    return text or (html or f"{subject}").replace("<br>", "\n").replace("<br/>", "\n")


def send_email(subject: str, to_email: str, html: Optional[str] = None, text: Optional[str] = None) -> bool:
    sg_key = os.environ.get("SENDGRID_API_KEY")
    if sg_key and requests:
        try:
            payload = {
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": os.environ.get("SMTP_FROM", "no-reply@localhost")},
                "subject": subject,
                "content": [
                    {"type": "text/plain", "value": _render_fallback(subject, html, text)},
                    {"type": "text/html", "value": html or _render_fallback(subject, html, text)}
                ]
            }
            r = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {sg_key}", "Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            return 200 <= r.status_code < 300
        except Exception:
            pass

    host = os.environ.get("SMTP_HOST")
    user = os.environ.get("SMTP_USER")
    pwd = os.environ.get("SMTP_PASS")
    port = int(os.environ.get("SMTP_PORT", "587"))
    use_ssl = os.environ.get("SMTP_SSL", "false").lower() in ("1", "true", "yes", "on")
    sender = os.environ.get("SMTP_FROM", user or "no-reply@localhost")
    if not host:
        print(f"[MAIL] (LOG ONLY) To: {to_email} | Subject: {subject}\n{_render_fallback(subject, html, text)}")
        return True

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email
    part1 = MIMEText(_render_fallback(subject, html, text), "plain", "utf-8")
    part2 = MIMEText(html or _render_fallback(subject, html, text), "html", "utf-8")
    msg.attach(part1)
    msg.attach(part2)
    try:
        if use_ssl:
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=ctx) as server:
                if user and pwd:
                    server.login(user, pwd)
                server.sendmail(sender, [to_email], msg.as_string())
        else:
            with smtplib.SMTP(host, port) as server:
                server.starttls(context=ssl.create_default_context())
                if user and pwd:
                    server.login(user, pwd)
                server.sendmail(sender, [to_email], msg.as_string())
        return True
    except Exception as e:
        print("[MAIL] Falha no envio:", e)
        return False
