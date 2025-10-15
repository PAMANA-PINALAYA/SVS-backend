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