from fastapi import APIRouter, Query
import psycopg2
import os
import json

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