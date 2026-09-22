import json
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Career, Skill, RecommendationRecord
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key' # In production, use a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///careercompass.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Default traits for the system
DEFAULT_TRAITS = [
    {"name": "Logic & Problem Solving", "trait_key": "logic"},
    {"name": "Building & Creating", "trait_key": "building"},
    {"name": "Technology & Computers", "trait_key": "technology"},
    {"name": "Analysis & Data", "trait_key": "analysis"},
    {"name": "Curiosity & Research", "trait_key": "curiosity"},
    {"name": "People & Communication", "trait_key": "people"},
    {"name": "Creativity & Art", "trait_key": "creative"}
]

# Hardcoded careers to seed the DB
DEFAULT_CAREERS = [
    {
        "id": "software-engineer",
        "title": "Software Engineer",
        "category": "Build & ship",
        "description": "Design reliable products, APIs, and systems that turn ideas into useful software.",
        "icon": "</>",
        "color": "teal",
        "skills": json.dumps(["Python", "Java", "Problem solving", "SQL", "Git"]),
        "traits": json.dumps(["logic", "building", "technology"]),
        "streams": json.dumps(["science", "computer"]),
        "salary": "8.5 LPA",
        "demand": 94,
        "roadmap": json.dumps(["Programming foundations", "Data structures", "Backend development", "Build 3 projects"]),
    },
    {
        "id": "data-analyst",
        "title": "Data Analyst",
        "category": "Find the signal",
        "description": "Turn messy information into clear decisions with analysis, dashboards, and storytelling.",
        "icon": "▥",
        "color": "coral",
        "skills": json.dumps(["SQL", "Excel", "Python", "Statistics", "Power BI"]),
        "traits": json.dumps(["analysis", "curiosity", "people"]),
        "streams": json.dumps(["science", "commerce", "computer"]),
        "salary": "7.2 LPA",
        "demand": 89,
        "roadmap": json.dumps(["Statistics basics", "SQL queries", "Data visualization", "Publish a case study"]),
    },
    {
        "id": "product-designer",
        "title": "Product Designer",
        "category": "Shape the experience",
        "description": "Understand people and craft digital experiences that are simple, useful, and memorable.",
        "icon": "✦",
        "color": "yellow",
        "skills": json.dumps(["UX research", "Figma", "Visual design", "Prototyping", "Communication"]),
        "traits": json.dumps(["creative", "people", "building"]),
        "streams": json.dumps(["arts", "science", "commerce", "computer"]),
        "salary": "6.8 LPA",
        "demand": 82,
        "roadmap": json.dumps(["Design principles", "User interviews", "Figma workflows", "Create a portfolio"]),
    },
    {
        "id": "cybersecurity-analyst",
        "title": "Cybersecurity Analyst",
        "category": "Protect what matters",
        "description": "Investigate threats and strengthen the systems people and organisations rely on.",
        "icon": "⌁",
        "color": "blue",
        "skills": json.dumps(["Networking", "Linux", "Python", "Risk analysis", "Security tools"]),
        "traits": json.dumps(["logic", "technology", "analysis"]),
        "streams": json.dumps(["science", "computer"]),
        "salary": "9.1 LPA",
        "demand": 91,
        "roadmap": json.dumps(["Networking", "Linux essentials", "Security fundamentals", "Earn a starter certification"]),
    },
    {
        "id": "digital-marketer",
        "title": "Digital Marketer",
        "category": "Move ideas forward",
        "description": "Connect brands with the right people through strategy, content, and measurable campaigns.",
        "icon": "↗",
        "color": "purple",
        "skills": json.dumps(["Content strategy", "SEO", "Analytics", "Communication", "Campaigns"]),
        "traits": json.dumps(["creative", "people", "curiosity"]),
        "streams": json.dumps(["commerce", "arts", "science"]),
        "salary": "6.2 LPA",
        "demand": 86,
        "roadmap": json.dumps(["Audience research", "Content writing", "SEO foundations", "Run a mini campaign"]),
    },
    {
        "id": "ai-engineer",
        "title": "AI & ML Engineer",
        "category": "Future tech",
        "description": "Build intelligent systems that learn from data and automate complex problem-solving.",
        "icon": "🧠",
        "color": "teal",
        "skills": json.dumps(["Python", "TensorFlow", "Mathematics", "Machine Learning", "Data Modeling"]),
        "traits": json.dumps(["logic", "technology", "analysis"]),
        "streams": json.dumps(["science", "computer"]),
        "salary": "12.5 LPA",
        "demand": 98,
        "roadmap": json.dumps(["Linear Algebra & Calculus", "Machine Learning Algorithms", "Deep Learning Frameworks", "Build an AI model"]),
    },
    {
        "id": "cloud-architect",
        "title": "Cloud Architect",
        "category": "Build & ship",
        "description": "Design and manage robust, scalable cloud infrastructures for modern applications.",
        "icon": "☁️",
        "color": "blue",
        "skills": json.dumps(["AWS/Azure/GCP", "Networking", "DevOps", "Security", "Linux"]),
        "traits": json.dumps(["logic", "building", "technology"]),
        "streams": json.dumps(["science", "computer"]),
        "salary": "14.2 LPA",
        "demand": 92,
        "roadmap": json.dumps(["Cloud fundamentals", "Networking & Security", "Containerization", "Gain a Cloud Certification"]),
    },
    {
        "id": "financial-analyst",
        "title": "Financial Analyst",
        "category": "Find the signal",
        "description": "Analyze financial data, spot trends, and guide businesses in making profitable decisions.",
        "icon": "📈",
        "color": "coral",
        "skills": json.dumps(["Excel", "Financial Modeling", "Accounting", "Statistics", "Risk Management"]),
        "traits": json.dumps(["analysis", "logic", "curiosity"]),
        "streams": json.dumps(["commerce", "science"]),
        "salary": "7.5 LPA",
        "demand": 85,
        "roadmap": json.dumps(["Accounting Basics", "Corporate Finance", "Financial Modeling", "Pass CFA Level 1"]),
    },
    {
        "id": "content-creator",
        "title": "Content Creator / Strategist",
        "category": "Shape the experience",
        "description": "Design engaging written and visual content to captivate audiences across digital platforms.",
        "icon": "✍️",
        "color": "yellow",
        "skills": json.dumps(["Copywriting", "Video Editing", "Social Media", "Storytelling", "SEO"]),
        "traits": json.dumps(["creative", "people", "curiosity"]),
        "streams": json.dumps(["arts", "commerce", "science"]),
        "salary": "5.8 LPA",
        "demand": 88,
        "roadmap": json.dumps(["Writing fundamentals", "Visual storytelling", "Audience building", "Publish your portfolio"]),
    },
    {
        "id": "hr-manager",
        "title": "Human Resources Manager",
        "category": "Move ideas forward",
        "description": "Recruit, develop, and support the people who make an organisation successful.",
        "icon": "🤝",
        "color": "purple",
        "skills": json.dumps(["Communication", "Conflict Resolution", "Empathy", "Management", "Labor Laws"]),
        "traits": json.dumps(["people", "logic"]),
        "streams": json.dumps(["arts", "commerce"]),
        "salary": "6.5 LPA",
        "demand": 80,
        "roadmap": json.dumps(["Organizational behavior", "Recruitment strategies", "Employee relations", "HR internship"]),
    },
    {
        "id": "biotech-researcher",
        "title": "Biotech Researcher",
        "category": "Find the signal",
        "description": "Conduct experiments to develop new products or processes in medicine, agriculture, or energy.",
        "icon": "🔬",
        "color": "teal",
        "skills": json.dumps(["Biology", "Chemistry", "Data Analysis", "Lab Techniques", "Research"]),
        "traits": json.dumps(["curiosity", "analysis", "logic"]),
        "streams": json.dumps(["science"]),
        "salary": "7.0 LPA",
        "demand": 78,
        "roadmap": json.dumps(["Basic sciences", "Lab safety and techniques", "Specialized biology", "Publish a research paper"]),
    },
    {
        "id": "game-developer",
        "title": "Game Developer",
        "category": "Build & ship",
        "description": "Combine code, art, and logic to create interactive entertainment experiences.",
        "icon": "🎮",
        "color": "yellow",
        "skills": json.dumps(["C++ / C#", "Unity / Unreal Engine", "3D Math", "Problem Solving", "Creativity"]),
        "traits": json.dumps(["creative", "building", "technology"]),
        "streams": json.dumps(["science", "computer", "arts"]),
        "salary": "8.0 LPA",
        "demand": 84,
        "roadmap": json.dumps(["Programming basics", "Game engines", "Game design principles", "Release an indie game"]),
    },
    {
        "id": "operations-manager",
        "title": "Operations Manager",
        "category": "Move ideas forward",
        "description": "Optimize processes and ensure an organization runs smoothly and efficiently day-to-day.",
        "icon": "⚙️",
        "color": "blue",
        "skills": json.dumps(["Logistics", "Project Management", "Leadership", "Problem Solving", "Analytics"]),
        "traits": json.dumps(["logic", "people", "analysis"]),
        "streams": json.dumps(["commerce", "science"]),
        "salary": "8.5 LPA",
        "demand": 86,
        "roadmap": json.dumps(["Process optimization", "Supply chain basics", "Team leadership", "Get a Six Sigma cert"]),
    },
    {
        "id": "psychologist",
        "title": "Psychologist",
        "category": "Find the signal",
        "description": "Study human behavior and mental processes to help people overcome challenges.",
        "icon": "🧠",
        "color": "purple",
        "skills": json.dumps(["Empathy", "Active Listening", "Research", "Counseling", "Critical Thinking"]),
        "traits": json.dumps(["people", "curiosity", "analysis"]),
        "streams": json.dumps(["arts", "science"]),
        "salary": "6.0 LPA",
        "demand": 82,
        "roadmap": json.dumps(["Foundational psychology", "Counseling techniques", "Clinical practice", "Obtain a license"]),
    },
    {
        "id": "blockchain-developer",
        "title": "Blockchain Developer",
        "category": "Future tech",
        "description": "Build decentralized applications and smart contracts using cryptographic principles.",
        "icon": "⛓️",
        "color": "teal",
        "skills": json.dumps(["Solidity", "Cryptography", "JavaScript", "Smart Contracts", "Web3"]),
        "traits": json.dumps(["technology", "logic", "building"]),
        "streams": json.dumps(["science", "computer"]),
        "salary": "14.5 LPA",
        "demand": 89,
        "roadmap": json.dumps(["Cryptography basics", "Ethereum & Smart Contracts", "Web3 integration", "Deploy a dApp"]),
    }
]

