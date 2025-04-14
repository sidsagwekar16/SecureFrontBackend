# routes/employee.py
from fastapi import APIRouter, HTTPException, Query
from db import add_document, get_document_by_id, update_document, delete_document, get_documents_by_field
from models import EmployeeModel
from typing import List
import uuid
import logging

router = APIRouter(prefix="/v1/employees", tags=["Employees"])
logger = logging.getLogger(__name__)

@router.get("/{employee_id}")
def get_employee_by_id(employee_id: str):
    return get_document_by_id("employees", employee_id)

@router.patch("/{employee_id}")
def update_employee_by_id(employee_id: str, employee: EmployeeModel):
    return update_document("employees", employee_id, employee.dict(exclude_unset=True))

@router.delete("/{employee_id}")
def delete_employee_by_id(employee_id: str):
    delete_document("employees", employee_id)
    return {"message": "Deleted"}

@router.get("/all")
def get_all_employees(agency_id: str = Query(...)):
    return get_documents_by_field("employees", "agencyId", agency_id)

@router.post("/add")
def add_employee(employee: EmployeeModel):
    data = employee.dict(exclude_unset=True)
    if not data.get("employeeCode"):
        data["employeeCode"] = f"EMP-{str(uuid.uuid4())[:6].upper()}"
    return add_document("employees", data)
