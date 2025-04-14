# routes/geofences.py
from fastapi import APIRouter, HTTPException, Query
from db import add_document, get_document_by_id, update_document, delete_document, get_documents_by_field
from models import GeoFence
from utils import validate_geofence_coordinates
import logging

router = APIRouter(prefix="/v1/geofences", tags=["GeoFences"])
logger = logging.getLogger(__name__)

@router.get("", response_model=list)
def read_geofences(agency_id: str = Query(...)):
    geofences = get_documents_by_field("geofences", "agencyId", agency_id)
    return geofences

@router.get("/{geofence_id}", response_model=GeoFence)
def read_geofence(geofence_id: str, agency_id: str = Query(...)):
    geofence = get_document_by_id("geofences", geofence_id)
    if geofence.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return geofence

@router.post("", response_model=GeoFence)
def create_geofence(geofence: GeoFence):
    data = geofence.dict(exclude_unset=True)
    validate_geofence_coordinates(data["coordinates"])
    result = add_document("geofences", data)
    return result

@router.put("/{geofence_id}", response_model=GeoFence)
def update_geofence(geofence_id: str, geofence: GeoFence, agency_id: str = Query(...)):
    existing_geofence = get_document_by_id("geofences", geofence_id)
    if existing_geofence.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    data = geofence.dict(exclude_unset=True)
    validate_geofence_coordinates(data["coordinates"])
    data["geoFenceId"] = geofence_id
    result = update_document("geofences", geofence_id, data)
    return result

@router.patch("/{geofence_id}", response_model=GeoFence)
def partial_update_geofence(geofence_id: str, geofence: GeoFence, agency_id: str = Query(...)):
    existing_geofence = get_document_by_id("geofences", geofence_id)
    if existing_geofence.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    data = geofence.dict(exclude_unset=True, exclude_none=True)
    if "coordinates" in data:
        validate_geofence_coordinates(data["coordinates"])
    result = update_document("geofences", geofence_id, data)
    return result

@router.delete("/{geofence_id}")
def delete_geofence(geofence_id: str, agency_id: str = Query(...)):
    geofence = get_document_by_id("geofences", geofence_id)
    if geofence.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    delete_document("geofences", geofence_id)
    return {"message": f"GeoFence {geofence_id} deleted"}
