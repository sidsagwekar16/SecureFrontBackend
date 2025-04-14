# models.py
from pydantic import BaseModel
from typing import Optional, List, Dict

class LoginRequest(BaseModel):
    idToken: str

class AgencyCreate(BaseModel):
    name: str
    contactEmail: str
    contactPhone: str
    address: str
    subscriptionPlan: str

class Agency(AgencyCreate):
    agencyId: str
    createdAt: str
    updatedAt: str

class Site(BaseModel):
    id: Optional[str] = None
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
    userId: str
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
    employee: EmployeeModel
