from fastapi import APIRouter, HTTPException, Body, Query
from fastapi import Request
from datetime import datetime
import os
from config.stripe import stripe, get_stripe_customer_id
from schemas.billing import (
    CreatePortalSessionRequest,
    CreateCheckoutSessionRequest,
    CreateSetupIntentRequest,
)



router = APIRouter(prefix="/billing", tags=["Billing"])

def get_stripe_customer_id(user_id: str) -> str:
    from firebase_admin import firestore
    db = firestore.client()
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    customer_id = user_doc.to_dict().get("stripeCustomerId")
    if not customer_id:
        raise HTTPException(status_code=404, detail="Stripe customer ID not found")
    return customer_id

@router.post("/create-portal-session")
def create_portal_session(payload: CreatePortalSessionRequest):
    try:
        print("Received userId:", payload.userId)

        customer_id = get_stripe_customer_id(payload.userId)

        print("Stripe Customer ID:", customer_id)

        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url="https://yourfrontend.com/billing"
        )

        return {"url": session.url}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/create-checkout-session")
def create_checkout_session(
    userId: str = Body(...),
    additionalSites: int = Body(0)
):
    try:
        customer_id = get_stripe_customer_id(userId)

        line_items = [
            {
                "price": "price_1REugUHs9JHjI5tFuW5pKs8P",  # ✅ software subscription
                "quantity": 1
            }
        ]

        if additionalSites > 0:
            line_items.append({
                "price": "price_1REulLHs9JHjI5tFw8Qjfx5Q",  # ✅ site addon
                "quantity": additionalSites
            })

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=line_items,
            mode="subscription",
            success_url="https://yourfrontend.com/billing/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://yourfrontend.com/billing/cancel"
        )

        return {"checkoutUrl": session.url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-setup-intent")
def create_setup_intent(data: CreateSetupIntentRequest):
    try:
        customer_id = get_stripe_customer_id(data.userId)
        intent = stripe.SetupIntent.create(customer=customer_id)
        return {"clientSecret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 🔄 Handle events
    if event["type"] == "invoice.paid":
        invoice = event["data"]["object"]
        # update Firestore, mark invoice paid, etc.

    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        # update subscription status or features

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        # handle downgrade or cancellation

    return {"status": "success"}

@router.get("/invoices")
def get_invoices(userId: str = Query(...)):
    try:
        customer_id = get_stripe_customer_id(userId)
        invoices = stripe.Invoice.list(customer=customer_id, limit=10)

        return {
            "success": True,
            "invoices": [
                {
                    "id": inv.id,
                    "amount": inv.amount_paid / 100,
                    "currency": inv.currency.upper(),
                    "status": inv.status,
                    "created": datetime.fromtimestamp(inv.created).isoformat(),
                    "hosted_invoice_url": inv.hosted_invoice_url,
                    "invoice_pdf": inv.invoice_pdf
                }
                for inv in invoices.auto_paging_iter()
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")
    
@router.get("/payment-methods")
async def get_payment_methods(userId: str):
    try:
        customer_id = get_stripe_customer_id(userId)
        payment_methods = stripe.PaymentMethod.list(
            customer=customer_id,
            type="card"
        )

        return {
            "success": True,
            "methods": [
                {
                    "brand": pm.card.brand,
                    "last4": pm.card.last4,
                    "exp_month": pm.card.exp_month,
                    "exp_year": pm.card.exp_year,
                    "id": pm.id,
                    "isDefault": pm.id == stripe.Customer.retrieve(customer_id).invoice_settings.default_payment_method
                }
                for pm in payment_methods["data"]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving payment methods: {str(e)}")

@router.get("/site-usage")
def get_site_usage(userId: str = Query(...)):
    try:
        from firebase_admin import firestore
        db = firestore.client()

        # Get agencyId from user
        user_doc = db.collection("users").document(userId).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        agency_id = user_doc.to_dict().get("agencyId")

        if not agency_id:
            raise HTTPException(status_code=400, detail="User is not linked to an agency")

        # Get current assigned sites
        site_count = len(list(db.collection("sites").where("agencyId", "==", agency_id).stream()))

        # Get allowed count from billing metadata (optional)
        agency_doc = db.collection("billing").document(agency_id).get()
        allowed = agency_doc.to_dict().get("totalSites", 5) if agency_doc.exists else 5

        return {
            "success": True,
            "siteCount": site_count,
            "siteLimit": allowed
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch site usage: {str(e)}")


@router.post("/purchase-site")
def purchase_site(userId: str = Body(...), quantity: int = Body(...)):
    try:
        customer_id = get_stripe_customer_id(userId)

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": os.getenv("STRIPE_ADDITIONAL_SITE_PRICE_ID"),  # should be $50/mo
                "quantity": quantity
            }],
            mode="subscription",
            success_url="https://yourfrontend.com/dashboard/billing?success=true",
            cancel_url="https://yourfrontend.com/dashboard/billing?cancel=true"
        )

        return {"success": True, "checkoutUrl": session.url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start site purchase: {str(e)}")


@router.get("/billing/subscription-status")
async def subscription_status(userId: str = Query(...)):
    # your existing logic using userId

    try:
        customer_id = get_stripe_customer_id(userId)

        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status="all",
            limit=1
        )

        if not subscriptions.data:
            return {
                "subscribed": False,
                "planName": None,
                "renewalDate": None
            }

        subscription = subscriptions.data[0]

        if subscription.status not in ["active", "trialing"]:
            return {
                "subscribed": False,
                "planName": None,
                "renewalDate": None
            }

        plan_name = subscription["items"]["data"][0]["price"].get("nickname", "Professional")
        renewal_date = datetime.fromtimestamp(subscription.current_period_end).isoformat()

        return {
            "subscribed": True,
            "planName": plan_name,
            "renewalDate": renewal_date
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch subscription status: {str(e)}")