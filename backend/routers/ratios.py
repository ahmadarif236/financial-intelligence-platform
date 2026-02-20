from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from services.auth_service import get_current_user
from services.ratio_service import calculate_ratios

router = APIRouter(prefix="/api/ratios", tags=["Financial Ratios"])


@router.get("/")
def get_ratios(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Please create a company and upload data first")
    return calculate_ratios(db, current_user.company_id)
