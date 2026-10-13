from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import io


def generate_triage_report_pdf(assessment_data: dict) -> bytes:
    """Generate a PDF report from triage assessment data."""
    
    # Create PDF in memory
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0F52BA'),
        spaceAfter=12,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0F52BA'),
        spaceAfter=6,
        spaceBefore=6
    )
    
    # Content
    story = []
    
    # Header
    story.append(Paragraph("🩺 AI Medical Triage Assessment Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Report Info
    report_date = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
    story.append(Paragraph(f"<b>Report Generated:</b> {report_date}", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    # Patient Information
    story.append(Paragraph("Patient Information", heading_style))
    patient_table_data = [
        ["Age", str(assessment_data.get("age", "N/A"))],
        ["Gender", assessment_data.get("gender", "N/A")],
        ["Symptom Duration", assessment_data.get("duration", "N/A")],
        ["Severity Score", f"{assessment_data.get('severity_score', 0)}/10"],
        ["Pre-existing Conditions", assessment_data.get("existing_conditions", "None")],
    ]
    patient_table = Table(patient_table_data, colWidths=[2.5*inch, 3.5*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F1F9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Urgency Assessment
    story.append(Paragraph("Urgency Assessment", heading_style))
    urgency_level = assessment_data.get("urgency_level", "ROUTINE")
    urgency_colors = {
        "EMERGENCY": colors.red,
        "URGENT": colors.orange,
        "ROUTINE": colors.blue,
        "SELF_CARE": colors.green
    }
    
    urgency_text = Paragraph(
        f"<b>Level:</b> <font color='{urgency_colors.get(urgency_level, colors.black)}' size=14><b>{urgency_level}</b></font>",
        styles['Normal']
    )
    story.append(urgency_text)
    story.append(Spacer(1, 0.1*inch))
    
    # Recommended Action
    story.append(Paragraph(f"<b>Recommended Action:</b><br/>{assessment_data.get('recommended_action', 'N/A')}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Red Flags
    if assessment_data.get("red_flags_detected"):
        story.append(Paragraph("⚠️ Red Flags Detected", heading_style))
        for flag in assessment_data.get("red_flags_detected", []):
            story.append(Paragraph(f"• {flag}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Clinical Summary
    story.append(Paragraph("Clinical Summary", heading_style))
    story.append(Paragraph(assessment_data.get("summary", "N/A"), styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Questions for Doctor
    if assessment_data.get("questions_for_doctor"):
        story.append(Paragraph("Questions to Ask Your Doctor", heading_style))
        for q in assessment_data.get("questions_for_doctor", []):
            story.append(Paragraph(f"• {q}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Disclaimer
    story.append(Paragraph("⚠️ IMPORTANT DISCLAIMER", heading_style))
    story.append(Paragraph(assessment_data.get("disclaimer", "N/A"), styles['Normal']))
    
    # Build PDF
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def generate_report_analysis_pdf(report_data: dict) -> bytes:
    """Generate a PDF report from medical report analysis."""
    
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0F52BA'),
        spaceAfter=12,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0F52BA'),
        spaceAfter=6,
        spaceBefore=6
    )
    
    story = []
    
    # Header
    story.append(Paragraph("📄 Medical Report Analysis", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Report Date
    report_date = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
    story.append(Paragraph(f"<b>Analysis Generated:</b> {report_date}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Summary
    story.append(Paragraph("Plain English Summary", heading_style))
    story.append(Paragraph(report_data.get("summary", "N/A"), styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Key Findings
    if report_data.get("key_findings"):
        story.append(Paragraph("Key Findings", heading_style))
        for finding in report_data.get("key_findings", []):
            story.append(Paragraph(f"• {finding}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Abnormal Values
    if report_data.get("abnormal_values"):
        story.append(Paragraph("⚠️ Abnormal Values Detected", heading_style))
        for value in report_data.get("abnormal_values", []):
            story.append(Paragraph(f"• {value}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Simplified Terms
    if report_data.get("simplified_terms"):
        story.append(Paragraph("Medical Terms Explained", heading_style))
        for term, explanation in report_data.get("simplified_terms", {}).items():
            story.append(Paragraph(f"<b>{term}:</b> {explanation}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Next Steps
    if report_data.get("next_steps"):
        story.append(Paragraph("Next Steps", heading_style))
        for step in report_data.get("next_steps", []):
            story.append(Paragraph(f"• {step}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Disclaimer
    story.append(Paragraph("⚠️ IMPORTANT DISCLAIMER", heading_style))
    story.append(Paragraph(report_data.get("disclaimer", "N/A"), styles['Normal']))
    
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
