# routes/messages.py
from fastapi import APIRouter, HTTPException, Query, Header
from db import add_document, get_documents_by_field, get_document_by_id, update_document
from models import Message, BroadcastMessage, SiteNotification
from datetime import datetime
import logging

router = APIRouter(prefix="/v1/messages", tags=["Messages"])
logger = logging.getLogger(__name__)

@router.get("", response_model=list)
def get_messages(agency_id: str = Query(...)):
    return get_documents_by_field("messages", "agencyId", agency_id)

@router.post("", response_model=Message)
def create_message(message: Message):
    return add_document("messages", message.dict(exclude_unset=True))

@router.post("/broadcast", response_model=dict)
def broadcast_message(broadcast: BroadcastMessage, agency_id: str = Query(...)):
    site = get_document_by_id("sites", broadcast.siteId)
    if site.get("agencyId") != agency_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    notification = SiteNotification(
        siteId=broadcast.siteId,
        agencyId=agency_id,
        senderId="admin",
        text=broadcast.text,
        createdAt=datetime.utcnow().isoformat() + "Z"
    )
    from config import db
    doc_ref = db.collection("sites").document(notification.siteId).collection("notifications").document()
    doc_ref.set(notification.dict())
    return {"message": "Broadcast saved as site notification", "notificationId": doc_ref.id}
