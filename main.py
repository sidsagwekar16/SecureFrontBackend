##############################################
# main.py - Single File SecureFront Application
# Version: 1.3.16  # Updated version for sites CRUD and broadcast
# Last Updated: 2025-03-16
##############################################

import logging
from dotenv import load_dotenv
load_dotenv()
import firebase_admin.messaging as messaging
from typing import Annotated
from datetime import datetime
from fastapi.responses import StreamingResponse
from fastapi import Header, Depends
from typing import List, Dict, Optional
import io
from dateutil.parser import isoparse
import csv
from firebase_admin import auth
from fastapi import FastAPI, HTTPException, Query, Body, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from firebase_admin import credentials, initialize_app, firestore
from shapely.geometry import Point, Polygon
from pydantic import BaseModel, constr
from datetime import timezone
from typing import Optional
import uuid
from firebase_admin import firestore
import random
from typing import List
import string
from routes.billing import router as billing_router




# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#####################################################
# 1. Firebase & Firestore Setup
#####################################################

import os
import base64
if "FIREBASE_CREDENTIALS_BASE64" in os.environ:
    decoded = base64.b64decode(os.environ["FIREBASE_CREDENTIALS_BASE64"])
    with open("firebase_key.json", "wb") as f:
        f.write(decoded)
    cred = credentials.Certificate("firebase_key.json")
else:
    cred = credentials.Certificate("serviceAccountKey.json")  # fallback

initialize_app(cred)
db = firestore.client()

#####################################################
# 2. Firestore Helper Functions
#####################################################

def get_stripe_customer_id(user_id: str) -> str:
    db = firestore.client()
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise Exception("User not found")

    data = doc.to_dict()
    if "stripeCustomerId" not in data:
        raise Exception("stripeCustomerId not set for user")

    return data["stripeCustomerId"]

def add_document(collection: str, data: dict) -> dict:
    doc_ref = db.collection(collection).document()
    id_field = "agencyId" if collection == "agencies" else "id"
    data[id_field] = doc_ref.id
    now = datetime.utcnow().isoformat() + "Z"
    data["createdAt"] = now
    data["updatedAt"] = now
    logger.info(f"Adding document to {collection} with {id_field}: {doc_ref.id}")
    doc_ref.set(data)
    return data

def get_documents_by_field(collection: str, field: str, value: str) -> List[dict]:
    logger.info(f"Querying {collection} where {field} = {value}")
    docs = (
        db.collection(collection).stream()
        if field == "all"
        else db.collection(collection).where(field, "==", value).stream()
    )

    result = []
    for doc in docs:
        data = doc.to_dict()

        # 🔁 Inject Firestore document ID safely
        if "id" not in data:
            data["id"] = doc.id

        result.append(data)

    logger.info(f"Found {len(result)} documents in {collection}")
    return result

def get_document_by_id(collection: str, doc_id: str) -> dict:
    if not doc_id:
        raise HTTPException(status_code=400, detail="Document ID is required")
    logger.info(f"Fetching document from {collection} with ID: {doc_id}")
    doc_ref = db.collection(collection).document(doc_id)
    doc = doc_ref.get()
    if not doc.exists:
        logger.error(f"Document with ID {doc_id} not found in {collection}")
        raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found in {collection}")
    logger.info(f"Found document: {doc.to_dict()}")
    return doc.to_dict()

