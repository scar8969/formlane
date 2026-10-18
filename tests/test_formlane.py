"""B8 formbackend — tests. Run: pytest test_formlane.py"""

import pytest

flask_ok = True
try:
    import flask_sqlalchemy
except ImportError:
    flask_ok = False


class FakeReq:
    def __init__(self, ip="1.2.3.4"):
        self.remote_addr = ip
        self.form = {}
        self._json = {}

    def get_json(self, force=True, silent=True):
        return self._json


def test_honeypot():
    from formbackend.forms.spam import is_spam

    class Form:
        spam_json = '{"honeypot": true}'

    r = FakeReq()
    assert is_spam(Form(), r, {"_honeypot": "filled"})
    assert not is_spam(Form(), r, {"name": "alice"})


def test_keyword_filter():
    from formbackend.forms.spam import is_spam

    class Form:
        spam_json = '{"keywords": ["viagra"]}'

    assert is_spam(Form(), FakeReq(), {"msg": "buy viagra now"})


def test_rate_limit():
    from formbackend.forms.spam import is_spam

    class Form:
        spam_json = '{"rate": 2}'

    r = FakeReq()
    assert not is_spam(Form(), r, {"a": 1})
    assert not is_spam(Form(), r, {"a": 2})
    assert is_spam(Form(), r, {"a": 3})


@pytest.mark.skipif(not flask_ok, reason="flask-sqlalchemy not installed")
def test_capture_fields():
    from formbackend.forms.endpoints import capture

    class Form:
        id = 1

    r = FakeReq()
    r._json = {"name": "alice", "msg": "hi"}
    sub = capture(Form(), r)
    assert "alice" in sub.fields_json
