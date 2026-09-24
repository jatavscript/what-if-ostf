"""Main Application Entry Point for Internal Marks 'What-If' Simulator.

Interactive academic performance simulator for MCA / Engineering students to model
external examination outcomes, calculate target grade requirements, detect attendance
risks, and visualize grade boundaries.
"""

import os
from typing import Any, Dict, List
import streamlit as st

# Application Core Modules
from modules.database import get_all_subjects, init_db
from modules.calculations import calculate_overall_percentage, calculate_subject_result
from modules.recommendations import generate_recommendations

# UI Components
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.simulator import (
    render_simulator,
    render_target_grade_calculator,
    render_scenario_comparison,
)
from components.subject_setup import render_subject_setup
from components.reports import render_reports_page


def load_custom_css() -> None:
    """Inject custom stylesheet into Streamlit app."""
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "custom.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def compute_simulation_state(
    subjects: List[Dict[str, Any]],
    passing_percentage: float = 40.0,
    min_attendance: float = 75.0,
) -> tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]:
    """Compute active simulation metrics based on current session slider values."""
    results: List[Dict[str, Any]] = []

    for s in subjects:
        subj_name = s["subject_name"]
        int_max = float(s["internal_max"])
        int_obt = float(s["internal_obtained"])
        ext_max = float(s["external_max"])
        att = float(s["attendance"])

        slider_key = f"slider_ext_{subj_name}"
        if slider_key not in st.session_state:
            st.session_state[slider_key] = float(round(0.60 * ext_max))

        sim_ext = min(ext_max, max(0.0, float(st.session_state[slider_key])))

        res = calculate_subject_result(
            internal_obtained=int_obt,
            internal_max=int_max,
            external_obtained=sim_ext,
            external_max=ext_max,
            passing_percentage=passing_percentage,
        )
        res["subject_name"] = subj_name
        res["attendance"] = att
        results.append(res)

    overall_summary = calculate_overall_percentage(results, passing_percentage)
    recommendations = generate_recommendations(
        results,
        overall_summary,
        min_attendance=min_attendance,
        passing_percentage=passing_percentage,
    )

    return results, overall_summary, recommendations


def main() -> None:
    """Main execution function."""
    st.set_page_config(
        page_title="Internal Marks 'What-If' Simulator",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject styling
    load_custom_css()

    # Initialize SQLite Database
    init_db()

    # Render Sidebar and retrieve settings
    sidebar_state = render_sidebar()
    active_page = sidebar_state["active_page"]
    passing_pct = sidebar_state["passing_percentage"]
    min_att = sidebar_state["min_attendance"]
    student_name = sidebar_state["student_name"]
    student_id = sidebar_state["student_id"]

    # Load subjects
    subjects = get_all_subjects()

    # Compute current active simulation metrics
    results, overall_summary, recommendations = compute_simulation_state(
        subjects,
        passing_percentage=passing_pct,
        min_attendance=min_att,
    )

    # Route navigation
    if active_page == "📊 Dashboard":
        render_dashboard(
            results=results,
            overall_summary=overall_summary,
            recommendations=recommendations,
            min_attendance=min_att,
            passing_percentage=passing_pct,
        )

    elif active_page == "🎛️ What-If Simulator":
        render_simulator(
            subjects=subjects,
            passing_percentage=passing_pct,
            min_attendance=min_att,
        )

    elif active_page == "🎯 Target Grade Calculator":
        render_target_grade_calculator(subjects=subjects)

    elif active_page == "⚖️ Scenario Comparison":
        render_scenario_comparison(
            subjects=subjects,
            passing_percentage=passing_pct,
        )

    elif active_page == "📚 Subject Setup":
        render_subject_setup(min_attendance=min_att)

    elif active_page == "📥 Export & Reports":
        render_reports_page(
            results=results,
            overall_summary=overall_summary,
            recommendations=recommendations,
            student_name=student_name,
            student_id=student_id,
        )

    # Academic Footer
    st.markdown(
        """
        <div class="app-footer">
            <b>Internal Marks "What-If" Simulator</b> • Developed for MCA Academic Demonstration & Viva Evaluation<br>
            <span style="font-size: 0.775rem;">
                Built with Python 3, Streamlit, SQLite3, and Plotly. Designed for student productivity and performance optimization.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
