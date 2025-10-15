from pydantic import BaseModel
from app.routers.responder_backend.config import get_db_conn
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import os
from app.routers.responder_backend.utils import insert_log

router = APIRouter()

class UpdateResponderProfile(BaseModel):
    responder_id: int
    full_name: str
    phone: str
    email: str
    address: str

@router.post("/update_responder_profile")
def update_responder_profile(data: UpdateResponderProfile):
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE responders SET full_name=%s, phone=%s, email=%s, address=%s WHERE id=%s",
            (data.full_name, data.phone, data.email, data.address, data.responder_id)
        )
        conn.commit()
        # Log profile update
        insert_log(
            data.responder_id,
            "Profile Update",
            f"Updated profile: name='{data.full_name}', phone='{data.phone}', email='{data.email}', address='{data.address}'"
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploaded_profile_picture")

@router.post("/upload_profile_picture")
async def upload_profile_picture(responder_id: int = Form(...), file: UploadFile = File(...)):
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        ext = os.path.splitext(file.filename)[1]
        filename = f"responder_{responder_id}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        # Save the filename to the database
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE responders SET photo = %s WHERE id = %s",
            (filename, responder_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))