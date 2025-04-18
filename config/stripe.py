import os
import stripe
from firebase_admin import firestore

from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")




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