from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.schemas.auth import SignupRequest
from src.database import get_db
from src.services.user_service import create_user_with_confirmation

router = APIRouter()

@router.post("/signup")
async def signup(signup_request: SignupRequest, db: Session = Depends(get_db)):
    try:
        # Assuming create_user_with_confirmation should take db and signup_request
        user, confirmation_link = create_user_with_confirmation(db, signup_request)
        return {"user": user, "confirmation_link": confirmation_link}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
