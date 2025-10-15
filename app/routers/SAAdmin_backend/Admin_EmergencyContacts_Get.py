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

@router.get("/admin/emergency_contacts")
def get_emergency_contacts():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name, phone, role, address, is_active FROM emergency_contacts ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [
            {
                "name": row[0],
                "phone": row[1],
                "role": row[2],
                "address": row[3],
                "is_active": row[4]
            }
            for row in rows
        ]
    finally:
        cursor.close()
        conn.close()