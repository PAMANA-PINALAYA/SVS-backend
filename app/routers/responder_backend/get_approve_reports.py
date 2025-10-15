from fastapi import APIRouter, Query
import psycopg2
import os
import json

router = APIRouter()

def get_db_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "SmartSurveillanceSystem"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASS", "123")
    )

@router.get("/get_approve_reports")
def get_approve_reports(responder_id: int = Query(...)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, report_title, description, category, status, photos, submitted_at
            FROM responders_report
            WHERE responder_id = %s AND status = 'Approved'
            ORDER BY submitted_at DESC
        """, (responder_id,))
        reports = []
        for row in cursor.fetchall():
            photos = []
            if row[5]:
                try:
                    photos = json.loads(row[5])
                except Exception:
                    photos = []
            reports.append({
                "id": row[0],
                "report_title": row[1],
                "description": row[2],
                "category": row[3],
                "status": row[4],
                "photos": photos,
                "submitted_at": row[6].strftime("%Y-%m-%d %H:%M"),
            })
        return {"approved": reports}
    finally:
        cursor.close()
        conn.close()