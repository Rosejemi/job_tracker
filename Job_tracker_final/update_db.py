import sqlite3

DB = "jobs.db"

def migrate():
    con = sqlite3.connect(DB)
    c = con.cursor()

    # 1. Create resumes table
    c.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT,
        content_text TEXT,
        upload_date TEXT
    )
    """)
    print("Checked/Created 'resumes' table.")

    # 2. Add columns to jobs table
    # SQLite doesn't support IF NOT EXISTS for ADD COLUMN directly in a simple way for multiple cols without check.
    # We will try adding them one by one and ignore errors if they exist.
    
    columns_to_add = [
        ("description", "TEXT"),
        ("match_score", "INTEGER"),
        ("resume_id", "INTEGER")
    ]

    for col_name, col_type in columns_to_add:
        try:
            c.execute(f"ALTER TABLE jobs ADD COLUMN {col_name} {col_type}")
            print(f"Added column '{col_name}' to 'jobs' table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column '{col_name}' already exists in 'jobs' table.")
            else:
                print(f"Error adding column '{col_name}': {e}")

    con.commit()
    con.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
