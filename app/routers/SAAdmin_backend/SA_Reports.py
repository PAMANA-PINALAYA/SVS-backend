from fastapi import APIRouter, HTTPException, Query
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
@router.get("/admin/reports")
def fetch_reports():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT rr.id, r.full_name, rr.report_title, rr.description, rr.category, rr.status, rr.photos, rr.submitted_at, rr.rejection_reason, rr.approved_by
            FROM responders_report rr
            JOIN responders r ON rr.responder_id = r.id
            ORDER BY rr.submitted_at DESC
        """)
        reports = []
        for row in cursor.fetchall():
            photo_list = []
            if row[6]:
                try:
                    photos_raw = row[6]
                    if isinstance(photos_raw, str):
                        photo_list = json.loads(photos_raw.replace('""', '"'))
                    elif isinstance(photos_raw, list):
                        photo_list = photos_raw
                    else:
                        photo_list = []
                    if not isinstance(photo_list, list):
                        photo_list = []
                    photo_list = [str(p) for p in photo_list]
                except Exception:
                    photo_list = []
            reports.append({
                "id": row[0],
                "responder_name": row[1],
                "title": row[2],
                "description": row[3],
                "category": row[4],
                "status": row[5],
                "photos": photo_list,
                "submitted_at": row[7].strftime("%Y-%m-%d %H:%M"),
                "rejection_reason": row[8] or "",
                "approved_by": row[9] or "",
                "submitted_to": ""
            })
        return reports
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/report/{report_id}")
def get_report(report_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT rr.id, r.full_name, rr.report_title, rr.description, rr.category, rr.status, rr.photos, rr.submitted_at, rr.rejection_reason, rr.approved_by
            FROM responders_report rr
            JOIN responders r ON rr.responder_id = r.id
            WHERE rr.id = %s
        """, (report_id,))
        row = cursor.fetchone()
        if not row:
            return None
        photo_list = []
        if row[6]:
            try:
                photos_raw = row[6]
                if isinstance(photos_raw, str):
                    photo_list = json.loads(photos_raw.replace('""', '"'))
                elif isinstance(photos_raw, list):
                    photo_list = photos_raw
                else:
                    photo_list = []
                if not isinstance(photo_list, list):
                    photo_list = []
                photo_list = [str(p) for p in photo_list]
            except Exception:
                photo_list = []
        return {
            "id": row[0],
            "responder_name": row[1],
            "title": row[2],
            "description": row[3],
            "category": row[4],
            "status": row[5],
            "photos": photo_list,
            "submitted_at": row[7].strftime("%Y-%m-%d %H:%M"),
            "rejection_reason": row[8] or "",
            "approved_by": row[9] or "",
            "submitted_to": ""
        }
    finally:
        cursor.close()
        conn.close()

@router.delete("/admin/report/{report_id}")
def delete_report(report_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM responders_report WHERE id = %s", (report_id,))
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/report/export_pdf")
def export_report_pdf(report_id: int, output_path: str):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    y = height - 40
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, f"Report: {report['title']}")
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(40, y, f"Responder: {report['responder_name']}")
    y -= 20
    c.drawString(40, y, f"Category: {report['category']}")
    y -= 20
    c.drawString(40, y, f"Status: {report['status']}")
    y -= 20
    c.drawString(40, y, f"Submitted At: {report['submitted_at']}")
    y -= 20
    c.drawString(40, y, f"Approved By: {report.get('approved_by', '')}")
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Description:")
    y -= 20
    c.setFont("Helvetica", 12)
    for line in report['description'].splitlines():
        c.drawString(50, y, line)
        y -= 15
    if report['rejection_reason']:
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Rejection Reason:")
        y -= 20
        c.setFont("Helvetica", 12)
        for line in report['rejection_reason'].splitlines():
            c.drawString(50, y, line)
            y -= 15
    if report['photos']:
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Photos:")
        y -= 20
        c.setFont("Helvetica", 10)
        for photo in report['photos']:
            c.drawString(50, y, photo)
            y -= 15
    c.save()
    return {"success": True, "output_path": output_path}