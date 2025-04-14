# routes/leave_requests.py
from fastapi import APIRouter, Query
from db import add_document, get_documents_by_field
from models import LeaveRequest
from typing import List

router = APIRouter(prefix="/v1/leave-requests", tags=["Leave Requests"])

@router.get("", response_model=List[LeaveRequest])
def read_leave_requests(agency_id: str = Query(...)):
    return get_documents_by_field("leaveRequests", "agencyId", agency_id)

@router.post("", response_model=LeaveRequest)
def create_leave_request(leave_req: LeaveRequest):
    return add_document("leaveRequests", leave_req.dict(exclude_unset=True))
