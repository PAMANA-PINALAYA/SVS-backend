from fastapi import APIRouter, Body
from app.routers.responder_backend.config import get_db_conn
from app.routers.responder_backend.utils import insert_log
from datetime import datetime, timezone, timedelta

router = APIRouter()

@router.post("/alerts/action")
def take_action(alert_id: int = Body(..., embed=True), responder_id: int = Body(..., embed=True)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        now = datetime.now(timezone.utc)
        cursor.execute("""
            UPDATE admin_alert_pushing
            SET status = 'action taken',
                action_status = 'ongoing',
                action_started_at = %s,
                action_finished_at = NULL,
                action_duration = NULL
            WHERE id = %s
        """, (now, alert_id))
        conn.commit()
        # Log action start
        insert_log(
            responder_id,
            "Alert Action Start",
            f"Started action on alert {alert_id} at {now.isoformat()}"
        )
        return {"success": True, "action_started_at": now.isoformat()}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()

@router.post("/alerts/finish_action")
def finish_action(alert_id: int = Body(..., embed=True), responder_id: int = Body(None, embed=True)):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        now = datetime.now(timezone.utc)
        cursor.execute("""
            SELECT action_started_at, title, assigned_responder
            FROM admin_alert_pushing
            WHERE id = %s
        """, (alert_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            return {"success": False, "error": "Action not started"}
        started_at, alert_title, responder_id_db = row

        # Ensure started_at is timezone-aware UTC
        if started_at and started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)

        duration = now - started_at if started_at else timedelta(0)
        if duration.total_seconds() < 0:
            duration = timedelta(0)

        responder_name = "Unknown"
        actual_responder_id = responder_id if responder_id is not None else responder_id_db
        if actual_responder_id:
            cursor.execute("SELECT full_name FROM responders WHERE id = %s", (actual_responder_id,))
            res = cursor.fetchone()
            if res and res[0]:
                responder_name = res[0]

        cursor.execute("""
            UPDATE admin_alert_pushing
            SET action_status = 'finished',
                action_finished_at = %s,
                action_duration = %s
            WHERE id = %s
        """, (now, duration, alert_id))
        conn.commit()
        # Log action finish
        insert_log(
            actual_responder_id,
            "Alert Action Finish",
            f"Responder '{responder_name}' finished action for alert: {alert_title} at {now.isoformat()}"
        )
        return {
            "success": True,
            "action_finished_at": now.isoformat(),
            "action_duration": str(duration)
        }
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()