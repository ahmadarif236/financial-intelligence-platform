from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
import xlsxwriter
from sqlalchemy.orm import Session
from services.statement_service import generate_profit_and_loss, generate_balance_sheet, generate_cash_flow
from services.ratio_service import calculate_ratios


def generate_pdf_report(db: Session, company_id: int, company_name: str, commentary: dict = None) -> BytesIO:
    """Generate a board-ready PDF report."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=22,
                                  textColor=colors.HexColor("#0f172a"), spaceAfter=20)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14,
                                    textColor=colors.HexColor("#1e40af"), spaceBefore=15, spaceAfter=10)
    body_style = ParagraphStyle('CustomBody', parent=styles['Normal'], fontSize=10,
                                 spaceAfter=8, leading=14)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=11,
                                     textColor=colors.HexColor("#64748b"), spaceAfter=15)

    elements = []

    # Title
    elements.append(Paragraph(f"Financial Intelligence Report", title_style))
    elements.append(Paragraph(f"{company_name}", subtitle_style))
    elements.append(HRFlowable(width="100%", color=colors.HexColor("#1e40af"), thickness=2))
    elements.append(Spacer(1, 20))

    # Financial Statements
    pnl = generate_profit_and_loss(db, company_id)
    bs = generate_balance_sheet(db, company_id)
    cf = generate_cash_flow(db, company_id)
    ratios = calculate_ratios(db, company_id)

    # P&L Section
    elements.append(Paragraph("Profit & Loss Statement", heading_style))
    pnl_data = [["Line Item", "Amount"]]
    for section in pnl["sections"]:
        if section.get("is_subtotal"):
            pnl_data.append([f"<b>{section['name']}</b>", f"<b>{section['total']:,.2f}</b>"])
        else:
            for item in section.get("items", []):
                pnl_data.append([f"  {item['line']}", f"{item['amount']:,.2f}"])
            if section["items"]:
                pnl_data.append([f"Total {section['name']}", f"{section['total']:,.2f}"])

    if pnl_data:
        table = Table(pnl_data, colWidths=[350, 150])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e40af")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(table)

    elements.append(Spacer(1, 20))

    # Balance Sheet Section
    elements.append(Paragraph("Balance Sheet", heading_style))
    bs_data = [["Line Item", "Amount"]]
    for section in bs["sections"]:
        if section.get("is_subtotal"):
            bs_data.append([f"<b>{section['name']}</b>", f"<b>{section['total']:,.2f}</b>"])
        else:
            for item in section.get("items", []):
                bs_data.append([f"  {item['line']}", f"{item['amount']:,.2f}"])
            if section["items"]:
                bs_data.append([f"Total {section['name']}", f"{section['total']:,.2f}"])

    if bs_data:
        table = Table(bs_data, colWidths=[350, 150])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e40af")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(table)

    elements.append(Spacer(1, 20))

    # Ratios Section
    elements.append(Paragraph("Financial Ratios", heading_style))
    for category, data in ratios.items():
        elements.append(Paragraph(data["title"], ParagraphStyle('RatioTitle', parent=styles['Normal'],
                                                                  fontSize=11, spaceBefore=8, spaceAfter=4,
                                                                  textColor=colors.HexColor("#334155"))))
        ratio_data = [["Ratio", "Value", "Benchmark", "Status"]]
        for r in data["ratios"]:
            unit = r.get("unit", "x")
            status_color = "🟢" if r["status"] == "good" else "🟡" if r["status"] == "warning" else "🔴"
            ratio_data.append([r["name"], f"{r['value']}{unit}", r["benchmark"], r["status"].upper()])

        table = Table(ratio_data, colWidths=[180, 80, 120, 80])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#475569")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 8))

    # AI Commentary Section
    if commentary:
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("AI CFO Commentary", heading_style))

        if commentary.get("executive_summary"):
            elements.append(Paragraph("Executive Summary", ParagraphStyle('CommentTitle', parent=styles['Normal'],
                                                                           fontSize=11, spaceBefore=8, spaceAfter=4,
                                                                           textColor=colors.HexColor("#1e40af"))))
            elements.append(Paragraph(commentary["executive_summary"], body_style))

        if commentary.get("risk_flags"):
            elements.append(Paragraph("Risk Flags", ParagraphStyle('RiskTitle', parent=styles['Normal'],
                                                                     fontSize=11, spaceBefore=8, spaceAfter=4,
                                                                     textColor=colors.HexColor("#dc2626"))))
            for flag in commentary["risk_flags"]:
                elements.append(Paragraph(f"⚠ {flag}", body_style))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_excel_report(db: Session, company_id: int, company_name: str) -> BytesIO:
    """Generate Excel report with all financial data."""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})

    # Formats
    title_fmt = workbook.add_format({
        "bold": True, "font_size": 16, "font_color": "#1e40af",
        "bottom": 2, "bottom_color": "#1e40af"
    })
    header_fmt = workbook.add_format({
        "bold": True, "bg_color": "#1e40af", "font_color": "#ffffff",
        "border": 1, "font_size": 11
    })
    subtotal_fmt = workbook.add_format({
        "bold": True, "bg_color": "#e2e8f0", "border": 1,
        "font_size": 11, "num_format": "#,##0.00"
    })
    cell_fmt = workbook.add_format({"border": 1, "font_size": 10})
    money_fmt = workbook.add_format({"border": 1, "font_size": 10, "num_format": "#,##0.00"})

    pnl = generate_profit_and_loss(db, company_id)
    bs = generate_balance_sheet(db, company_id)
    cf = generate_cash_flow(db, company_id)
    ratios = calculate_ratios(db, company_id)

    # P&L Sheet
    ws = workbook.add_worksheet("Profit & Loss")
    ws.set_column(0, 0, 40)
    ws.set_column(1, 1, 20)
    ws.write(0, 0, f"Profit & Loss - {company_name}", title_fmt)
    row = 2
    ws.write(row, 0, "Line Item", header_fmt)
    ws.write(row, 1, "Amount", header_fmt)
    row += 1
    for section in pnl["sections"]:
        if section.get("is_subtotal"):
            ws.write(row, 0, section["name"], subtotal_fmt)
            ws.write(row, 1, section["total"], subtotal_fmt)
        else:
            for item in section.get("items", []):
                ws.write(row, 0, f"  {item['line']}", cell_fmt)
                ws.write(row, 1, item["amount"], money_fmt)
                row += 1
            ws.write(row, 0, f"Total {section['name']}", subtotal_fmt)
            ws.write(row, 1, section["total"], subtotal_fmt)
        row += 1

    # Balance Sheet
    ws2 = workbook.add_worksheet("Balance Sheet")
    ws2.set_column(0, 0, 40)
    ws2.set_column(1, 1, 20)
    ws2.write(0, 0, f"Balance Sheet - {company_name}", title_fmt)
    row = 2
    ws2.write(row, 0, "Line Item", header_fmt)
    ws2.write(row, 1, "Amount", header_fmt)
    row += 1
    for section in bs["sections"]:
        if section.get("is_subtotal"):
            ws2.write(row, 0, section["name"], subtotal_fmt)
            ws2.write(row, 1, section["total"], subtotal_fmt)
        else:
            for item in section.get("items", []):
                ws2.write(row, 0, f"  {item['line']}", cell_fmt)
                ws2.write(row, 1, item["amount"], money_fmt)
                row += 1
            ws2.write(row, 0, f"Total {section['name']}", subtotal_fmt)
            ws2.write(row, 1, section["total"], subtotal_fmt)
        row += 1

    # Ratios Sheet
    ws3 = workbook.add_worksheet("Financial Ratios")
    ws3.set_column(0, 0, 30)
    ws3.set_column(1, 4, 20)
    ws3.write(0, 0, "Financial Ratios", title_fmt)
    row = 2
    for category, data in ratios.items():
        ws3.write(row, 0, data["title"], header_fmt)
        ws3.write(row, 1, "Value", header_fmt)
        ws3.write(row, 2, "Benchmark", header_fmt)
        ws3.write(row, 3, "Status", header_fmt)
        row += 1
        for r in data["ratios"]:
            unit = r.get("unit", "x")
            ws3.write(row, 0, r["name"], cell_fmt)
            ws3.write(row, 1, f"{r['value']}{unit}", cell_fmt)
            ws3.write(row, 2, r["benchmark"], cell_fmt)
            ws3.write(row, 3, r["status"].upper(), cell_fmt)
            row += 1
        row += 1

    workbook.close()
    output.seek(0)
    return output
