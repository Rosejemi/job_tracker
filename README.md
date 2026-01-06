This project is a Job Application Tracker web application built using Python (Flask) and SQLite. It allows users to manage their job search process, including tracking applications, uploading resumes, and analyzing how well their resume matches specific job descriptions.

Here is a detailed breakdown of the project:

Tech Stack
Backend: Python (Flask)
Database: SQLite (
jobs.db
)
Frontend: HTML/CSS (likely with Jinja2 templates)
Key Libraries: PyPDF2 (for parsing PDF resumes)
Key Features
User Authentication:
Start/Login pages (/, /register) allow users to create an account and sign in securely.
User sessions are managed to keep data private.
Dashboard (/dashboard):
The central hub where users can see a list of all their tracked jobs.
It displays the status of applications (e.g., Applied, Interview, Offer) and the match score.
Job Management:
Add/Edit Jobs: Users can input job details like Company, Role, Location, Status, and Job Description.
Automated Match Score: When a job description is added, the app automatically compares it against the user's latest uploaded resume. It calculates a percentage score based on keyword overlap (logic in 
utils.py
).
Resume System:
Users can upload resumes (PDF or TXT format).
The app extracts text from these files to use for the "Match Score" algorithm.
Users can view and manage their uploaded resumes.
Analytics:
An API endpoint (/analytics-data) provides data on the status of applications (e.g., how many jobs are in "Applied" vs "Rejected"), likely used for visualization on the frontend.
AI Assistant / Chatbot:
A built-in chatbot (/chat) that provides keyword-based advice on "Resume Tips", "Interview Prep", and motivation.
Theming:
Includes a light/dark mode feature toggled via session state.
