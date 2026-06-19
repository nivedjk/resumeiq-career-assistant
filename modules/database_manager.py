import sqlite3

DB_PATH = "database/careermatch.db"


def create_table():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_name TEXT,
        job_name TEXT,
        score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_job_result(
    resume_name,
    job_name,
    score
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO job_results
    (
        resume_name,
        job_name,
        score
    )
    VALUES (?, ?, ?)
    """, (
        resume_name,
        job_name,
        score
    ))

    conn.commit()
    conn.close()


def get_resume_history():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        resume_name,
        job_name,
        score,
        created_at
    FROM job_results
    ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    history = {}

    for row in rows:

        resume_name = row[0]

        if resume_name not in history:
            history[resume_name] = []

        history[resume_name].append(
            (
                row[1],  # job_name
                row[2],  # score
                row[3]   # date
            )
        )

    return history


def clear_history():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM job_results
    """)

    conn.commit()
    conn.close()