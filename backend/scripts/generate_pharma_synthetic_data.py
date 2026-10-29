import os
from pathlib import Path
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "config" / "industries" / "pharma" / "data" / "unstructured"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def generate_pharma_excel():
    xlsx_path = DATA_DIR / "Pharma_Batch_Analytical_Testing_Q1.xlsx"
    wb = openpyxl.Workbook()

    # Sheet 1: Batch_Analytical_Release
    ws1 = wb.active
    ws1.title = "Batch_Release_Testing"
    headers1 = [
        "Batch_ID", "Drug_Name", "Manufacturing_Date", "Lot_Size_Kg",
        "Purity_HPLC_Pct", "Dissolution_30min_Pct", "Microbial_Limit_CFU",
        "Assay_Specification", "Quality_Decision", "QA_Officer"
    ]
    ws1.append(headers1)

    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    for col in range(1, len(headers1) + 1):
        cell = ws1.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font

    batches = [
        ["LOT-4890-CV", "CardioVastin 20mg", "2026-01-10", 250.0, 99.4, 91.2, 8, "Pass cGMP Spec", "RELEASED", "Dr. A. Chen"],
        ["LOT-4891-CV", "CardioVastin 20mg", "2026-02-14", 250.0, 99.2, 88.5, 12, "Pass cGMP Spec (Purity >= 98.5%, Dissolution >= 85%)", "RELEASED", "Dr. A. Chen"],
        ["LOT-4892-CV", "CardioVastin 20mg", "2026-03-01", 250.0, 97.8, 79.4, 140, "FAIL (Low Purity & Microbial Out of Spec)", "QUARANTINED_REJECTED", "Dr. M. Kowalski"],
        ["LOT-4893-CV", "CardioVastin 20mg", "2026-03-18", 250.0, 99.5, 93.0, 6, "Pass cGMP Spec", "RELEASED", "Dr. A. Chen"],
    ]
    for row in batches:
        ws1.append(row)

    # Sheet 2: Adverse_Event_Log
    ws2 = wb.create_sheet(title="Clinical_Safety_Reports")
    headers2 = ["Report_ID", "Trial_ID", "Subject_ID", "Reaction", "Severity", "Seriousness", "Report_Date", "Days_To_Notify_FDA"]
    ws2.append(headers2)
    for col in range(1, len(headers2) + 1):
        cell = ws2.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font

    safety_events = [
        ["AER-2026-001", "NCT-04829102", "SUBJ-104", "Transient headache", "Mild", "No", "2026-01-15", 3],
        ["AER-2026-002", "NCT-04829102", "SUBJ-219", "Mild nausea", "Mild", "No", "2026-01-22", 4],
        ["AER-2026-003", "NCT-04829102", "SUBJ-382", "Elevated Liver ALT (>3x ULN)", "Moderate", "No", "2026-02-05", 5],
        ["AER-2026-004", "NCT-04829102", "SUBJ-512", "Atrial Fibrillation with Hospitalization", "Severe", "Yes (SAE)", "2026-02-18", 8],
        ["AER-2026-005", "NCT-04829102", "SUBJ-789", "Myalgia and muscle tenderness", "Moderate", "No", "2026-03-02", 4],
    ]
    for row in safety_events:
        ws2.append(row)

    wb.save(xlsx_path)
    print(f"Generated: {xlsx_path}")

