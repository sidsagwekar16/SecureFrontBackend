# routes/attendance.py
from fastapi import APIRouter, HTTPException, Query
from db import add_document, get_document_by_id, update_document, get_documents_by_field
from models import Attendance
from datetime import datetime
import logging

router = APIRouter(prefix="/v1/attendance", tags=["Attendance"])
logger = logging.getLogger(__name__)

@router.get("", response_model=list)
def read_attendance(agency_id: str = Query(...)):
    return get_documents_by_field("attendance", "agencyId", agency_id)

@router.post("/clockin", response_model=Attendance)
def clock_in(attendance: Attendance):
    data = attendance.dict(exclude_unset=True)
    if "lat" not in data or "lng" not in data:
        raise HTTPException(status_code=400, detail="Latitude and longitude are required for clock-in")
    # Geofence validation can be added here
    return add_document("attendance", data)

@router.post("/clockout", response_model=Attendance)
def clock_out(attendance_id: str = Query(...), agency_id: str = Query(...)):
    attendance = get_document_by_id("attendance", attendance_id)
    if attendance.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return update_document("attendance", attendance_id, {"clockOut": datetime.utcnow().isoformat() + "Z"})

@router.post("/break", response_model=Attendance)
def add_break(attendance_id: str, break_start: str, break_end: str = None, agency_id: str = Query(...)):
    doc = get_document_by_id("attendance", attendance_id)
    if doc.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    break_periods = doc.get("breakPeriods", [])
    break_periods.append({"breakStart": break_start, "breakEnd": break_end})
    return update_document("attendance", attendance_id, {"breakPeriods": break_periods})
