from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
import sqlite3
from datetime import datetime
import hashlib
import os
from werkzeug.utils import secure_filename
from utils import extract_text_from_file, calculate_match_score, allowed_file

app = Flask(__name__)
app.secret_key = "jobtracker_secret"
DB = "jobs.db"
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def get_latest_resume_text(user_id):
    con = db()
    resume = con.execute(
        "SELECT content_text FROM resumes WHERE user_id=? ORDER BY id DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    con.close()
    return resume[0] if resume else ""

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = hash_pw(request.form["password"])
        con = db()
        user = con.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()
        con.close()

        if user:
            session["user_id"] = user[0]
            session["theme"] = "light"
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        con = db()
        try:
            con.execute(
                "INSERT INTO users(name,email,password) VALUES(?,?,?)",
                (
                    request.form["name"],
                    request.form["email"],
                    hash_pw(request.form["password"])
                )
            )
            con.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash("Registration failed. Email might already exist.", "danger")
        finally:
            con.close()

    return render_template("register.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = db()
    jobs = con.execute(
        "SELECT * FROM jobs WHERE user_id=? ORDER BY id DESC",
        (session["user_id"],)
    ).fetchall()
    
    # Check if user has a resume
    has_resume = con.execute("SELECT 1 FROM resumes WHERE user_id=? LIMIT 1", (session["user_id"],)).fetchone()
    con.close()

    return render_template(
        "dashboard.html",
        jobs=jobs,
        theme=session.get("theme", "light"),
        has_resume=bool(has_resume)
    )

# ---------------- RESUME ----------------
@app.route("/resume", methods=["GET", "POST"])
def resume():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    con = db()
    
    if request.method == "POST":
        if 'resume_file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['resume_file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract text
            content_text = extract_text_from_file(filepath)
            
            con.execute(
                "INSERT INTO resumes(user_id, filename, content_text, upload_date) VALUES(?,?,?,?)",
                (session["user_id"], filename, content_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            con.commit()
            flash("Resume uploaded and analyzed successfully!", "success")
        else:
            flash("Invalid file type. Only PDF and TXT allowed for now.", "danger")
            
    resumes = con.execute(
        "SELECT * FROM resumes WHERE user_id=? ORDER BY id DESC",
        (session["user_id"],)
    ).fetchall()
    con.close()
    
    return render_template("resume.html", resumes=resumes, theme=session.get("theme", "light"))

# ---------------- RESUME ACTIONS ----------------
@app.route("/resume/view/<int:id>")
def view_resume(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    con = db()
    resume = con.execute("SELECT filename FROM resumes WHERE id=? AND user_id=?", (id, session["user_id"])).fetchone()
    con.close()
    
    if resume:
        return send_from_directory(app.config['UPLOAD_FOLDER'], resume[0])
    
    flash("Resume not found.", "danger")
    return redirect(url_for("resume"))

@app.route("/resume/delete/<int:id>", methods=["POST"])
def delete_resume(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    con = db()
    resume = con.execute("SELECT filename FROM resumes WHERE id=? AND user_id=?", (id, session["user_id"])).fetchone()
    
    if resume:
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], resume[0])
            if os.path.exists(filepath):
                os.remove(filepath)
            
            con.execute("DELETE FROM resumes WHERE id=?", (id,))
            con.commit()
            flash("Resume deleted successfully.", "success")
        except Exception as e:
            flash(f"Error deleting file: {str(e)}", "danger")
    else:
        flash("Resume not found.", "danger")
        
    con.close()
    return redirect(url_for("resume"))

# ---------------- ADD JOB ----------------
@app.route("/add", methods=["POST"])
def add_job():
    if "user_id" not in session:
        return redirect(url_for("login"))

    company = request.form["company"]
    if company == "Other":
        company = request.form["other_company"]

    location = request.form["location"]
    if location == "Other":
        location = request.form["other_location"]
        
    description = request.form.get("description", "")
    
    # Calculate match score if description exists
    match_score = 0
    if description:
        resume_text = get_latest_resume_text(session["user_id"])
        match_score = calculate_match_score(resume_text, description)

    con = db()
    con.execute(
        "INSERT INTO jobs(user_id,company,role,location,status,date,description,match_score) VALUES(?,?,?,?,?,?,?,?)",
        (
            session["user_id"],
            company,
            request.form["role"],
            location,
            request.form["status"],
            datetime.now().strftime("%d-%m-%Y"),
            description,
            match_score
        )
    )
    con.commit()
    con.close()

    flash(f"Job added! Match Score: {match_score}%", "success")
    return redirect(url_for("dashboard"))

# ---------------- DELETE JOB ----------------
@app.route("/delete/<int:id>", methods=["POST"])
def delete_job(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    con = db()
    con.execute(
        "DELETE FROM jobs WHERE id=? AND user_id=?",
        (id, session["user_id"])
    )
    con.commit()
    con.close()

    flash("Job deleted successfully!", "success")
    return redirect(url_for("dashboard"))

# ---------------- UPDATE JOB ----------------
@app.route("/update/<int:id>", methods=["POST"])
def update_job(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    description = request.form.get("description", "")
    
    # Recalculate match score
    match_score = 0
    if description:
        resume_text = get_latest_resume_text(session["user_id"])
        match_score = calculate_match_score(resume_text, description)
        
    con = db()
    con.execute("""
        UPDATE jobs SET company=?, role=?, location=?, status=?, description=?, match_score=?
        WHERE id=? AND user_id=?
    """, (
        request.form["company"],
        request.form["role"],
        request.form["location"],
        request.form["status"],
        description,
        match_score,
        id,
        session["user_id"]
    ))
    con.commit()
    con.close()

    flash(f"Job updated! New Match Score: {match_score}%", "success")
    return redirect(url_for("dashboard"))

# ---------------- THEME ----------------
@app.route("/theme/<theme>")
def toggle_theme(theme):
    session["theme"] = theme
    return redirect(request.referrer or url_for("dashboard"))

# ---------------- CHATBOT ----------------
@app.route("/chat", methods=["POST"])
def chat():
    msg = request.form["message"].lower()
    
    # Simple keyword matching for "Major Project" level
    if "resume" in msg:
        if "upl" in msg:
            reply = "You can upload your resume in the 'Resume' tab to enable automatic matching."
        elif "tip" in msg:
            reply = "Key Resume Tips: 1. Use action verbs (Managed, Created). 2. Quantify results (Increased sales by 20%). 3. Tailor keywords to the job description."
        else:
            reply = "Your resume is your ticket! Keep it updated and upload it here to see how well it matches job descriptions."
            
    elif "interview" in msg:
        if "prep" in msg:
            reply = "For prep: Research the company, practice STAR method answers, and prepare 3 questions for them."
        else:
            reply = "Interviews are about fit. Be confident, honest, and enthusiastic about the role."
            
    elif "motivation" in msg:
        reply = "Rejection is just redirection. Every 'No' brings you closer to the right 'Yes'. Keep going!"
        
    elif "job" in msg:
        reply = "Quality over quantity. Apply to jobs where you meet at least 60% of requirements and tailor your application."
        
    elif "hello" in msg or "hi" in msg:
        reply = "Hello! I'm ready to help you land your next role. Ask me about resumes or interviews."
        
    else:
        reply = "I'm still learning! Try asking about 'Resume Tips', 'Interview Prep', or 'Job Search' strategies."
        
    return jsonify({"response": reply})

# ---------------- ANALYTICS DATA ----------------
@app.route("/analytics-data")
def analytics_data():
    if "user_id" not in session:
        return jsonify({})
    
    con = db()
    jobs = con.execute("SELECT status, date FROM jobs WHERE user_id=?", (session["user_id"],)).fetchall()
    con.close()
    
    status_counts = {}
    dates = []
    
    for status, date in jobs:
        status_counts[status] = status_counts.get(status, 0) + 1
        dates.append(date)
        
    return jsonify({
        "status_counts": status_counts,
        # For timeline, we might want to aggregate by date, simplified for now
        "total_jobs": len(jobs)
    })

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
