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

@router.post("/admin/profile/update")
def update_admin_profile(admin_id: int, full_name: str, photo: str = None):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        if photo:
            cursor.execute(
                "UPDATE admin_users SET full_name = %s, photo = %s WHERE id = %s",
                (full_name, photo, admin_id)
            )
        else:
            cursor.execute(
                "UPDATE admin_users SET full_name = %s WHERE id = %s",
                (full_name, admin_id)
            )
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating admin profile: {e}")
    finally:
        cursor.close()
        conn.close()