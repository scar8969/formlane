"""Command line front-end for the form backend.

The web stack is imported lazily inside the functions that need it, so
``python cli.py --help`` works before the requirements are installed.
"""
import argparse
import json
import sys

def _app():
    """Import the Flask app and push an application context for the caller."""
    try:
        from ._app import app
    except ModuleNotFoundError as exc:
        print("error: cannot import the application (%s)" % exc, file=sys.stderr)
        print("hint: install the requirements first: pip install -r requirements.txt", file=sys.stderr)
        raise SystemExit(2)
    ctx = app.app_context()
    ctx.push()
    return ctx

def _models():
    from .models import Form, Submission, db
    return Form, Submission, db

def cmd_forms(args):
    ctx = _app()
    try:
        Form, Submission, db = _models()
        rows = Form.query.order_by(Form.id).all()
        data = [{"id": f.id, "name": f.name, "token": f.token,
                 "submissions": Submission.query.filter_by(form_id=f.id).count()}
                for f in rows]
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            for row in data:
                print("%-4s %-28s %-12s %d submissions"
                      % (row["id"], row["name"][:28], row["token"], row["submissions"]))
            print("-- %d form(s)" % len(data))
    finally:
        ctx.pop()
    return 0

def cmd_create(args):
    ctx = _app()
    try:
        Form, Submission, db = _models()
        import secrets
        deliver = {}
        if args.email:
            deliver["email"] = {"to": args.email}
        if args.webhook:
            deliver["webhook"] = args.webhook
        form = Form(token=secrets.token_urlsafe(6), name=args.name,
                    deliver_json=json.dumps(deliver),
                    spam_json=json.dumps({"honeypot": True} if args.honeypot else {}))
        db.session.add(form)
        db.session.commit()
        print("created #%s %s" % (form.id, form.name))
        print("endpoint: POST /f/%s" % form.token)
    finally:
        ctx.pop()
    return 0

def cmd_submissions(args):
    ctx = _app()
    try:
        Form, Submission, db = _models()
        form = db.session.get(Form, args.id)
        if form is None:
            print("error: no form with id %s" % args.id, file=sys.stderr)
            return 1
        rows = (Submission.query.filter_by(form_id=form.id)
                .order_by(Submission.id.desc()).limit(args.limit).all())
        if args.json:
            print(json.dumps([{"id": s.id, "fields": json.loads(s.fields_json or "{}"),
                               "spam": bool(s.spam), "delivered": bool(s.delivered)}
                              for s in rows], indent=2))
        else:
            for s in rows:
                print("%-4s %-40s spam=%s delivered=%s"
                      % (s.id, (s.fields_json or "")[:40], bool(s.spam), bool(s.delivered)))
            print("-- %d submission(s)" % len(rows))
    finally:
        ctx.pop()
    return 0

def cmd_test(args):
    ctx = _app()
    try:
        from ._app import app
        Form, Submission, db = _models()
        form = Form.query.filter_by(token=args.token).first()
        if form is None:
            print("error: no form with token %s" % args.token, file=sys.stderr)
            return 1
        client = app.test_client()
        resp = client.post("/f/%s" % form.token, json={"cli": "smoke", "email": "you@example.com"})
        print("%s %s %s" % (resp.status_code, resp.content_type, resp.get_data(as_text=True)))
        return 0 if resp.status_code == 200 else 1
    finally:
        ctx.pop()

def cmd_serve(args):
    try:
        from ._app import app
    except ModuleNotFoundError as exc:
        print("error: cannot import the application (%s)" % exc, file=sys.stderr)
        return 2
    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0

def build_parser():
    p = argparse.ArgumentParser(prog="formbackend", description="Form backend CLI")
    sub = p.add_subparsers(dest="cmd", metavar="command")

    s = sub.add_parser("forms", help="list forms with submission counts")
    s.add_argument("--json", action="store_true", help="emit JSON")
    s.set_defaults(func=cmd_forms)

    s = sub.add_parser("create", help="create a form endpoint")
    s.add_argument("name", help="human-readable form name")
    s.add_argument("--email", help="forward submissions to this address")
    s.add_argument("--webhook", help="POST submissions to this URL")
    s.add_argument("--honeypot", action="store_true", help="enable the honeypot field check")
    s.set_defaults(func=cmd_create)

    s = sub.add_parser("submissions", help="show recent submissions for a form")
    s.add_argument("id", type=int, help="form id")
    s.add_argument("--limit", type=int, default=20, help="max rows (default 20)")
    s.add_argument("--json", action="store_true", help="emit JSON")
    s.set_defaults(func=cmd_submissions)

    s = sub.add_parser("test", help="post a sample submission to a form token")
    s.add_argument("token", help="form token, as shown by `forms`")
    s.set_defaults(func=cmd_test)

    s = sub.add_parser("serve", help="run the development server")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=5000)
    s.add_argument("--debug", action="store_true")
    s.set_defaults(func=cmd_serve)
    return p

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return args.func(args)
