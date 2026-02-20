import json
import os
from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from models.account import MasterAccount, AccountMapping
from models.financial_data import TrialBalanceEntry


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# Keyword-based mapping rules for auto-mapping
TYPE_TO_CATEGORY = {
    "bank": {"category": "Asset", "sub_category": "Current Asset", "codes": ["1000", "1020"]},
    "cash": {"category": "Asset", "sub_category": "Current Asset", "codes": ["1000", "1010"]},
    "petty cash": {"category": "Asset", "sub_category": "Current Asset", "codes": ["1010"]},
    "accounts receivable": {"category": "Asset", "sub_category": "Current Asset", "codes": ["1100", "1110"]},
    "receivable": {"category": "Asset", "sub_category": "Current Asset", "codes": ["1100"]},
    "inventory": {"category": "Asset", "sub_category": "Current Asset", "codes": ["1200"]},
    "prepaid": {"category": "Asset", "sub_category": "Current Asset", "codes": ["1300"]},
    "fixed asset": {"category": "Asset", "sub_category": "Non-Current Asset", "codes": ["2000"]},
    "property": {"category": "Asset", "sub_category": "Non-Current Asset", "codes": ["2000"]},
    "vehicle": {"category": "Asset", "sub_category": "Non-Current Asset", "codes": ["2040"]},
    "furniture": {"category": "Asset", "sub_category": "Non-Current Asset", "codes": ["2050"]},
    "computer": {"category": "Asset", "sub_category": "Non-Current Asset", "codes": ["2060"]},
    "depreciation": {"category": "Asset", "sub_category": "Non-Current Asset", "codes": ["2070"]},
    "accumulated depreciation": {"category": "Asset", "sub_category": "Non-Current Asset", "codes": ["2070"]},
    "intangible": {"category": "Asset", "sub_category": "Non-Current Asset", "codes": ["2100"]},
    "accounts payable": {"category": "Liability", "sub_category": "Current Liability", "codes": ["3000", "3010"]},
    "payable": {"category": "Liability", "sub_category": "Current Liability", "codes": ["3000"]},
    "accrued": {"category": "Liability", "sub_category": "Current Liability", "codes": ["3020"]},
    "salary payable": {"category": "Liability", "sub_category": "Current Liability", "codes": ["3030"]},
    "vat payable": {"category": "Liability", "sub_category": "Current Liability", "codes": ["3100"]},
    "tax payable": {"category": "Liability", "sub_category": "Current Liability", "codes": ["3110"]},
    "loan": {"category": "Liability", "sub_category": "Non-Current Liability", "codes": ["4000", "4010"]},
    "borrowing": {"category": "Liability", "sub_category": "Non-Current Liability", "codes": ["4000"]},
    "end of service": {"category": "Liability", "sub_category": "Non-Current Liability", "codes": ["4100"]},
    "capital": {"category": "Equity", "sub_category": "Equity", "codes": ["5000"]},
    "retained earnings": {"category": "Equity", "sub_category": "Equity", "codes": ["5100"]},
    "reserve": {"category": "Equity", "sub_category": "Equity", "codes": ["5200"]},
    "revenue": {"category": "Revenue", "sub_category": "Operating Revenue", "codes": ["6000"]},
    "sales": {"category": "Revenue", "sub_category": "Operating Revenue", "codes": ["6010"]},
    "income": {"category": "Revenue", "sub_category": "Other Income", "codes": ["6500"]},
    "cost of goods": {"category": "Expense", "sub_category": "Cost of Sales", "codes": ["7000"]},
    "cogs": {"category": "Expense", "sub_category": "Cost of Sales", "codes": ["7000"]},
    "direct material": {"category": "Expense", "sub_category": "Cost of Sales", "codes": ["7010"]},
    "direct labor": {"category": "Expense", "sub_category": "Cost of Sales", "codes": ["7020"]},
    "selling expense": {"category": "Expense", "sub_category": "Operating Expense", "codes": ["8000"]},
    "marketing": {"category": "Expense", "sub_category": "Operating Expense", "codes": ["8020"]},
    "admin expense": {"category": "Expense", "sub_category": "Operating Expense", "codes": ["8100"]},
    "general expense": {"category": "Expense", "sub_category": "Operating Expense", "codes": ["8100"]},
    "rent expense": {"category": "Expense", "sub_category": "Operating Expense", "codes": ["8130"]},
    "utility": {"category": "Expense", "sub_category": "Operating Expense", "codes": ["8140"]},
    "depreciation expense": {"category": "Expense", "sub_category": "Operating Expense", "codes": ["8200"]},
    "interest expense": {"category": "Expense", "sub_category": "Finance Cost", "codes": ["9010"]},
    "bank charge": {"category": "Expense", "sub_category": "Finance Cost", "codes": ["9020"]},
    "tax expense": {"category": "Expense", "sub_category": "Tax", "codes": ["9100"]},
    "zakat": {"category": "Expense", "sub_category": "Tax", "codes": ["9200"]},
    "other income": {"category": "Revenue", "sub_category": "Other Income", "codes": ["6500"]},
    "other expense": {"category": "Expense", "sub_category": "Operating Expense", "codes": ["8100"]},
    "cost": {"category": "Expense", "sub_category": "Cost of Sales", "codes": ["7000"]},
    "expense": {"category": "Expense", "sub_category": "Operating Expense", "codes": ["8100"]},
}


