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

@router.post("/superadmin/device/integrate")
def submit_integration(cctv_id: int, mic_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO device_integration (cctv_id, microphone_id, link_type) VALUES (%s, %s, %s)",
            (cctv_id, mic_id, 'integrated')
        )
        conn.commit()
        return {"success": True, "message": "Integration successful."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error integrating devices: {e}")
    finally:
        cursor.close()
        conn.close()