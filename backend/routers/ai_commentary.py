from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.company import Company
from services.auth_service import get_current_user
from services.ai_service import generate_commentary

router = APIRouter(prefix="/api/ai", tags=["AI Commentary"])


@router.get("/commentary")
async def get_ai_commentary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Please create a company and upload data first")

    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    company_name = company.name if company else "Company"

    commentary = await generate_commentary(db, current_user.company_id, company_name)
    return commentary
