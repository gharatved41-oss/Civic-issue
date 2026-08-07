"""
database.py
Handles all SQLite persistence for the Civic Sense AI app:
- users (login/roles)
- incidents (citizen-reported civic issues)
"""

import sqlite3
import hashlib
from datetime import datetime
import pandas as pd

DB_PATH = "civic_sense.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role TEXT NOT NULL DEFAULT 'citizen',
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            category TEXT,
            description TEXT,
            location_text TEXT,
            lat REAL,
            lon REAL,
            priority TEXT,
            status TEXT DEFAULT 'Pending',
            image_name TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()

    # Seed default admin + demo citizen if users table is empty
    cur.execute("SELECT COUNT(*) as c FROM users")
    if cur.fetchone()["c"] == 0:
        now = datetime.now().isoformat()
        cur.execute(
            "INSERT INTO users (username, password, email, role, created_at) VALUES (?, ?, ?, ?, ?)",
            ("admin", hash_password("admin123"), "admin@civicsense.ai", "admin", now),
        )
        cur.execute(
            "INSERT INTO users (username, password, email, role, created_at) VALUES (?, ?, ?, ?, ?)",
            ("citizen", hash_password("citizen123"), "citizen@civicsense.ai", "citizen", now),
        )
        conn.commit()

        # Seed a couple of sample incidents so the map/dashboard aren't empty on first run
        sample = [
            (2, "citizen", "Pothole", "Large pothole causing traffic slowdown near main junction.",
             "MG Road, Vasai", 19.4667, 72.8000, "High", "Pending", None, now, now),
            (2, "citizen", "Garbage", "Overflowing garbage bin not collected for a week.",
             "Station Road, Virar", 19.4559, 72.8117, "Medium", "In Progress", None, now, now),
        ]
        cur.executemany("""
            INSERT INTO incidents (user_id, username, category, description, location_text,
                lat, lon, priority, status, image_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample)
        conn.commit()

    conn.close()


# ---------------- USER FUNCTIONS ----------------

def create_user(username, password, email, role="citizen"):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password, email, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (username, hash_password(password), email, role, datetime.now().isoformat()),
        )
        conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()


def verify_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row and row["password"] == hash_password(password):
        return dict(row)
    return None


# ---------------- INCIDENT FUNCTIONS ----------------

def add_incident(user_id, username, category, description, location_text, lat, lon, priority, image_name=None):
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now().isoformat()
    cur.execute("""
        INSERT INTO incidents (user_id, username, category, description, location_text,
            lat, lon, priority, status, image_name, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?, ?, ?)
    """, (user_id, username, category, description, location_text, lat, lon, priority, image_name, now, now))
    conn.commit()
    incident_id = cur.lastrowid
    conn.close()
    return incident_id


def get_incidents(status=None, category=None, username=None):
    conn = get_connection()
    query = "SELECT * FROM incidents WHERE 1=1"
    params = []
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if username:
        query += " AND username = ?"
        params.append(username)
    query += " ORDER BY created_at DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def update_incident_status(incident_id, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE incidents SET status = ?, updated_at = ? WHERE id = ?",
        (status, datetime.now().isoformat(), incident_id),
    )
    conn.commit()
    conn.close()


def delete_incident(incident_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM incidents WHERE id = ?", (incident_id,))
    conn.commit()
    conn.close()


def get_stats():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM incidents", conn)
    conn.close()
    stats = {
        "total": len(df),
        "pending": len(df[df["status"] == "Pending"]) if not df.empty else 0,
        "in_progress": len(df[df["status"] == "In Progress"]) if not df.empty else 0,
        "resolved": len(df[df["status"] == "Resolved"]) if not df.empty else 0,
        "by_category": df["category"].value_counts().to_dict() if not df.empty else {},
        "by_priority": df["priority"].value_counts().to_dict() if not df.empty else {},
    }
    return stats, df
