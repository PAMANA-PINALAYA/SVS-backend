from fastapi import APIRouter, HTTPException
import psycopg2
import os
from app.routers.SAAdmin_backend.admin_log_helper import log_action

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

@router.get("/admin/tips_resources")
def get_tips_resources():
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, title, description, resource_type, link FROM tips_resources ORDER BY id DESC")
        resources = cursor.fetchall()
        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "resource_type": row[3],
                "link": row[4]
            }
            for row in resources
        ]
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/tips_resources/add")
def post_tips_resource(title: str, description: str, resource_type: str, link: str, created_by: int, admin_name: str = None):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO tips_resources (title, description, resource_type, link, created_by) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (title, description, resource_type, link if link else None, created_by)
        )
        resource_id = cursor.fetchone()[0]
        conn.commit()
        log_action(created_by, "add_tips_resource", f"Added tips/resource '{title}'", resource_id, admin_name)
        return {"success": True, "resource_id": resource_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/tips_resources/edit")
def edit_tips_resource(resource_id: int, title: str, description: str, resource_type: str, link: str, admin_id: int = None, admin_name: str = None):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE tips_resources SET title=%s, description=%s, resource_type=%s, link=%s, updated_at=NOW() WHERE id=%s",
            (title, description, resource_type, link if link else None, resource_id)
        )
        conn.commit()
        if admin_id:
            log_action(admin_id, "edit_tips_resource", f"Edited tips/resource '{title}'", resource_id, admin_name)
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/admin/tips_resources/delete")
def delete_tips_resource(resource_id: int, admin_id: int = None, admin_name: str = None):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT title FROM tips_resources WHERE id=%s", (resource_id,))
        row = cursor.fetchone()
        title = row[0] if row else "Unknown"
        cursor.execute("DELETE FROM tips_resources WHERE id=%s", (resource_id,))
        conn.commit()
        if admin_id:
            log_action(admin_id, "delete_tips_resource", f"Deleted tips/resource '{title}'", resource_id, admin_name)
        return {"success": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()