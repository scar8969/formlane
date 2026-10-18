import json
import secrets
from typing import Any

from flask import Blueprint, jsonify, request

from ..models import Form, Submission, db
from .deliver import deliver_email, deliver_webhook
from .endpoints import capture, get_form
from .spam import is_spam

bp = Blueprint("forms", __name__)
_hits: dict[str, Any] = {}


@bp.post("/f/<token>")
def submit(token):
    form = get_form(token)
    if not form:
        return jsonify({"error": "not_found"}), 404
    fields = request.get_json(force=True, silent=True) or request.form.to_dict()
    if is_spam(form, request, fields):
        return jsonify({"error": "spam"}), 403
    sub = capture(form, request)
    db.session.add(sub)
    db.session.flush()
    # deliver
    ok_email = deliver_email(form, sub) if "email" in form.deliver_json else False
    ok_webhook = deliver_webhook(form, sub) if "webhook" in form.deliver_json else False
    sub.delivered = 1 if (ok_email or ok_webhook) else 0
    db.session.commit()
    return jsonify({"status": "received", "id": sub.id})


@bp.get("/api/forms")
def list_forms():
    return jsonify(
        {
            "forms": [
                {
                    "id": f.id,
                    "name": f.name,
                    "token": f.token,
                    "submissions": Submission.query.filter_by(form_id=f.id).count(),
                }
                for f in Form.query.all()
            ]
        }
    )


@bp.post("/api/forms")
def add_form():
    d = request.get_json(force=True, silent=True) or {}
    # deliver_json/spam_json are read back with json.loads by deliver/spam, so
    # they have to be JSON text -- str(dict) produces a Python repr that only
    # looks similar and makes every delivery silently fail.
    f = Form(
        token=secrets.token_urlsafe(6),
        name=d.get("name", ""),
        deliver_json=json.dumps(d.get("deliver") or {}),
        spam_json=json.dumps(d.get("spam") or {}),
    )
    db.session.add(f)
    db.session.commit()
    return jsonify({"id": f.id, "token": f.token})


@bp.get("/api/forms/<int:fid>/submissions")
def submissions(fid):
    rows = [
        {
            "id": s.id,
            "fields": s.fields_json,
            "spam": bool(s.spam),
            "delivered": bool(s.delivered),
            "at": s.at.isoformat() if s.at else "",
        }
        for s in Submission.query.filter_by(form_id=fid)
        .order_by(Submission.id.desc())
        .limit(100)
        .all()
    ]
    return jsonify({"submissions": rows})
