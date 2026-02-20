import pandas as pd
from io import BytesIO
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from models.upload import Upload
from models.financial_data import TrialBalanceEntry, GeneralLedgerEntry
import os
import xlsxwriter


UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def validate_trial_balance(df: pd.DataFrame) -> dict:
    """Validate trial balance file structure."""
    errors = []
    warnings = []

    # Check minimum required columns
    required_patterns = {
        "account_code": ["account code", "code", "acct code", "account no", "account number", "a"],
        "account_name": ["account name", "account", "name", "description", "c"],
        "debit": ["debit", "dr", "debit amount"],
        "credit": ["credit", "cr", "credit amount"],
    }

    col_mapping = {}
    normalized_cols = {str(c).strip().lower(): c for c in df.columns}

    for field, patterns in required_patterns.items():
        found = False
        for pattern in patterns:
            if pattern in normalized_cols:
                col_mapping[field] = normalized_cols[pattern]
                found = True
                break
        if not found:
            # Try partial match
            for col_lower, col_orig in normalized_cols.items():
                for pattern in patterns:
                    if pattern in col_lower or col_lower in pattern:
                        col_mapping[field] = col_orig
                        found = True
                        break
                if found:
                    break

    if "account_code" not in col_mapping and "account_name" not in col_mapping:
        errors.append("Could not identify account code or account name columns")

    # Check for balance column as alternative to debit/credit
    if "debit" not in col_mapping and "credit" not in col_mapping:
        for pattern in ["balance", "amount", "net", "total"]:
            if pattern in normalized_cols:
                col_mapping["balance"] = normalized_cols[pattern]
                break
        if "balance" not in col_mapping:
            errors.append("Could not find debit/credit or balance columns")

    # Check for empty data
    if len(df) == 0:
        errors.append("File contains no data rows")

    # Check for duplicates
    if "account_code" in col_mapping:
        dupes = df[col_mapping["account_code"]].duplicated().sum()
        if dupes > 0:
            warnings.append(f"Found {dupes} duplicate account codes")

    # Check for missing values
    for field, col in col_mapping.items():
        nulls = df[col].isnull().sum()
        if nulls > 0:
            warnings.append(f"Column '{col}' has {nulls} missing values")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "column_mapping": col_mapping,
        "row_count": len(df),
        "columns_found": list(df.columns),
    }


def parse_trial_balance(df: pd.DataFrame, col_mapping: dict) -> list[dict]:
    """Parse and standardize trial balance data."""
    entries = []

    for _, row in df.iterrows():
        entry = {
            "account_code": str(row.get(col_mapping.get("account_code", ""), "")).strip(),
            "account_name": str(row.get(col_mapping.get("account_name", ""), "")).strip(),
            "debit": 0.0,
            "credit": 0.0,
            "balance": 0.0,
        }

        if "debit" in col_mapping:
            try:
                val = row[col_mapping["debit"]]
                entry["debit"] = float(val) if pd.notna(val) else 0.0
            except (ValueError, TypeError):
                entry["debit"] = 0.0

        if "credit" in col_mapping:
            try:
                val = row[col_mapping["credit"]]
                entry["credit"] = float(val) if pd.notna(val) else 0.0
            except (ValueError, TypeError):
                entry["credit"] = 0.0

        if "balance" in col_mapping:
            try:
                val = row[col_mapping["balance"]]
                entry["balance"] = float(val) if pd.notna(val) else 0.0
            except (ValueError, TypeError):
                entry["balance"] = 0.0
        else:
            entry["balance"] = entry["debit"] - entry["credit"]

        # Skip empty rows
        if entry["account_code"] or entry["account_name"]:
            entries.append(entry)

    # Remove duplicates (keep last occurrence)
    seen = {}
    unique_entries = []
    for e in entries:
        key = e["account_code"] or e["account_name"]
        if key in seen:
            unique_entries[seen[key]] = e
        else:
            seen[key] = len(unique_entries)
            unique_entries.append(e)

    return unique_entries


def save_trial_balance_entries(db: Session, entries: list[dict], company_id: int, upload_id: int):
    """Save parsed trial balance entries to database."""
    for entry in entries:
        db_entry = TrialBalanceEntry(
            company_id=company_id,
            upload_id=upload_id,
            account_code=entry["account_code"],
            account_name=entry["account_name"],
            debit=entry["debit"],
            credit=entry["credit"],
            balance=entry["balance"],
        )
        db.add(db_entry)
    db.commit()


def generate_template() -> BytesIO:
    """Generate a downloadable trial balance template."""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})

    # Trial Balance sheet
    ws_tb = workbook.add_worksheet("Trial Balance")
    header_fmt = workbook.add_format({
        "bold": True, "bg_color": "#1a1a2e", "font_color": "#ffffff",
        "border": 1, "font_size": 12
    })
    cell_fmt = workbook.add_format({"border": 1, "font_size": 11})
    money_fmt = workbook.add_format({"border": 1, "font_size": 11, "num_format": "#,##0.00"})

    headers = ["Account Code", "Account Name", "Debit", "Credit"]
    for col, header in enumerate(headers):
        ws_tb.write(0, col, header, header_fmt)
        ws_tb.set_column(col, col, 20)

    # Sample data
    sample = [
        ["1000", "Cash and Cash Equivalents", 50000, 0],
        ["1100", "Accounts Receivable", 120000, 0],
        ["1200", "Inventory", 80000, 0],
        ["2000", "Property, Plant and Equipment", 500000, 0],
        ["3000", "Accounts Payable", 0, 95000],
        ["4000", "Long-term Borrowings", 0, 200000],
        ["5000", "Share Capital", 0, 300000],
        ["5100", "Retained Earnings", 0, 55000],
        ["6000", "Revenue", 0, 800000],
        ["7000", "Cost of Goods Sold", 480000, 0],
        ["8100", "General and Admin Expenses", 150000, 0],
        ["8200", "Depreciation Expense", 70000, 0],
    ]
    for row_idx, row_data in enumerate(sample, 1):
        ws_tb.write(row_idx, 0, row_data[0], cell_fmt)
        ws_tb.write(row_idx, 1, row_data[1], cell_fmt)
        ws_tb.write(row_idx, 2, row_data[2], money_fmt)
        ws_tb.write(row_idx, 3, row_data[3], money_fmt)

    # General Ledger sheet
    ws_gl = workbook.add_worksheet("General Ledger")
    gl_headers = ["Date", "Account Code", "Account Name", "Description", "Reference", "Debit", "Credit"]
    for col, header in enumerate(gl_headers):
        ws_gl.write(0, col, header, header_fmt)
        ws_gl.set_column(col, col, 18)

    workbook.close()
    output.seek(0)
    return output
