from sqlalchemy.orm import Session
from services.statement_service import generate_profit_and_loss, generate_balance_sheet


def calculate_ratios(db: Session, company_id: int) -> dict:
    """Calculate comprehensive financial ratios."""
    pnl = generate_profit_and_loss(db, company_id)
    bs = generate_balance_sheet(db, company_id)

    pnl_s = pnl["summary"]
    bs_s = bs["summary"]

    revenue = pnl_s.get("revenue", 0)
    cogs = pnl_s.get("cogs", 0)
    gross_profit = pnl_s.get("gross_profit", 0)
    operating_profit = pnl_s.get("operating_profit", 0)
    net_profit = pnl_s.get("net_profit", 0)
    ebitda = pnl_s.get("ebitda", 0)

    total_current_assets = bs_s.get("total_current_assets", 0)
    total_non_current_assets = bs_s.get("total_non_current_assets", 0)
    total_assets = bs_s.get("total_assets", 0)
    total_current_liabilities = bs_s.get("total_current_liabilities", 0)
    total_non_current_liabilities = bs_s.get("total_non_current_liabilities", 0)
    total_liabilities = bs_s.get("total_liabilities", 0)
    total_equity = bs_s.get("total_equity", 0)

    # Helper for safe division
    def safe_div(a, b, pct=False):
        if b == 0:
            return 0
        result = a / b
        return round(result * 100, 2) if pct else round(result, 2)

    # Estimate components (simplified from available data)
    # For a real system, these would come from detailed mapping
    inventory = 0
    receivables = 0
    payables = 0
    cash = 0
    short_term_debt = 0
    interest_expense = 0

    for section in bs["sections"]:
        for item in section.get("items", []):
            line_lower = item["line"].lower()
            if "inventor" in line_lower:
                inventory += item["amount"]
            elif "receivable" in line_lower:
                receivables += item["amount"]
            elif "payable" in line_lower:
                payables += item["amount"]
            elif "cash" in line_lower:
                cash += item["amount"]
            elif "short-term" in line_lower or "current portion" in line_lower:
                short_term_debt += item["amount"]

    for section in pnl["sections"]:
        for item in section.get("items", []):
            if "interest" in item["line"].lower() or "finance" in item["line"].lower():
                interest_expense += item["amount"]

    # Quick assets = current assets - inventory
    quick_assets = total_current_assets - inventory

    ratios = {
        "liquidity": {
            "title": "Liquidity Ratios",
            "ratios": [
                {
                    "name": "Current Ratio",
                    "value": safe_div(total_current_assets, total_current_liabilities),
                    "formula": "Current Assets / Current Liabilities",
                    "benchmark": "1.5 - 2.0",
                    "status": "good" if safe_div(total_current_assets, total_current_liabilities) >= 1.5 else "warning" if safe_div(total_current_assets, total_current_liabilities) >= 1.0 else "danger",
                },
                {
                    "name": "Quick Ratio",
                    "value": safe_div(quick_assets, total_current_liabilities),
                    "formula": "(Current Assets - Inventory) / Current Liabilities",
                    "benchmark": "1.0 - 1.5",
                    "status": "good" if safe_div(quick_assets, total_current_liabilities) >= 1.0 else "warning" if safe_div(quick_assets, total_current_liabilities) >= 0.5 else "danger",
                },
                {
                    "name": "Cash Ratio",
                    "value": safe_div(cash, total_current_liabilities),
                    "formula": "Cash / Current Liabilities",
                    "benchmark": "0.5 - 1.0",
                    "status": "good" if safe_div(cash, total_current_liabilities) >= 0.5 else "warning" if safe_div(cash, total_current_liabilities) >= 0.2 else "danger",
                },
            ]
        },
        "profitability": {
            "title": "Profitability Ratios",
            "ratios": [
                {
                    "name": "Gross Margin",
                    "value": safe_div(gross_profit, revenue, pct=True),
                    "unit": "%",
                    "formula": "Gross Profit / Revenue × 100",
                    "benchmark": "30% - 50%",
                    "status": "good" if safe_div(gross_profit, revenue, pct=True) >= 30 else "warning" if safe_div(gross_profit, revenue, pct=True) >= 15 else "danger",
                },
                {
                    "name": "EBITDA Margin",
                    "value": safe_div(ebitda, revenue, pct=True),
                    "unit": "%",
                    "formula": "EBITDA / Revenue × 100",
                    "benchmark": "15% - 25%",
                    "status": "good" if safe_div(ebitda, revenue, pct=True) >= 15 else "warning" if safe_div(ebitda, revenue, pct=True) >= 8 else "danger",
                },
                {
                    "name": "Net Margin",
                    "value": safe_div(net_profit, revenue, pct=True),
                    "unit": "%",
                    "formula": "Net Profit / Revenue × 100",
                    "benchmark": "10% - 20%",
                    "status": "good" if safe_div(net_profit, revenue, pct=True) >= 10 else "warning" if safe_div(net_profit, revenue, pct=True) >= 3 else "danger",
                },
                {
                    "name": "Return on Equity (ROE)",
                    "value": safe_div(net_profit, total_equity, pct=True),
                    "unit": "%",
                    "formula": "Net Profit / Total Equity × 100",
                    "benchmark": "15% - 25%",
                    "status": "good" if safe_div(net_profit, total_equity, pct=True) >= 15 else "warning" if safe_div(net_profit, total_equity, pct=True) >= 8 else "danger",
                },
                {
                    "name": "Return on Assets (ROA)",
                    "value": safe_div(net_profit, total_assets, pct=True),
                    "unit": "%",
                    "formula": "Net Profit / Total Assets × 100",
                    "benchmark": "5% - 15%",
                    "status": "good" if safe_div(net_profit, total_assets, pct=True) >= 5 else "warning" if safe_div(net_profit, total_assets, pct=True) >= 2 else "danger",
                },
            ]
        },
        "working_capital": {
            "title": "Working Capital Ratios",
            "ratios": [
                {
                    "name": "Days Sales Outstanding (DSO)",
                    "value": safe_div(receivables * 365, revenue),
                    "unit": "days",
                    "formula": "Receivables / Revenue × 365",
                    "benchmark": "30 - 60 days",
                    "status": "good" if safe_div(receivables * 365, revenue) <= 45 else "warning" if safe_div(receivables * 365, revenue) <= 90 else "danger",
                },
                {
                    "name": "Days Payable Outstanding (DPO)",
                    "value": safe_div(payables * 365, cogs),
                    "unit": "days",
                    "formula": "Payables / COGS × 365",
                    "benchmark": "30 - 60 days",
                    "status": "good" if safe_div(payables * 365, cogs) >= 30 else "warning",
                },
                {
                    "name": "Inventory Days",
                    "value": safe_div(inventory * 365, cogs),
                    "unit": "days",
                    "formula": "Inventory / COGS × 365",
                    "benchmark": "30 - 90 days",
                    "status": "good" if safe_div(inventory * 365, cogs) <= 60 else "warning" if safe_div(inventory * 365, cogs) <= 120 else "danger",
                },
                {
                    "name": "Cash Conversion Cycle",
                    "value": round(safe_div(receivables * 365, revenue) + safe_div(inventory * 365, cogs) - safe_div(payables * 365, cogs), 2),
                    "unit": "days",
                    "formula": "DSO + Inventory Days - DPO",
                    "benchmark": "< 60 days",
                    "status": "good" if (safe_div(receivables * 365, revenue) + safe_div(inventory * 365, cogs) - safe_div(payables * 365, cogs)) <= 60 else "warning",
                },
            ]
        },
        "leverage": {
            "title": "Leverage Ratios",
            "ratios": [
                {
                    "name": "Debt to Equity",
                    "value": safe_div(total_liabilities, total_equity),
                    "formula": "Total Liabilities / Total Equity",
                    "benchmark": "0.5 - 1.5",
                    "status": "good" if safe_div(total_liabilities, total_equity) <= 1.5 else "warning" if safe_div(total_liabilities, total_equity) <= 3 else "danger",
                },
                {
                    "name": "Interest Coverage",
                    "value": safe_div(ebitda, interest_expense) if interest_expense > 0 else 999,
                    "formula": "EBITDA / Interest Expense",
                    "benchmark": "> 3.0x",
                    "status": "good" if safe_div(ebitda, interest_expense) >= 3 or interest_expense == 0 else "warning" if safe_div(ebitda, interest_expense) >= 1.5 else "danger",
                },
            ]
        },
    }

    return ratios
