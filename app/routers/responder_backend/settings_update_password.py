from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import psycopg2

DB_HOST = "localhost"
DB_NAME = "SmartSurveillanceSystem"
DB_USER = "postgres"
DB_PASS = "123"

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

router = APIRouter()

class ChangePasswordRequest(BaseModel):
    responder_id: int
    old_password: str
    new_password: str

@router.post("/change_password")
def change_password(data: ChangePasswordRequest):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT password FROM responders WHERE id=%s",
            (data.responder_id,)
        )
        result = cursor.fetchone()
        if not result or result[0] != data.old_password:
            raise HTTPException(status_code=400, detail="Old password is incorrect.")
        cursor.execute(
            "UPDATE responders SET password=%s WHERE id=%s",
            (data.new_password, data.responder_id)
        )
        conn.commit()
        return {"success": True, "message": "Password changed successfully."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()