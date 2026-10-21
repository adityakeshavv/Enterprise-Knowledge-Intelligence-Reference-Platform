import os
from pathlib import Path
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from PIL import Image, ImageDraw, ImageFont

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "config" / "industries" / "manufacturing" / "data" / "unstructured"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def generate_excel_logs():
    xlsx_path = DATA_DIR / "Plant_A_Shift_Incident_Logs_Q1.xlsx"
    wb = openpyxl.Workbook()
    
    # Sheet 1: Shift_Incidents
    ws1 = wb.active
    ws1.title = "Shift_Incidents"
    headers1 = ["Incident_ID", "Date", "Shift", "Line_ID", "Equipment", "Failure_Description", "Action_Taken", "Technician"]
    ws1.append(headers1)
    
    # Style header
    header_fill = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    for col in range(1, len(headers1) + 1):
        cell = ws1.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font

    incidents = [
        ["INC-101", "2024-03-02", "Shift 1", "Line_3_Assembly", "Hydraulic Pump Unit 2", "Fluid pressure oscillation observed. Minor vibration in return valve.", "Adjusted pressure regulator to 160 bar. Monitored for 2 hours.", "Tech-409"],
        ["INC-102", "2024-03-08", "Shift 2", "Line_3_Assembly", "Hydraulic Pump Unit 2", "Severe pump cavitation and high-frequency screech. Oil temperature reached 78C.", "Emergency shutdown. Inspected seal housing. Found cracking on primary ring.", "Tech-112"],
        ["INC-103", "2024-03-10", "Shift 1", "Line_3_Assembly", "Hydraulic Pump Unit 2", "Replaced defective hydraulic seal with new inventory batch AFD-SEAL-882. Line test passed.", "Seal replaced. Pump refilled with standard hydraulic oil ISO-VG-46.", "Tech-409"],
        ["INC-104", "2024-03-14", "Shift 3", "Line_3_Assembly", "Hydraulic Pump Unit 2", "Unplanned stoppage ERR-HYD-401. Seal blowout occurred during high-pressure run.", "Isolated pump. Initiated root cause investigation. Suspected component material flaw.", "Tech-303"],
        ["INC-105", "2024-03-18", "Shift 1", "Line_1_Stamping", "Mechanical Press 4", "Electrical relay chatter on contactor C2.", "Cleaned contact points and verified voltage drop.", "Tech-202"],
    ]
    for row in incidents:
        ws1.append(row)

    # Sheet 2: Component_Inventory
    ws2 = wb.create_sheet(title="Component_Replacements")
    headers2 = ["Work_Order", "Date", "Part_Number", "Supplier", "Batch_Code", "Cost_USD", "Lifespan_Hours"]
    ws2.append(headers2)
    for col in range(1, len(headers2) + 1):
        cell = ws2.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font

    replacements = [
        ["WO-8910", "2024-03-10", "AFD-SEAL-882", "Apex Fluid Dynamics", "BATCH-APEX-24Q1-A", 14200.00, 180],
        ["WO-8944", "2024-03-15", "VORT-VALVE-12", "Vortex Precision Pumps", "BATCH-VORTEX-24Q1", 8500.00, 2400],
        ["WO-9012", "2024-03-21", "REL-ABB-102", "ABB Components", "BATCH-ABB-991", 2300.00, 8500],
    ]
    for row in replacements:
        ws2.append(row)

    wb.save(xlsx_path)
    print(f"Generated: {xlsx_path}")

