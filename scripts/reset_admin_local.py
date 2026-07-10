from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import ADMIN_EMAIL, DB_PATH
from app.core.db import init_db
from app.security.passwords import hash_password


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset admin local credentials.")
    parser.add_argument("--email", default=ADMIN_EMAIL or "admin@nutriavicola.local")
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    email = args.email.strip().lower()
    password = args.password
    now = datetime.now(timezone.utc).isoformat()

    init_db(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    try:
        role = conn.execute(
            "SELECT id FROM roles WHERE code = 'admin'"
        ).fetchone()
        row = conn.execute(
            "SELECT id FROM users WHERE lower(email) = ?",
            (email,),
        ).fetchone()
        if row:
            user_id = int(row[0])
        else:
            cur = conn.execute(
                """
                INSERT INTO users (
                    email, password_hash, full_name, is_active, must_change_pwd,
                    failed_attempts, created_at, updated_at
                ) VALUES (?, ?, ?, 1, 0, 0, ?, ?)
                """,
                (email, hash_password(password), "Administrador", now, now),
            )
            user_id = int(cur.lastrowid)

        conn.execute(
            """
            UPDATE users
            SET password_hash = ?,
                is_active = 1,
                must_change_pwd = 0,
                failed_attempts = 0,
                locked_until = NULL,
                updated_at = ?
            WHERE id = ?
            """,
            (hash_password(password), now, user_id),
        )
        if role is not None:
            conn.execute(
                "INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)",
                (user_id, int(role[0])),
            )
        conn.commit()
    finally:
        conn.close()
    print("RESET_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
