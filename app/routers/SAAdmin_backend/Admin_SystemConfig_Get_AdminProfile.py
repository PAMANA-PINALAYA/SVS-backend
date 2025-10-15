from fastapi import APIRouter
import psycopg2
import os

router = APIRouter()

def get_db_conn():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    else:
        return psycopg2.connect(
            host="localhost",
            dbname="SmartSurveillanceSystem",
            user="postgres",
            password="123"
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