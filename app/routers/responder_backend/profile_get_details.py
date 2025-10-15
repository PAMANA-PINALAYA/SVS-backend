from fastapi import APIRouter, Query
from app.routers.responder_backend.config import get_db_conn

router = APIRouter()

@router.get("/profile/details")
def get_profile_details(responder_id: int = Query(...)):
    conn = get_db_conn()
    cursor = conn.cursor()

    # Get basic profile info (remove bio)
    cursor.execute("SELECT full_name, assigned_at, photo FROM responders WHERE id = %s", (responder_id,))
    row = cursor.fetchone()
    full_name, assigned_at, photo = row if row else ("", "", "")

    # Actions taken and finished
    cursor.execute("SELECT COUNT(*) FROM admin_alert_pushing WHERE assigned_responder = %s", (responder_id,))
    actions_taked = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM admin_alert_pushing WHERE assigned_responder = %s AND action_status = 'finished'", (responder_id,))
    actions_finished = cursor.fetchone()[0]

    # Reports submitted and approved
    cursor.execute("SELECT COUNT(*) FROM responders_report WHERE responder_id = %s", (responder_id,))
    reports_submitted = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM responders_report WHERE responder_id = %s AND status ILIKE 'approved'", (responder_id,))
    reports_approved = cursor.fetchone()[0]

    # Average response time (in minutes)
    cursor.execute("""
        SELECT EXTRACT(EPOCH FROM (action_finished_at - action_started_at))/60
        FROM admin_alert_pushing
        WHERE assigned_responder = %s AND action_status = 'finished' AND action_started_at IS NOT NULL AND action_finished_at IS NOT NULL
    """, (responder_id,))
    response_times = [r[0] for r in cursor.fetchall() if r[0] is not None]
    avg_response_time = round(sum(response_times)/len(response_times), 1) if response_times else 0.0

    # Average patrol time (in minutes)
    cursor.execute("""
        SELECT EXTRACT(EPOCH FROM (finish_time::timestamp - start_time::timestamp))/60
        FROM patrolling
        WHERE responder_id = %s AND start_time IS NOT NULL AND finish_time IS NOT NULL
    """, (responder_id,))
    patrol_times = [r[0] for r in cursor.fetchall() if r[0] is not None]
    avg_patrol_time = round(sum(patrol_times)/len(patrol_times), 1) if patrol_times else 0.0

    # Resolved cases: finished alerts + approved reports
    resolved_cases = actions_finished + reports_approved

    # Gallery photos
    cursor.execute("""
        SELECT filename
        FROM responder_gallery
        WHERE responder_id = %s
        ORDER BY uploaded_at DESC
    """, (responder_id,))
    gallery_photos = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return {
        "full_name": full_name,
        "assigned_at": assigned_at,
        "photo": photo,
        "gallery": gallery_photos,
        "actionsTaked": actions_taked,
        "actionsFinished": actions_finished,
        "reportsSubmitted": reports_submitted,
        "reportsApproved": reports_approved,
        "avgResponseTime": avg_response_time,
        "avgPatrolTime": avg_patrol_time,
        "resolvedCases": resolved_cases
    }