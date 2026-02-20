from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.upload import Upload
from services.auth_service import get_current_user
from services.upload_service import validate_trial_balance, parse_trial_balance, save_trial_balance_entries, generate_template
import pandas as pd
import os
from io import BytesIO

router = APIRouter(prefix="/api/upload", tags=["Upload"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/trial-balance")
async def upload_trial_balance(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Please create a company profile first")

    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are accepted")

    # Read file
    contents = await file.read()
    try:
        df = pd.read_excel(BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read Excel file: {str(e)}")

    # Validate
    validation = validate_trial_balance(df)

    if not validation["valid"]:
        return {
            "status": "error",
            "validation": validation,
        }

    # Save file to disk
    file_path = os.path.join(UPLOAD_DIR, f"{current_user.company_id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(contents)

    # Create upload record
    upload = Upload(
        company_id=current_user.company_id,
        filename=file.filename,
        file_type="trial_balance",
        file_path=file_path,
        status="processing",
        uploaded_by=current_user.id,
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)

    # Parse and save entries
    try:
        entries = parse_trial_balance(df, validation["column_mapping"])
        save_trial_balance_entries(db, entries, current_user.company_id, upload.id)
        upload.status = "completed"
        upload.row_count = len(entries)
        db.commit()
    except Exception as e:
        upload.status = "failed"
        upload.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    return {
        "status": "success",
        "upload_id": upload.id,
        "validation": validation,
        "entries_processed": len(entries),
    }


@router.post("/general-ledger")
async def upload_general_ledger(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="Please create a company profile first")

    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are accepted")

    contents = await file.read()
    file_path = os.path.join(UPLOAD_DIR, f"{current_user.company_id}_gl_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(contents)

    upload = Upload(
        company_id=current_user.company_id,
        filename=file.filename,
        file_type="general_ledger",
        file_path=file_path,
        status="completed",
        uploaded_by=current_user.id,
    )
    db.add(upload)
    db.commit()

    return {
        "status": "success",
        "upload_id": upload.id,
        "message": "General ledger uploaded successfully",
    }


@router.get("/template")
def download_template():
    template = generate_template()
    return StreamingResponse(
        template,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=trial_balance_template.xlsx"},
    )


@router.get("/history")
def get_upload_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.company_id:
        return []

    uploads = db.query(Upload).filter(
        Upload.company_id == current_user.company_id
    ).order_by(Upload.created_at.desc()).all()

    return [
        {
            "id": u.id,
            "filename": u.filename,
            "file_type": u.file_type,
            "status": u.status,
            "row_count": u.row_count,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in uploads
    ]
