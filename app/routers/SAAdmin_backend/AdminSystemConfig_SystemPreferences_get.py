from fastapi import APIRouter, HTTPException
import csv
import os
import json

router = APIRouter()

PREFS_FILE = "system_preferences.json"
CONTACTS_FILE = "emergency_contacts.json"

@router.post("/admin/system/export_csv")
def export_data_csv(data_type: str, path: str):
    data_map = {
        "logs": [["ID", "Action", "Timestamp"], [1, "Login", "2025-09-27"]],
        "reports": [["ID", "Title", "Status"], [1, "Incident", "Open"]],
        "users": [["ID", "Name", "Role"], [1, "Juan Dela Cruz", "Responder"]],
    }
    data = data_map.get(data_type, [])
    try:
        with open(path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Export error: {e}")

@router.get("/admin/system/preferences")
def get_preferences():
    if os.path.exists(PREFS_FILE):
        with open(PREFS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@router.post("/admin/system/preferences")
def save_preferences(prefs: dict):
    with open(PREFS_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=2)
    return {"success": True}

@router.get("/admin/system/emergency_contacts")
def get_emergency_contacts():
    if os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@router.post("/admin/system/emergency_contacts")
def save_emergency_contacts(contacts: dict):
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2)
    return {"success": True}