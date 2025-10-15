from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.routers.responder_backend.config import get_db_conn
from app.routers.responder_backend.utils import insert_log
import os
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "patrol_photos")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/submit_patrolling")
async def submit_patrolling(
    responder_id: int = Form(...),
    area: str = Form(...),
    start_time: str = Form(...),
    finish_time: str = Form(...),
    findings: str = Form(...),
    description: str = Form(...),
    photo: UploadFile = File(None)
):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        photo_filename = None
        if photo:
            photo_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{photo.filename}"
            photo_path = os.path.join(UPLOAD_DIR, photo_filename)
            with open(photo_path, "wb") as f:
                f.write(await photo.read())
        cursor.execute(
            """
            INSERT INTO patrolling (
                responder_id, area, start_time, finish_time, findings, description, photo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                responder_id,
                area,
                start_time,
                finish_time,
                findings,
                description,
                photo_filename
            )
        )
        conn.commit()
        # Log the patrol
        insert_log(
            responder_id,
            "Patrol",
            f"Patrol in {area}: started at {start_time}, finished at {finish_time}. Findings: {findings}"
        )
        return {"success": True, "message": "Patrol submitted."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()