def load_master_accounts(db: Session):
    """Load IFRS master chart of accounts into database if not already loaded."""
    existing = db.query(MasterAccount).count()
    if existing > 0:
        return

    json_path = os.path.join(DATA_DIR, "ifrs_chart_of_accounts.json")
    with open(json_path, "r") as f:
        accounts = json.load(f)

    for acc in accounts:
        db.add(MasterAccount(**acc))
    db.commit()


def find_best_match(name: str, source_type: str, master_accounts: list[MasterAccount]) -> tuple:
    """Find the best matching master account using fuzzy matching and type hints."""
    name_lower = name.lower().strip()
    type_lower = (source_type or "").lower().strip()

    # Step 1: Try exact type match from TYPE_TO_CATEGORY
    best_codes = None
    best_score = 0.0

    # Check type-based mapping first
    for keyword, mapping in TYPE_TO_CATEGORY.items():
        if keyword in type_lower or keyword in name_lower:
            score = len(keyword) / max(len(name_lower), len(type_lower), 1)
            if score > best_score or (keyword in type_lower and score >= best_score * 0.8):
                best_codes = mapping["codes"]
                best_score = max(score, 0.5)

    # Step 2: Fuzzy name matching against master accounts
    best_master = None
    best_fuzzy = 0.0

    for master in master_accounts:
        # Direct name similarity
        ratio = SequenceMatcher(None, name_lower, master.name.lower()).ratio()

        # Boost score if type matches category
        if type_lower and (type_lower in master.category.lower() or type_lower in master.sub_category.lower()):
            ratio += 0.2

        # Boost if code prefix matches
        if best_codes and master.code in best_codes:
            ratio += 0.3

        if ratio > best_fuzzy:
            best_fuzzy = ratio
            best_master = master

    # If we have type-based codes but fuzzy match was weak, use type-based
    if best_codes and best_fuzzy < 0.5:
        for master in master_accounts:
            if master.code == best_codes[0]:
                return master, max(best_score, 0.4)

    if best_master and best_fuzzy >= 0.3:
        return best_master, best_fuzzy

    return None, 0.0


def auto_map_accounts(db: Session, company_id: int) -> dict:
    """Auto-map uploaded company accounts to IFRS master chart."""
    load_master_accounts(db)

    master_accounts = db.query(MasterAccount).all()

    # Get unique accounts from trial balance
    tb_entries = db.query(
        TrialBalanceEntry.account_code,
        TrialBalanceEntry.account_name
    ).filter(
        TrialBalanceEntry.company_id == company_id
    ).distinct().all()

    # Also check existing mappings
    existing_mappings = {
        m.source_code: m for m in
        db.query(AccountMapping).filter(AccountMapping.company_id == company_id).all()
    }

    mapped = 0
    unmapped = 0
    results = []

    for code, name in tb_entries:
        if code in existing_mappings and existing_mappings[code].is_mapped:
            mapped += 1
            continue

        # Get source type from existing mapping if available
        source_type = existing_mappings[code].source_type if code in existing_mappings else ""

        best_master, confidence = find_best_match(name, source_type, master_accounts)

        if best_master and confidence >= 0.35:
            if code in existing_mappings:
                mapping = existing_mappings[code]
                mapping.master_account_id = best_master.id
                mapping.is_mapped = True
                mapping.mapped_by = "auto"
            else:
                mapping = AccountMapping(
                    company_id=company_id,
                    source_code=code,
                    source_name=name,
                    source_type=source_type,
                    master_account_id=best_master.id,
                    is_mapped=True,
                    mapped_by="auto",
                )
                db.add(mapping)
            mapped += 1
            results.append({
                "source_code": code,
                "source_name": name,
                "mapped_to": best_master.name,
                "mapped_code": best_master.code,
                "confidence": round(confidence, 2),
            })
        else:
            if code not in existing_mappings:
                mapping = AccountMapping(
                    company_id=company_id,
                    source_code=code,
                    source_name=name,
                    source_type=source_type,
                    is_mapped=False,
                )
                db.add(mapping)
            unmapped += 1
            results.append({
                "source_code": code,
                "source_name": name,
                "mapped_to": None,
                "confidence": 0,
            })

    db.commit()

    return {
        "total": len(tb_entries),
        "mapped": mapped,
        "unmapped": unmapped,
        "results": results,
    }


def manual_map_account(db: Session, mapping_id: int, master_account_id: int) -> AccountMapping:
    """Manually map an account to a master account."""
    mapping = db.query(AccountMapping).filter(AccountMapping.id == mapping_id).first()
    if not mapping:
        return None

    mapping.master_account_id = master_account_id
    mapping.is_mapped = True
    mapping.mapped_by = "manual"
    db.commit()
    db.refresh(mapping)
    return mapping


def get_mappings(db: Session, company_id: int) -> list:
    """Get all account mappings for a company."""
    mappings = db.query(AccountMapping).filter(
        AccountMapping.company_id == company_id
    ).all()

    result = []
    for m in mappings:
        master_name = None
        master_code = None
        master_category = None
        if m.master_account:
            master_name = m.master_account.name
            master_code = m.master_account.code
            master_category = m.master_account.category

        result.append({
            "id": m.id,
            "source_code": m.source_code,
            "source_name": m.source_name,
            "source_type": m.source_type,
            "master_code": master_code,
            "master_name": master_name,
            "master_category": master_category,
            "is_mapped": m.is_mapped,
            "mapped_by": m.mapped_by,
        })

    return result