with app.app_context():
    db.create_all()
    # Seed Data
    if not User.query.filter_by(email='admin@careercompass.com').first():
        admin = User(name='Admin', email='admin@careercompass.com', password_hash=bcrypt.generate_password_hash('admin').decode('utf-8'), role='admin')
        db.session.add(admin)
        db.session.commit()
    
    if Career.query.count() == 0:
        for c in DEFAULT_CAREERS:
            db.session.add(Career(**c))
        db.session.commit()

    if Skill.query.count() == 0:
        for s in DEFAULT_TRAITS:
            db.session.add(Skill(name=s['name'], trait_key=s['trait_key']))
        db.session.commit()

def recommend(profile):
    interests = set(profile.get("interests", []))
    stream = profile.get("stream", "")
    confidence = float(profile.get("confidence", 3))
    scores = []
    
    careers = Career.query.all()

    for c in careers:
        career = c.to_dict()
        score = 0
        matched = []
        for trait in career["traits"]:
            if trait in interests:
                score += 18
                matched.append(trait)
        if stream in career["streams"]:
            score += 14
        score += min(confidence * 2, 10)
        score += career["demand"] / 25
        scores.append({**career, "score": round(min(score, 100)), "matched": matched})

    scores.sort(key=lambda item: item["score"], reverse=True)
    return scores

