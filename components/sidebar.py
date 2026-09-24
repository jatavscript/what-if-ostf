"""Sidebar Component for Internal Marks 'What-If' Simulator.

Handles navigation, global academic thresholds, student profile metadata,
and database status actions.
"""

from typing import Any, Dict
import streamlit as st
from modules.database import get_all_subjects, reset_to_sample_data


def render_sidebar() -> Dict[str, Any]:
    """Render the sidebar controls and return the active navigation state and user settings."""
    with st.sidebar:
        # App Branding Header
        st.markdown(
            """
            <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
                <div style="background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
                            width: 52px; height: 52px; border-radius: 14px;
                            display: flex; align-items: center; justify-content: center;
                            margin: 0 auto 0.75rem auto; box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3);">
                    <span style="font-size: 26px; color: white;">🎯</span>
                </div>
                <h2 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: #1E293B;">What-If Simulator</h2>
                <p style="margin: 0.2rem 0 0 0; font-size: 0.8rem; color: #64748B; font-weight: 500;">
                    Internal Marks & Grade Forecaster
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Navigation Menu
        st.markdown("### 📌 Navigation")
        nav_options = [
            "📊 Dashboard",
            "🎛️ What-If Simulator",
            "🎯 Target Grade Calculator",
            "⚖️ Scenario Comparison",
            "📚 Subject Setup",
            "📥 Export & Reports",
        ]

        active_page = st.radio(
            "Go to",
            nav_options,
            label_visibility="collapsed",
            index=st.session_state.get("nav_index", 0),
        )

        st.markdown("---")

        # Student Profile Section
        st.markdown("### 👤 Student Profile")
        student_name = st.text_input(
            "Student Name",
            value=st.session_state.get("student_name", "Arjun Sharma"),
            key="input_student_name",
        )
        st.session_state["student_name"] = student_name

        student_id = st.text_input(
            "Roll / Reg Number",
            value=st.session_state.get("student_id", "MCA-2026-042"),
            key="input_student_id",
        )
        st.session_state["student_id"] = student_id

        st.markdown("---")

        # Academic Rules & Thresholds
        st.markdown("### ⚙️ Evaluation Rules")
        passing_percentage = st.slider(
            "Passing Threshold (%)",
            min_value=30.0,
            max_value=50.0,
            value=float(st.session_state.get("passing_pct", 40.0)),
            step=1.0,
            help="Minimum overall percentage required to pass a subject (Default: 40%).",
        )
        st.session_state["passing_pct"] = passing_percentage

        min_attendance = st.slider(
            "Min Attendance (%)",
            min_value=60.0,
            max_value=85.0,
            value=float(st.session_state.get("min_att", 75.0)),
            step=5.0,
            help="University minimum attendance required to appear for external exams (Default: 75%).",
        )
        st.session_state["min_att"] = min_attendance

        st.markdown("---")

        # Database Quick Reset
        st.markdown("### 🔄 Sample Data")
        if st.button("Reset to Default Sample Subjects", use_container_width=True):
            reset_to_sample_data()
            st.session_state["subjects_cache"] = get_all_subjects()
            # Clear slider overrides
            for k in list(st.session_state.keys()):
                if k.startswith("slider_ext_"):
                    del st.session_state[k]
            st.success("Sample curriculum data reloaded!")
            st.rerun()

        # Footer Viva / Project Info
        st.markdown(
            """
            <div style="font-size: 0.725rem; color: #94A3B8; text-align: center; margin-top: 1.5rem;">
                MCA Mini-Project Edition<br>
                v1.0.0 • SQLite & Streamlit
            </div>
            """,
            unsafe_allow_html=True,
        )

    return {
        "active_page": active_page,
        "student_name": student_name,
        "student_id": student_id,
        "passing_percentage": passing_percentage,
        "min_attendance": min_attendance,
    }
