# routes/sites.py
from fastapi import APIRouter, HTTPException, Query
from db import add_document, get_document_by_id, update_document, delete_document, get_documents_by_field
from models import Site
from typing import List
import logging

router = APIRouter(prefix="/v1/sites", tags=["Sites"])
logger = logging.getLogger(__name__)

@router.get("", response_model=List[Site])
def read_sites(agency_id: str = Query(...)):
    sites = get_documents_by_field("sites", "agencyId", agency_id)
    for site in sites:
        if "siteId" not in site:
            site["siteId"] = site["id"]
    logger.info(f"Retrieved {len(sites)} sites for agency {agency_id}")
    return sites

@router.get("/{site_id}", response_model=Site)
def read_site(site_id: str, agency_id: str = Query(...)):
    site = get_document_by_id("sites", site_id)
    if site.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return site

@router.post("", response_model=Site)
def create_site(site: Site):
    data = site.dict(exclude_unset=True)
    result = add_document("sites", data)
    logger.info(f"Created site {result.get('id')} for agency {data.get('agencyId')}")
    return result

@router.put("/{site_id}", response_model=Site)
def update_site(site_id: str, site: Site, agency_id: str = Query(...)):
    existing_site = get_document_by_id("sites", site_id)
    if existing_site.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    data = site.dict(exclude_unset=True)
    data["siteId"] = site_id
    result = update_document("sites", site_id, data)
    return result

@router.patch("/{site_id}", response_model=Site)
def partial_update_site(site_id: str, site: Site, agency_id: str = Query(...)):
    existing_site = get_document_by_id("sites", site_id)
    if existing_site.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    data = site.dict(exclude_unset=True, exclude_none=True)
    result = update_document("sites", site_id, data)
    return result

@router.delete("/{site_id}")
def delete_site(site_id: str, agency_id: str = Query(...)):
    site = get_document_by_id("sites", site_id)
    if site.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    delete_document("sites", site_id)
    return {"message": f"Site {site_id} deleted"}
