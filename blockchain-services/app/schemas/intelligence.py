from pydantic import BaseModel

class ThreatShareRequest(BaseModel):
    text: str
    entities: str

class ThreatShareResponse(BaseModel):
    transaction_hash: str
    threat_id: int
    status: str