from fastapi import APIRouter, Query
from app.routers.responder_backend.config import get_db_conn
import json

router = APIRouter()

@router.get("/get_reports")
def get_reports(responder_id: int = Query(...)):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, report_title, description, category, status, submitted_at, photos, rejection_reason
        FROM responders_report
        WHERE responder_id = %s
        ORDER BY submitted_at DESC
    """, (responder_id,))
    reports = cursor.fetchall()
    report_list = []
    for row in reports:
        photos = []
        if row[6]:
            try:
                # Fix: Remove extra quotes if present
                photos_raw = row[6]
                if isinstance(photos_raw, str):
                    photos = json.loads(photos_raw.replace('""', '"'))
                elif isinstance(photos_raw, list):
                    photos = photos_raw
                else:
                    photos = []
                # Ensure it's a list of strings
                if not isinstance(photos, list):
                    photos = []
                photos = [str(p) for p in photos]
            except Exception:
                photos = []
        report_list.append({
            "id": row[0],
            "report_title": row[1],
            "description": row[2],
            "category": row[3],
            "status": row[4],
            "submitted_at": str(row[5]),
            "photos": photos,
            "rejection_reason": row[7] if len(row) > 7 and row[7] else ""
        })
    cursor.close()
    conn.close()
    return {"reports": report_list}