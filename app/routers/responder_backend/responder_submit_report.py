import os
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
from app.routers.responder_backend.config import get_db_conn
from app.routers.responder_backend.utils import insert_log
from datetime import datetime

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.routers.SAAdmin_backend.Admin_Notification_get import add_admin_notification
router = APIRouter()

UPLOAD_DIR = "uploaded_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/submit_report")
async def submit_report(
    responder_id: int = Form(...),
    report_title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    status: str = Form(...),
    photos: List[UploadFile] = File(None)
):
    conn = get_db_conn()
    cursor = conn.cursor()
    photo_paths = []
    try:
        if photos:
            for photo in photos[:10]:  # Limit to 10
                file_location = os.path.join(UPLOAD_DIR, photo.filename)
                with open(file_location, "wb") as f:
                    f.write(await photo.read())
                photo_paths.append(f"uploaded_photos/{photo.filename}")
        cursor.execute(
            "INSERT INTO responders_report (responder_id, report_title, description, category, status, photos) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (responder_id, report_title, description, category, status, json.dumps(photo_paths))
        )
        report_id = cursor.fetchone()[0]
        conn.commit()
        # Log report submission
        insert_log(
            responder_id,
            "Report Submit",
            f"Submitted report '{report_title}' at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        # --- Add notification for admins ---
        add_admin_notification(
            title="New Report Submitted",
            description=f"Responder submitted a new report: '{report_title}'",
            notif_type="report",
            related_id=report_id
        )
        return {"success": True}
    except Exception as e:
        print("Submit report error:", e)
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()