def update_document(collection: str, doc_id: str, data: dict) -> dict:
    if not doc_id:
        raise HTTPException(status_code=400, detail="Document ID is required")
    doc_ref = db.collection(collection).document(doc_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found in {collection}")
    now = datetime.utcnow().isoformat() + "Z"
    data["updatedAt"] = now
    doc_ref.update(data)
    return doc_ref.get().to_dict()

def generate_unique_employee_join_code() -> str:
    for _ in range(10):
        code = "JOIN-EMP-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        existing = db.collection("employees").where("joinCode", "==", code).limit(1).stream()
        if not any(existing):
            return code
    raise HTTPException(status_code=500, detail="Failed to generate unique join code")



def delete_document(collection: str, doc_id: str):
    if not doc_id:
        raise HTTPException(status_code=400, detail="Document ID is required")
    doc_ref = db.collection(collection).document(doc_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found in {collection}")
    doc_ref.delete()

def is_inside_geofence(user_lat: float, user_lng: float, polygon_coords: List[Dict[str, float]]) -> bool:
    polygon_points = [(p["lng"], p["lat"]) for p in polygon_coords]
    polygon = Polygon(polygon_points)
    point = Point(user_lng, user_lat)
    return polygon.contains(point)

def validate_geofence_coordinates(coordinates: List[Dict[str, float]]) -> None:
    if len(coordinates) < 3:
        raise HTTPException(status_code=400, detail="Geofence must have at least 3 coordinates to form a polygon")
    for coord in coordinates:
        if "lat" not in coord or "lng" not in coord:
            raise HTTPException(status_code=400, detail="Each coordinate must have 'lat' and 'lng' fields")
        if not isinstance(coord["lat"], (int, float)) or not isinstance(coord["lng"], (int, float)):
            raise HTTPException(status_code=400, detail="Coordinates 'lat' and 'lng' must be numbers")
    try:
        polygon_points = [(p["lat"], p["lng"]) for p in coordinates]
        Polygon(polygon_points)
    except Exception as e:
        logger.error(f"Invalid geofence coordinates: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid geofence coordinates: unable to form a valid polygon")
    
    

    #send push helper   

def send_push(uid: str, title: str, body: str, data: dict = {}):
    doc = db.collection("devices").document(uid).get()
    if not doc.exists:
        logger.warning(f"No device tokens found for {uid}")
        return

    tokens = doc.to_dict().get("tokens", [])
    if not tokens:
        return

    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data=data,
        tokens=tokens
    )

    response = messaging.send_multicast(message)
    logger.info(f"Sent notification to {len(tokens)} devices: {response.success_count} success")


def safe_parse_datetime(dt_str: str) -> datetime:
    try:
        return isoparse(dt_str)
    except Exception:
        return None



#####################################################
# 3. Pydantic Models
#####################################################

class UserAgencyMapping(BaseModel):
    userId: str
    agencyId: str

class LoginRequest(BaseModel):
    idToken: str


class AgencyCreate(BaseModel):
    name: str
    contactEmail: str
    contactPhone: str
    address: str
    subscriptionPlan: str

class CompleteSignupPayload(BaseModel):
    idToken: str
    agency: AgencyCreate


class Agency(AgencyCreate):
    agencyId: str
    createdAt: str
    updatedAt: str

class Site(BaseModel):
    id: Optional[str] = None  # ✅ Add this line
    siteId: Optional[str] = None
    agencyId: str
    name: str
    description: str
    address: str
    assignedHours: int
    coordinates: Optional[List[Dict[str, float]]] = []
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class Shift(BaseModel):
    shiftId: Optional[str] = None
    agencyId: str
    employeeId: str
    siteId: str
    shiftStart: str
    shiftEnd: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class LeaveRequest(BaseModel):
    leaveRequestId: Optional[str] = None
    agencyId: str
    userId: str
    startDate: str
    endDate: str
    reason: str
    status: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class Incident(BaseModel):
    incidentId: Optional[str] = None
    agencyId: str
    siteId: str
    userId: str
    timestamp: str
    description: str
    images: Optional[List[str]] = []
    location: Dict[str, float]
    severity: str
    status: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None



class Billing(BaseModel):
    billingId: Optional[str] = None
    agencyId: str
    stripeCustomerId: str
    subscriptionId: str
    currentPlan: str
    nextBillingDate: str
    paymentHistory: Optional[List[dict]] = []
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class BreakPeriod(BaseModel):
    breakStart: str
    breakEnd: Optional[str] = None

class Attendance(BaseModel):
    attendanceId: Optional[str] = None
    agencyId: str
    userId: str
    siteId: str
    clockIn: Optional[str] = None
    clockOut: Optional[str] = None
    scheduledStart: Optional[str] = None
    shiftId: Optional[str] = None
    hoursWorked: Optional[float] = 0
    overtimeHours: Optional[float] = 0
    breakPeriods: Optional[List[BreakPeriod]] = []
    lat: Optional[float] = None
    lng: Optional[float] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class Message(BaseModel):
    messageId: Optional[str] = None
    agencyId: str
    senderId: str
    text: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class BroadcastMessage(BaseModel):
    siteId: str
    text: str

class HourlyReport(BaseModel):
    id: Optional[str] = None
    agencyId: str
    siteId: str
    userId: str  # 👈 Needed to fetch employee-specific reports
    reportText: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    

class SiteNotification(BaseModel):
    siteId: str
    senderId: str
    agencyId: str
    text: str
    audience: Optional[str] = "clocked-in"
    createdAt: Optional[str] = None





class EmployeeModel(BaseModel):
    name: str
    uid: Optional[str] = None  # ✅ Add this
    employeeCode: Optional[str] = None 
    joinCode: Optional[str] = None 
    role: Optional[str] = None 
    status: Optional[str] = None 
    site: Optional[str] = None 
    joinCodeStatus: Optional[str] = "unused" 
    assignedsiteID: Optional[str] = None 
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    dateOfBirth: Optional[str] = None
    emergencyContact: Optional[str] = None
    emergencyPhone: Optional[str] = None
    agencyId: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class EmployeeJoinCodeRegisterPayload(BaseModel):
    idToken: str
    joinCode: str
   

#####################################################
# 4. FastAPI Application
#####################################################

app = FastAPI(
    title="SecureFront Single-File API",
    description="API without authentication for testing purposes",
    version="1.3.16"  # Updated version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#####################################################


app.include_router(billing_router)

#  login endpoints
#####################################################


@app.post("/dev/create-stripe-customer")
def create_stripe_customer(userId: str = Body(...), email: str = Body(...)):
    try:
        import stripe
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        # 1. Create Stripe customer
        customer = stripe.Customer.create(email=email)

        # 2. Save stripeCustomerId in Firestore
        db.collection("users").document(userId).set({
            "stripeCustomerId": customer.id
        }, merge=True)

        return {
            "success": True,
            "message": "Stripe customer created and linked",
            "stripeCustomerId": customer.id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stripe customer creation failed: {str(e)}")


@app.post("/auth/login")
def login_user(payload: LoginRequest):
    try:
        decoded_token = auth.verify_id_token(payload.idToken)
        uid = decoded_token['uid']

        # Try to fetch agencyId from custom claims or fallback to Firestore user doc
        agency_id = decoded_token.get("agencyId")
        if not agency_id:
            user_doc = db.collection("users").document(uid).get()
            if user_doc.exists:
                agency_id = user_doc.to_dict().get("agencyId")

        if not agency_id:
            raise HTTPException(status_code=400, detail="Agency ID not associated with user")

        return {
            "message": "Login successful",
            "uid": uid,
            "agencyId": agency_id
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
    

@app.post("/auth/logout")
def logout_user():
    return {
        "message": "Logout handled client-side by clearing session/token."
    }

    
@app.post("/auth/complete-signup")
def complete_signup(payload: CompleteSignupPayload):
    try:
        if payload.idToken.count('.') != 2:
            raise HTTPException(400, "Invalid Firebase ID token format")

        decoded_token = auth.verify_id_token(payload.idToken)
        uid = decoded_token["uid"]

        # Check if this user already has an agency
        user_doc = db.collection("users").document(uid).get()
        if user_doc.exists:
            raise HTTPException(status_code=400, detail="User already linked to an agency")

        # ✅ Create agency
        agency_data = payload.agency.dict()
        agency_data["ownerId"] = uid
        new_agency = add_document("agencies", agency_data)

        # ✅ Link user to agency in Firestore
        db.collection("users").document(uid).set({
            "agencyId": new_agency["agencyId"]
        })

        return {"message": "Signup complete", "agencyId": new_agency["agencyId"]}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Signup failed: {str(e)}")

    
###################################################
# 🧠 OPTIONAL: Helper to auto-fetch agencyId from user
#####################################################
def get_agency_id(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    id_token = authorization.split(" ")[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        agency_id = decoded_token.get("agencyId")
        if not agency_id:
            user_doc = db.collection("users").document(uid).get()
            if not user_doc.exists:
                raise HTTPException(status_code=403, detail="User not linked to an agency")
            agency_id = user_doc.to_dict().get("agencyId")
        return agency_id
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Invalid token: {str(e)}")
#####################################################
# 5. Agency Endpoints
#####################################################

@app.get("/v1/agencies", response_model=List[Agency])
def read_agencies():
    docs = db.collection("agencies").stream()
    result = []
    for doc in docs:
        agency_data = doc.to_dict()
        if "id" in agency_data and "agencyId" not in agency_data:
            agency_data["agencyId"] = agency_data.pop("id")
        result.append(agency_data)
    logger.info(f"Retrieved {len(result)} agencies")
    return result

@app.get("/v1/agencies/{agency_id}", response_model=Agency)
def read_agency(agency_id: str):
    agency_data = get_document_by_id("agencies", agency_id)
    if "id" in agency_data and "agencyId" not in agency_data:
        agency_data["agencyId"] = agency_data.pop("id")
    return agency_data

@app.post("/v1/agencies", response_model=Agency)
def create_agency(agency: AgencyCreate):
    data = agency.dict()
    return add_document("agencies", data)

#####################################################
# 6. Site Endpoints (Enhanced CRUD)
#####################################################

@app.get("/v1/sites", response_model=List[Site])
def read_sites(agency_id: str = Query(...)):
    sites = get_documents_by_field("sites", "agencyId", agency_id)

    # 🔁 Convert Firestore document ID to siteId so the Pydantic model picks it up
    for site in sites:
        if "siteId" not in site:
            site["siteId"] = site["id"]  # ✅ Fix is here

    logger.info(f"Retrieved {len(sites)} sites for agency {agency_id}")
    return sites


@app.get("/v1/sites/{site_id}", response_model=Site)
def read_site(site_id: str, agency_id: str = Query(...)):
    site = get_document_by_id("sites", site_id)
    if site.get("agencyId") != agency_id:
        logger.warning(f"Unauthorized access attempt to site {site_id} by agency {agency_id}")
        raise HTTPException(status_code=403, detail="Unauthorized")
    logger.info(f"Retrieved site {site_id} for agency {agency_id}")
    return site

@app.post("/v1/sites", response_model=Site)
def create_site(site: Site):
    data = site.dict(exclude_unset=True)
    result = add_document("sites", data)
    logger.info(f"Created site {result['id']} for agency {data['agencyId']}")
    return result

@app.put("/v1/sites/{site_id}", response_model=Site)
def update_site(site_id: str, site: Site, agency_id: str = Query(...)):
    existing_site = get_document_by_id("sites", site_id)
    if existing_site.get("agencyId") != agency_id:
        logger.warning(f"Unauthorized update attempt to site {site_id} by agency {agency_id}")
        raise HTTPException(status_code=403, detail="Unauthorized")
    data = site.dict(exclude_unset=True)
    data["siteId"] = site_id
    result = update_document("sites", site_id, data)
    logger.info(f"Updated site {site_id} for agency {agency_id}")
    return result

@app.patch("/v1/sites/{site_id}", response_model=Site)
def partial_update_site(site_id: str, site: Site, agency_id: str = Query(...)):
    existing_site = get_document_by_id("sites", site_id)
    if existing_site.get("agencyId") != agency_id:
        logger.warning(f"Unauthorized patch attempt to site {site_id} by agency {agency_id}")
        raise HTTPException(status_code=403, detail="Unauthorized")
    data = site.dict(exclude_unset=True, exclude_none=True)
    result = update_document("sites", site_id, data)
    logger.info(f"Partially updated site {site_id} for agency {agency_id}")
    return result

@app.delete("/v1/sites/{site_id}")
def delete_site(site_id: str, agency_id: str = Query(...)):
    site = get_document_by_id("sites", site_id)
    if site.get("agencyId") != agency_id:
        logger.warning(f"Unauthorized delete attempt to site {site_id} by agency {agency_id}")
        raise HTTPException(status_code=403, detail="Unauthorized")
    delete_document("sites", site_id)
    logger.info(f"Deleted site {site_id} for agency {agency_id}")
    return {"message": f"Site {site_id} deleted"}

#####################################################
# 7. Shift Endpoints
#####################################################

@app.get("/v1/shifts", response_model=List[Shift])
def read_shifts(agency_id: str = Query(...)):
    return get_documents_by_field("shifts", "agencyId", agency_id)

@app.post("/v1/shifts", response_model=Shift)
def create_shift(shift: Shift):
    return add_document("shifts", shift.dict(exclude_unset=True))

@app.delete("/v1/shifts/{shift_id}")
def delete_shift(shift_id: str, agency_id: str = Query(...)):
    shift = get_document_by_id("shifts", shift_id)
    if shift.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    delete_document("shifts", shift_id)
    return {"message": f"Shift {shift_id} deleted"}

#####################################################
# 8. Leave Request Endpoints
#####################################################

@app.get("/v1/leave-requests", response_model=List[LeaveRequest])
def read_leave_requests(agency_id: str = Query(...)):
    return get_documents_by_field("leaveRequests", "agencyId", agency_id)

@app.post("/v1/leave-requests", response_model=LeaveRequest)
def create_leave_request(leave_req: LeaveRequest):
    return add_document("leaveRequests", leave_req.dict(exclude_unset=True))

#####################################################
# 9. Incident Endpoints
#####################################################

@app.get("/v1/incidents", response_model=List[Incident])
def read_incidents(agency_id: str = Query(...)):
    return get_documents_by_field("incidents", "agencyId", agency_id)

@app.post("/v1/incidents", response_model=Incident)
def create_incident(incident: Incident):
    return add_document("incidents", incident.dict(exclude_unset=True))

@app.post("/mobile/incidents")
def submit_incident(report: Incident):
    data = report.dict(exclude_unset=True)
    saved = add_document("incidents", data)
    saved["id"] = saved["id"]  # Ensure ID is returned
    return saved

@app.get("/mobile/reports")
def get_reports_for_employee(employee_id: str = Query(...), agency_id: str = Query(...)):
    # Hourly Reports
    hourly = db.collection("hourlyReports") \
        .where("userId", "==", employee_id) \
        .where("agencyId", "==", agency_id) \
        .order_by("createdAt", direction=firestore.Query.DESCENDING) \
        .stream()

    hourly_list = [
        {**doc.to_dict(), "type": "hourly", "id": doc.id}
        for doc in hourly
    ]

    # Incident Reports
    incidents = db.collection("incidents") \
        .where("userId", "==", employee_id) \
        .where("agencyId", "==", agency_id) \
        .order_by("createdAt", direction=firestore.Query.DESCENDING) \
        .stream()

    incident_list = [
        {**doc.to_dict(), "type": "incident", "id": doc.id}
        for doc in incidents
    ]

    return sorted(hourly_list + incident_list, key=lambda x: x.get("createdAt", ""), reverse=True)


#####################################################
# 10. GeoFence Endpoints
#####################################################


#####################################################
# 11. Billing Endpoints
#####################################################

@app.get("/v1/billing", response_model=List[Billing])
def read_billing(agency_id: str = Query(...)):
    return get_documents_by_field("billing", "agencyId", agency_id)

@app.post("/v1/billing", response_model=Billing)
def create_billing(billing: Billing):
    return add_document("billing", billing.dict(exclude_unset=True))

#####################################################
# 12. Attendance Endpoints
#####################################################

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
from typing import List
from firebase_admin import firestore




@app.post("/v1/attendance/mark-absentees")
def mark_absentees(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    agency_id: str = Query(...)
):
    try:
        target_date = datetime.fromisoformat(date).date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    now = datetime.now(timezone.utc)
    marked = []

    # Fetch shifts for the date and agency
    shifts = db.collection("shifts").where("agencyId", "==", agency_id).stream()

    for shift_doc in shifts:
        shift = shift_doc.to_dict()
        shift_id = shift_doc.id

        shift_start = datetime.fromisoformat(shift["shiftStart"].replace("Z", "+00:00"))
        shift_end = datetime.fromisoformat(shift["shiftEnd"].replace("Z", "+00:00"))

        if shift_start.date() != target_date:
            continue

        if now < shift_end:
            continue  # Shift not yet over

        # Check if any attendance exists
        existing_attendance = db.collection("attendance") \
            .where("shiftId", "==", shift_id) \
            .limit(1).stream()

        if any(existing_attendance):
            continue  # Already present or marked

        # Create absent record
        timestamp = now.isoformat().replace("+00:00", "Z")
        absent_record = {
            "agencyId": shift["agencyId"],
            "userId": shift["employeeId"],
            "siteId": shift["siteId"],
            "shiftId": shift_id,
            "status": "absent",
            "clockIn": None,
            "clockOut": None,
            "hoursWorked": 0,
            "overtimeHours": 0,
            "createdAt": timestamp,
            "updatedAt": timestamp
        }

        db.collection("attendance").add(absent_record)
        marked.append(absent_record)

    return {
        "success": True,
        "message": f"{len(marked)} absentees marked for {date}",
        "absentees": marked
    }


@app.post("/v1/attendance/start-break", response_model=Attendance)
def start_break(attendanceId: str):
    now_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    attendance = get_document_by_id("attendance", attendanceId)

    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")

    break_periods = attendance.get("breakPeriods", [])

    # Check for active break
    if any(bp.get("breakEnd") is None for bp in break_periods):
        raise HTTPException(status_code=400, detail="A break is already in progress")

    break_periods.append({"breakStart": now_str, "breakEnd": None})

    updated = update_document("attendance", attendanceId, {
        "breakPeriods": break_periods,
        "updatedAt": now_str
    })

    return updated


@app.post("/v1/attendance/end-break", response_model=Attendance)
def end_break(attendanceId: str):
    now_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    attendance = get_document_by_id("attendance", attendanceId)

    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")

    break_periods = attendance.get("breakPeriods", [])
    for bp in reversed(break_periods):
        if bp.get("breakEnd") is None:
            bp["breakEnd"] = now_str
            break
    else:
        raise HTTPException(status_code=400, detail="No active break to end")

    updated = update_document("attendance", attendanceId, {
        "breakPeriods": break_periods,
        "updatedAt": now_str
    })

    return updated

@app.get("/v1/attendance/site-summary")
def get_site_attendance_summary(
    agency_id: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    try:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()

        # 1. All active employees grouped by site
        employees = get_documents_by_field("employees", "agencyId", agency_id)
        site_employee_map = {}

        for emp in employees:
            if emp.get("status") == "active" and emp.get("assignedsiteID"):
                site_id = emp["assignedsiteID"]
                site_employee_map.setdefault(site_id, []).append(emp["id"])

        # 2. All attendance records (not filtered yet)
        attendance_records = get_documents_by_field("attendance", "agencyId", agency_id)

        # 3. Get site names
        sites = get_documents_by_field("sites", "agencyId", agency_id)
        site_id_name_map = {s["id"]: s.get("name", "Unnamed Site") for s in sites if "id" in s}

        # 4. Build summary
        site_summary = []
        for site_id, employee_ids in site_employee_map.items():
            filtered_attendance = [
                a for a in attendance_records
                if a.get("userId") in employee_ids
                and a.get("siteId") == site_id
                and a.get("clockIn")
                and start <= datetime.fromisoformat(a["clockIn"].replace("Z", "+00:00")).date() <= end
            ]

            present = len(filtered_attendance)
            late = sum(
                1 for a in filtered_attendance
                if "scheduledStart" in a and
                datetime.fromisoformat(a["clockIn"].replace("Z", "+00:00")) >
                datetime.fromisoformat(a["scheduledStart"].replace("Z", "+00:00"))
            )

            total = len(employee_ids)
            absent = max(total - present, 0)
            attendance_rate = f"{round((present / total) * 100)}%" if total else "0%"

            site_summary.append({
                "siteId": site_id,
                "siteName": site_id_name_map.get(site_id, site_id),
                "date": str(end),
                "totalEmployees": total,
                "present": present,
                "absent": absent,
                "late": late,
                "attendanceRate": attendance_rate,
            })

        return {"success": True, "data": site_summary}

    except Exception as e:
        logger.error(f"[Site Summary Error] {str(e)}")
        return {"success": False, "message": str(e)}



@app.get("/v1/attendance/summary")
def get_attendance_summary(agency_id: str = Query(...)):
    from datetime import datetime, timedelta

    today = datetime.utcnow().date()
    now = datetime.utcnow()

    # 1. Fetch today's shifts for this agency
    all_shifts = db.collection("shifts").where("agencyId", "==", agency_id).stream()
    today_shifts = []
    scheduled_employee_ids = set()

    for shift_doc in all_shifts:
        shift = shift_doc.to_dict()
        shift_start = safe_parse_datetime(shift.get("shiftStart"))
        if shift_start and shift_start.date() == today:
            today_shifts.append((shift_doc.id, shift))
            scheduled_employee_ids.add(shift["employeeId"])

    # 2. Fetch all employees of the agency
    all_employees = get_documents_by_field("employees", "agencyId", agency_id)
    valid_employees = [
    e for e in all_employees
    if e.get("status") == "active"
    and e.get("joinCodeStatus") == "used"
    and e.get("assignedsiteID")
    ]
    all_employee_ids = set(e["id"] for e in valid_employees)


    # 3. Fetch today’s attendance
    attendance = db.collection("attendance").where("agencyId", "==", agency_id).stream()
    present_ids = set()
    late_count = 0
    overtime_total = 0

    for att_doc in attendance:
        att = att_doc.to_dict()
        clock_in = safe_parse_datetime(att.get("clockIn"))
        if not clock_in or clock_in.date() != today:
            continue

        user_id = att["userId"]
        present_ids.add(user_id)
        overtime_total += att.get("overtimeHours", 0)

        # Check if late
        scheduled_start = safe_parse_datetime(att.get("scheduledStart"))
        if scheduled_start and clock_in > scheduled_start:
            late_count += 1

    # 4. Absentees
    scheduled_absentees = scheduled_employee_ids - present_ids
    unscheduled_absentees = all_employee_ids - scheduled_employee_ids - present_ids

    return {
        "present": len(present_ids),
        "totalScheduled": len(scheduled_employee_ids),
        "absent": {
            "total": len(scheduled_absentees) + len(unscheduled_absentees),
            "scheduled": len(scheduled_absentees),
            "unscheduled": len(unscheduled_absentees)
        },
        "late": {
            "count": late_count,
            "percentage": round((late_count / len(present_ids)) * 100, 1) if present_ids else 0.0
        },
        "overtime": {
            "totalHours": round(overtime_total, 2),
            "period": "this_week"
        }
    }


@app.get("/v1/attendance", response_model=List[Attendance])
def read_attendance(agency_id: str = Query(...)):
    return get_documents_by_field("attendance", "agencyId", agency_id)

@app.post("/v1/attendance/clockin", response_model=Attendance)
def clock_in(attendance: Attendance):
    from datetime import datetime, timedelta

    data = attendance.dict(exclude_unset=True)
    user_id = data["userId"]
    agency_id = data["agencyId"]
    site_id = data["siteId"]
    now = datetime.now(timezone.utc)
    now_str = now.isoformat().replace("+00:00", "Z")

    # Check geolocation
    if "lat" not in data or "lng" not in data:
        raise HTTPException(status_code=400, detail="Latitude and longitude are required for clock-in")

    # ✅ Load geofence from site
    site = get_document_by_id("sites", site_id)
    coordinates = site.get("coordinates", [])

    if not coordinates or len(coordinates) < 3:
        raise HTTPException(status_code=404, detail=f"No valid geofence coordinates defined for site {site_id}")

    inside = is_inside_geofence(data["lat"], data["lng"], coordinates)
    if not inside:
        raise HTTPException(status_code=403, detail="You are outside the geofence for this site")

    # Prevent multiple clock-ins today
    today = now.date()   
    start = datetime.combine(today, datetime.min.time()).isoformat() + "Z"
    end = datetime.combine(today, datetime.max.time()).isoformat() + "Z"

    existing = db.collection("attendance") \
        .where("userId", "==", user_id) \
        .where("clockIn", ">=", start) \
        .where("clockIn", "<=", end) \
        .limit(1).stream()

    if any(existing):
        raise HTTPException(status_code=409, detail="Already clocked in today")

    # ⏰ REQUIRED: Find a valid shift — fail if not found
    shift_id = None
    scheduled_start = None

    potential_shifts = db.collection("shifts") \
        .where("employeeId", "==", user_id) \
        .where("siteId", "==", site_id) \
        .where("agencyId", "==", agency_id).stream()

    shifts_today = []
    for shift_doc in potential_shifts:
        shift = shift_doc.to_dict()
        shift_start = datetime.fromisoformat(shift["shiftStart"].replace("Z", "+00:00"))
        shift_end = datetime.fromisoformat(shift["shiftEnd"].replace("Z", "+00:00"))
        if shift_start.date() == today:
            shifts_today.append((shift_doc.id, shift, shift_start, shift_end))

    # Find the best shift for now
    best_shift = None
    min_delta = timedelta(hours=24)

    for sid, sdata, sstart, send in shifts_today:
        if sstart - timedelta(minutes=30) <= now <= send + timedelta(minutes=15):
            delta = abs(now - sstart)
            if delta < min_delta:
                best_shift = (sid, sdata, sstart)
                min_delta = delta

    # ❌ Block clock-in if no matching shift
    if not best_shift:
        raise HTTPException(status_code=403, detail="You do not have a scheduled shift to clock in for")

    shift_id = best_shift[0]
    scheduled_start = best_shift[2].isoformat() + "Z"

    # ✅ Build attendance record
    record = {
        "agencyId": agency_id,
        "userId": user_id,
        "siteId": site_id,
        "clockIn": now_str,
        "lat": data["lat"],
        "lng": data["lng"],
        "shiftId": shift_id,
        "scheduledStart": scheduled_start,
        "createdAt": now_str,
        "updatedAt": now_str
    }

    saved_doc = db.collection("attendance").document()
    saved_doc.set(record)
    record["attendanceId"] = saved_doc.id  # 🔁 inject the ID
    logger.info("Clock-in success", extra={"userId": user_id, "siteId": site_id, "shiftId": shift_id})

    return record







@app.post("/v1/attendance/clockout")
def clock_out(attendanceId: str):
    now = datetime.now(timezone.utc)
    now_str = now.isoformat().replace("+00:00", "Z")

    # 🟡 Fetch attendance record
    attendance = get_document_by_id("attendance", attendanceId)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    if attendance.get("clockOut"):
        raise HTTPException(status_code=400, detail="Already clocked out")

    # 🧠 Handle Z/+00:00 conflicts
    raw_clock_in = attendance["clockIn"]
    if raw_clock_in.endswith("Z") and "+00:00" in raw_clock_in:
        raw_clock_in = raw_clock_in.replace("Z", "")

    clock_in_time = datetime.fromisoformat(raw_clock_in)

    # 🕒 Handle breaks
    break_minutes = 0
    for b in attendance.get("breakPeriods", []):
        start_raw = b.get("breakStart")
        end_raw = b.get("breakEnd")
        if not end_raw:
            continue

        if start_raw.endswith("Z") and "+00:00" in start_raw:
            start_raw = start_raw.replace("Z", "")
        if end_raw.endswith("Z") and "+00:00" in end_raw:
            end_raw = end_raw.replace("Z", "")

        start = datetime.fromisoformat(start_raw)
        end = datetime.fromisoformat(end_raw)
        break_minutes += (end - start).total_seconds() / 60

    total_minutes = (now - clock_in_time).total_seconds() / 60 - break_minutes
    hours_worked = round(total_minutes / 60, 2)
    overtime_hours = 0

    # 🟢 Check shift and calculate overtime
    shift_id = attendance.get("shiftId")
    if shift_id:
        shift = get_document_by_id("shifts", shift_id)
        if shift:
            shift_start = datetime.fromisoformat(shift["shiftStart"].replace("Z", "+00:00"))
            shift_end = datetime.fromisoformat(shift["shiftEnd"].replace("Z", "+00:00"))
            scheduled_hours = (shift_end - shift_start).total_seconds() / 3600
            overtime_hours = round(max(0, hours_worked - scheduled_hours), 2)

            # ✅ Mark shift as completed
            update_document("shifts", shift_id, {
                "status": "completed",
                "updatedAt": now_str
            })

    # ✏️ Update attendance
    update_document("attendance", attendanceId, {
        "clockOut": now_str,
        "hoursWorked": hours_worked,
        "overtimeHours": overtime_hours,
        "updatedAt": now_str
    })

    logger.info("Clock-out success", extra={
        "attendanceId": attendanceId,
        "userId": attendance["userId"],
        "siteId": attendance["siteId"],
        "hoursWorked": hours_worked,
        "overtimeHours": overtime_hours
    })

    return {
        "success": True,
        "message": "Clock-out successful",
        "data": {
            "clockOut": now_str,
            "hoursWorked": hours_worked,
            "overtimeHours": overtime_hours
        }
    }


#####################################################
# 13. time sheets 
#####################################################
@app.get("/v1/timesheets")
def get_timesheets(
    agency_id: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    employee_id: str = Query(None),
    site_id: str = Query(None)
):
    from datetime import datetime

    def parse_utc(dt_str: str) -> datetime:
        if dt_str.endswith("Z") and "+00:00" in dt_str:
            dt_str = dt_str.replace("Z", "")
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

    start = datetime.fromisoformat(start_date).date()
    end = datetime.fromisoformat(end_date).date()

    employees = {e["id"]: e for e in get_documents_by_field("employees", "agencyId", agency_id)}
    sites = {s["id"]: s for s in get_documents_by_field("sites", "agencyId", agency_id)}
    shifts = get_documents_by_field("shifts", "agencyId", agency_id)

    timesheet = []

    for shift in shifts:
        shift_start = parse_utc(shift["shiftStart"])
        shift_end = parse_utc(shift["shiftEnd"])
        shift_date = shift_start.date()

        if not (start <= shift_date <= end):
            continue
        if employee_id and shift["employeeId"] != employee_id:
            continue
        if site_id and shift["siteId"] != site_id:
            continue

        emp = employees.get(shift["employeeId"], {})
        site = sites.get(shift["siteId"], {})

        attendance = db.collection("attendance").where("shiftId", "==", shift["id"]).limit(1).stream()
        record = next(attendance, None)

        entry = {
            "shiftId": shift["id"],
            "employeeId": shift["employeeId"],
            "employeeName": emp.get("name", "Unknown"),
            "siteName": site.get("name", "Unknown"),
            "date": str(shift_date),
            "shiftStart": shift["shiftStart"],
            "shiftEnd": shift["shiftEnd"],
            "clockIn": None,
            "clockOut": None,
            "hoursWorked": 0,
            "overtimeHours": 0,
            "status": "Absent"
        }

        if record:
            r = record.to_dict()
            entry["clockIn"] = r.get("clockIn")
            entry["clockOut"] = r.get("clockOut")
            entry["hoursWorked"] = r.get("hoursWorked", 0)
            entry["overtimeHours"] = r.get("overtimeHours", 0)

            if entry["clockIn"]:
                ci = parse_utc(entry["clockIn"])
                sched = parse_utc(shift["shiftStart"])
                entry["status"] = "Late" if ci > sched else "Present"

        timesheet.append(entry)

    return {
        "success": True,
        "count": len(timesheet),
        "data": timesheet
    }





@app.get("/v1/timesheets/export")
def export_timesheets(
    agency_id: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    employee_id: str = Query(None),
    site_id: str = Query(None)
):
    def parse_utc(dt_str: str) -> datetime:
        if not dt_str:
            return None
        if dt_str.endswith("Z") and "+00:00" in dt_str:
            dt_str = dt_str.replace("Z", "")
        try:
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except Exception:
            return None

    def format_datetime(dt: datetime) -> str:
        return dt.strftime("%d-%m-%Y %H:%M") if dt else ""

    # Fetch timesheet data
    data = get_timesheets(
        agency_id=agency_id,
        start_date=start_date,
        end_date=end_date,
        employee_id=employee_id,
        site_id=site_id
    )["data"]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "Employee Name", "Employee Code", "Site",
        "Date", "Shift Start", "Shift End",
        "Clock In", "Clock Out",
        "Scheduled Hours", "Break Minutes",
        "Hours Worked", "Overtime Hours", "Status", "Remarks"
    ])
    writer.writeheader()

    for row in data:
        scheduled_start = parse_utc(row.get("shiftStart"))
        scheduled_end = parse_utc(row.get("shiftEnd"))
        clock_in = parse_utc(row.get("clockIn"))
        clock_out = parse_utc(row.get("clockOut"))

        scheduled_hours = round((scheduled_end - scheduled_start).total_seconds() / 3600, 2) if scheduled_start and scheduled_end else 0

        # Fetch break time
        break_minutes = 0
        attendance = db.collection("attendance").where("shiftId", "==", row["shiftId"]).limit(1).stream()
        record = next(attendance, None)
        if record:
            att = record.to_dict()
            for b in att.get("breakPeriods", []):
                bs = parse_utc(b.get("breakStart"))
                be = parse_utc(b.get("breakEnd"))
                if bs and be:
                    break_minutes += (be - bs).total_seconds() / 60

        # Load employeeCode
        emp = get_document_by_id("employees", row.get("employeeId", "")) if row.get("employeeId") else {}
        emp_code = emp.get("employeeCode", "")

        writer.writerow({
            "Employee Name": row.get("employeeName", ""),
            "Employee Code": emp_code,
            "Site": row.get("siteName", ""),
            "Date": row.get("date", ""),
            "Shift Start": format_datetime(scheduled_start),
            "Shift End": format_datetime(scheduled_end),
            "Clock In": format_datetime(clock_in),
            "Clock Out": format_datetime(clock_out),
            "Scheduled Hours": scheduled_hours,
            "Break Minutes": round(break_minutes),
            "Hours Worked": row.get("hoursWorked", 0),
            "Overtime Hours": row.get("overtimeHours", 0),
            "Status": row.get("status", ""),
            "Remarks": ""
        })

    output.seek(0)
    filename = f"timesheet_{start_date}_to_{end_date}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

#####################################################
# 13. Message Endpoints (Including Broadcast)
#####################################################

@app.get("/v1/messages", response_model=List[Message])
def get_messages(agency_id: str = Query(...)):
    return get_documents_by_field("messages", "agencyId", agency_id)

@app.post("/v1/messages", response_model=Message)
def create_message(message: Message):
    return add_document("messages", message.dict(exclude_unset=True))

def get_sender_id(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    token = authorization.split(" ")[1]
    try:
        decoded = auth.verify_id_token(token)
        logger.info(f"[Auth] Token decoded. UID: {decoded['uid']}")
        return decoded["uid"]
    except Exception as e:
        logger.error(f"[Auth] Token decoding failed: {e}")
        raise HTTPException(status_code=403, detail="Invalid Firebase ID token")


@app.post("/v1/messages/broadcast", response_model=Dict[str, str])
def broadcast_message(
    broadcast: BroadcastMessage,
    agency_id: str = Query(...)
):
    site = get_document_by_id("sites", broadcast.siteId)
    if site.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    notification = SiteNotification(
        siteId=broadcast.siteId,
        agencyId=agency_id,
        senderId="admin",  # ✅ fallback value
        text=broadcast.text,
        createdAt=datetime.utcnow().isoformat() + "Z"
    )

    doc_ref = db.collection("sites").document(notification.siteId).collection("notifications").document()
    doc_ref.set(notification.dict())

    return {
        "message": "Broadcast saved as site notification",
        "notificationId": doc_ref.id
    }




@app.get("/mobile/messages/broadcast")
def get_broadcast_messages(employee_id: str = Query(...)):
    # Get employee's site
    employees = get_documents_by_field("employees", "employeeCode", employee_id)
    if not employees:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee = employees[0]
    site_id = employee.get("site")
    if not site_id:
        raise HTTPException(status_code=400, detail="Employee is not assigned to any site")

    # Fetch messages sent to that site
    site_messages = get_documents_by_field("siteMessages", "siteId", site_id)
    return sorted(site_messages, key=lambda x: x.get("createdAt", ""), reverse=True)

@app.get("/web/messages/broadcast", response_model=List[Message])
def get_broadcasts_for_agency(agency_id: str = Query(...)):
    messages = get_documents_by_field("siteMessages", "agencyId", agency_id)
    messages.sort(key=lambda m: m.get("createdAt", ""), reverse=True)  # Sort newest first
    return messages



#####################################################
# 14. Hourly Report Endpoints
#####################################################

@app.get("/web/hourly-reports", response_model=List[HourlyReport])
def get_hourly_reports(agency_id: str = Query(...)):
    return get_documents_by_field("hourlyReports", "agencyId", agency_id)

@app.post("/web/hourly-reports", response_model=HourlyReport)
def create_hourly_report(report: HourlyReport):
    data = report.dict(exclude_unset=True)
    saved = add_document("hourlyReports", data)
    # Patch in the Firestore document ID as reportId
    db.collection("hourlyReports").document(saved["id"]).update({"reportId": saved["id"]})
    return saved


@app.delete("/web/hourly-reports/{report_id}")
def delete_hourly_report(report_id: str, agency_id: str = Query(...)):
    report = get_document_by_id("hourlyReports", report_id)
    if report.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    delete_document("hourlyReports", report_id)
    return {"message": f"Hourly Report {report_id} deleted"}

#####################################################
# 15. Scheduling Endpoint
#####################################################
from datetime import datetime, timezone

def parse_utc(dt_str: str) -> datetime:
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

def check_shift_conflict(employee_id: str, new_start: str, new_end: str, exclude_shift_id: Optional[str] = None) -> bool:
    new_start_dt = parse_utc(new_start)
    new_end_dt = parse_utc(new_end)

    shifts = db.collection("shifts").where("employeeId", "==", employee_id).stream()
    for shift in shifts:
        data = shift.to_dict()
        if exclude_shift_id and shift.id == exclude_shift_id:
            continue  # skip the shift being updated

        existing_start = parse_utc(data["shiftStart"])
        existing_end = parse_utc(data["shiftEnd"])

        # Check overlap
        if (existing_start < new_end_dt) and (new_start_dt < existing_end):
            return True
    return False


@app.get("/v1/calendar/shifts")
def get_calendar_shifts(
    agency_id: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    site_id: Optional[str] = Query(None)
):
    shifts = get_documents_by_field("shifts", "agencyId", agency_id)

    start = datetime.fromisoformat(start_date.rstrip("Z"))
    end = datetime.fromisoformat(end_date.rstrip("Z"))

    filtered_shifts = []
    for shift in shifts:
        shift_start = datetime.fromisoformat(shift["shiftStart"].rstrip("Z"))
        shift_end = datetime.fromisoformat(shift["shiftEnd"].rstrip("Z"))

        # 🧠 Date range overlap check
        if (shift_end < start or shift_start > end):
            continue

        # ❗ Site filter
        if site_id and shift.get("siteId") != site_id:
            continue

        filtered_shifts.append(shift)

    # Format as FullCalendar events
    calendar_events = []
    for shift in filtered_shifts:
        employee_id = shift["employeeId"]
        site_id = shift["siteId"]

        employee = get_document_by_id("employees", employee_id)
        site = get_document_by_id("sites", site_id)

        calendar_events.append({
            "id": shift["id"],
            "title": f"{employee['name']} - {site['name']}",
            "start": shift["shiftStart"],
            "end": shift["shiftEnd"],
            "extendedProps": {
                "employeeId": employee_id,
                "employeeName": employee["name"],
                "siteId": site_id,
                "siteName": site["name"]
            }
        })

    return calendar_events



@app.post("/v1/calendar/shifts")
def create_calendar_shift(
    employee_id: str = Body(...),
    site_id: str = Body(...),
    start: str = Body(...),
    end: str = Body(...),
    agency_id: str = Body(...)
):
    """Create a shift from calendar UI"""

    # ✅ Conflict check
    if check_shift_conflict(employee_id, start, end):
        raise HTTPException(
            status_code=409,
            detail="Shift conflict: Employee already has a shift during this time."
        )

    shift = Shift(
        agencyId=agency_id,
        employeeId=employee_id,
        siteId=site_id,
        shiftStart=start,
        shiftEnd=end
    )
    
    result = add_document("shifts", shift.dict(exclude_unset=True))
    
    employee = get_document_by_id("employees", employee_id)
    site = get_document_by_id("sites", site_id)
    
    return {
        "id": result["id"],
        "title": f"{employee['name']} - {site['name']}",
        "start": result["shiftStart"],
        "end": result["shiftEnd"],
        "extendedProps": {
            "employeeId": employee_id,
            "employeeName": employee["name"],
            "siteId": site_id,
            "siteName": site["name"]
        }
    }


@app.put("/v1/calendar/shifts/{shift_id}")
def update_calendar_shift(
    shift_id: str,
    start: str = Body(...),
    end: str = Body(...),
    employee_id: Optional[str] = Body(None),
    site_id: Optional[str] = Body(None),
    agency_id: str = Query(...)
):
    """Update shift times or assignment from calendar dragging/resizing"""
    shift = get_document_by_id("shifts", shift_id)
    if shift.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    emp_id_to_check = employee_id if employee_id else shift["employeeId"]

    # ✅ Conflict check
    if check_shift_conflict(emp_id_to_check, start, end, exclude_shift_id=shift_id):
        raise HTTPException(
            status_code=409,
            detail="Shift conflict: Employee already has a shift during this time."
        )

    update_data = {
        "shiftStart": start,
        "shiftEnd": end,
    }
    if employee_id:
        update_data["employeeId"] = employee_id
    if site_id:
        update_data["siteId"] = site_id

    result = update_document("shifts", shift_id, update_data)

    employee = get_document_by_id("employees", result["employeeId"])
    site = get_document_by_id("sites", result["siteId"])

    return {
        "id": shift_id,
        "title": f"{employee['name']} - {site['name']}",
        "start": result["shiftStart"],
        "end": result["shiftEnd"],
        "extendedProps": {
            "employeeId": result["employeeId"],
            "employeeName": employee["name"],
            "siteId": result["siteId"],
            "siteName": site["name"]
        }
    }

#####################################################
# 16. employee endpoints
#####################################################

@app.post("/web/employee/add")
def add_employee(employee: EmployeeModel):
    data = employee.dict(exclude_unset=True)

    # Do not add uid here, it will be filled during mobile registration
    if not data.get("employeeCode"):
        data["employeeCode"] = f"EMP-{str(uuid.uuid4())[:6].upper()}"

    # ✅ Generate join code and mark it as unused
    data["joinCode"] = generate_unique_employee_join_code()
    data["joinCodeStatus"] = "unused"

    return add_document("employees", data)




def get_documents_by_field(collection: str, field: str, value: str) -> List[dict]:
    logger.info(f"Querying {collection} where {field} = {value}")
    docs = db.collection(collection).stream() if field == "all" else db.collection(collection).where(field, "==", value).stream()
    result = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id  # 🔥 Include Firestore document ID
        result.append(data)
    logger.info(f"Found {len(result)} documents in {collection}")
    return result



@app.get("/v1/employees/{employee_id}")
def get_employee_by_id(employee_id: str):
    return get_document_by_id("employees", employee_id)

@app.patch("/v1/employees/{employee_id}")
def update_employee_by_id(employee_id: str, employee: EmployeeModel):
    return update_document("employees", employee_id, employee.dict(exclude_unset=True))

@app.delete("/v1/employees/{employee_id}")
def delete_employee_by_id(employee_id: str):
    delete_document("employees", employee_id)
    return {"message": "Deleted"}


@app.get("/web/employee/all")
def get_all_employees(agency_id: str = Query(...)):
    return get_documents_by_field("employees", "agencyId", agency_id)

@app.post("/v1/employees/bulk-import")
def bulk_import_employees(employees: List[EmployeeModel] = Body(...)):
    batch = db.batch()
    now = datetime.utcnow().isoformat()
    imported = 0
    failed = []

    for emp in employees:
        try:
            data = emp.dict(exclude_unset=True)

            if not data.get("employeeCode"):
                data["employeeCode"] = f"EMP-{str(uuid.uuid4())[:6].upper()}"

            if not data.get("createdAt"):
                data["createdAt"] = now
            data["updatedAt"] = now

            # Generate new document reference
            doc_ref = db.collection("employees").document()
            batch.set(doc_ref, data)
            imported += 1
        except Exception as e:
            failed.append({"employee": emp.name, "error": str(e)})

    try:
        batch.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch write failed: {str(e)}")

    return {
        "success": True,
        "imported": imported,
        "failed": failed,
    }

#####################################################
# 16. Site Endpoints (Enhanced CRUD)
#####################################################








@app.post("/mobile/hourly-reports", response_model=HourlyReport)
def submit_hourly_report(report: HourlyReport):
    data = report.dict(exclude_unset=True)
    saved = add_document("hourlyReports", data)

    # Explicitly include the document ID as reportId
    saved["reportId"] = saved["id"]
    return saved


@app.get("/mobile/hourly-reports", response_model=List[HourlyReport])
def get_my_reports(user_id: str = Query(...), agency_id: str = Query(...)):
    reports = db.collection("hourlyReports").where("agencyId", "==", agency_id).where("userId", "==", user_id).stream()
    return [r.to_dict() for r in reports]

@app.post("/mobile/geofence/verify")
def verify_geofence(site_id: str = Query(...), lat: float = Query(...), lng: float = Query(...)):
    geofences = get_documents_by_field("geofences", "siteId", site_id)
    if not geofences:
        raise HTTPException(status_code=404, detail="No geofence found for this site")
    inside = any(is_inside_geofence(lat, lng, g["coordinates"]) for g in geofences)
    return {"insideGeofence": inside}

@app.get("/mobile/shifts/assigned", response_model=List[Shift])
def get_assigned_shifts(employee_id: str = Query(...)):
    return get_documents_by_field("shifts", "employeeId", employee_id)

@app.patch("/mobile/shifts/{shift_id}/status")
def update_shift_status(shift_id: str, status: str = Query(...), employee_id: str = Query(...)):
    shift = get_document_by_id("shifts", shift_id)
    if shift.get("employeeId") != employee_id:
        raise HTTPException(status_code=403, detail="You are not assigned to this shift")
    return update_document("shifts", shift_id, {"status": status})


@app.get("/mobile/shifts/open", response_model=List[Shift])
def get_open_shifts(agency_id: str = Query(...)):
    shifts = db.collection("shifts").where("agencyId", "==", agency_id).where("status", "==", "open").stream()
    return [s.to_dict() for s in shifts]


#test pending
@app.patch("/mobile/shifts/{shift_id}/apply")
def apply_for_shift(shift_id: str, employee_id: str = Query(...)):
    shift = get_document_by_id("shifts", shift_id)

    if shift.get("status") != "open" or shift.get("employeeId"):
        raise HTTPException(status_code=400, detail="Shift is not open for application")

    # ✅ Conflict check before applying
    if check_shift_conflict(employee_id, shift["shiftStart"], shift["shiftEnd"]):
        raise HTTPException(
            status_code=409,
            detail="Shift conflict: You already have a shift during this time."
        )

    return update_document("shifts", shift_id, {
        "employeeId": employee_id,
        "status": "pending"
    })



@app.post("/mobile/employee/login")
def mobile_login(payload: LoginRequest):
    try:
        decoded = auth.verify_id_token(payload.idToken)
        uid = decoded["uid"]

        # Lookup employee by UID
        employees = get_documents_by_field("employees", "uid", uid)
        if not employees:
            raise HTTPException(status_code=404, detail="Employee not found")

        employee = employees[0]
        return {
            "message": "Employee login successful",
            "uid": uid,
            "employeeId": employee["employeeCode"],
            "agencyId": employee["agencyId"],
             "siteId": employee.get("site"), 
            "name": employee["name"],
            "status": employee["status"]
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Mobile login failed: {str(e)}")



class EmployeeRegisterPayload(BaseModel):
    idToken: str
    agencyCode: str
    employee: EmployeeModel

@app.post("/mobile/employee/register")
def register_with_join_code(payload: EmployeeJoinCodeRegisterPayload):
    decoded = auth.verify_id_token(payload.idToken)
    uid = decoded["uid"]
    email = decoded.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Firebase token")

    # Check if UID is already linked
    existing = get_documents_by_field("employees", "uid", uid)
    if existing:
        raise HTTPException(status_code=400, detail="Employee already registered")

    # Match unclaimed employee with joinCode
    emp_query = db.collection("employees") \
        .where("joinCode", "==", payload.joinCode) \
        .stream()

    matched_doc = None
    for doc in emp_query:
        data = doc.to_dict()
        if not data.get("uid"):  # uid is None or not present
            matched_doc = doc
            break  # ✅ Only break if we find a valid unclaimed doc

    if not matched_doc:
        raise HTTPException(status_code=404, detail="Invalid or already used join code")

    emp_id = matched_doc.id
    emp_data = matched_doc.to_dict()

    updated_data = {
        "uid": uid,
        "email": email,
        "status": "active",
        "joinCodeStatus": "used",
        "updatedAt": datetime.utcnow().isoformat() + "Z"
    }

    db.collection("employees").document(emp_id).update(updated_data)
    emp_data.update(updated_data)

    return {
        "message": "Employee successfully registered",
        "uid": uid,
        "employeeId": emp_data["employeeCode"],
        "agencyId": emp_data["agencyId"],
        "siteId": emp_data.get("site"),
        "name": emp_data["name"],
        "status": emp_data["status"]
    }





@app.post("/web/employee/{employee_id}/reset-join-code")
def regenerate_join_code(employee_id: str):
    new_code = generate_unique_employee_join_code()
    update_document("employees", employee_id, {
        "joinCode": new_code,
        "updatedAt": datetime.utcnow().isoformat() + "Z"
    })
    return {"success": True, "joinCode": new_code}




## push notficiation module 

#send push helper 



#register your mobile device 

##############
#reports 
#

@app.get("/mobile/reports", response_model=List[HourlyReport])
def get_reports_for_employee(employee_id: str = Query(...), agency_id: str = Query(...)):
    reports = db.collection("hourlyReports") \
        .where("userId", "==", employee_id) \
        .where("agencyId", "==", agency_id) \
        .order_by("createdAt", direction=firestore.Query.DESCENDING) \
        .stream()

    return [r.to_dict() for r in reports]

@app.get("/mobile/hourly-reports/{report_id}")
def get_single_hourly_report(report_id: str, agency_id: str = Query(...)):
    report = get_document_by_id("hourlyReports", report_id)

    if report["agencyId"] != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to report")

    site = get_document_by_id("sites", report["siteId"])
    employee = get_document_by_id("employees", report["userId"])

    # Format datetime
    dt = safe_parse_datetime(report.get("createdAt"))
    formatted_time = dt.strftime("%b %d, %Y at %#I:%M %p") if dt else None

    return {
        "reportType": "Hourly Report",
        "status": "Submitted",
        "datetime": formatted_time,
        "location": site["name"],
        "submittedBy": employee["name"],
        "reportText": report.get("reportText"),
        "images": report.get("images", []),
        "agencyId": agency_id
    }






##########################################
#mobile api for screens
##########################################
@app.get("/mobile/home")
def get_mobile_home(employee_id: str = Query(...)):
    now = datetime.now(timezone.utc)
    today = now.date()

    # 🔍 1. Get employee
    employee = get_document_by_id("employees", employee_id)
    site_id = employee.get("assignedsiteID")
    agency_id = employee.get("agencyId")

    # 🔍 2. Today’s shift
    shifts = db.collection("shifts") \
        .where("employeeId", "==", employee_id) \
        .where("siteId", "==", site_id) \
        .where("agencyId", "==", agency_id).stream()

    current_shift = None
    next_shift = None

    # Preload site name once
    site_name = get_document_by_id("sites", site_id).get("name", "Unknown")

    # Get today's attendance record
    start_time = datetime.combine(today, datetime.min.time()).isoformat() + "Z"
    end_time = datetime.combine(today, datetime.max.time()).isoformat() + "Z"
    attendance_today = list(
        db.collection("attendance")
        .where("userId", "==", employee_id)
        .where("clockIn", ">=", start_time)
        .where("clockIn", "<=", end_time)
        .limit(1)
        .stream()
    )
    clocked_in = any(attendance_today)
    has_clocked_out = any(a.to_dict().get("clockOut") for a in attendance_today)

    for shift_doc in shifts:
        shift = shift_doc.to_dict()
        start = safe_parse_datetime(shift.get("shiftStart"))
        end = safe_parse_datetime(shift.get("shiftEnd"))
        if not start or not end:
            continue

        if start.date() == today:
            # 🚨 Status logic includes clock-out check
            shift_status = (
                "Completed" if has_clocked_out
                else "Ongoing" if start <= now <= end
                else "Upcoming" if now < start
                else "Completed"
            )

            current_shift = {
                "siteName": site_name,
                "shiftStart": shift["shiftStart"],
                "shiftEnd": shift["shiftEnd"],
                "status": shift_status
            }

            if start > now:
                next_shift = start

    # ⏱ 3. Geofence check
    geofence_status = "outside"
    lat = employee.get("lat")
    lng = employee.get("lng")
    coordinates = get_document_by_id("sites", site_id).get("coordinates", [])

    if lat and lng and coordinates:
        inside = is_inside_geofence(lat, lng, coordinates)
        geofence_status = "inside" if inside else "outside"

    # 🕘 4. Recent Activity
    attendance_logs = db.collection("attendance") \
        .where("userId", "==", employee_id) \
        .order_by("clockIn", direction=firestore.Query.DESCENDING) \
        .limit(4).stream()

    recent_activity = []
    for record in attendance_logs:
        data = record.to_dict()
        clock_in = data.get("clockIn")
        clock_out = data.get("clockOut")
        dt = safe_parse_datetime(clock_in)

        if dt:
            clockout_dt = safe_parse_datetime(clock_out)
            recent_activity.append({
                "date": dt.strftime("%b %d, %Y"),
                "clockIn": dt.strftime("%I:%M %p").lstrip("0"),
                "clockOut": clockout_dt.strftime("%I:%M %p").lstrip("0") if clockout_dt else None
            })

    # 🧠 5. Shift status
    shift_status = {
        "currentStatus": "On Duty" if clocked_in else "Off Duty",
        "nextShiftAt": next_shift.isoformat() + "Z" if next_shift else None,
        "in": str(next_shift - now).split(".")[0] if next_shift else None
    }

    return {
        "clockedIn": clocked_in,
        "currentShift": current_shift,
        "geofenceStatus": geofence_status,
        "shiftStatus": shift_status,
        "recentActivity": recent_activity
    }


##############
#dashboard
###############
@app.get("/v1/dashboard/metrics")
def get_dashboard_metrics(agency_id: str = Query(...)):
    try:
        # Load site metadata to map siteId → siteName
        sites = db.collection("sites").where("agencyId", "==", agency_id).stream()
        site_name_map = {s.id: s.to_dict().get("name", s.id) for s in sites}

        # Group employees by assignedsiteID
        employees = db.collection("employees").where("agencyId", "==", agency_id).stream()
        site_employees = {}
        all_employees = []

        for doc in employees:
            data = doc.to_dict()
            site_id = data.get("assignedsiteID")  # ✅ Correct field
            if not site_id:
                continue
            site_employees.setdefault(site_id, []).append(doc.id)
            all_employees.append(doc.id)

        # Group today's attendance by siteId, only include clocked-in AND not clocked-out
        today = datetime.utcnow().date().isoformat()
        attendance = db.collection("attendance").where("agencyId", "==", agency_id).stream()
        site_attendance = {}
        all_attendance = []

        for doc in attendance:
            data = doc.to_dict()
            clock_in = data.get("clockIn", "")
            clock_out = data.get("clockOut")

            if not clock_in or not clock_in.startswith(today):
                continue
            if clock_out:  # ✅ Exclude those who have clocked out
                continue

            site_id = data.get("siteId")
            if not site_id:
                continue

            site_attendance.setdefault(site_id, []).append(data)
            all_attendance.append(data)

        # Group hourly reports by siteId
        reports = db.collection("hourlyReports").where("agencyId", "==", agency_id).stream()
        site_reports = {}
        all_reports = []

        for doc in reports:
            data = doc.to_dict()
            site_id = data.get("siteId")
            if not site_id:
                continue
            site_reports[site_id] = site_reports.get(site_id, 0) + 1
            all_reports.append(data)

        # Aggregate per siteId
        site_ids = set(site_employees.keys()) | set(site_attendance.keys()) | set(site_reports.keys())
        metrics = {}

        for site_id in site_ids:
            emp_count = len(site_employees.get(site_id, []))
            att_count = len(site_attendance.get(site_id, []))
            rep_count = site_reports.get(site_id, 0)

            metrics[site_id] = {
                "attendancePercentage": round((att_count / emp_count) * 100, 1) if emp_count else 0,
                "activeOnDuty": att_count,
                "reports": rep_count,
                "siteName": site_name_map.get(site_id, "Unnamed Site")
            }

        # Add global summary under "all"
        metrics["all"] = {
            "attendancePercentage": round((len(all_attendance) / len(all_employees)) * 100, 1) if all_employees else 0,
            "activeOnDuty": len(all_attendance),
            "reports": len(all_reports),
            "siteName": "All Sites"
        }

        return {
            "success": True,
            "sites": metrics  # ⬅️ now keyed by siteId
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")






#####################################################

@app.get("/")
def root():
    return {
        "message": "Welcome to the SecureFront API by BluOrigin Team v1.3.31 shift conflict resolved"
    }


#####################################################

#######################################################