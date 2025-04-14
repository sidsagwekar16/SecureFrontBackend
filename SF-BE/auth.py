# auth.py
from fastapi import APIRouter, HTTPException
from firebase_admin import auth
from config import db, logger
from db import add_document
from datetime import datetime

router = APIRouter()

@router.post("/auth/login")
def login_user(payload: dict):
    try:
        decoded_token = auth.verify_id_token(payload.get("idToken"))
        uid = decoded_token["uid"]
        agency_id = decoded_token.get("agencyId")
        if not agency_id:
            user_doc = db.collection("users").document(uid).get()
            if user_doc.exists:
                agency_id = user_doc.to_dict().get("agencyId")
        if not agency_id:
            raise HTTPException(status_code=400, detail="Agency ID not associated with user")
        return {"message": "Login successful", "uid": uid, "agencyId": agency_id}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

@router.post("/auth/logout")
def logout_user():
    return {"message": "Logout handled client-side by clearing session/token."}

@router.post("/auth/complete-signup")
def complete_signup(payload: dict):
    try:
        id_token = payload.get("idToken")
        if id_token.count('.') != 2:
            raise HTTPException(400, "Invalid Firebase ID token format")
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        user_doc = db.collection("users").document(uid).get()
        if user_doc.exists:
            raise HTTPException(status_code=400, detail="User already linked to an agency")
        # Create agency using add_document and data from payload
        agency_data = payload.get("agency")
        if not agency_data:
            raise HTTPException(status_code=400, detail="Agency data is required")
        agency_data["ownerId"] = uid
        new_agency = add_document("agencies", agency_data)
        db.collection("users").document(uid).set({"agencyId": new_agency.get("agencyId")})
        return {"message": "Signup complete", "agencyId": new_agency.get("agencyId")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Signup failed: {str(e)}")
