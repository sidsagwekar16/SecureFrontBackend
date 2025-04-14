# routes/join_code.py
from fastapi import APIRouter, HTTPException, Query
from db import add_document
from models import JoinCode, EmployeeJoinCodeRegisterPayload
from datetime import datetime
import random
import string
from config import db
import logging

router = APIRouter(prefix="/v1/join-code", tags=["Join Code"])
logger = logging.getLogger(__name__)

def generate_unique_join_code(length: int = 6) -> str:
    for _ in range(10):
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        code = f"JOIN-{suffix}"
        existing = list(db.collection("joiningCodes").where("code", "==", code).limit(1).stream())
        if not existing:
            return code
    raise HTTPException(status_code=500, detail="Unable to generate unique join code")

@router.post("/generate")
def generate_join_code(agency_id: str = Query(...)):
    code = generate_unique_join_code()
    data = {
        "code": code,
        "agencyId": agency_id,
        "used": False,
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "usedAt": None,
        "usedBy": None
    }
    saved = add_document("joiningCodes", data)
    return {"message": "Join code generated", "joinCode": saved.get("code")}

@router.post("/employee/register")
def register_with_join_code(payload: dict):
    from firebase_admin import auth
    try:
        decoded = auth.verify_id_token(payload.get("idToken"))
        uid = decoded.get("uid")
        existing = list(db.collection("employees").where("uid", "==", uid).stream())
        if existing:
            raise HTTPException(status_code=400, detail="Employee already registered")
        join_query = list(db.collection("joiningCodes")
                          .where("code", "==", payload.get("joinCode"))
                          .where("used", "==", False)
                          .limit(1).stream())
        if not join_query:
            raise HTTPException(status_code=400, detail="Invalid or already used join code")
        join_doc = join_query[0]
        join_data = join_doc.to_dict()
        agency_id = join_data.get("agencyId")
        def generate_employee_code(length=6):
            return "EMP-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        employee_code = generate_employee_code()
        employee_data = payload.get("employee")
        if not employee_data:
            raise HTTPException(status_code=400, detail="Employee data is required")
        employee_data["uid"] = uid
        employee_data["agencyId"] = agency_id
        employee_data["status"] = "active"
        employee_data["createdAt"] = datetime.utcnow().isoformat() + "Z"
        employee_data["updatedAt"] = datetime.utcnow().isoformat() + "Z"
        employee_data["employeeCode"] = employee_code
        from db import add_document
        new_employee = add_document("employees", employee_data)
        db.collection("joiningCodes").document(join_doc.id).update({
            "used": True,
            "usedBy": uid,
            "usedAt": datetime.utcnow().isoformat() + "Z"
        })
        return {
            "message": "Employee registered successfully",
            "uid": uid,
            "employeeId": employee_code,
            "agencyId": agency_id,
            "siteId": new_employee.get("site"),
            "name": new_employee.get("name"),
            "status": new_employee.get("status")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")
