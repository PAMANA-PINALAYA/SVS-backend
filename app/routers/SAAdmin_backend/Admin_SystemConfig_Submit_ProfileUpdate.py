from fastapi import APIRouter, HTTPException
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