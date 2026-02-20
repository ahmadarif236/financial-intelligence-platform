from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from services.auth_service import get_current_user
from services.statement_service import generate_profit_and_loss, generate_balance_sheet, generate_cash_flow

router = APIRouter(prefix="/api/statements", tags=["Financial Statements"])


@router.get("/profit-loss")
def get_profit_loss(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Please create a company and upload data first")
    return generate_profit_and_loss(db, current_user.company_id)


@router.get("/balance-sheet")
def get_balance_sheet(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Please create a company and upload data first")
    return generate_balance_sheet(db, current_user.company_id)


@router.get("/cash-flow")
def get_cash_flow(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Please create a company and upload data first")
    return generate_cash_flow(db, current_user.company_id)


@router.get("/all")
def get_all_statements(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Please create a company and upload data first")
    return {
        "profit_loss": generate_profit_and_loss(db, current_user.company_id),
        "balance_sheet": generate_balance_sheet(db, current_user.company_id),
        "cash_flow": generate_cash_flow(db, current_user.company_id),
    }
