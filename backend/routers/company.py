from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
from models.company import Company
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/company", tags=["Company"])


class CompanyCreate(BaseModel):
    name: str
    country: str = "UAE"
    industry: str | None = None
    currency: str = "AED"
    fiscal_year_end: str = "December"
    tax_registration: str | None = None
    address: str | None = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    country: str
    industry: str | None
    currency: str
    fiscal_year_end: str
    tax_registration: str | None
    address: str | None


@router.post("/", response_model=CompanyResponse)
def create_company(req: CompanyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    company = Company(**req.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)

    # Assign company to user
    current_user.company_id = company.id
    db.commit()

    return company


@router.get("/", response_model=CompanyResponse | None)
def get_company(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.company_id:
        return None
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    return company


@router.put("/", response_model=CompanyResponse)
def update_company(req: CompanyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.company_id:
        raise HTTPException(status_code=404, detail="No company found. Create one first.")

    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    for key, value in req.model_dump().items():
        setattr(company, key, value)

    db.commit()
    db.refresh(company)
    return company
