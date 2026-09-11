import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle

# =========================================
# CONFIG
# =========================================

OUTPUT_DIR = "ai_diagnostic_reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================================
# CLINICAL MAPPINGS (FIXED, NON-LLM)
# =========================================

CLASS_MAP = {
    0: "No Diabetic Retinopathy",
    1: "Mild Diabetic Retinopathy",
    2: "Moderate Diabetic Retinopathy",
    3: "Severe Diabetic Retinopathy",
    4: "Proliferative Diabetic Retinopathy"
}

INTERPRETATION_MAP = {
    0: "No visible retinal lesions detected. Retina appears normal.",
    1: "Early microaneurysms detected. Mild retinal changes present.",
    2: "Presence of hemorrhages and exudates indicating moderate disease.",
    3: "Extensive retinal hemorrhages and venous abnormalities observed.",
    4: "Neovascularization detected. High risk of vision loss."
}

RECOMMENDATION_MAP = {
    0: "Routine annual retinal screening recommended.",
    1: "Follow-up screening advised within 6–12 months.",
    2: "Ophthalmology consultation advised within 3–6 months.",
    3: "Urgent ophthalmologist referral required.",
    4: "Immediate specialist intervention strongly recommended."
}

# =========================================
# PDF GENERATOR FUNCTION
# =========================================

def generate_ai_report(
    output_pdf,
    patient_info,
    image_path,
    predicted_class,
    confidence
):
    styles = getSampleStyleSheet()
    # ensure 'Small' style exists for the disclaimer; add fallback if missing
    if 'Small' not in styles.byName:
        styles.add(ParagraphStyle('Small', parent=styles['Normal'], fontSize=8))

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []

    # -------------------------------------
    # Header
    # -------------------------------------
    header = Paragraph(
        "<b>ABC Eye Care Hospital</b><br/>"
        "Department of Ophthalmology<br/>"
        "AI Diagnostic Report",
        styles["Title"]
    )
    header.alignment = TA_CENTER
    story.append(header)
    story.append(Spacer(1, 20))

    # -------------------------------------
    # Patient Information Table
    # -------------------------------------
    patient_table = Table([
        ["Patient Name", patient_info["name"]],
        ["Patient ID", patient_info["id"]],
        ["Age", patient_info["age"]],
        ["Gender", patient_info["gender"]],
        ["Report Date", patient_info["date"]],
        ["Referring Doctor", patient_info["doctor"]],
    ], colWidths=[2.5*inch, 3.5*inch])

    patient_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONT", (0,0), (-1,-1), "Helvetica", 10),
    ]))

    story.append(patient_table)
    story.append(Spacer(1, 25))

    # -------------------------------------
    # Fundus Image
    # -------------------------------------
    story.append(Paragraph("<b>Analyzed Retinal Image</b>", styles["Heading3"]))
    story.append(Spacer(1, 10))

    fundus_img = Image(image_path, width=3.5*inch, height=3.5*inch)
    fundus_img.hAlign = "CENTER"
    story.append(fundus_img)
    story.append(Spacer(1, 20))

    # -------------------------------------
    # AI Diagnosis Section
    # -------------------------------------
    diagnosis_name = CLASS_MAP[predicted_class]
    interpretation = INTERPRETATION_MAP[predicted_class]
    recommendation = RECOMMENDATION_MAP[predicted_class]

    diagnosis_text = f"""
    <b>AI Prediction:</b> {diagnosis_name}<br/>
    <b>Model Confidence:</b> {confidence:.2f}%<br/><br/>

    <b>Clinical Interpretation:</b><br/>
    {interpretation}<br/><br/>

    <b>Recommended Action:</b><br/>
    {recommendation}
    """

    story.append(Paragraph(diagnosis_text, styles["Normal"]))
    story.append(Spacer(1, 20))

    # -------------------------------------
    # Disclaimer
    # -------------------------------------
    disclaimer = Paragraph(
        "<i>"
        "Disclaimer: This AI-generated report is intended to assist clinicians "
        "and should not be used as a standalone diagnostic tool. Final diagnosis "
        "must be confirmed by a certified ophthalmologist."
        "</i>",
        styles["Small"]
    )
    story.append(disclaimer)

    doc.build(story)

    print(f"✅ AI Diagnostic PDF generated: {output_pdf}")