# --- Routes ---

@app.route("/")
def index():
    return render_template("index.html")

# --- Authentication ---

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        stream = request.form.get('stream')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(name=name, email=email, password_hash=hashed_password, role='student', stream=stream)
        db.session.add(user)
        try:
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            flash('Email already registered.', 'danger')
            
    return render_template('auth/register.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))

# --- Student Module ---

@app.route("/student")
@login_required
def student_dashboard():
    if current_user.role != 'student':
        abort(403)
    records = RecommendationRecord.query.filter_by(user_id=current_user.id).order_by(RecommendationRecord.timestamp.desc()).all()
    parsed_records = []
    for r in records:
        parsed_records.append({
            "timestamp": r.timestamp,
            "results": json.loads(r.results) if r.results else []
        })
    return render_template('student/dashboard.html', records=parsed_records)

@app.route("/student/assessment", methods=['GET'])
@login_required
def assessment():
    if current_user.role != 'student':
        abort(403)
    skills = Skill.query.all()
    return render_template('student/assessment.html', skills=skills, user=current_user)

@app.route("/api/recommend", methods=['POST'])
@login_required
def api_recommend():
    profile = request.get_json(silent=True) or {}
    if not profile.get("stream") or len(profile.get("interests", [])) < 1:
        return jsonify({"error": "Choose your study stream and at least one interest."}), 400
    
    results = recommend(profile)
    top_results = results[:3]
    
    # Save record
    record = RecommendationRecord(
        user_id=current_user.id,
        input_data=json.dumps(profile),
        results=json.dumps(top_results)
    )
    db.session.add(record)
    db.session.commit()
    
    return jsonify({"profile": profile, "recommendations": top_results})

# --- Admin Module ---

@app.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)
    users_count = User.query.filter_by(role='student').count()
    careers_count = Career.query.count()
    records_count = RecommendationRecord.query.count()
    return render_template('admin/dashboard.html', users_count=users_count, careers_count=careers_count, records_count=records_count)

@app.route("/admin/students")
@login_required
def admin_students():
    if current_user.role != 'admin':
        abort(403)
    students = User.query.filter_by(role='student').all()
    return render_template('admin/manage_students.html', students=students)

@app.route("/admin/careers")
@login_required
def admin_careers():
    if current_user.role != 'admin':
        abort(403)
    careers = Career.query.all()
    return render_template('admin/manage_careers.html', careers=careers)

@app.route("/admin/skills")
@login_required
def admin_skills():
    if current_user.role != 'admin':
        abort(403)
    skills = Skill.query.all()
    return render_template('admin/manage_skills.html', skills=skills)

@app.route("/admin/records")
@login_required
def admin_records():
    if current_user.role != 'admin':
        abort(403)
    records = RecommendationRecord.query.order_by(RecommendationRecord.timestamp.desc()).all()
    return render_template('admin/records.html', records=records)

@app.route("/api/careers")
def api_careers():
    careers = [c.to_dict() for c in Career.query.all()]
    return jsonify(careers)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
