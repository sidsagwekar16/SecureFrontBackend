# routes/agencies.py
from fastapi import APIRouter, HTTPException
from db import add_document, get_document_by_id
from models import Agency, AgencyCreate
from typing import List
import logging
from config import db

router = APIRouter(prefix="/v1/agencies", tags=["Agencies"])
logger = logging.getLogger(__name__)

@router.get("", response_model=List[Agency])
def read_agencies():
    docs = db.collection("agencies").stream()
    agencies = []
    for doc in docs:
        agency_data = doc.to_dict()
        if "id" in agency_data and "agencyId" not in agency_data:
            agency_data["agencyId"] = agency_data.pop("id")
        agencies.append(agency_data)
    logger.info(f"Retrieved {len(agencies)} agencies")
    return agencies

@router.get("/{agency_id}", response_model=Agency)
def read_agency(agency_id: str):
    agency_data = get_document_by_id("agencies", agency_id)
    if "id" in agency_data and "agencyId" not in agency_data:
        agency_data["agencyId"] = agency_data.pop("id")
    return agency_data

@router.post("", response_model=Agency)
def create_agency(agency: AgencyCreate):
    data = agency.dict()
    return add_document("agencies", data)
