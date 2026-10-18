import json
import os
import secrets

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from . import paths
from .forms.api import bp
from .models import Form, Submission, db

# templates/ is copied to the project root by the build, next to web/.


def build_app():
    """Build the application: configuration, database, then routes."""
    app = Flask(__name__, template_folder=str(paths.TEMPLATES_DIR))
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "FORMBACKEND_DB_URI", "sqlite:///" + str(paths.INSTANCE_DIR / "formbackend.db")
    )
    app.config["SECRET_KEY"] = os.environ.get("FORMBACKEND_SECRET_KEY", "formbackend-local")
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(bp)

    def _delivery_label(deliver_json):
        try:
            cfg = json.loads(deliver_json or "{}")
        except Exception:
            cfg = {}
        kinds = [k for k in ("email", "webhook", "slack") if cfg.get(k)]
        return ", ".join(kinds)

    @app.context_processor
    def _inject():
        example = Form.query.order_by(Form.id).first()
        return {
            "app_name": "📬 formbackend",
            "stats": _stats(),
            "endpoint_example": url_for(
                "forms.submit", token=example.token if example else "TOKEN", _external=True
            ),
        }

    def _stats():
        return {
            "forms": Form.query.count(),
            "submissions": Submission.query.count(),
            "spam": Submission.query.filter_by(spam=1).count(),
            "delivered": Submission.query.filter_by(delivered=1).count(),
        }

    def _form_rows():
        return [
            {
                "id": f.id,
                "name": f.name,
                "token": f.token,
                "sub_count": Submission.query.filter_by(form_id=f.id).count(),
                "spam_count": Submission.query.filter_by(form_id=f.id, spam=1).count(),
                "delivery": _delivery_label(f.deliver_json),
            }
            for f in Form.query.order_by(Form.id).all()
        ]

    @app.get("/")
    def index():
        return render_template("index.html", forms=_form_rows())

    @app.get("/submissions")
    def submissions():
        form_id = request.args.get("form", type=int)
        query = Submission.query
        if form_id:
            query = query.filter(Submission.form_id == form_id)
        rows = query.order_by(Submission.id.desc()).limit(200).all()
        names = {f.id: (f.name or "form #%d" % f.id) for f in Form.query.all()}
        return render_template(
            "submissions.html",
            submissions=rows,
            forms=_form_rows(),
            form_id=form_id,
            form_names=names,
        )

    @app.route("/forms/new", methods=["GET", "POST"])
    def new_form():
        if request.method == "POST":
            name = (request.form.get("name") or "").strip()
            if not name:
                flash("A form name is required.", "error")
                return redirect(url_for("new_form"))
            deliver = {}
            email = (request.form.get("email") or "").strip()
            webhook = (request.form.get("webhook") or "").strip()
            if email:
                deliver["email"] = {
                    "to": email,
                    "from": "forms@localhost",
                    "host": "localhost",
                    "port": 25,
                }
            if webhook:
                deliver["webhook"] = webhook
            spam = {}
            if request.form.get("honeypot"):
                spam["honeypot"] = True
            keywords = [
                k.strip() for k in (request.form.get("keywords") or "").split(",") if k.strip()
            ]
            if keywords:
                spam["keywords"] = keywords
            form = Form(
                token=secrets.token_urlsafe(6),
                name=name,
                deliver_json=json.dumps(deliver),
                spam_json=json.dumps(spam),
            )
            db.session.add(form)
            db.session.commit()
            flash(
                "Created %s -- POST to %s" % (name, url_for("forms.submit", token=form.token)),
                "success",
            )
            return redirect(url_for("index"))
        return render_template("new_form.html")

    @app.get("/api/health")
    def health():
        return jsonify(
            {"status": "ok", "forms": Form.query.count(), "submissions": Submission.query.count()}
        )

    # python -m web.app
    if __name__ == "__main__":
        app.run(host="127.0.0.1", port=5000, debug=False)

    return app


app = build_app()
