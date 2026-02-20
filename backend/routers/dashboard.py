from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.company import Company
from services.auth_service import get_current_user
from services.statement_service import generate_profit_and_loss, generate_balance_sheet, generate_cash_flow
from services.ratio_service import calculate_ratios

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/")
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.company_id:
        return {
            "has_data": False,
            "company": None,
            "kpis": {},
        }

    company = db.query(Company).filter(Company.id == current_user.company_id).first()

    try:
        pnl = generate_profit_and_loss(db, current_user.company_id)
        bs = generate_balance_sheet(db, current_user.company_id)
        cf = generate_cash_flow(db, current_user.company_id)
        ratios = calculate_ratios(db, current_user.company_id)

        # Extract cash position
        cash = 0
        for section in bs["sections"]:
            for item in section.get("items", []):
                if "cash" in item["line"].lower():
                    cash += item["amount"]

        # Calculate net debt
        total_debt = bs["summary"]["total_liabilities"]
        net_debt = total_debt - cash

        # Working capital
        working_capital = bs["summary"]["total_current_assets"] - bs["summary"]["total_current_liabilities"]

        # CCC from ratios
        ccc = 0
        if "working_capital" in ratios:
            for r in ratios["working_capital"]["ratios"]:
                if r["name"] == "Cash Conversion Cycle":
                    ccc = r["value"]

        kpis = {
            "revenue": pnl["summary"]["revenue"],
            "ebitda": pnl["summary"]["ebitda"],
            "net_profit": pnl["summary"]["net_profit"],
            "cash_position": cash,
            "net_debt": net_debt,
            "working_capital": working_capital,
            "cash_conversion_cycle": ccc,
            "gross_margin": round((pnl["summary"]["gross_profit"] / pnl["summary"]["revenue"] * 100) if pnl["summary"]["revenue"] else 0, 1),
            "net_margin": round((pnl["summary"]["net_profit"] / pnl["summary"]["revenue"] * 100) if pnl["summary"]["revenue"] else 0, 1),
            "total_assets": bs["summary"]["total_assets"],
            "total_equity": bs["summary"]["total_equity"],
        }

        return {
            "has_data": True,
            "company": {
                "id": company.id,
                "name": company.name,
                "country": company.country,
                "currency": company.currency,
            } if company else None,
            "kpis": kpis,
        }

    except Exception as e:
        return {
            "has_data": False,
            "company": {
                "id": company.id,
                "name": company.name,
                "country": company.country,
                "currency": company.currency,
            } if company else None,
            "kpis": {},
            "error": str(e),
        }