def generate_trial_protocol_pdf():
    pdf_path = DATA_DIR / "Clinical_Trial_Protocol_CardioVastin_PH3.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#0F172A'))
    h2_style = ParagraphStyle(name='H2Style', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#1E3A8A'), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle(name='BodyStyle', parent=styles['Normal'], fontSize=9.5, leading=13.5, textColor=colors.HexColor('#334155'), spaceAfter=8)
    callout_style = ParagraphStyle(name='Callout', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#065F46'), backColor=colors.HexColor('#ECFDF5'), borderPadding=6, spaceAfter=8)

    story = []

    # Page 1
    story.append(Paragraph("CLINICAL STUDY PROTOCOL: CARDIOVASTIN PHASE 3 (CV-301)", title_style))
    story.append(Paragraph("Protocol ID: CV-301-PH3 | Investigational Product: CardioVastin (20 mg oral daily) | NCT-04829102", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Section 1.0 — Study Rationale & Objectives", h2_style))
    story.append(Paragraph("CardioVastin is a novel synthetic small-molecule dual PCSK9/HMG-CoA inhibitor designed to lower low-density lipoprotein cholesterol (LDL-C) and attenuate coronary plaque progression in high-risk atherosclerotic cardiovascular disease (ASCVD) patients.", body_style))

    story.append(Paragraph("Section 2.0 — Study Population & Randomization", h2_style))
    story.append(Paragraph("The trial randomized <b>1,200 adult patients</b> across 48 clinical investigation centers in a 1:1 double-blind fashion to either CardioVastin 20 mg once daily (N=600) or matching placebo (N=600) for a 24-week treatment period.", body_style))

    story.append(Spacer(1, 150))
    story.append(PageBreak())

    # Page 2
    story.append(Paragraph("Section 3.0 — Primary Efficacy Endpoint", h2_style))
    story.append(Paragraph("<b>Primary Endpoint Definition:</b> The primary efficacy endpoint was the percentage change in serum LDL-C concentration from baseline to Week 24.", body_style))
    story.append(Paragraph("<b>Trial Primary Efficacy Results:</b> CardioVastin achieved a statistically significant <b>48.4% mean reduction in LDL-C at Week 24</b> (p &lt; 0.001 versus placebo). Placebo demonstrated a 1.2% reduction. The primary efficacy endpoint was formally met across all pre-specified patient subgroups.", callout_style))

    story.append(Paragraph("Section 4.0 — Safety Tolerability & Adverse Events Profile", h2_style))
    story.append(Paragraph("Overall incidence of treatment-emergent adverse events (TEAEs) was <b>3.8%</b> in the CardioVastin arm versus 3.2% in the placebo group. The most commonly reported events were transient headache (1.4%), mild elevated liver transaminases (ALT/AST &gt; 3x ULN, 0.8%), and myalgia (0.6%). Discontinuation due to adverse events was low at 1.1%.", body_style))

    doc.build(story)
    print(f"Generated: {pdf_path}")

def generate_fda_approval_pdf():
    pdf_path = DATA_DIR / "FDA_Regulatory_Approval_Summary_CardioVastin.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Heading1'], fontSize=15, leading=19, textColor=colors.HexColor('#0F172A'))
    h2_style = ParagraphStyle(name='H2Style', parent=styles['Heading2'], fontSize=11.5, leading=15, textColor=colors.HexColor('#1E3A8A'), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle(name='BodyStyle', parent=styles['Normal'], fontSize=9.5, leading=13.5, textColor=colors.HexColor('#334155'), spaceAfter=8)
    callout_style = ParagraphStyle(name='Callout', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#1E40AF'), backColor=colors.HexColor('#EFF6FF'), borderPadding=6, spaceAfter=8)

    story = []

    story.append(Paragraph("US FOOD & DRUG ADMINISTRATION (FDA) — SUMMARY BASIS OF APPROVAL", title_style))
    story.append(Paragraph("Center for Drug Evaluation and Research (CDER) | Application Number: NDA 218492 | Drug: CardioVastin", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. Executive Regulatory Action Summary", h2_style))
    story.append(Paragraph("The FDA has granted formal marketing approval for <b>CardioVastin (20 mg oral film-coated tablets)</b> as an adjunct to diet alone or in combination with statins for adults with primary hyperlipidemia and established atherosclerotic cardiovascular disease.", body_style))

    story.append(Paragraph("2. Clinical Evidence Verification", h2_style))
    story.append(Paragraph("Approval is grounded in pivotal Phase 3 Study CV-301 (N=1,200), demonstrating a robust <b>48.4% reduction in LDL-C</b> (p &lt; 0.0001) and statistically significant reductions in Apolipoprotein B (-39.2%) and non-HDL-C (-44.1%).", body_style))

    story.append(Paragraph("3. Post-Marketing Commitments & Pediatric Exemption", h2_style))
    story.append(Paragraph("The sponsor must conduct a post-approval 5-year Major Adverse Cardiovascular Events (MACE) cardiovascular outcomes trial (CVOT). No Boxed Warning (Black Box) was required by CDER due to favorable hepatic and renal safety profiles.", callout_style))

    doc.build(story)
    print(f"Generated: {pdf_path}")

def generate_pv_sop_pdf():
    pdf_path = DATA_DIR / "SOP-PV-042_Adverse_Event_Reporting_Triage.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Heading1'], fontSize=15, leading=19, textColor=colors.HexColor('#0F172A'))
    h2_style = ParagraphStyle(name='H2Style', parent=styles['Heading2'], fontSize=11.5, leading=15, textColor=colors.HexColor('#991B1B'), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle(name='BodyStyle', parent=styles['Normal'], fontSize=9.5, leading=13.5, textColor=colors.HexColor('#334155'), spaceAfter=8)
    warning_style = ParagraphStyle(name='Warning', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#991B1B'), backColor=colors.HexColor('#FEF2F2'), borderPadding=6, spaceAfter=8)

    story = []

    story.append(Paragraph("STANDARD OPERATING PROCEDURE: GLOBAL PHARMACOVIGILANCE & SAFETY TRIAGE", title_style))
    story.append(Paragraph("Document: SOP-PV-042 (v3.0) | Department: Drug Safety & Pharmacovigilance | Effective: 2025-2027", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Section 1.0 — Purpose & Regulatory Authority", h2_style))
    story.append(Paragraph("This SOP enforces compliance with FDA 21 CFR 312.32 (IND safety reports), 21 CFR 314.80 (post-marketing 15-day alert reports), and ICH E2A guidance for rapid identification, triage, and notification of serious adverse reactions.", body_style))

    story.append(Paragraph("Section 2.0 — Expedited Reporting Timelines", h2_style))
    story.append(Paragraph("<b>Fatal or Life-Threatening SAEs:</b> Must be reported to the FDA and relevant institutional review boards (IRBs) no later than <b>7 calendar days</b> following initial receipt of information.", body_style))
    story.append(Paragraph("<b>Serious, Unexpected Adverse Events (SUSARs):</b> Must be submitted within <b>15 calendar days</b>. Any safety event causing inpatient hospitalization or persistent functional incapacity qualifies as serious and triggers mandatory 15-day expedited reporting.", warning_style))

    story.append(Paragraph("Section 3.0 — Audit & Quality Inspection Rules", h2_style))
    story.append(Paragraph("All Individual Case Safety Reports (ICSRs) must be logged into the safety database within 24 hours of receipt. A reporting latency exceeding 15 days constitutes a critical regulatory compliance violation subject to FDA Form 483 warning letters.", body_style))

    doc.build(story)
    print(f"Generated: {pdf_path}")

def generate_gmp_release_sop_pdf():
    pdf_path = DATA_DIR / "Quality_Batch_Release_SOP_Cleanroom_GMP.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Heading1'], fontSize=15, leading=19, textColor=colors.HexColor('#0F172A'))
    h2_style = ParagraphStyle(name='H2Style', parent=styles['Heading2'], fontSize=11.5, leading=15, textColor=colors.HexColor('#1E3A8A'), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle(name='BodyStyle', parent=styles['Normal'], fontSize=9.5, leading=13.5, textColor=colors.HexColor('#334155'), spaceAfter=8)
    callout_style = ParagraphStyle(name='Callout', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#1E40AF'), backColor=colors.HexColor('#EFF6FF'), borderPadding=6, spaceAfter=8)

    story = []

    story.append(Paragraph("STANDARD OPERATING PROCEDURE: FINISHED PRODUCT COMMERCIAL BATCH RELEASE", title_style))
    story.append(Paragraph("Document: SOP-QA-GMP-882 | Department: Quality Assurance & Analytical Chemistry | cGMP", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Section 1.0 — Analytical Release Criteria for CardioVastin Tablets", h2_style))
    story.append(Paragraph("Every commercial batch of CardioVastin 20 mg tablets must meet the following validated release specifications prior to QA QP (Qualified Person) sign-off under 21 CFR Part 211:", body_style))

    story.append(Paragraph("<b>1. Active Ingredient Purity (HPLC):</b> Must be <b>&gt;= 98.5%</b>. Total related impurities must not exceed 1.0%.", body_style))
    story.append(Paragraph("<b>2. In Vitro Dissolution Rate (USP App 2, 50 rpm):</b> Not less than <b>85% dissolved within 30 minutes</b> in pH 6.8 phosphate buffer.", body_style))
    story.append(Paragraph("<b>3. Total Aerobic Microbial Count (TAMC):</b> Less than <b>100 CFU/g</b>. Absence of Escherichia coli and Salmonella.", body_style))

    story.append(Paragraph("Section 2.0 — Lot 4891 Release Investigation Verdict", h2_style))
    story.append(Paragraph("<b>Batch Verification Summary:</b> Lot 4891 achieved <b>99.2% purity</b>, an average <b>88.5% dissolution at 30 minutes</b>, and a microbial count of <b>12 CFU/g</b>. All parameters fully conform to release specifications. The lot is certified and approved for commercial pharmaceutical distribution.", callout_style))

    doc.build(story)
    print(f"Generated: {pdf_path}")

if __name__ == "__main__":
    generate_pharma_excel()
    generate_trial_protocol_pdf()
    generate_fda_approval_pdf()
    generate_pv_sop_pdf()
    generate_gmp_release_sop_pdf()
    print("All Pharma synthetic documents generated successfully.")
