from app import app
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime


db = SQLAlchemy(app)


def send_mail(email):
    receivers = [email]
    mail = Mail(current_app)
    msg = Message('اطلاعیه', sender='moiencompany@gmail.com', recipients=receivers)
    msg.html = '<p>با سلام. شما دسترسی لازم برای ایجاد اپلیکیشن ها و ورژن آن ها را در سایت ما گرفتید.</p>'
    mail.send(msg)


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    author = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    releases = db.relationship('Release', backref='applications', lazy=True)


class Release(db.Model):
    __tablename__ = 'releases'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    version = db.Column(db.String(64), nullable=False)
    changelog = db.Column(db.Text, nullable=False)
    app_link = db.Column(db.String(255), nullable=False)
    date_of_release = db.Column(db.DateTime, nullable=False, default=datetime.now())


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    access = db.Column(db.Boolean, nullable=False, default=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
