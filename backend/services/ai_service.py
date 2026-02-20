import httpx
import json
from config import get_settings
from sqlalchemy.orm import Session
from services.statement_service import generate_profit_and_loss, generate_balance_sheet, generate_cash_flow
from services.ratio_service import calculate_ratios

settings = get_settings()


def build_financial_context(db: Session, company_id: int, company_name: str = "Company") -> str:
    """Build a comprehensive financial context string for the AI."""
    pnl = generate_profit_and_loss(db, company_id)
    bs = generate_balance_sheet(db, company_id)
    cf = generate_cash_flow(db, company_id)
    ratios = calculate_ratios(db, company_id)

    context = f"""
FINANCIAL DATA FOR {company_name.upper()}

=== PROFIT & LOSS STATEMENT ===
Revenue: {pnl['summary']['revenue']:,.2f}
Cost of Revenue: {pnl['summary']['cogs']:,.2f}
Gross Profit: {pnl['summary']['gross_profit']:,.2f}
Operating Expenses: {pnl['summary']['operating_expenses']:,.2f}
Operating Profit: {pnl['summary']['operating_profit']:,.2f}
EBITDA: {pnl['summary']['ebitda']:,.2f}
Net Profit: {pnl['summary']['net_profit']:,.2f}

=== BALANCE SHEET ===
Total Current Assets: {bs['summary']['total_current_assets']:,.2f}
Total Non-Current Assets: {bs['summary']['total_non_current_assets']:,.2f}
Total Assets: {bs['summary']['total_assets']:,.2f}
Total Current Liabilities: {bs['summary']['total_current_liabilities']:,.2f}
Total Non-Current Liabilities: {bs['summary']['total_non_current_liabilities']:,.2f}
Total Liabilities: {bs['summary']['total_liabilities']:,.2f}
Total Equity: {bs['summary']['total_equity']:,.2f}

=== CASH FLOW STATEMENT ===
Cash from Operations: {cf['summary']['cash_from_operations']:,.2f}
Cash from Investing: {cf['summary']['cash_from_investing']:,.2f}
Cash from Financing: {cf['summary']['cash_from_financing']:,.2f}
Net Change in Cash: {cf['summary']['net_change']:,.2f}

=== KEY FINANCIAL RATIOS ===
"""
    for category, data in ratios.items():
        context += f"\n{data['title']}:\n"
        for r in data["ratios"]:
            unit = r.get("unit", "x")
            context += f"  - {r['name']}: {r['value']}{unit} (Benchmark: {r['benchmark']}, Status: {r['status']})\n"

    return context


async def generate_commentary(db: Session, company_id: int, company_name: str = "Company") -> dict:
    """Generate AI-powered financial commentary."""
    financial_context = build_financial_context(db, company_id, company_name)

    prompt = f"""You are an expert CFO advisor specializing in GCC markets (UAE and KSA). 
Analyze the following financial data and provide a comprehensive, board-level financial commentary.

{financial_context}

Please provide your analysis in the following JSON format:
{{
    "executive_summary": "A 3-4 paragraph executive summary suitable for board presentation",
    "revenue_analysis": "Analysis of revenue and margin performance with key observations",
    "cash_flow_analysis": "Cash flow analysis highlighting operational efficiency",
    "working_capital_commentary": "Working capital management assessment",
    "risk_flags": ["List of identified risk flags as separate items"],
    "covenant_warnings": ["Any bank covenant early warning indicators"],
    "strategic_observations": ["Strategic observations and recommendations for GCC market context"],
    "overall_health": "good/warning/critical"
}}

Ensure the tone is:
- Professional and board-level
- GCC market-focused (UAE/KSA context)
- Actionable with specific recommendations
- Balanced between positive observations and areas of concern
"""

    if not settings.AI_API_KEY or settings.AI_API_KEY == "your-api-key-here":
        # Return default commentary when no AI key is configured
        return generate_default_commentary(db, company_id, company_name)

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                settings.AI_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.AI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.AI_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are an expert CFO advisor for GCC region companies. Respond only with valid JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 3000,
                },
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Parse JSON from response
            try:
                commentary = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                commentary = json.loads(content)

            return commentary

    except Exception as e:
        print(f"AI API error: {e}")
        return generate_default_commentary(db, company_id, company_name)


