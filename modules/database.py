"""Database Module for Internal Marks 'What-If' Simulator.

Provides SQLite3 local persistence for subjects and saved simulation scenarios.
Includes transactional integrity, constraint enforcement, and sample data seeding.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "simulator.db")

SAMPLE_SUBJECTS: List[Dict[str, Any]] = [
    {
        "subject_name": "Data Structures",
        "internal_max": 30.0,
        "internal_obtained": 22.0,
        "external_max": 70.0,
        "attendance": 82.0,
    },
    {
        "subject_name": "Python Programming",
        "internal_max": 30.0,
        "internal_obtained": 18.0,
        "external_max": 70.0,
        "attendance": 68.0,  # Warning case (< 75%)
    },
    {
        "subject_name": "Database Management",
        "internal_max": 30.0,
        "internal_obtained": 25.0,
        "external_max": 70.0,
        "attendance": 90.0,
    },
    {
        "subject_name": "Software Engineering",
        "internal_max": 30.0,
        "internal_obtained": 24.0,
        "external_max": 70.0,
        "attendance": 78.0,
    },
]


def get_db_connection() -> sqlite3.Connection:
    """Create and return a configured SQLite connection with row factory enabled."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Initialize database tables and populate sample subjects if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Subjects Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT UNIQUE NOT NULL,
            internal_max REAL NOT NULL,
            internal_obtained REAL NOT NULL,
            external_max REAL NOT NULL,
            attendance REAL NOT NULL
        )
    """)

    # Scenarios Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Scenario Scores Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scenario_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id INTEGER NOT NULL,
            subject_name TEXT NOT NULL,
            simulated_external REAL NOT NULL,
            FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE
        )
    """)

    conn.commit()

    # Seed initial sample data if empty
    cursor.execute("SELECT COUNT(*) as count FROM subjects")
    count = cursor.fetchone()["count"]
    if count == 0:
        reset_to_sample_data(conn)
    else:
        conn.close()


def reset_to_sample_data(existing_conn: Optional[sqlite3.Connection] = None) -> None:
    """Reset subjects table to the default MCA curriculum sample subjects."""
    conn = existing_conn or get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM subjects")
    for s in SAMPLE_SUBJECTS:
        cursor.execute(
            """
            INSERT INTO subjects (subject_name, internal_max, internal_obtained, external_max, attendance)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                s["subject_name"],
                float(s["internal_max"]),
                float(s["internal_obtained"]),
                float(s["external_max"]),
                float(s["attendance"]),
            ),
        )
    conn.commit()
    if existing_conn is None:
        conn.close()


def get_all_subjects() -> List[Dict[str, Any]]:
    """Retrieve all configured subjects ordered by subject name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects ORDER BY subject_name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_subject(
    subject_name: str,
    internal_max: float,
    internal_obtained: float,
    external_max: float,
    attendance: float,
) -> Tuple[bool, str]:
    """Add a new subject after validating data constraints."""
    name = subject_name.strip()
    if not name:
        return False, "Subject name cannot be empty."

    if internal_max <= 0:
        return False, "Internal maximum marks must be greater than 0."

    if internal_obtained < 0:
        return False, "Internal obtained marks cannot be negative."

    if internal_obtained > internal_max:
        return False, f"Internal obtained marks ({internal_obtained}) cannot exceed maximum ({internal_max})."

    if external_max <= 0:
        return False, "External maximum marks must be greater than 0."

    if not (0.0 <= attendance <= 100.0):
        return False, "Attendance percentage must be between 0% and 100%."

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO subjects (subject_name, internal_max, internal_obtained, external_max, attendance)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, float(internal_max), float(internal_obtained), float(external_max), float(attendance)),
        )
        conn.commit()
        return True, f"Subject '{name}' added successfully."
    except sqlite3.IntegrityError:
        return False, f"A subject with name '{name}' already exists."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()


def update_subject(
    subject_id: int,
    subject_name: str,
    internal_max: float,
    internal_obtained: float,
    external_max: float,
    attendance: float,
) -> Tuple[bool, str]:
    """Update existing subject details with rigorous validation."""
    name = subject_name.strip()
    if not name:
        return False, "Subject name cannot be empty."

    if internal_max <= 0:
        return False, "Internal maximum marks must be greater than 0."

    if internal_obtained < 0:
        return False, "Internal obtained marks cannot be negative."

    if internal_obtained > internal_max:
        return False, f"Internal obtained marks ({internal_obtained}) cannot exceed maximum ({internal_max})."

    if external_max <= 0:
        return False, "External maximum marks must be greater than 0."

    if not (0.0 <= attendance <= 100.0):
        return False, "Attendance percentage must be between 0% and 100%."

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE subjects
            SET subject_name = ?, internal_max = ?, internal_obtained = ?, external_max = ?, attendance = ?
            WHERE id = ?
            """,
            (name, float(internal_max), float(internal_obtained), float(external_max), float(attendance), subject_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return False, f"Subject with ID {subject_id} not found."
        return True, f"Subject '{name}' updated successfully."
    except sqlite3.IntegrityError:
        return False, f"Another subject with name '{name}' already exists."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()


def delete_subject(subject_id: int) -> Tuple[bool, str]:
    """Delete a subject by its primary key ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) as count FROM subjects")
        count = cursor.fetchone()["count"]
        if count <= 1:
            return False, "At least one subject is required for simulation. Cannot delete the only subject."

        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
        return True, "Subject deleted successfully."
    except Exception as e:
        return False, f"Error deleting subject: {str(e)}"
    finally:
        conn.close()


def save_scenario(
    scenario_name: str,
    scores: Dict[str, float],
    description: str = "",
) -> Tuple[bool, str]:
    """Persist a simulated external examination marks scenario for multi-scenario comparison."""
    name = scenario_name.strip()
    if not name:
        return False, "Scenario name cannot be empty."

    if not scores:
        return False, "No subject scores provided to save in scenario."

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO scenarios (scenario_name, description) VALUES (?, ?)",
            (name, description),
        )
        scenario_id = cursor.lastrowid

        for subj_name, ext_score in scores.items():
            cursor.execute(
                """
                INSERT INTO scenario_scores (scenario_id, subject_name, simulated_external)
                VALUES (?, ?, ?)
                """,
                (scenario_id, subj_name, float(ext_score)),
            )

        conn.commit()
        return True, f"Scenario '{name}' saved successfully."
    except sqlite3.IntegrityError:
        return False, f"Scenario with name '{name}' already exists. Please choose a different name."
    except Exception as e:
        conn.rollback()
        return False, f"Failed to save scenario: {str(e)}"
    finally:
        conn.close()


def get_saved_scenarios() -> List[Dict[str, Any]]:
    """Retrieve all saved scenarios with their creation timestamps."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scenarios ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_scenario_scores(scenario_id: int) -> Dict[str, float]:
    """Retrieve simulated scores mapped by subject name for a given scenario ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT subject_name, simulated_external FROM scenario_scores WHERE scenario_id = ?",
        (scenario_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return {row["subject_name"]: row["simulated_external"] for row in rows}


def delete_scenario(scenario_id: int) -> Tuple[bool, str]:
    """Delete a scenario and its associated scores."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM scenarios WHERE id = ?", (scenario_id,))
        conn.commit()
        return True, "Scenario removed successfully."
    except Exception as e:
        return False, f"Failed to delete scenario: {str(e)}"
    finally:
        conn.close()
