from fastapi import APIRouter
import psycopg2
import os
import psutil
import time
from datetime import datetime, timedelta

router = APIRouter()

def get_db_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ.get("DB_NAME", "SmartSurveillanceSystem"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASS", "123")
    )

@router.get("/admin/dashboard/users")
def get_total_users():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM admin_users")
        admins = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM responders")
        responders = cursor.fetchone()[0]
        return {"admins": admins, "responders": responders}
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/dashboard/active_devices")
def get_active_devices():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM cctv_cameras WHERE status='online'")
        cctv = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM microphones WHERE status='online'")
        mics = cursor.fetchone()[0]
        return {"cctv": cctv, "microphones": mics}
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/dashboard/alerts_trends")
def get_alerts_trends():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        today = datetime.now().date()
        week_ago = today - timedelta(days=6)
        month_ago = today - timedelta(days=29)
        cursor.execute("""
            SELECT DATE("timestamp"), COUNT(*) FROM camera_alerts
            WHERE "timestamp" >= %s
            GROUP BY DATE("timestamp")
            ORDER BY DATE("timestamp")
        """, (week_ago,))
        daily = cursor.fetchall()
        cursor.execute("""
            SELECT DATE_TRUNC('week', "timestamp")::date, COUNT(*) FROM camera_alerts
            WHERE "timestamp" >= %s
            GROUP BY DATE_TRUNC('week', "timestamp")
            ORDER BY DATE_TRUNC('week', "timestamp")
        """, (month_ago,))
        weekly = cursor.fetchall()
        cursor.execute("""
            SELECT DATE_TRUNC('month', "timestamp")::date, COUNT(*) FROM camera_alerts
            WHERE "timestamp" >= %s
            GROUP BY DATE_TRUNC('month', "timestamp")
            ORDER BY DATE_TRUNC('month', "timestamp")
        """, (today.replace(day=1) - timedelta(days=365),))
        monthly = cursor.fetchall()
        return {"daily": daily, "weekly": weekly, "monthly": monthly}
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/dashboard/reports_summary")
def get_reports_summary():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM responders_report")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM responders_report WHERE status='Approved'")
        approved = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM responders_report WHERE status='Pending'")
        pending = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM responders_report WHERE status='Rejected'")
        rejected = cursor.fetchone()[0]
        return {"total": total, "approved": approved, "pending": pending, "rejected": rejected}
    finally:
        cursor.close()
        conn.close()

@router.get("/admin/dashboard/system_health")
def get_system_health():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    uptime = time.time() - psutil.boot_time()
    net = psutil.net_io_counters()
    return {
        "cpu": cpu,
        "memory": mem.percent,
        "uptime": uptime,
        "network_sent": net.bytes_sent,
        "network_recv": net.bytes_recv
    }

@router.get("/admin/dashboard/security_notices")
def get_security_notices():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM system_logs WHERE event_type='failed_login' AND event_time >= NOW() - INTERVAL '1 day'
        """)
        failed_logins = cursor.fetchone()[0]
        cursor.execute("""
            SELECT COUNT(*) FROM system_logs WHERE event_type='suspicious_activity' AND event_time >= NOW() - INTERVAL '1 day'
        """)
        suspicious = cursor.fetchone()[0]
        return {"failed_logins": failed_logins, "suspicious": suspicious}
    finally:
        cursor.close()
        conn.close()