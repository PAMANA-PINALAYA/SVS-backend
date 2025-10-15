from fastapi import APIRouter
import psycopg2
import os

router = APIRouter()

def get_db_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "SmartSurveillanceSystem"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASS", "123")
    )

@router.get("/admin/profile")
def get_admin_profile(admin_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT full_name, email, photo FROM admin_users WHERE id = %s", (admin_id,))
        row = cursor.fetchone()
        if row:
            return {
                "full_name": row[0],
                "email": row[1],
                "photo": row[2] if row[2] else "policeman.png"
            }
        return None
    finally:
        cursor.close()
        conn.close()