"""Subject Setup Component for Internal Marks 'What-If' Simulator.

Provides dynamic course curriculum management with strict input validation,
SQLite persistence, live error messaging, and sample curriculum restoration.
"""

from typing import Any, Dict, List
import pandas as pd
import streamlit as st
from modules.database import (
    add_subject,
    delete_subject,
    get_all_subjects,
    reset_to_sample_data,
    update_subject,
)


def render_subject_setup(min_attendance: float = 75.0) -> None:
    """Render the subject curriculum management interface."""
    st.markdown(
        """
        <div class="section-header">
            <h2 class="section-title">
                <span>📚</span> Subject Curriculum Management
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "Configure your enrolled subjects, internal assessment scores, external examination maximum weights, "
        "and attendance percentages. Changes immediately synchronize with your database and live simulator."
    )

    subjects = get_all_subjects()

    tab_overview, tab_add, tab_edit, tab_delete = st.tabs(
        [
            "📋 Current Subjects",
            "➕ Add New Subject",
            "✏️ Edit Subject",
            "🗑️ Remove Subject",
        ]
    )

    # TAB 1: Current Subjects Overview
    with tab_overview:
        st.markdown(f"#### Enrolled Subjects ({len(subjects)})")

        if not subjects:
            st.warning("No subjects configured. Add a subject or reset to sample data.")
        else:
            table_rows = []
            for s in subjects:
                att = s["attendance"]
                att_status = "Eligible" if att >= min_attendance else f"SHORTAGE (-{min_attendance - att:.1f}%)"
                table_rows.append({
                    "Subject Name": s["subject_name"],
                    "Internal Scored": f"{s['internal_obtained']:.0f} / {s['internal_max']:.0f}",
                    "Internal %": f"{(s['internal_obtained'] / s['internal_max'] * 100):.1f}%",
                    "External Max": f"{s['external_max']:.0f}",
                    "Total Max": f"{s['internal_max'] + s['external_max']:.0f}",
                    "Attendance": f"{s['attendance']:.1f}%",
                    "Eligibility Status": att_status,
                })

            df = pd.DataFrame(table_rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            col_btn1, col_btn2 = st.columns([1, 4])
            with col_btn1:
                if st.button("🔄 Reset Sample Curriculum", key="btn_reset_curriculum"):
                    reset_to_sample_data()
                    st.success("Default MCA sample subjects restored!")
                    st.rerun()

    # TAB 2: Add New Subject
    with tab_add:
        st.markdown("#### ➕ Add New Academic Subject")
        with st.form("form_add_subject", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                new_name = st.text_input("Subject Name", placeholder="e.g. Cloud Computing", help="Unique course title")
                internal_max = st.number_input(
                    "Internal Maximum Marks",
                    min_value=1.0,
                    max_value=100.0,
                    value=30.0,
                    step=5.0,
                    help="Total marks allocated to internal assessments (e.g. 30)",
                )
                internal_obt = st.number_input(
                    "Internal Obtained Marks",
                    min_value=0.0,
                    max_value=100.0,
                    value=20.0,
                    step=1.0,
                    help="Marks secured in midterms, assignments, and practicals",
                )

            with col_b:
                external_max = st.number_input(
                    "External Maximum Marks",
                    min_value=1.0,
                    max_value=200.0,
                    value=70.0,
                    step=10.0,
                    help="Maximum marks possible in university end-semester examination (e.g. 70)",
                )
                attendance = st.slider(
                    "Current Attendance (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=80.0,
                    step=1.0,
                    help="Student attendance percentage recorded by department",
                )

            submitted = st.form_submit_button("Add Subject to Curriculum", type="primary")

            if submitted:
                # Rigorous validation
                name_clean = new_name.strip()
                if not name_clean:
                    st.error("Validation Error: Subject name cannot be empty.")
                elif internal_obt > internal_max:
                    st.error(f"Validation Error: Internal scored ({internal_obt}) cannot exceed internal max ({internal_max}).")
                else:
                    success, msg = add_subject(
                        name_clean,
                        internal_max,
                        internal_obt,
                        external_max,
                        attendance,
                    )
                    if success:
                        st.success(f"Success: {msg}")
                        st.rerun()
                    else:
                        st.error(f"Error: {msg}")

    # TAB 3: Edit Subject
    with tab_edit:
        st.markdown("#### ✏️ Modify Subject Details")
        if not subjects:
            st.info("No subjects available to edit.")
        else:
            subject_names = [s["subject_name"] for s in subjects]
            selected_subject_name = st.selectbox("Select Subject to Edit", subject_names, key="edit_subject_select")

            # Retrieve current data
            selected_sub = next((s for s in subjects if s["subject_name"] == selected_subject_name), None)

            if selected_sub:
                with st.form("form_edit_subject"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        edit_name = st.text_input("Subject Name", value=selected_sub["subject_name"])
                        edit_int_max = st.number_input(
                            "Internal Maximum Marks",
                            min_value=1.0,
                            max_value=100.0,
                            value=float(selected_sub["internal_max"]),
                            step=5.0,
                        )
                        edit_int_obt = st.number_input(
                            "Internal Obtained Marks",
                            min_value=0.0,
                            max_value=100.0,
                            value=float(selected_sub["internal_obtained"]),
                            step=1.0,
                        )

                    with col_e2:
                        edit_ext_max = st.number_input(
                            "External Maximum Marks",
                            min_value=1.0,
                            max_value=200.0,
                            value=float(selected_sub["external_max"]),
                            step=10.0,
                        )
                        edit_att = st.slider(
                            "Attendance (%)",
                            min_value=0.0,
                            max_value=100.0,
                            value=float(selected_sub["attendance"]),
                            step=1.0,
                        )

                    btn_update = st.form_submit_button("Save Changes", type="primary")

                    if btn_update:
                        if edit_int_obt > edit_int_max:
                            st.error(f"Internal scored ({edit_int_obt}) cannot exceed internal maximum ({edit_int_max}).")
                        else:
                            success, msg = update_subject(
                                selected_sub["id"],
                                edit_name.strip(),
                                edit_int_max,
                                edit_int_obt,
                                edit_ext_max,
                                edit_att,
                            )
                            if success:
                                st.success(f"Updated: {msg}")
                                st.rerun()
                            else:
                                st.error(f"Update failed: {msg}")

    # TAB 4: Delete Subject
    with tab_delete:
        st.markdown("#### 🗑️ Remove Subject from Curriculum")
        if not subjects:
            st.info("No subjects to remove.")
        else:
            del_names = [s["subject_name"] for s in subjects]
            to_delete = st.selectbox("Select Subject to Delete", del_names, key="del_subject_select")
            del_sub = next((s for s in subjects if s["subject_name"] == to_delete), None)

            if del_sub:
                st.warning(
                    f"Are you sure you want to permanently delete **{del_sub['subject_name']}**? "
                    "This action cannot be undone."
                )
                if st.button(f"Confirm Deletion of '{del_sub['subject_name']}'", type="primary"):
                    success, msg = delete_subject(del_sub["id"])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
