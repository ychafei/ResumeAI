from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # "admin", "employer", "applicant"

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)  #  Fix: Add Foreign Key for Job
    match_score = db.Column(db.Float, nullable=False)
    suggestions = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=False)
    
    user = db.relationship('User', backref='resumes')  #  Relationship with User
    job = db.relationship('Job', backref='resumes')    #  Relationship with Job
