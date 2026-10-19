from flask_sqlalchemy import SQLAlchemy

from .clock import utcnow

db = SQLAlchemy()


class Form(db.Model):
    __tablename__ = "forms"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(16), unique=True)
    name = db.Column(db.String(64), default="")
    deliver_json = db.Column(db.Text, default="{}")
    spam_json = db.Column(db.Text, default="{}")
    created_at = db.Column(db.DateTime, default=utcnow)


class Submission(db.Model):
    __tablename__ = "submissions"
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey("forms.id"), index=True)
    fields_json = db.Column(db.Text, default="{}")
    ip = db.Column(db.String(64), default="")
    spam = db.Column(db.Integer, default=0)
    delivered = db.Column(db.Integer, default=0)
    at = db.Column(db.DateTime, default=utcnow)
