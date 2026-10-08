from ..models import Form

import json

import secrets, string

_ALPHABET = string.ascii_letters + string.digits

def get_form(token: str) -> Form:
    return Form.query.filter_by(token=token).first()

def capture(form, request):
    from ..models import Submission
    fields = request.get_json(force=True, silent=True) or request.form.to_dict()
    return Submission(form_id=form.id, fields_json=json.dumps(fields),
                      ip=request.remote_addr or "")
