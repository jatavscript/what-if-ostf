"""Reports and Export Component for Internal Marks 'What-If' Simulator.

Provides downloadable academic reports in PDF, Excel, and CSV formats,
along with export preview scorecards.
"""

from datetime import datetime
from typing import Any, Dict, List
import pandas as pd
import streamlit as st
from modules.export import export_to_csv, export_to_excel, export_to_pdf


def render_reports_page(
    results: List[Dict[str, Any]],
    overall_summary: Dict[str, Any],
    recommendations: Dict[str, Any],
    student_name: str,
    student_id: str,
) -> None:
    """Render the academic report generation and file download interface."""
    st.markdown(
        """
        <div class="section-header">
            <h2 class="section-title">
                <span>📥</span> Academic Performance Reports & Export
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "Download your simulated examination forecasts, projected GPA, and academic advisory analysis "
        "in various formats suitable for academic counseling, department reviews, or personal planning."
    )

    if not results:
        st.warning("No subject data available to generate reports.")
        return

    # Document Metadata Customization
    st.markdown("#### 📄 Document Header Customization")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        doc_student = st.text_input("Candidate Name", value=student_name, key="rep_name")
    with col_m2:
        doc_id = st.text_input("Register / Roll No", value=student_id, key="rep_id")
    with col_m3:
        doc_date = st.text_input("Report Date", value=datetime.now().strftime("%d %B %Y"), disabled=True)

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # Export Download Cards Grid
    st.markdown("#### 💾 Download Performance Reports")
    col_d1, col_d2, col_d3 = st.columns(3)

    # 1. PDF Report
    with col_d1:
        st.markdown(
            """
            <div class="custom-card" style="text-align: center; border-top: 4px solid #4F46E5;">
                <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">📄</div>
                <h4 style="margin: 0 0 0.35rem 0; color: #1E293B;">Official PDF Report</h4>
                <p style="font-size: 0.85rem; color: #64748B; margin-bottom: 1rem;">
                    Formal academic scorecard including metadata, marks summary, and advisory guidance.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            pdf_bytes = export_to_pdf(
                results=results,
                overall_summary=overall_summary,
                student_name=doc_student,
                student_id=doc_id,
                recommendations=recommendations,
            )
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name=f"Academic_Simulation_{doc_id}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error preparing PDF: {str(e)}")

    # 2. Excel Workbook
    with col_d2:
        st.markdown(
            """
            <div class="custom-card" style="text-align: center; border-top: 4px solid #16A34A;">
                <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">📊</div>
                <h4 style="margin: 0 0 0.35rem 0; color: #1E293B;">Excel Workbook (.xlsx)</h4>
                <p style="font-size: 0.85rem; color: #64748B; margin-bottom: 1rem;">
                    Multi-sheet spreadsheet with subject-wise calculations and executive performance tabs.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            excel_bytes = export_to_excel(
                results=results,
                overall_summary=overall_summary,
                student_name=doc_student,
            )
            st.download_button(
                label="⬇️ Download Excel (.xlsx)",
                data=excel_bytes,
                file_name=f"Academic_Simulation_{doc_id}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error preparing Excel: {str(e)}")

    # 3. CSV Dataset
    with col_d3:
        st.markdown(
            """
            <div class="custom-card" style="text-align: center; border-top: 4px solid #06B6D4;">
                <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">📑</div>
                <h4 style="margin: 0 0 0.35rem 0; color: #1E293B;">Raw CSV Dataset</h4>
                <p style="font-size: 0.85rem; color: #64748B; margin-bottom: 1rem;">
                    Standard CSV dataset for automated data pipelines, Pandas analysis, or archive.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            csv_bytes = export_to_csv(results, overall_summary)
            st.download_button(
                label="⬇️ Download CSV (.csv)",
                data=csv_bytes,
                file_name=f"Academic_Simulation_{doc_id}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error preparing CSV: {str(e)}")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Live Preview of Export Data
    st.markdown("#### 👁️ Report Data Preview")
    preview_data = []
    for r in results:
        preview_data.append({
            "Subject": r["subject_name"],
            "Internal (Obt/Max)": f"{r['internal_obtained']:.0f} / {r['internal_max']:.0f}",
            "Sim External (Obt/Max)": f"{r['external_obtained']:.0f} / {r['external_max']:.0f}",
            "Total Marks": f"{r['total_obtained']:.0f} / {r['total_max']:.0f}",
            "Percentage": f"{r['percentage']:.1f}%",
            "Grade": r["grade"],
            "Pass/Fail": "PASS" if r["is_pass"] else "FAIL",
            "Attendance": f"{r.get('attendance', 100):.0f}%",
        })

    df_prev = pd.DataFrame(preview_data)
    st.dataframe(df_prev, use_container_width=True, hide_index=True)
