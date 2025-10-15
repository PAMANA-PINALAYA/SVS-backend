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