import sqlite3

conn = sqlite3.connect('jobs.db')
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    filename TEXT,
    content_text TEXT,
    upload_date TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    company TEXT,
    role TEXT,
    location TEXT,
    status TEXT,
    date TEXT,
    description TEXT,
    match_score INTEGER,
    resume_id INTEGER
)
""")

conn.commit()
conn.close()
print("✅ Database initialized successfully")
