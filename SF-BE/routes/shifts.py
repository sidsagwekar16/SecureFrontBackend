# routes/shifts.py
from fastapi import APIRouter, HTTPException, Query
from db import add_document, get_document_by_id, update_document, delete_document, get_documents_by_field
from models import Shift
from typing import List
import logging

router = APIRouter(prefix="/v1/shifts", tags=["Shifts"])
logger = logging.getLogger(__name__)

@router.get("", response_model=List[Shift])
def read_shifts(agency_id: str = Query(...)):
    return get_documents_by_field("shifts", "agencyId", agency_id)

@router.post("", response_model=Shift)
def create_shift(shift: Shift):
    return add_document("shifts", shift.dict(exclude_unset=True))

@router.delete("/{shift_id}")
def delete_shift(shift_id: str, agency_id: str = Query(...)):
    shift = get_document_by_id("shifts", shift_id)
    if shift.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    delete_document("shifts", shift_id)
    return {"message": f"Shift {shift_id} deleted"}
