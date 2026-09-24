"""Dashboard Component for Internal Marks 'What-If' Simulator.

Renders executive KPI metrics, interactive Plotly visualizations, attendance flags,
and actionable academic advisory insights.
"""

from typing import Any, Dict, List
import streamlit as st
from modules.charts import (
    create_attendance_overview_chart,
    create_grade_boundary_visualizer,
    create_grade_distribution_chart,
    create_internal_external_split_chart,
    create_subject_percentage_chart,
)


def render_dashboard(
    results: List[Dict[str, Any]],
    overall_summary: Dict[str, Any],
    recommendations: Dict[str, Any],
    min_attendance: float = 75.0,
    passing_percentage: float = 40.0,
) -> None:
    """Render the primary executive academic dashboard."""
    # Top Hero Banner
    student_name = st.session_state.get("student_name", "Student")
    overall_grade = overall_summary.get("overall_grade", "N/A")
    overall_pct = overall_summary.get("overall_percentage", 0.0)
    cgpa = overall_summary.get("overall_cgpa", 0.0)

    st.markdown(
        f"""
        <div class="hero-banner">
            <h1 class="hero-title">
                <span>🎓</span> Welcome back, {student_name}!
            </h1>
            <p class="hero-subtitle">
                Interactive academic performance simulation and external examination 'what-if' forecasting.
                Track your trajectory, eliminate backlogs, and plan targets for high GPA.
            </p>
            <div class="hero-badges">
                <span class="hero-badge-pill">📌 Overall Grade: <b>{overall_grade}</b></span>
                <span class="hero-badge-pill">📊 Projected Aggregate: <b>{overall_pct:.1f}%</b></span>
                <span class="hero-badge-pill">⭐ Projected CGPA: <b>{cgpa:.2f} / 10.0</b></span>
                <span class="hero-badge-pill">📚 Enrolled Subjects: <b>{overall_summary.get('total_subjects', 0)}</b></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. KPI Metric Summary Cards
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card accent-indigo">
                <div class="metric-header">
                    <span class="metric-label">Projected %</span>
                    <div class="metric-icon-wrap">📊</div>
                </div>
                <div class="metric-value">{overall_pct:.1f}%</div>
                <div class="metric-subtext">Total: {overall_summary.get('total_obtained', 0):.0f}/{overall_summary.get('total_max', 0):.0f} Marks</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        grade_color = "#16A34A" if overall_grade in ["O", "A+", "A"] else ("#F59E0B" if overall_grade in ["B+", "B"] else "#DC2626")
        st.markdown(
            f"""
            <div class="metric-card accent-purple">
                <div class="metric-header">
                    <span class="metric-label">Projected Grade</span>
                    <div class="metric-icon-wrap">🎯</div>
                </div>
                <div class="metric-value" style="color: {grade_color};">{overall_grade}</div>
                <div class="metric-subtext">CGPA: {cgpa:.2f} / 10.0</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        pass_count = overall_summary.get("passing_count", 0)
        tot_count = overall_summary.get("total_subjects", 0)
        st.markdown(
            f"""
            <div class="metric-card accent-green">
                <div class="metric-header">
                    <span class="metric-label">Passing Subjects</span>
                    <div class="metric-icon-wrap">✅</div>
                </div>
                <div class="metric-value">{pass_count} <span style="font-size: 1.1rem; color: #64748B;">/ {tot_count}</span></div>
                <div class="metric-subtext">{tot_count - pass_count} backlog risk</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        fail_count = overall_summary.get("failing_count", 0)
        fail_style = "accent-red" if fail_count > 0 else "accent-green"
        st.markdown(
            f"""
            <div class="metric-card {fail_style}">
                <div class="metric-header">
                    <span class="metric-label">Failing Count</span>
                    <div class="metric-icon-wrap">{"⚠️" if fail_count > 0 else "🛡️"}</div>
                </div>
                <div class="metric-value" style="color: {'#DC2626' if fail_count > 0 else '#16A34A'};">{fail_count}</div>
                <div class="metric-subtext">Cutoff: {passing_percentage:.0f}% min</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col5:
        att_risks = overall_summary.get("attendance_risk_count", 0)
        att_style = "accent-red" if att_risks > 0 else "accent-green"
        st.markdown(
            f"""
            <div class="metric-card {att_style}">
                <div class="metric-header">
                    <span class="metric-label">Attendance Risk</span>
                    <div class="metric-icon-wrap">{"⏱️" if att_risks > 0 else "📋"}</div>
                </div>
                <div class="metric-value" style="color: {'#DC2626' if att_risks > 0 else '#16A34A'};">{att_risks}</div>
                <div class="metric-subtext">Below {min_attendance:.0f}% rule</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 2. Critical Alerts & Recommendations Callouts
    crit_warnings = recommendations.get("critical_warnings", [])
    pri_improvements = recommendations.get("priority_improvements", [])
    opportunities = recommendations.get("grade_opportunities", [])

    if crit_warnings or pri_improvements:
        for warn in crit_warnings:
            st.markdown(
                f"""
                <div class="alert-card alert-warning-box">
                    <span style="font-size: 1.4rem;">⚠️</span>
                    <div>{warn}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        for imp in pri_improvements:
            st.markdown(
                f"""
                <div class="alert-card alert-danger-box">
                    <span style="font-size: 1.4rem;">🚨</span>
                    <div>{imp}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if opportunities:
        for opp in opportunities[:2]:  # Show top 2 grade opportunities
            st.markdown(
                f"""
                <div class="alert-card alert-info-box">
                    <span style="font-size: 1.4rem;">🚀</span>
                    <div>{opp}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 3. Visual Charts Grid (Row 1)
    st.markdown("### 📈 Academic Performance Analytics")

    chart_col1, chart_col2 = st.columns([1.6, 1.0])

    with chart_col1:
        st.plotly_chart(
            create_subject_percentage_chart(results, passing_percentage),
            use_container_width=True,
        )

    with chart_col2:
        st.plotly_chart(
            create_grade_distribution_chart(results),
            use_container_width=True,
        )

    # 4. Visual Charts Grid (Row 2)
    chart_col3, chart_col4 = st.columns([1.3, 1.0])

    with chart_col3:
        st.plotly_chart(
            create_internal_external_split_chart(results),
            use_container_width=True,
        )

    with chart_col4:
        st.plotly_chart(
            create_grade_boundary_visualizer(overall_pct, "Overall Performance Gauge", passing_percentage),
            use_container_width=True,
        )

    # 5. Weakest Subject Deep Dive & Attendance Section
    detail_col1, detail_col2 = st.columns([1.2, 1.0])

    with detail_col1:
        weakest = recommendations.get("weakest_subject_analysis")
        st.markdown("### 🔍 Critical Focus Subject")
        if weakest:
            status_badge = (
                '<span class="status-pill status-pass">Passing</span>'
                if weakest["is_pass"]
                else '<span class="status-pill status-fail">Failing / Backlog Risk</span>'
            )
            st.markdown(
                f"""
                <div class="custom-card" style="border-left: 5px solid {'#16A34A' if weakest['is_pass'] else '#DC2626'};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                        <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #1E293B;">
                            {weakest['subject_name']}
                        </h3>
                        {status_badge}
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem; background: #F8FAFC; padding: 0.8rem; border-radius: 8px;">
                        <div>
                            <span style="font-size: 0.75rem; color: #64748B; text-transform: uppercase;">Projected Score</span><br>
                            <b style="font-size: 1.15rem; color: #1E293B;">{weakest['percentage']:.1f}%</b>
                        </div>
                        <div>
                            <span style="font-size: 0.75rem; color: #64748B; text-transform: uppercase;">Grade</span><br>
                            <b style="font-size: 1.15rem; color: #4F46E5;">{weakest['grade']}</b>
                        </div>
                        <div>
                            <span style="font-size: 0.75rem; color: #64748B; text-transform: uppercase;">Internal / Sim Ext</span><br>
                            <b style="font-size: 0.95rem; color: #1E293B;">{weakest['internal_score']} | {weakest['simulated_external']}</b>
                        </div>
                    </div>
                    <p style="margin: 0; font-size: 0.9rem; color: #334155; line-height: 1.5;">
                        💡 <b>Advisory Recommendation:</b> {weakest['advice']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No subject data available.")

    with detail_col2:
        st.markdown("### 📋 Attendance Compliance")
        st.plotly_chart(
            create_attendance_overview_chart(results, min_attendance),
            use_container_width=True,
        )

    # 6. Detailed Tabular Breakdown
    st.markdown("### 📊 Comprehensive Subject Scorecard")
    table_rows = ""
    for r in results:
        status_html = (
            '<span class="status-pill status-pass">PASS</span>'
            if r["is_pass"]
            else '<span class="status-pill status-fail">FAIL</span>'
        )
        att = r.get("attendance", 100.0)
        att_html = (
            f'<span class="att-pill att-good">✓ {att:.0f}%</span>'
            if att >= min_attendance
            else f'<span class="att-pill att-warning">⚠️ {att:.0f}%</span>'
        )
        grade_badge = f'<span class="grade-badge grade-{r["grade"].replace("+", "-plus")}">{r["grade"]}</span>'

        table_rows += f"""
        <tr>
            <td style="font-weight: 600;">{r['subject_name']}</td>
            <td>{r['internal_obtained']:.0f} / {r['internal_max']:.0f}</td>
            <td><b>{r['external_obtained']:.0f}</b> / {r['external_max']:.0f}</td>
            <td>{r['total_obtained']:.0f} / {r['total_max']:.0f}</td>
            <td><b>{r['percentage']:.1f}%</b></td>
            <td>{grade_badge}</td>
            <td>{status_html}</td>
            <td>{att_html}</td>
        </tr>
        """

    st.markdown(
        f"""
        <table class="custom-table">
            <thead>
                <tr>
                    <th>Subject Name</th>
                    <th>Internal Marks</th>
                    <th>Simulated External</th>
                    <th>Total Marks</th>
                    <th>Projected %</th>
                    <th>Grade</th>
                    <th>Status</th>
                    <th>Attendance</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )
