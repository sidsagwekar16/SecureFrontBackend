# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from routes import (
    agencies,
    sites,
    shifts,
    leave_requests,
    incidents,
    geofences,
    billing,
    attendance,
    messages,
    hourly_reports,
    calendar,
    employee,
    join_code
)

app = FastAPI(
    title="SecureFront API",
    description="Modular refactored API for SecureFront",
    version="1.3.16"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(agencies.router)
app.include_router(sites.router)
app.include_router(shifts.router)
app.include_router(leave_requests.router)
app.include_router(incidents.router)
app.include_router(geofences.router)
app.include_router(billing.router)
app.include_router(attendance.router)
app.include_router(messages.router)
app.include_router(hourly_reports.router)
app.include_router(calendar.router)
app.include_router(employee.router)
app.include_router(join_code.router)

@app.get("/")
def root():
    return {"message": "Welcome to the SecureFront API"}
