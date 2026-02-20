from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
from models.account import MasterAccount
from services.auth_service import get_current_user
from services.mapping_service import auto_map_accounts, manual_map_account, get_mappings

router = APIRouter(prefix="/api/mapping", tags=["Account Mapping"])


class ManualMapRequest(BaseModel):
    mapping_id: int
    master_account_id: int


@router.post("/auto-map")
def run_auto_mapping(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Please create a company profile first")

    result = auto_map_accounts(db, current_user.company_id)
    return result


@router.post("/manual-map")
def run_manual_mapping(
    req: ManualMapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mapping = manual_map_account(db, req.mapping_id, req.master_account_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")

    return {"status": "success", "mapping_id": mapping.id}


@router.get("/")
def get_account_mappings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.company_id:
        return []
    return get_mappings(db, current_user.company_id)


@router.get("/master-accounts")
def get_master_accounts(db: Session = Depends(get_db)):
    accounts = db.query(MasterAccount).order_by(MasterAccount.code).all()
    return [
        {
            "id": a.id,
            "code": a.code,
            "name": a.name,
            "category": a.category,
            "sub_category": a.sub_category,
        }
        for a in accounts
    ]
