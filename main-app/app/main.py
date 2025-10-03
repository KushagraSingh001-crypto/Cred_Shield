from fastapi import FastAPI, HTTPException
from app.schemas.intelligence import ThreatShareRequest, ThreatShareResponse
from app.blockchain.web3_client import Web3Client

app = FastAPI(title="Intelligence Sharing Service", version="1.0.0")

# Initialize Web3 client
web3_client = None

@app.on_event("startup")
async def startup_event():
    global web3_client
    try:
        web3_client = Web3Client()
        print("Web3 client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Web3 client: {e}")

@app.post("/share", response_model=ThreatShareResponse)
async def share_threat(request: ThreatShareRequest):
    """Share threat intelligence to blockchain"""
    if not web3_client:
        raise HTTPException(status_code=500, detail="Blockchain client not initialized")
    
    try:
        # Log threat to blockchain
        tx_hash, threat_id = web3_client.log_threat(request.text, request.entities)
        
        return ThreatShareResponse(
            transaction_hash=tx_hash,
            threat_id=threat_id,
            status="Successfully logged to blockchain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to share threat: {str(e)}")

@app.get("/threat/{threat_id}")
async def get_threat(threat_id: int):
    """Get threat details by ID"""
    if not web3_client:
        raise HTTPException(status_code=500, detail="Blockchain client not initialized")
    
    try:
        threat = web3_client.get_threat(threat_id)
        return threat
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Threat not found: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get blockchain statistics"""
    if not web3_client:
        raise HTTPException(status_code=500, detail="Blockchain client not initialized")
    
    try:
        threat_count = web3_client.get_threat_count()
        return {
            "total_threats": threat_count,
            "contract_address": web3_client.contract_address
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "intelligence-sharing"}