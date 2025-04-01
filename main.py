##############################################
# main.py - Single File SecureFront Application
# Version: 1.3.16  # Updated version for sites CRUD and broadcast
# Last Updated: 2025-03-16
##############################################

import logging
from typing import Annotated
from datetime import datetime
from fastapi import Header, Depends
from typing import List, Dict, Optional
from firebase_admin import auth
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from firebase_admin import credentials, initialize_app, firestore
from shapely.geometry import Point, Polygon
from pydantic import BaseModel, constr
from typing import Optional
import uuid
import random
import string

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
    location: Dict[str, float]
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

class GeoFence(BaseModel):
    geoFenceId: Optional[str] = None
    agencyId: str
    siteId: str
    coordinates: List[Dict[str, float]]
    radius: Optional[float] = None
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
    clockIn: str
    clockOut: Optional[str] = None
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
    reportId: Optional[str] = None
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


class JoinCode(BaseModel):
    code: str
    agencyId: str
    used: bool = False
    createdAt: Optional[str] = None
    usedAt: Optional[str] = None
    usedBy: Optional[str] = None    


class EmployeeModel(BaseModel):
    name: str
    employeeCode: Optional[str] = None 
    role: Optional[str] = None 
    status: Optional[str] = None 
    site: Optional[str] = None 
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
    employee: EmployeeModel

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
#  login endpoints
#####################################################
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

#####################################################
# 10. GeoFence Endpoints
#####################################################

@app.get("/v1/geofences", response_model=List[GeoFence])
def read_geofences(agency_id: str = Query(...)):
    geofences = get_documents_by_field("geofences", "agencyId", agency_id)
    logger.info(f"Retrieved {len(geofences)} geofences for agency {agency_id}")
    return geofences

@app.get("/v1/geofences/{geofence_id}", response_model=GeoFence)
def read_geofence(geofence_id: str, agency_id: str = Query(...)):
    geofence = get_document_by_id("geofences", geofence_id)
    if geofence.get("agencyId") != agency_id:
        logger.warning(f"Unauthorized access attempt to geofence {geofence_id} by agency {agency_id}")
        raise HTTPException(status_code=403, detail="Unauthorized")
    logger.info(f"Retrieved geofence {geofence_id} for agency {agency_id}")
    return geofence

@app.post("/v1/geofences", response_model=GeoFence)
def create_geofence(geofence: GeoFence):
    data = geofence.dict(exclude_unset=True)
    validate_geofence_coordinates(data["coordinates"])
    result = add_document("geofences", data)
    logger.info(f"Created geofence {result['id']} for agency {data['agencyId']} and site {data['siteId']}")
    return result

@app.put("/v1/geofences/{geofence_id}", response_model=GeoFence)
def update_geofence(geofence_id: str, geofence: GeoFence, agency_id: str = Query(...)):
    existing_geofence = get_document_by_id("geofences", geofence_id)
    if existing_geofence.get("agencyId") != agency_id:
        logger.warning(f"Unauthorized update attempt to geofence {geofence_id} by agency {agency_id}")
        raise HTTPException(status_code=403, detail="Unauthorized")
    data = geofence.dict(exclude_unset=True)
    validate_geofence_coordinates(data["coordinates"])
    data["geoFenceId"] = geofence_id
    result = update_document("geofences", geofence_id, data)
    logger.info(f"Updated geofence {geofence_id} for agency {agency_id}")
    return result

@app.patch("/v1/geofences/{geofence_id}", response_model=GeoFence)
def partial_update_geofence(geofence_id: str, geofence: GeoFence, agency_id: str = Query(...)):
    existing_geofence = get_document_by_id("geofences", geofence_id)
    if existing_geofence.get("agencyId") != agency_id:
        logger.warning(f"Unauthorized patch attempt to geofence {geofence_id} by agency {agency_id}")
        raise HTTPException(status_code=403, detail="Unauthorized")
    data = geofence.dict(exclude_unset=True, exclude_none=True)
    if "coordinates" in data:
        validate_geofence_coordinates(data["coordinates"])
    result = update_document("geofences", geofence_id, data)
    logger.info(f"Partially updated geofence {geofence_id} for agency {agency_id}")
    return result

