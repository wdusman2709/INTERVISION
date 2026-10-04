import sqlite3
from pathlib import Path


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "intervision.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """Create and return a database connection."""

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False,
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():
    """Create all required database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # Candidates
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            education TEXT,
            skills TEXT,
            experience TEXT,
            job_role TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # --------------------------------------------------------
    # Interviews
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            difficulty TEXT,
            interview_type TEXT,
            number_of_questions INTEGER,
            average_score REAL,
            highest_score REAL,
            lowest_score REAL,
            completed_questions INTEGER,
            total_questions INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id)
                REFERENCES candidates(id)
        )
        """
    )

    # --------------------------------------------------------
    # Answers
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            question TEXT,
            answer TEXT,
            category TEXT,
            score REAL,
            relevance REAL,
            correctness REAL,
            completeness REAL,
            clarity REAL,
            feedback TEXT,
            strengths TEXT,
            weaknesses TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_id)
                REFERENCES interviews(id)
        )
        """
    )

    connection.commit()
    connection.close()


# ============================================================
# CANDIDATE FUNCTIONS
# ============================================================

def create_candidate(
    name,
    education,
    skills,
    experience,
    job_role,
):
    """Create a candidate and return the candidate ID."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO candidates
        (
            name,
            education,
            skills,
            experience,
            job_role
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            education,
            skills,
            experience,
            job_role,
        ),
    )

    candidate_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return candidate_id


# ============================================================
# INTERVIEW FUNCTIONS
# ============================================================

def create_interview(
    candidate_id,
    difficulty,
    interview_type,
    number_of_questions,
):
    """Create a new interview and return its ID."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO interviews
        (
            candidate_id,
            difficulty,
            interview_type,
            number_of_questions,
            average_score,
            highest_score,
            lowest_score,
            completed_questions,
            total_questions
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            candidate_id,
            difficulty,
            interview_type,
            number_of_questions,
            0,
            0,
            0,
            0,
            number_of_questions,
        ),
    )

    interview_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return interview_id


# ============================================================
# ANSWER FUNCTIONS
# ============================================================

def save_answer(
    interview_id,
    question,
    answer,
    category,
    score,
    relevance,
    correctness,
    completeness,
    clarity,
    feedback,
    strengths,
    weaknesses,
):
    """Save an evaluated interview answer."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO answers
        (
            interview_id,
            question,
            answer,
            category,
            score,
            relevance,
            correctness,
            completeness,
            clarity,
            feedback,
            strengths,
            weaknesses
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            interview_id,
            question,
            answer,
            category,
            score,
            relevance,
            correctness,
            completeness,
            clarity,
            feedback,
            "\n".join(strengths)
            if isinstance(strengths, list)
            else str(strengths),
            "\n".join(weaknesses)
            if isinstance(weaknesses, list)
            else str(weaknesses),
        ),
    )

    connection.commit()
    connection.close()


# ============================================================
# INTERVIEW SUMMARY
# ============================================================

def update_interview_summary(
    interview_id,
    scores,
):
    """Update interview statistics."""

    if not scores:
        return

    numeric_scores = [
        float(score)
        for score in scores
    ]

    average_score = (
        sum(numeric_scores)
        / len(numeric_scores)
    )

    highest_score = max(numeric_scores)
    lowest_score = min(numeric_scores)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE interviews
        SET
            average_score = ?,
            highest_score = ?,
            lowest_score = ?,
            completed_questions = ?
        WHERE id = ?
        """,
        (
            average_score,
            highest_score,
            lowest_score,
            len(numeric_scores),
            interview_id,
        ),
    )

    connection.commit()
    connection.close()