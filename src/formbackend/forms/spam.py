import json, time

def is_spam(form, request, fields):
    try:
        spam = json.loads(form.spam_json or "{}")
    except Exception:
        spam = {}
    if spam.get("honeypot") and fields.get("_honeypot"):
        return True
    for kw in spam.get("keywords", []):
        if kw.lower() in json.dumps(fields).lower():
            return True
    rate = spam.get("rate", 0)
    if rate:
        key = request.remote_addr or "?"
        now = time.monotonic()
        ts = [t for t in _hits.get(key, []) if now - t < 60]
        if len(ts) >= rate:
            return True
        ts.append(now)
        _hits[key] = ts
    return False

_hits = {}