def generate_sop_pdf():
    pdf_path = DATA_DIR / "SOP-Maint-Line3-Hydraulics-v2.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#1E3A8A'))
    h2_style = ParagraphStyle(name='H2Style', parent=styles['Heading2'], fontSize=13, leading=16, textColor=colors.HexColor('#1F2937'), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle(name='BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#374151'), spaceAfter=8)
    callout_style = ParagraphStyle(name='Callout', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#1E40AF'), backColor=colors.HexColor('#EFF6FF'), borderPadding=6, spaceAfter=10)

    story = []

    # Page 1
    story.append(Paragraph("STANDARD OPERATING PROCEDURE: HYDRAULIC SYSTEM MAINTENANCE", title_style))
    story.append(Paragraph("Document ID: SOP-Maint-Line3-Hydraulics-v2 | Department: Reliability Engineering | Plant A", body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Section 1.0 — Purpose & Operational Scope", h2_style))
    story.append(Paragraph("This procedure establishes mandatory preventive maintenance and fluid replenishment standards for high-pressure hydraulic pumps on Line 3 Assembly. Compliance is mandatory for all reliability technicians.", body_style))

    story.append(Paragraph("Section 2.0 — Safety Protocols & Pressure Depressurization", h2_style))
    story.append(Paragraph("Before servicing pump assemblies, technicians must execute Lockout/Tagout (LOTO) Protocol 4. Ensure reservoir pressure is fully vented to 0 bar via the primary manual relief valve.", body_style))

    story.append(Spacer(1, 200))
    story.append(PageBreak())

    # Page 2
    story.append(Paragraph("Section 3.0 — Wear Inspection & Seal Tolerances", h2_style))
    story.append(Paragraph("High-pressure elastomer seals (Part AFD-SEAL-882) must be inspected for thermal micro-fissures and durometer degradation. Any seal showing radial cracking must be replaced immediately.", body_style))

    story.append(Paragraph("Section 4.0 — Fluid Evacuation & Flush Protocols", h2_style))
    story.append(Paragraph("Hydraulic fluid degradation is the primary driver of premature seal blowout and pump cavitation. Standard mineral oils oxidize rapidly under peak assembly cycles.", body_style))

    story.append(Paragraph("Section 4.2 — Mandatory Synthetic Oil Flush Intervals", h2_style))
    story.append(Paragraph("<b>Crucial Preventive Measure:</b> Pumps operating above 180 bar must undergo complete fluid evacuation and replenishment with high-grade synthetic ester hydraulic fluid every <b>250 operational hours</b>. Historical telemetry demonstrates that implementing quarterly synthetic flushes reduced similar pump cavitation and seal breakdown downtime by <b>41% during 2023</b>.", callout_style))

    doc.build(story)
    print(f"Generated: {pdf_path}")

def generate_supplier_bulletin_pdf():
    pdf_path = DATA_DIR / "Supplier_Quality_Bulletin_Apex_2024.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#DC2626'))
    body_style = ParagraphStyle(name='BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#1F2937'), spaceAfter=8)

    story = [
        Paragraph("SUPPLIER QUALITY ADVISORY & RECALL NOTICE", title_style),
        Paragraph("Issuing Vendor: Apex Fluid Dynamics Inc. | Bulletin Ref: APX-QB-2024-03", body_style),
        Spacer(1, 10),
        Paragraph("<b>Subject:</b> Premature Degradation in High-Pressure Seal Batch <b>BATCH-APEX-24Q1-A</b> (Part AFD-SEAL-882)", body_style),
        Paragraph("Apex Fluid Dynamics has identified a curing inconsistency in nitrile elastomer batches dispatched between January 15, 2024 and March 1, 2024. Affected seals exhibit an elevated defect rate of <b>1,850 PPM</b>, leading to micro-tearing at pressures exceeding 175 bar.", body_style),
        Paragraph("<b>Corrective Recommendation:</b> Customers utilizing batch BATCH-APEX-24Q1-A on continuous assembly lines should quarantine uninstalled inventory and replace installed seals during next scheduled shift downtime.", body_style)
    ]
    doc.build(story)
    print(f"Generated: {pdf_path}")

def generate_ocr_scan_image():
    img_path = DATA_DIR / "Inspection_Scan_Pump_Seal.png"
    # Create white canvas
    img = Image.new('RGB', (850, 450), color=(250, 250, 248))
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((40, 30), "PLANT A - RELIABILITY INSPECTION FORM", fill=(20, 20, 20))
    draw.line([(40, 50), (810, 50)], fill=(100, 100, 100), width=2)

    # Fields
    draw.text((40, 70), "Date: 2024-03-10   |   Shift: 1   |   Technician: Tech-409 (Marcus Vance)", fill=(40, 40, 40))
    draw.text((40, 100), "Equipment: Line 3 Assembly - Main Hydraulic Pump Unit 2", fill=(40, 40, 40))
    draw.text((40, 130), "Component Serviced: High-Pressure Seal (AFD-SEAL-882)", fill=(40, 40, 40))
    draw.text((40, 160), "Inspection Notes: Primary seal replaced. Pre-test torque verified to 125 Nm.", fill=(40, 40, 40))
    draw.text((40, 190), "Cavitation Check: Normal audible pump frequency. No visible oil leakage.", fill=(40, 40, 40))
    draw.text((40, 220), "Status: SIGNED OFF AND CLEARED FOR PRODUCTION - MARCH 10", fill=(20, 20, 20))

    # Stamp box (Red)
    draw.rectangle([(550, 260), (780, 350)], outline=(180, 20, 20), width=3)
    draw.text((580, 280), "MAINTENANCE VERIFIED", fill=(180, 20, 20))
    draw.text((590, 305), "STAMP #409 - PASSED", fill=(180, 20, 20))
    draw.text((610, 325), "DATE: 2024-03-10", fill=(180, 20, 20))

    img.save(img_path)
    print(f"Generated: {img_path}")

if __name__ == "__main__":
    generate_excel_logs()
    generate_sop_pdf()
    generate_supplier_bulletin_pdf()
    generate_ocr_scan_image()
