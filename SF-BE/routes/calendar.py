# routes/calendar.py
from fastapi import APIRouter, HTTPException, Query, Body
from db import add_document, get_documents_by_field, get_document_by_id, update_document
from models import Shift
from datetime import datetime
import logging

router = APIRouter(prefix="/v1/calendar", tags=["Calendar"])
logger = logging.getLogger(__name__)

@router.get("/shifts")
def get_calendar_shifts(agency_id: str = Query(...), start_date: str = Query(...), end_date: str = Query(...)):
    shifts = get_documents_by_field("shifts", "agencyId", agency_id)
    start = datetime.fromisoformat(start_date.rstrip("Z"))
    end = datetime.fromisoformat(end_date.rstrip("Z"))
    filtered_shifts = []
    for shift in shifts:
        shift_start = datetime.fromisoformat(shift["shiftStart"].rstrip("Z"))
        shift_end = datetime.fromisoformat(shift["shiftEnd"].rstrip("Z"))
        if (shift_start >= start and shift_start <= end) or (shift_end >= start and shift_end <= end):
            filtered_shifts.append(shift)
    calendar_events = []
    for shift in filtered_shifts:
        calendar_events.append({
            "id": shift["id"],
            "title": f"{shift['employeeId']} - {shift['siteId']}",
            "start": shift["shiftStart"],
            "end": shift["shiftEnd"],
            "extendedProps": {
                "employeeId": shift["employeeId"],
                "siteId": shift["siteId"]
            }
        })
    return calendar_events

@router.post("/shifts")
def create_calendar_shift(
    employee_id: str = Body(...),
    site_id: str = Body(...),
    start: str = Body(...),
    end: str = Body(...),
    agency_id: str = Body(...)
):
    shift = Shift(
        agencyId=agency_id,
        employeeId=employee_id,
        siteId=site_id,
        shiftStart=start,
        shiftEnd=end
    )
    result = add_document("shifts", shift.dict(exclude_unset=True))
    return {
        "id": result.get("id"),
        "title": f"{employee_id} - {site_id}",
        "start": result.get("shiftStart"),
        "end": result.get("shiftEnd"),
        "extendedProps": {
            "employeeId": employee_id,
            "siteId": site_id
        }
    }

@router.put("/shifts/{shift_id}")
def update_calendar_shift(
    shift_id: str,
    start: str = Body(...),
    end: str = Body(...),
    agency_id: str = Query(...)
):
    shift = get_document_by_id("shifts", shift_id)
    if shift.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    update_data = {"shiftStart": start, "shiftEnd": end}
    result = update_document("shifts", shift_id, update_data)
    return {
        "id": shift_id,
        "title": f"{result.get('employeeId')} - {result.get('siteId')}",
        "start": result.get("shiftStart"),
        "end": result.get("shiftEnd"),
        "extendedProps": {
            "employeeId": result.get("employeeId"),
            "siteId": result.get("siteId")
        }
    }
