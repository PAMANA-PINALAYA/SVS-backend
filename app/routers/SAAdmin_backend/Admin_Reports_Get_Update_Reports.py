from fastapi import APIRouter, HTTPException
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

@router.get("/admin/reports")
def fetch_reports():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT rr.id, r.full_name, rr.report_title, rr.description, rr.category, rr.status, rr.photos, rr.submitted_at, rr.rejection_reason
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
                "rejection_reason": row[8] or ""
            })
        return reports
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/reports/approve")
def approve_report(report_id: int, admin_name: str):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE responders_report SET status = 'Approved', rejection_reason = NULL, approved_by = %s WHERE id = %s",
            (admin_name, report_id)
        )
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/reports/reject")
def reject_report(report_id: int, reason: str):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE responders_report SET status = 'Rejected', rejection_reason = %s WHERE id = %s",
            (reason, report_id)
        )
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/patrolling_logs")
def fetch_patrolling_logs():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT p.id, r.full_name, p.area, p.start_time, p.finish_time, p.findings, p.description, p.photo
            FROM patrolling p
            JOIN responders r ON p.responder_id = r.id
            ORDER BY p.start_time DESC
        """)
        logs = []
        for row in cursor.fetchall():
            logs.append({
                "id": row[0],
                "responder_name": row[1],
                "area": row[2],
                "start_time": row[3].strftime("%Y-%m-%d %H:%M") if row[3] else "",
                "finish_time": row[4].strftime("%Y-%m-%d %H:%M") if row[4] else "",
                "findings": row[5] or "",
                "description": row[6] or "",
                "photo": row[7] or ""
            })
        return logs
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/patrolling_log/{patrol_id}")
def fetch_patrolling_log_by_id(patrol_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT p.id, r.full_name, p.area, p.start_time, p.finish_time, p.findings, p.description, p.photo
            FROM patrolling p
            JOIN responders r ON p.responder_id = r.id
            WHERE p.id = %s
        """, (patrol_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "responder_name": row[1],
                "area": row[2],
                "start_time": row[3].strftime("%Y-%m-%d %H:%M") if row[3] else "",
                "finish_time": row[4].strftime("%Y-%m-%d %H:%M") if row[4] else "",
                "findings": row[5] or "",
                "description": row[6] or "",
                "photo": row[7] or ""
            }
        return None
    finally:
        cursor.close()
        conn.close()