"""Simulator Component for Internal Marks 'What-If' Simulator.

Provides interactive sliders for external marks forecasting, instant calculations,
scenario preset batch controls, scenario persistence, and target grade solver.
"""

from typing import Any, Dict, List, Tuple
import pandas as pd
import streamlit as st
from modules.calculations import (
    DEFAULT_GRADE_SCALE,
    calculate_overall_percentage,
    calculate_required_external_marks,
    calculate_subject_result,
    get_grade,
)
from modules.charts import (
    create_grade_boundary_visualizer,
    create_scenario_comparison_chart,
    create_subject_percentage_chart,
)
from modules.database import (
    delete_scenario,
    get_all_subjects,
    get_saved_scenarios,
    get_scenario_scores,
    save_scenario,
)


def render_simulator(
    subjects: List[Dict[str, Any]],
    passing_percentage: float = 40.0,
    min_attendance: float = 75.0,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Render the interactive What-If Simulator and return calculated results and summary."""
    st.markdown(
        """
        <div class="section-header">
            <h2 class="section-title">
                <span>🎛️</span> Interactive External Exam "What-If" Simulator
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "Adjust the sliders below to simulate different external examination scores. "
        "The system instantly recomputes your total scores, subject percentages, letter grades, "
        "and backlog status in real time."
    )

    if not subjects:
        st.warning("No subjects configured. Please configure subjects in the 'Subject Setup' page.")
        return [], {}

    # Quick Batch Presets
    st.markdown("#### ⚡ Quick Simulation Presets")
    col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)

    with col_p1:
        if st.button("🛡️ Safe Attempt (40%)", use_container_width=True):
            for s in subjects:
                st.session_state[f"slider_ext_{s['subject_name']}"] = float(round(0.40 * s["external_max"]))
            st.rerun()

    with col_p2:
        if st.button("📊 Average (60%)", use_container_width=True):
            for s in subjects:
                st.session_state[f"slider_ext_{s['subject_name']}"] = float(round(0.60 * s["external_max"]))
            st.rerun()

    with col_p3:
        if st.button("🚀 Strong (80%)", use_container_width=True):
            for s in subjects:
                st.session_state[f"slider_ext_{s['subject_name']}"] = float(round(0.80 * s["external_max"]))
            st.rerun()

    with col_p4:
        if st.button("🌟 Maximum (100%)", use_container_width=True):
            for s in subjects:
                st.session_state[f"slider_ext_{s['subject_name']}"] = float(s["external_max"])
            st.rerun()

    with col_p5:
        if st.button("🔄 Reset Sliders", use_container_width=True):
            for s in subjects:
                st.session_state[f"slider_ext_{s['subject_name']}"] = float(round(0.60 * s["external_max"]))
            st.rerun()

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Subject Simulator Cards with Live Sliders
    results: List[Dict[str, Any]] = []

    for s in subjects:
        subj_name = s["subject_name"]
        int_max = float(s["internal_max"])
        int_obt = float(s["internal_obtained"])
        ext_max = float(s["external_max"])
        att = float(s["attendance"])

        # Default slider value is 60% of external max
        slider_key = f"slider_ext_{subj_name}"
        default_val = float(round(0.60 * ext_max))

        if slider_key not in st.session_state:
            st.session_state[slider_key] = default_val

        # Ensure current session value is within valid slider bounds
        current_val = min(ext_max, max(0.0, float(st.session_state[slider_key])))

        # Simulator Subject Card
        with st.container():
            col_left, col_right = st.columns([1.5, 1.0])

            with col_left:
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: baseline; gap: 0.6rem; margin-bottom: 0.2rem;">
                        <h4 style="margin: 0; color: #1E293B;">{subj_name}</h4>
                        <span style="font-size: 0.8rem; color: #64748B;">
                            (Internal: <b>{int_obt:.0f}/{int_max:.0f}</b> • External Max: <b>{ext_max:.0f}</b>)
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                sim_ext = st.slider(
                    f"External Marks for {subj_name}",
                    min_value=0.0,
                    max_value=ext_max,
                    value=current_val,
                    step=1.0,
                    key=slider_key,
                    label_visibility="collapsed",
                )

            # Instant Math Calculation
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

            with col_right:
                grade_class = f"grade-{res['grade'].replace('+', '-plus')}"
                status_class = "status-pass" if res["is_pass"] else "status-fail"
                status_text = "PASS" if res["is_pass"] else "FAIL"

                next_info = res.get("next_grade_info", {})
                next_grade = next_info.get("next_grade")
                marks_to_next = res.get("marks_to_next_grade")

                if next_grade and marks_to_next is not None and res.get("can_reach_next_grade"):
                    target_msg = f"+{marks_to_next:.1f} marks for Grade <b>{next_grade}</b>"
                elif next_info.get("is_highest"):
                    target_msg = "⭐ Highest Grade Achieved"
                else:
                    target_msg = "Top boundary unreachable with remaining marks"

                st.markdown(
                    f"""
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 0.75rem 1rem; margin-top: 0.2rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                            <span style="font-size: 1.15rem; font-weight: 800; color: #1E293B;">
                                {res['total_obtained']:.0f} / {res['total_max']:.0f}
                                <span style="font-size: 0.9rem; color: #4F46E5; font-weight: 700;">({res['percentage']:.1f}%)</span>
                            </span>
                            <div style="display: flex; gap: 0.4rem;">
                                <span class="grade-badge {grade_class}">{res['grade']}</span>
                                <span class="status-pill {status_class}">{status_text}</span>
                            </div>
                        </div>
                        <div style="font-size: 0.78rem; color: #64748B;">
                            🎯 <span>{target_msg}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Visual Progress Bar for Subject Percentage
            pct_norm = min(1.0, max(0.0, res["percentage"] / 100.0))
            st.progress(pct_norm)
            st.markdown("<hr style='margin: 0.8rem 0; border: none; border-top: 1px solid #EDF2F7;'/>", unsafe_allow_html=True)

    # Compute Overall Aggregate
    overall_summary = calculate_overall_percentage(results, passing_percentage)

    # Live Simulation Summary Banner
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 📌 Live Simulation Summary")

    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    with s_col1:
        st.metric("Total Marks Projected", f"{overall_summary['total_obtained']:.0f} / {overall_summary['total_max']:.0f}")
    with s_col2:
        st.metric("Projected Percentage", f"{overall_summary['overall_percentage']:.2f}%")
    with s_col3:
        st.metric("Overall Grade", overall_summary["overall_grade"])
    with s_col4:
        st.metric("Projected CGPA", f"{overall_summary['overall_cgpa']:.2f} / 10.0")

    # Save Current Simulation as Scenario
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    with st.expander("💾 Save Current Simulation as a Scenario"):
        col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
        with col_s1:
            scenario_name_input = st.text_input("Scenario Name", placeholder="e.g. Midterm Target Plan")
        with col_s2:
            scenario_desc_input = st.text_input("Description (Optional)", placeholder="e.g. Aiming for 70%+ in all papers")
        with col_s3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Save Scenario", type="primary", use_container_width=True):
                if not scenario_name_input.strip():
                    st.error("Please provide a name for the scenario.")
                else:
                    scores_map = {r["subject_name"]: r["external_obtained"] for r in results}
                    success, msg = save_scenario(scenario_name_input.strip(), scores_map, scenario_desc_input.strip())
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

    return results, overall_summary


def render_target_grade_calculator(subjects: List[Dict[str, Any]]) -> None:
    """Render the Target Grade Solver component."""
    st.markdown(
        """
        <div class="section-header">
            <h2 class="section-title">
                <span>🎯</span> Target Grade Calculator & Marks Forecaster
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "Determine the precise external examination score you must achieve to secure your desired letter grade. "
        "Select your enrolled subject and chosen target grade below."
    )

    if not subjects:
        st.warning("No subjects enrolled.")
        return

    subject_names = [s["subject_name"] for s in subjects]
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        sel_subj = st.selectbox("Select Subject", subject_names, key="target_calc_subj")

    with col_t2:
        grade_targets = ["O (90%)", "A+ (80%)", "A (70%)", "B+ (60%)", "B (50%)", "C (40%)"]
        sel_target_label = st.selectbox("Select Target Grade", grade_targets, key="target_calc_grade")

    # Extract target percentage
    target_pct_map = {
        "O (90%)": 90.0,
        "A+ (80%)": 80.0,
        "A (70%)": 70.0,
        "B+ (60%)": 60.0,
        "B (50%)": 50.0,
        "C (40%)": 40.0,
    }
    target_pct = target_pct_map[sel_target_label]
    target_grade_char = sel_target_label.split(" ")[0]

    subj_obj = next((s for s in subjects if s["subject_name"] == sel_subj), None)
    if not subj_obj:
        return

    int_obt = float(subj_obj["internal_obtained"])
    int_max = float(subj_obj["internal_max"])
    ext_max = float(subj_obj["external_max"])

    req_data = calculate_required_external_marks(int_obt, int_max, ext_max, target_pct)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Result Banner
    if req_data["status"] == "Achievable":
        req_ext = req_data["required_external"]
        st.markdown(
            f"""
            <div class="custom-card" style="border-left: 6px solid #16A34A; background: #F0FDF4;">
                <h3 style="margin: 0 0 0.5rem 0; color: #166534; font-size: 1.35rem;">
                    ✅ Grade {target_grade_char} is Achievable!
                </h3>
                <p style="font-size: 1.1rem; color: #1E293B; margin: 0 0 0.8rem 0;">
                    You need at least <b>{req_ext:.1f} / {ext_max:.0f}</b> marks in the external examination
                    to achieve <b>Grade {target_grade_char}</b> ({target_pct:.0f}% aggregate).
                </p>
                <div style="font-size: 0.9rem; color: #475569;">
                    <b>Breakdown:</b> Internal Scored: {int_obt:.1f}/{int_max:.0f} •
                    Required External: {req_ext:.1f}/{ext_max:.0f} ({req_ext/ext_max*100:.1f}%) •
                    Target Total: {req_data['target_total_marks']:.1f}/{int_max + ext_max:.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif req_data["status"] == "Already Achieved":
        st.markdown(
            f"""
            <div class="custom-card" style="border-left: 6px solid #4F46E5; background: #EEF2FF;">
                <h3 style="margin: 0 0 0.5rem 0; color: #3730A3; font-size: 1.35rem;">
                    🎉 Already Secured!
                </h3>
                <p style="font-size: 1.1rem; color: #1E293B; margin: 0 0 0.8rem 0;">
                    {req_data['message']}
                </p>
                <div style="font-size: 0.9rem; color: #475569;">
                    Even with 0 marks in the external exam, your internal score secures the required threshold!
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:  # Impossible
        shortfall = req_data["shortfall"]
        max_pct = req_data.get("max_possible_percentage", 0.0)
        st.markdown(
            f"""
            <div class="custom-card" style="border-left: 6px solid #DC2626; background: #FEF2F2;">
                <h3 style="margin: 0 0 0.5rem 0; color: #991B1B; font-size: 1.35rem;">
                    ❌ Target Mathematically Unattainable
                </h3>
                <p style="font-size: 1.05rem; color: #1E293B; margin: 0 0 0.8rem 0;">
                    To achieve {target_pct:.0f}%, you would need <b>{req_data['required_external']:.1f} marks</b>,
                    but the external exam maximum is capped at <b>{ext_max:.0f} marks</b> (shortfall: {shortfall:.1f} marks).
                </p>
                <div style="font-size: 0.9rem; color: #475569;">
                    💡 <b>Maximum Achievable Score:</b> Even if you score 100% ({ext_max:.0f}/{ext_max:.0f}) in the external exam,
                    your maximum possible total is <b>{int_obt + ext_max:.1f} / {int_max + ext_max:.0f} ({max_pct:.1f}%)</b>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Comprehensive Target Table across ALL Grades for this Subject
    st.markdown("#### 📋 Target Matrix for All Letter Grades")
    matrix_rows = []
    for g_label, g_pct in target_pct_map.items():
        calc = calculate_required_external_marks(int_obt, int_max, ext_max, g_pct)
        g_name = g_label.split(" ")[0]

        if calc["status"] == "Achievable":
            status_badge = "✅ Achievable"
            req_str = f"{calc['required_external']:.1f} / {ext_max:.0f} ({calc['required_external']/ext_max*100:.1f}%)"
        elif calc["status"] == "Already Achieved":
            status_badge = "⭐ Already Secured"
            req_str = "0.0 / " + f"{ext_max:.0f}"
        else:
            status_badge = "❌ Unattainable"
            req_str = f"Needs {calc['required_external']:.1f} (Exceeds Max {ext_max:.0f})"

        matrix_rows.append({
            "Grade": g_name,
            "Target Percentage": f"{g_pct:.0f}%",
            "Target Total Marks": f"{calc['target_total_marks']:.1f} / {int_max + ext_max:.0f}",
            "Required External Score": req_str,
            "Feasibility": status_badge,
        })

    df_matrix = pd.DataFrame(matrix_rows)
    st.dataframe(df_matrix, use_container_width=True, hide_index=True)


def render_scenario_comparison(subjects: List[Dict[str, Any]], passing_percentage: float = 40.0) -> None:
    """Render the Multi-Scenario Comparison component."""
    st.markdown(
        """
        <div class="section-header">
            <h2 class="section-title">
                <span>⚖️</span> Academic Scenario Comparison
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "Compare projected outcomes across standard performance attempts "
        "(Safe 40%, Average 60%, Strong 80%) alongside your saved custom scenarios."
    )

    if not subjects:
        st.warning("No subjects configured.")
        return

    # Fetch saved scenarios from SQLite
    saved_scenarios = get_saved_scenarios()

    # Pre-defined benchmark scenarios
    benchmark_scenarios = [
        {"name": "Safe (40%)", "factor": 0.40},
        {"name": "Average (60%)", "factor": 0.60},
        {"name": "Strong (80%)", "factor": 0.80},
    ]

    # Build comparison dataset
    comparison_table = []
    scenario_names = ["Safe (40%)", "Average (60%)", "Strong (80%)"]

    # Also include any saved scenarios
    saved_scores_map = {}
    for sc in saved_scenarios:
        sc_name = sc["scenario_name"]
        scenario_names.append(sc_name)
        saved_scores_map[sc_name] = get_scenario_scores(sc["id"])

    for s in subjects:
        subj_name = s["subject_name"]
        int_max = float(s["internal_max"])
        int_obt = float(s["internal_obtained"])
        ext_max = float(s["external_max"])

        row = {"subject_name": subj_name}

        # Benchmarks
        for bm in benchmark_scenarios:
            sim_ext = round(bm["factor"] * ext_max)
            tot_obt = int_obt + sim_ext
            tot_max = int_max + ext_max
            pct = round(tot_obt / tot_max * 100.0, 1)
            gr = get_grade(pct, passing_percentage)

            row[f"{bm['name']}_ext"] = sim_ext
            row[f"{bm['name']}_pct"] = pct
            row[f"{bm['name']}_grade"] = gr

        # Saved scenarios
        for sc in saved_scenarios:
            sc_name = sc["scenario_name"]
            sim_ext = saved_scores_map[sc_name].get(subj_name, round(0.60 * ext_max))
            tot_obt = int_obt + sim_ext
            tot_max = int_max + ext_max
            pct = round(tot_obt / tot_max * 100.0, 1)
            gr = get_grade(pct, passing_percentage)

            row[f"{sc_name}_ext"] = sim_ext
            row[f"{sc_name}_pct"] = pct
            row[f"{sc_name}_grade"] = gr

        comparison_table.append(row)

    # 1. Comparison Chart
    st.plotly_chart(
        create_scenario_comparison_chart(comparison_table, scenario_names[:4]),
        use_container_width=True,
    )

    # 2. Comparison Summary Table
    st.markdown("#### 📋 Scenario Grade Matrix")
    display_rows = []
    for row in comparison_table:
        d_row = {"Subject": row["subject_name"]}
        for sc_name in scenario_names[:5]:  # show up to 5 scenarios cleanly
            d_row[sc_name] = f"{row.get(f'{sc_name}_pct', 0.0):.1f}% ({row.get(f'{sc_name}_grade', '-')})"
        display_rows.append(d_row)

    df_comp = pd.DataFrame(display_rows)
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    # 3. Manage Saved Scenarios
    if saved_scenarios:
        st.markdown("#### 📁 Saved Scenarios Library")
        for sc in saved_scenarios:
            col_sc1, col_sc2, col_sc3 = st.columns([3, 2, 1])
            with col_sc1:
                st.write(f"**{sc['scenario_name']}** — {sc.get('description', '')}")
            with col_sc2:
                st.caption(f"Created: {sc['created_at']}")
            with col_sc3:
                if st.button("🗑️ Delete", key=f"del_sc_{sc['id']}"):
                    delete_scenario(sc["id"])
                    st.rerun()
