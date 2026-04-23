from fastapi import APIRouter, Depends
from auth.security import get_api_key
from auth.generate_key import generate_api_key

router = APIRouter(prefix="/api-key", tags=["API Key"])


@router.get("/generate")
async def generate_new_key():
    """Generate a new API key (for demonstration)."""
    return {"api_key": generate_api_key()}


@router.get("/verify")
async def verify_key(api_key: str = Depends(get_api_key)):
    """Verify if the provided API key is valid."""
    return {"message": "API key is valid", "status": "authenticated"}
