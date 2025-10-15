from fastapi import APIRouter, HTTPException
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

@router.get("/admin/responders")
def fetch_responders():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, full_name, email, phone, username, is_active, created_at, approved, status
            FROM responders
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "full_name": row[1],
                "email": row[2],
                "phone": row[3],
                "username": row[4],
                "is_active": row[5],
                "created_at": row[6].strftime("%Y-%m-%d %H:%M") if row[6] else "",
                "approved": row[7],
                "status": row[8]
            }
            for row in rows
        ]
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/responders/update_status")
def update_responder_status(user_id: int, is_active: bool):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        new_status = 'approved' if is_active else 'suspended'
        cursor.execute("""
            UPDATE responders 
            SET is_active = %s, status = %s
            WHERE id = %s
        """, (is_active, new_status, user_id))
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/responders/delete")
def delete_responder(user_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM responders WHERE id = %s", (user_id,))
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()