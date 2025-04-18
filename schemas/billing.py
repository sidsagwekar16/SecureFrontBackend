from pydantic import BaseModel

class CreatePortalSessionRequest(BaseModel):
    userId: str

class CreateCheckoutSessionRequest(BaseModel):
    userId: str
    additionalSites: int

class CreateSetupIntentRequest(BaseModel):
    userId: str
