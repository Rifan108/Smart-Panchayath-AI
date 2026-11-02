"""
Authentication & User Management Service for Kerala Smart Panchayat AI Planner.
Provides secure SQLite user storage, password hashing, roles, and profile management.
"""

import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "users.db")


def get_db_connection():
    """Create and return a database connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize users table and insert default administrative users."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        govt_id TEXT,
        role TEXT NOT NULL,
        district TEXT,
        panchayat TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Schema migration: Ensure govt_id column exists if table was created previously
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if "govt_id" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN govt_id TEXT;")
        conn.commit()

    # Check if default admin exists
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    if count == 0:
        default_users = [
            (
                "admin",
                "admin@lsgd.kerala.gov.in",
                generate_password_hash("admin123"),
                "Dr. Rajesh Kumar IAS",
                "KL-IAS-2018-092",
                "District Planning Officer",
                "Kasaragod",
                "Manjeshwar",
            ),
            (
                "secretary",
                "secretary.manjeshwar@lsgd.kerala.gov.in",
                generate_password_hash("panchayat2025"),
                "Smt. Lakshmi Devi",
                "KL-LSGD-SEC-412",
                "Panchayat Secretary",
                "Kasaragod",
                "Manjeshwar",
            ),
            (
                "member",
                "wardmember.uppala@lsgd.kerala.gov.in",
                generate_password_hash("member123"),
                "Shri. Abdul Rahman",
                "KL-WARD-MBR-108",
                "Ward Member / Councillor",
                "Kasaragod",
                "Kumbla",
            ),
            (
                "citizen",
                "citizen.kerala@gmail.com",
                generate_password_hash("citizen123"),
                "Ananya Nair",
                "IND-CITIZEN-9921",
                "Citizen / Researcher",
                "Ernakulam",
                "Aluva",
            ),
        ]

        cursor.executemany(
            """
            INSERT INTO users (username, email, password_hash, full_name, govt_id, role, district, panchayat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            default_users,
        )
        conn.commit()
        print("[OK] User authentication database initialized with default accounts and Government IDs!")
    else:
        # Populate govt_id for existing default users if currently empty
        default_ids = {
            "admin": "KL-IAS-2018-092",
            "secretary": "KL-LSGD-SEC-412",
            "member": "KL-WARD-MBR-108",
            "citizen": "IND-CITIZEN-9921",
        }
        for u_name, g_id in default_ids.items():
            cursor.execute(
                "UPDATE users SET govt_id = ? WHERE username = ? AND (govt_id IS NULL OR govt_id = '')",
                (g_id, u_name),
            )
        conn.commit()

    conn.close()


def authenticate_user(username_or_email, password):
    """Verify username/email and password. Returns (success, message, user_dict)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM users WHERE username = ? OR email = ?
        """,
        (username_or_email.strip().lower(), username_or_email.strip().lower()),
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        return False, "User not found. Please register or check credentials.", None

    if not check_password_hash(user["password_hash"], password):
        return False, "Incorrect password. Please try again.", None

    user_dict = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "govt_id": user["govt_id"] if ("govt_id" in user.keys() and user["govt_id"]) else "KL-GOVT-VERIFIED",
        "role": user["role"],
        "district": user["district"],
        "panchayat": user["panchayat"],
    }
    return True, "Login successful!", user_dict


def register_user(username, email, password, full_name, govt_id=None, role="Citizen / Researcher", district="Kasaragod", panchayat="Manjeshwar"):
    """Register a new user account with official Government ID. Returns (success, message, user_dict)."""
    username = username.strip().lower()
    email = email.strip().lower()
    full_name = full_name.strip()
    govt_id = str(govt_id).strip().upper() if govt_id else ""

    if len(username) < 3:
        return False, "Username must be at least 3 characters long.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None
    if "@" not in email:
        return False, "Please enter a valid email address.", None
    if not govt_id or len(govt_id) < 3:
        return False, "Please enter a valid Government / Employee ID (e.g. PEN / Aadhaar / KILA ID / Voter ID).", None

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        pw_hash = generate_password_hash(password)
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, full_name, govt_id, role, district, panchayat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (username, email, pw_hash, full_name, govt_id, role, district, panchayat),
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        user_dict = {
            "id": user_id,
            "username": username,
            "email": email,
            "full_name": full_name,
            "govt_id": govt_id,
            "role": role,
            "district": district,
            "panchayat": panchayat,
        }
        return True, "Account registered successfully!", user_dict

    except sqlite3.IntegrityError as e:
        conn.close()
        if "username" in str(e):
            return False, "Username is already taken. Please choose another.", None
        return False, "Email is already registered. Please login.", None
    except Exception as e:
        conn.close()
        return False, f"Registration failed: {str(e)}", None


# Auto-initialize database on import
init_db()
