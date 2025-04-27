from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from models import db, User, Job, Resume
from resume_parser import extract_text
from flask_migrate import Migrate
#from ai_matcher import analyze_resume
from datetime import datetime
from ai_matcher_v2 import analyze_resume
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# Ensure the database tables are created
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 📌 Index Route
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/view-users')
@login_required
def view_users():
    if current_user.role != "employer":  # Ensure only employers can view users
        flash("Access Denied!", "danger")
        return redirect(url_for('dashboard'))

    users = User.query.all()  # Fetch all users
    return render_template('user_accounts.html', users=users)

@app.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != "employer":  # Only employers can delete users
        flash("Access Denied!", "danger")
        return redirect(url_for('dashboard'))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('view_users'))

    if user.role == "admin":  # Prevent deleting admin accounts
        flash("Cannot delete admin users!", "danger")
        return redirect(url_for('view_users'))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "success")

    return redirect(url_for('view_users'))

# 📌 Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            login_user(user)
            if user.role == "admin":
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password", "danger")
    
    return render_template('login.html')

# 📌 Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        if not email:
            flash("Email is required.", "danger")
            return redirect(url_for('signup'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Choose another.", "warning")
            return redirect(url_for('signup'))

        new_user = User(username=username, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# 📌 Dashboard (Employer & Applicant View)
@app.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.all()

    if current_user.role == "employer":
        return render_template('dashboard_employer.html', jobs=jobs)
    
    applications = Resume.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard_applicant.html', jobs=jobs, applications=applications)

# 📌 Admin Dashboard
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return "Access Denied"

    users = User.query.all()
    jobs = Job.query.all()
    return render_template('admin_dashboard.html', users=users, jobs=jobs)

# 📌 Show Resume Upload Page (Applicant Only)
@app.route('/apply/<int:job_id>')
@login_required
def upload_resume_page(job_id):
    if current_user.role != "applicant":
        return "Access Denied"

    job = Job.query.get(job_id)
    return render_template('upload_resume.html', job=job)

# 📌 Upload Resume (Applicant Only) - Now Supports Both File & Text Input
@app.route('/upload-resume/<int:job_id>', methods=['POST'])
@login_required
def upload_resume(job_id):
    if current_user.role != "applicant":
        flash("Access Denied: Only applicants can apply for jobs.", "danger")
        return redirect(url_for('dashboard'))

    job = Job.query.get(job_id)
    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for('dashboard'))

    # 🔹 Try getting resume text from the text box first
    resume_text = request.form.get('resume_text')

    # 🔹 If text box is empty, try file upload instead
    if not resume_text:
        file = request.files.get('resume')
        if file:
            resume_text = extract_text(file)  # Function to read file content
        else:
            flash("No resume provided. Upload a file or paste your resume.", "danger")
            return redirect(url_for('upload_resume_page', job_id=job_id))

    # 🔹 AI Analyzes Resume
    ai_result = analyze_resume(resume_text, job.description)
    match_score = ai_result.get('match_score', 0)
    suggestions = "\n".join(ai_result.get("suggestions", []))

    if match_score >= 75:
        new_resume = Resume(user_id=current_user.id, job_id=job.id, match_score=match_score,submitted_at=datetime.utcnow())
        db.session.add(new_resume)
        db.session.commit()
        flash("✅ Congratulations! You've been shortlisted for an interview!", "success")
    else:
        new_resume = Resume(user_id=current_user.id, job_id=job.id, match_score=match_score, suggestions= suggestions,submitted_at=datetime.utcnow())
        db.session.add(new_resume)
        db.session.commit()
        flash("❌ Unfortunately, we are pursuing other candidates at this time.", "danger")

    return redirect(url_for('dashboard'))

# 📌 Post a Job (Employer Only)
@app.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role != "employer":
        return "Access Denied"
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        if not title or not description:
            flash("Job title and description are required.", "danger")
            return redirect(url_for('post_job'))

        new_job = Job(title=title, description=description)
        db.session.add(new_job)
        db.session.commit()
        flash("Job posted successfully!", "success")
        return redirect(url_for('dashboard'))
    
    return render_template('post_job.html')

# 📌 View Applicants (Employer & Admin)
@app.route('/view-applicants/<int:job_id>')
@login_required
def view_applicants(job_id):
    if current_user.role not in ["employer", "admin"]:
        return "Access Denied"

    job = Job.query.get(job_id)
    resumes = Resume.query.filter_by(job_id=job_id).order_by(Resume.match_score.desc()).all()
    return render_template('view_applicants.html', job=job, resumes=resumes)

# 📌 Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/delete-resume/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    resume = Resume.query.get(resume_id)

    if not resume:
        flash("Resume not found.", "danger")
        return redirect(url_for('dashboard'))

    # Ensure that only the owner of the resume can delete it
    if resume.user_id != current_user.id:
        flash("You do not have permission to delete this resume.", "danger")
        return redirect(url_for('dashboard'))

    db.session.delete(resume)
    db.session.commit()
    flash("Resume deleted successfully.", "success")
    
    return redirect(url_for('dashboard'))


# Run the Flask App
if __name__ == '__main__':
    with app.app_context():
        migrate = Migrate(app, db)
        db.create_all()
    app.run(debug=True)
