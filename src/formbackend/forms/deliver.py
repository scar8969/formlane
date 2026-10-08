import json, smtplib, urllib.request
from email.message import EmailMessage

def deliver_email(form, sub):
    cfg = _config(form, "email", {})
    if not cfg:
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = f"New form submission: {form.name}"
        msg["From"] = cfg.get("from", "forms@localhost")
        msg["To"] = cfg["to"]
        msg.set_content(sub.fields_json)
        with smtplib.SMTP(cfg.get("host", "localhost"), int(cfg.get("port", 25)), timeout=10) as s:
            s.send_message(msg)
        return True
    except Exception:
        return False

def deliver_webhook(form, sub):
    url = _config(form, "webhook", "")
    if not url:
        return False
    try:
        req = urllib.request.Request(url, data=sub.fields_json.encode(), method="POST",
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status < 400
    except Exception:
        return False

def deliver_slack(form, sub):
    url = _config(form, "slack", "")
    if not url:
        return False
    try:
        payload = json.dumps({"text": f"New submission: {sub.fields_json}"}).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status < 400
    except Exception:
        return False

def _config(form, key, default=""):
    try:
        return json.loads(form.deliver_json or "{}").get(key, default)
    except Exception:
        return default
