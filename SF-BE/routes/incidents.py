# routes/incidents.py
from fastapi import APIRouter, Query
from db import add_document, get_documents_by_field
from models import Incident
from typing import List

router = APIRouter(prefix="/v1/incidents", tags=["Incidents"])

@router.get("", response_model=List[Incident])
def read_incidents(agency_id: str = Query(...)):
    return get_documents_by_field("incidents", "agencyId", agency_id)

@router.post("", response_model=Incident)
def create_incident(incident: Incident):
    return add_document("incidents", incident.dict(exclude_unset=True))
