# db.py
from datetime import datetime
from fastapi import HTTPException
from config import db, logger

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

def get_documents_by_field(collection: str, field: str, value: str) -> list:
    logger.info(f"Querying {collection} where {field} = {value}")
    docs = (
        db.collection(collection).stream()
        if field == "all"
        else db.collection(collection).where(field, "==", value).stream()
    )
    result = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id  # Include document ID
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