@app.delete("/v1/geofences/{geofence_id}")
def delete_geofence(geofence_id: str, agency_id: str = Query(...)):
    geofence = get_document_by_id("geofences", geofence_id)
    if geofence.get("agencyId") != agency_id:
        logger.warning(f"Unauthorized delete attempt to geofence {geofence_id} by agency {agency_id}")
        raise HTTPException(status_code=403, detail="Unauthorized")
    delete_document("geofences", geofence_id)
    logger.info(f"Deleted geofence {geofence_id} for agency {agency_id}")
    return {"message": f"GeoFence {geofence_id} deleted"}

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

@app.get("/v1/attendance", response_model=List[Attendance])
def read_attendance(agency_id: str = Query(...)):
    return get_documents_by_field("attendance", "agencyId", agency_id)

@app.post("/v1/attendance/clockin", response_model=Attendance)
def clock_in(attendance: Attendance):
    data = attendance.dict(exclude_unset=True)
    if "lat" not in data or "lng" not in data:
        raise HTTPException(status_code=400, detail="Latitude and longitude are required for clock-in")
    geofences = get_documents_by_field("geofences", "siteId", data["siteId"])
    if not geofences:
        raise HTTPException(status_code=404, detail=f"No geofences found for site {data['siteId']}")
    user_inside_geofence = False
    for geofence in geofences:
        if is_inside_geofence(data["lat"], data["lng"], geofence["coordinates"]):
            user_inside_geofence = True
            logger.info(f"User {data['userId']} is inside geofence {geofence['geoFenceId']} for site {data['siteId']}")
            break
    if not user_inside_geofence:
        logger.warning(f"User {data['userId']} is outside all geofences for site {data['siteId']}")
        raise HTTPException(status_code=403, detail="User is outside the geofence for this site")
    logger.info(f"Clock-in successful for user {data['userId']} at site {data['siteId']}")
    return add_document("attendance", data)

@app.post("/v1/attendance/clockout", response_model=Attendance)
def clock_out(attendance_id: str = Query(..., alias="attendanceId"), agency_id: str = Query(...)):
    attendance = get_document_by_id("attendance", attendance_id)
    if attendance.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return update_document("attendance", attendance_id, {"clockOut": datetime.utcnow().isoformat() + "Z"})

@app.post("/v1/attendance/break", response_model=Attendance)
def add_break(attendance_id: str, break_start: str, break_end: Optional[str] = None, agency_id: str = Query(...)):
    doc = get_document_by_id("attendance", attendance_id)
    if doc.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    break_periods = doc.get("breakPeriods", [])
    break_periods.append({"breakStart": break_start, "breakEnd": break_end})
    return update_document("attendance", attendance_id, {"breakPeriods": break_periods})

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
    return add_document("hourlyReports", report.dict(exclude_unset=True))

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

@app.post("/web/scheduling/optimize")
def optimize_scheduling(site_id: str, agency_id: str = Query(...)):
    return {"message": "Scheduling optimization is not fully implemented in single-file mode."}

#####################################################
# 16. Site Endpoints (Enhanced CRUD)
#####################################################

@app.post("/web/employee/add")
def add_employee(employee: EmployeeModel):
    data = employee.dict(exclude_unset=True)

    # Do not add uid here, it will be filled during mobile registration
    if not data.get("employeeCode"):
        data["employeeCode"] = f"EMP-{str(uuid.uuid4())[:6].upper()}"
    
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
def get_employee_by_id(employee_id: str, agency_id: str = Query(...)):
    employee = get_document_by_id("employees", employee_id)
    if employee.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return employee

@app.patch("/v1/employees/{employee_id}")
def update_employee_by_id(employee_id: str, employee: EmployeeModel, agency_id: str = Query(...)):
    existing = get_document_by_id("employees", employee_id)
    if existing.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return update_document("employees", employee_id, employee.dict(exclude_unset=True))

@app.delete("/v1/employees/{employee_id}")
def delete_employee_by_id(employee_id: str, agency_id: str = Query(...)):
    existing = get_document_by_id("employees", employee_id)
    if existing.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    delete_document("employees", employee_id)
    return {"message": "Deleted"}



@app.get("/web/employee/all")
def get_all_employees(agency_id: str = Query(...)):
    return get_documents_by_field("employees", "agencyId", agency_id)