def generate_default_commentary(db: Session, company_id: int, company_name: str) -> dict:
    """Generate rule-based commentary when AI is not available."""
    pnl = generate_profit_and_loss(db, company_id)
    bs = generate_balance_sheet(db, company_id)
    ratios = calculate_ratios(db, company_id)

    revenue = pnl["summary"]["revenue"]
    net_profit = pnl["summary"]["net_profit"]
    gross_margin = 0
    net_margin = 0
    if revenue > 0:
        gross_margin = (pnl["summary"]["gross_profit"] / revenue) * 100
        net_margin = (net_profit / revenue) * 100

    risk_flags = []
    covenant_warnings = []
    strategic_obs = []

    # Analyze ratios for flags
    for category, data in ratios.items():
        for r in data["ratios"]:
            if r["status"] == "danger":
                risk_flags.append(f"{r['name']} at {r['value']}{r.get('unit', 'x')} is below healthy levels (benchmark: {r['benchmark']})")
            elif r["status"] == "warning":
                covenant_warnings.append(f"{r['name']} at {r['value']}{r.get('unit', 'x')} requires monitoring (benchmark: {r['benchmark']})")

    if net_margin < 5:
        risk_flags.append("Net profit margin is below 5%, indicating significant pressure on profitability")
    if bs["summary"]["total_equity"] <= 0:
        risk_flags.append("Negative equity position requires immediate attention")

    # GCC-specific observations
    strategic_obs = [
        f"Revenue stands at {revenue:,.0f}, with operations generating a gross margin of {gross_margin:.1f}%",
        "Consider UAE Corporate Tax implications (9% rate) on profitability planning",
        "Working capital management should be aligned with GCC market payment cycles (typically 60-90 days)",
    ]

    overall = "good"
    if len(risk_flags) >= 3:
        overall = "critical"
    elif len(risk_flags) >= 1 or len(covenant_warnings) >= 2:
        overall = "warning"

    return {
        "executive_summary": f"{company_name} financial review indicates a revenue base of {revenue:,.0f} with net profit of {net_profit:,.0f}, "
                              f"yielding a net margin of {net_margin:.1f}%. Total assets stand at {bs['summary']['total_assets']:,.0f} "
                              f"with an equity position of {bs['summary']['total_equity']:,.0f}. "
                              f"The company's overall financial health is assessed as '{overall}' with "
                              f"{len(risk_flags)} risk flags and {len(covenant_warnings)} areas requiring monitoring. "
                              f"Operating in the GCC market context, the company should focus on maintaining strong liquidity "
                              f"and working capital management to support growth objectives.",
        "revenue_analysis": f"Revenue of {revenue:,.0f} with gross margin of {gross_margin:.1f}% and net margin of {net_margin:.1f}%. "
                            f"EBITDA stands at {pnl['summary']['ebitda']:,.0f}, indicating the operational cash generation capacity of the business.",
        "cash_flow_analysis": "Cash flow generation should be monitored closely to ensure operational activities are self-funding. "
                              "Emphasis should be placed on collection efficiency and vendor payment optimization.",
        "working_capital_commentary": "Working capital management is critical in the GCC market given typical payment cycles. "
                                      "Focus on DSO optimization and maintaining adequate cash reserves for operations.",
        "risk_flags": risk_flags if risk_flags else ["No critical risk flags identified at this time"],
        "covenant_warnings": covenant_warnings if covenant_warnings else ["No covenant warning indicators detected"],
        "strategic_observations": strategic_obs,
        "overall_health": overall,
    }
