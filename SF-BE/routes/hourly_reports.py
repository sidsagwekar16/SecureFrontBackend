# routes/hourly_reports.py
from fastapi import APIRouter, HTTPException, Query
from db import add_document, get_documents_by_field, delete_document, get_document_by_id
from models import HourlyReport
from typing import List

router = APIRouter(prefix="/web/hourly-reports", tags=["Hourly Reports"])

@router.get("", response_model=List[HourlyReport])
def get_hourly_reports(agency_id: str = Query(...)):
    return get_documents_by_field("hourlyReports", "agencyId", agency_id)

@router.post("", response_model=HourlyReport)
def create_hourly_report(report: HourlyReport):
    return add_document("hourlyReports", report.dict(exclude_unset=True))

@router.delete("/{report_id}")
def delete_hourly_report(report_id: str, agency_id: str = Query(...)):
    report = get_document_by_id("hourlyReports", report_id)
    if report.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    delete_document("hourlyReports", report_id)
    return {"message": f"Hourly Report {report_id} deleted"}