#####################################################
# 16. Site Endpoints (Enhanced CRUD)
#####################################################


def generate_unique_join_code(length: int = 6) -> str:
    for _ in range(10):  # Retry up to 10 times
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        code = f"JOIN-{suffix}"
        existing = db.collection("joiningCodes").where("code", "==", code).limit(1).stream()
        if not any(existing):
            return code
    raise HTTPException(status_code=500, detail="Unable to generate unique join code")

@app.post("/v1/join-code/generate")
def generate_join_code(agency_id: str = Query(...)):
    try:
        code = generate_unique_join_code()
        data = {
            "code": code,
            "agencyId": agency_id,
            "used": False,
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "usedAt": None,
            "usedBy": None
        }
        saved = add_document("joiningCodes", data)
        return {"message": "Join code generated", "joinCode": saved["code"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate join code: {str(e)}")



@app.post("/mobile/hourly-reports", response_model=HourlyReport)
def submit_hourly_report(report: HourlyReport):
    return add_document("hourlyReports", report.dict(exclude_unset=True))

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

@app.patch("/mobile/shifts/{shift_id}/apply")
def apply_for_shift(shift_id: str, employee_id: str = Query(...)):
    shift = get_document_by_id("shifts", shift_id)
    if shift.get("status") != "open" or shift.get("employeeId"):
        raise HTTPException(status_code=400, detail="Shift is not open for application")
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
    try:
        decoded = auth.verify_id_token(payload.idToken)
        uid = decoded["uid"]

        # Check if employee already exists
        existing = get_documents_by_field("employees", "uid", uid)
        if existing:
            raise HTTPException(status_code=400, detail="Employee already registered")

        # Validate join code
        join_query = db.collection("joiningCodes") \
            .where("code", "==", payload.joinCode) \
            .where("used", "==", False) \
            .limit(1).stream()

        join_doc = next(join_query, None)
        if not join_doc:
            raise HTTPException(status_code=400, detail="Invalid or already used join code")

        join_data = join_doc.to_dict()
        agency_id = join_data["agencyId"]

        # Generate random employee code
        def generate_employee_code(length=6):
            return "EMP-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

        employee_code = generate_employee_code()

        # Prepare employee data
        data = payload.employee.dict(exclude={"employeeCode"}, exclude_unset=True)
        data.update({
            "uid": uid,
            "agencyId": agency_id,
            "status": "active",
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "updatedAt": datetime.utcnow().isoformat() + "Z",
            "employeeCode": employee_code
        })

        new_employee = add_document("employees", data)

        db.collection("joiningCodes").document(join_doc.id).update({
            "used": True,
            "usedBy": uid,
            "usedAt": datetime.utcnow().isoformat() + "Z"
        })

        return {
            "message": "Employee registered successfully",
            "uid": uid,
            "employeeId": employee_code,
            "agencyId": agency_id,
            "siteId": new_employee.get("site"),
            "name": new_employee["name"],
            "status": new_employee["status"]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")





#####################################################

@app.get("/")
def root():
    return {
        "message": "Welcome to the SecureFront API by BluOrigin Team v1.3.31 broadcast via auth"
    }


#####################################################
# Usage:
# 1) Place serviceAccountKey.json next to this file
# 2) pip install fastapi uvicorn firebase-admin shapely
# 3) python -m uvicorn main:app --reload
# 4) Test endpoints with curl/Postman:
#    - POST /v1/sites {"agencyId": "AGENCY001", "name": "Site1", "description": "Test site", "address": "123 St", "assignedHours": 8, "location": {"lat": 19.171, "lng": 72.845}}
#    - GET /v1/sites/<site_id>?agency_id=<agency_id>
#    - PUT /v1/sites/<site_id>?agency_id=<agency_id> {"agencyId": "AGENCY001", "name": "Updated Site", ...}
#    - PATCH /v1/sites/<site_id>?agency_id=<agency_id> {"name": "Patched Site"}
#    - DELETE /v1/sites/<site_id>?agency_id=<agency_id>
#    - POST /v1/messages/broadcast?agency_id=AGENCY001&senderId=OPERATOR001 {"siteId": "SITE001", "text": "Emergency: Evacuate immediately"}
#######################################################