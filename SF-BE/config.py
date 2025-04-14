# config.py
import os
import base64
import logging
import firebase_admin
from firebase_admin import credentials, firestore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase credentials
if "FIREBASE_CREDENTIALS_BASE64" in os.environ:
    decoded = base64.b64decode(os.environ["FIREBASE_CREDENTIALS_BASE64"])
    with open("firebase_key.json", "wb") as f:
        f.write(decoded)
    cred = credentials.Certificate("firebase_key.json")
else:
    cred = credentials.Certificate("serviceAccountKey.json")  # fallback

firebase_admin.initialize_app(cred)
db = firestore.client()
