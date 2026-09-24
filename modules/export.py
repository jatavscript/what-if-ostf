"""Export Module for Internal Marks 'What-If' Simulator.

Generates downloadable CSV, formatted Excel workbooks, and professional PDF reports
containing student results, simulation projections, attendance audits, and recommendations.
"""

from datetime import datetime
import io
from typing import Any, Dict, List, Optional
import pandas as pd

# ReportLab imports for PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def export_to_csv(results: List[Dict[str, Any]], overall_summary: Dict[str, Any]) -> bytes:
    """Generate CSV bytes containing complete simulated subject records and aggregate row."""
    rows = []
    for r in results:
        rows.append({
            "Subject Name": r["subject_name"],
            "Internal Obtained": r["internal_obtained"],
            "Internal Max": r["internal_max"],
            "Simulated External": r["external_obtained"],
            "External Max": r["external_max"],
            "Total Obtained": r["total_obtained"],
            "Total Max": r["total_max"],
            "Percentage (%)": r["percentage"],
            "Grade": r["grade"],
            "Status": "PASS" if r["is_pass"] else "FAIL",
            "Attendance (%)": r.get("attendance", "N/A"),
            "Marks to Next Grade": r.get("marks_to_next_grade", 0.0),
        })

    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode("utf-8")


def export_to_excel(
    results: List[Dict[str, Any]],
    overall_summary: Dict[str, Any],
    student_name: str = "Student"
) -> bytes:
    """Generate a multi-sheet formatted Excel workbook using openpyxl."""
    output = io.BytesIO()

    # Sheet 1: Subject Results
    subject_rows = []
    for r in results:
        subject_rows.append({
            "Subject Name": r["subject_name"],
            "Internal Scored": r["internal_obtained"],
            "Internal Max": r["internal_max"],
            "Simulated External": r["external_obtained"],
            "External Max": r["external_max"],
            "Total Marks": r["total_obtained"],
            "Maximum Marks": r["total_max"],
            "Percentage (%)": r["percentage"],
            "Grade": r["grade"],
            "Status": "PASS" if r["is_pass"] else "FAIL",
            "Attendance (%)": r.get("attendance", "N/A"),
            "Attendance Status": "Eligible" if r.get("attendance", 100) >= 75 else "SHORTAGE",
            "Next Target Grade": r.get("next_grade_info", {}).get("next_grade", "Top Grade"),
            "Marks Required for Next Grade": r.get("marks_to_next_grade", 0.0),
        })

    df_subjects = pd.DataFrame(subject_rows)

    # Sheet 2: Overall Summary
    summary_data = [
        {"Metric": "Student Name", "Value": student_name},
        {"Metric": "Total Subjects", "Value": overall_summary.get("total_subjects", 0)},
        {"Metric": "Total Marks Scored", "Value": f"{overall_summary.get('total_obtained', 0):.1f} / {overall_summary.get('total_max', 0):.1f}"},
        {"Metric": "Overall Projected Percentage", "Value": f"{overall_summary.get('overall_percentage', 0):.2f}%"},
        {"Metric": "Overall Grade", "Value": overall_summary.get("overall_grade", "N/A")},
        {"Metric": "Overall Projected CGPA", "Value": f"{overall_summary.get('overall_cgpa', 0):.2f} / 10.0"},
        {"Metric": "Passing Subjects Count", "Value": overall_summary.get("passing_count", 0)},
        {"Metric": "Failing Subjects Count", "Value": overall_summary.get("failing_count", 0)},
        {"Metric": "Attendance Shortage Count", "Value": overall_summary.get("attendance_risk_count", 0)},
        {"Metric": "Simulation Date", "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
    ]
    df_summary = pd.DataFrame(summary_data)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_subjects.to_excel(writer, sheet_name="Subject Simulations", index=False)
        df_summary.to_excel(writer, sheet_name="Executive Summary", index=False)

    return output.getvalue()


def export_to_pdf(
    results: List[Dict[str, Any]],
    overall_summary: Dict[str, Any],
    student_name: str = "Student",
    student_id: str = "MCA-SIM",
    recommendations: Optional[Dict[str, Any]] = None,
) -> bytes:
    """Generate a clean, professional academic performance report in PDF format."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#312E81"),  # Deep indigo
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4B5563"),
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1F2937"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#374151"),
    )
    bullet_style = ParagraphStyle(
        "BulletDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#374151"),
        leftIndent=12,
        spaceAfter=4,
    )

    story = []

    # Title & Header
    story.append(Paragraph("ACADEMIC PERFORMANCE SIMULATION REPORT", title_style))
    story.append(Paragraph("Internal Marks 'What-If' Scenario Forecasting System", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#4F46E5"), spaceAfter=12))

    # Student & Metadata Info Card Table
    gen_time = datetime.now().strftime("%d %b %Y, %I:%M %p")
    meta_data = [
        [
            Paragraph(f"<b>Candidate:</b> {student_name}", body_style),
            Paragraph(f"<b>ID / Reg No:</b> {student_id}", body_style),
            Paragraph(f"<b>Generated:</b> {gen_time}", body_style),
        ],
        [
            Paragraph(f"<b>Total Subjects:</b> {overall_summary.get('total_subjects', len(results))}", body_style),
            Paragraph(f"<b>Overall Projected:</b> {overall_summary.get('overall_percentage', 0.0):.1f}% (Grade {overall_summary.get('overall_grade', '-')})", body_style),
            Paragraph(f"<b>Academic Standing:</b> {'ALL PASS' if overall_summary.get('is_pass') else 'BACKLOG DETECTED'}", body_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[180, 180, 180])
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # Subject Results Table
    story.append(Paragraph("Subject-Wise Simulation Breakdown", section_heading))
    headers = ["Subject", "Internal", "Sim Ext", "Total", "Pct (%)", "Grade", "Status", "Att (%)"]
    table_data = [headers]

    for r in results:
        row = [
            Paragraph(r["subject_name"], body_style),
            f"{r['internal_obtained']:.0f}/{r['internal_max']:.0f}",
            f"{r['external_obtained']:.0f}/{r['external_max']:.0f}",
            f"{r['total_obtained']:.0f}/{r['total_max']:.0f}",
            f"{r['percentage']:.1f}%",
            r["grade"],
            "PASS" if r["is_pass"] else "FAIL",
            f"{r.get('attendance', 100):.0f}%",
        ]
        table_data.append(row)

    # Aggregate Row
    table_data.append([
        Paragraph("<b>OVERALL AGGREGATE</b>", body_style),
        f"{overall_summary.get('total_internal_obtained', 0):.0f}/{overall_summary.get('total_internal_max', 0):.0f}",
        f"{overall_summary.get('total_external_obtained', 0):.0f}/{overall_summary.get('total_external_max', 0):.0f}",
        f"{overall_summary.get('total_obtained', 0):.0f}/{overall_summary.get('total_max', 0):.0f}",
        f"<b>{overall_summary.get('overall_percentage', 0):.1f}%</b>",
        f"<b>{overall_summary.get('overall_grade', '-')}</b>",
        "PASS" if overall_summary.get("is_pass") else "FAIL",
        "-",
    ])

    results_table = Table(table_data, colWidths=[150, 55, 55, 55, 60, 45, 60, 60])
    results_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8.5),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F8FAFC")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#EEF2FF")),
            ("LINEABOVE", (0, -1), (-1, -1), 1.5, colors.HexColor("#4F46E5")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )
    story.append(results_table)
    story.append(Spacer(1, 14))

    # Recommendations & Warnings Section
    if recommendations:
        story.append(Paragraph("Academic Advisory & Action Points", section_heading))

        # Critical Warnings
        for warn in recommendations.get("critical_warnings", []):
            clean_warn = warn.replace("**", "").replace("⚠️ ", "").replace("🚨 ", "")
            story.append(Paragraph(f"• <b>[Shortage Alert]</b> {clean_warn}", bullet_style))

        # Priority Improvements
        for imp in recommendations.get("priority_improvements", []):
            clean_imp = imp.replace("**", "").replace("🚨 ", "").replace("📈 ", "")
            story.append(Paragraph(f"• <b>[Action Required]</b> {clean_imp}", bullet_style))

        # Grade Opportunities
        for opp in recommendations.get("grade_opportunities", []):
            clean_opp = opp.replace("**", "").replace("🚀 ", "")
            story.append(Paragraph(f"• <b>[Upgrade Target]</b> {clean_opp}", bullet_style))

        # Weakest Subject Note
        weakest = recommendations.get("weakest_subject_analysis")
        if weakest:
            story.append(
                Paragraph(
                    f"• <b>[Priority Subject]</b> {weakest['subject_name']}: "
                    f"Currently lowest at {weakest['percentage']:.1f}% ({weakest['grade']}). {weakest['advice']}",
                    bullet_style,
                )
            )

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=8))
    disclaimer = (
        "<b>Notice:</b> This document is generated for academic simulation and predictive planning purposes. "
        "Projected grades are hypothetical calculations and do not constitute official university marksheets."
    )
    story.append(Paragraph(disclaimer, ParagraphStyle("Disc", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=7.5, leading=10, textColor=colors.HexColor("#64748B"))))

    doc.build(story)
    return buffer.getvalue()
