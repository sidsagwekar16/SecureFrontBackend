# routes/billing.py
from fastapi import APIRouter, Query
from db import add_document, get_documents_by_field
from models import Billing
from typing import List

router = APIRouter(prefix="/v1/billing", tags=["Billing"])

@router.get("", response_model=List[Billing])
def read_billing(agency_id: str = Query(...)):
    return get_documents_by_field("billing", "agencyId", agency_id)

@router.post("", response_model=Billing)
def create_billing(billing: Billing):
    return add_document("billing", billing.dict(exclude_unset=True))
