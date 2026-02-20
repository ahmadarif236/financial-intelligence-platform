from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.company import Company
from services.auth_service import get_current_user
from services.export_service import generate_pdf_report, generate_excel_report
from services.ai_service import generate_commentary

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/pdf")
async def export_pdf(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Please create a company and upload data first")

    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    company_name = company.name if company else "Company"

    # Get AI commentary
    commentary = await generate_commentary(db, current_user.company_id, company_name)

    pdf = generate_pdf_report(db, current_user.company_id, company_name, commentary)

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={company_name}_Financial_Report.pdf"},
    )


@router.get("/excel")
def export_excel(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Please create a company and upload data first")

    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    company_name = company.name if company else "Company"

    excel = generate_excel_report(db, current_user.company_id, company_name)

    return StreamingResponse(
        excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={company_name}_Financial_Report.xlsx"},
    )
