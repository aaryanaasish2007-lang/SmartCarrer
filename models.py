from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'admin' or 'student'
    stream = db.Column(db.String(50)) # For student
    
    records = db.relationship('RecommendationRecord', backref='user', lazy=True)

class Career(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    icon = db.Column(db.String(20))
    color = db.Column(db.String(20))
    skills = db.Column(db.Text) # JSON string
    traits = db.Column(db.Text) # JSON string
    streams = db.Column(db.Text) # JSON string
    salary = db.Column(db.String(50))
    demand = db.Column(db.Integer)
    roadmap = db.Column(db.Text) # JSON string

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
            "skills": json.loads(self.skills) if self.skills else [],
            "traits": json.loads(self.traits) if self.traits else [],
            "streams": json.loads(self.streams) if self.streams else [],
            "salary": self.salary,
            "demand": self.demand,
            "roadmap": json.loads(self.roadmap) if self.roadmap else []
        }

class RecommendationRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    input_data = db.Column(db.Text) # JSON string of profile data
    results = db.Column(db.Text) # JSON string of recommendations

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    trait_key = db.Column(db.String(50)) # Corresponding trait keyword like 'logic', 'creative'
