"""Recommendations Module for Internal Marks 'What-If' Simulator.

Generates precise, rule-based academic advisory insights, weakest subject diagnostics,
attendance shortage alerts, and next-grade acceleration tips.
"""

from typing import Any, Dict, List, Optional


def generate_recommendations(
    subject_results: List[Dict[str, Any]],
    overall_summary: Dict[str, Any],
    min_attendance: float = 75.0,
    passing_percentage: float = 40.0,
) -> Dict[str, Any]:
    """Generate categorized actionable insights and recommendations based on simulated academic data.

    Returns:
        Dict with keys:
            - critical_warnings: List[str]
            - priority_improvements: List[str]
            - grade_opportunities: List[str]
            - positive_highlights: List[str]
            - weakest_subject_analysis: Optional[Dict]
    """
    critical_warnings: List[str] = []
    priority_improvements: List[str] = []
    grade_opportunities: List[str] = []
    positive_highlights: List[str] = []

    if not subject_results:
        return {
            "critical_warnings": [],
            "priority_improvements": [],
            "grade_opportunities": [],
            "positive_highlights": [],
            "weakest_subject_analysis": None,
        }

    # 1. Attendance Shortage Audit
    shortage_subjects = [s for s in subject_results if s.get("attendance", 100.0) < min_attendance]
    if shortage_subjects:
        for s in shortage_subjects:
            shortfall = round(min_attendance - s["attendance"], 1)
            critical_warnings.append(
                f"⚠️ **Attendance Shortage in {s['subject_name']}**: Current attendance is {s['attendance']:.1f}% "
                f"(short by {shortfall}% from required {min_attendance:.0f}%). "
                f"Check your university's condonation/eligibility guidelines immediately."
            )
    else:
        positive_highlights.append(
            f"✅ **Attendance Compliant**: All subjects meet or exceed the {min_attendance:.0f}% university eligibility requirement."
        )

    # 2. Failing Subjects Evaluation
    failing_subjects = [s for s in subject_results if not s["is_pass"]]
    if failing_subjects:
        for s in failing_subjects:
            priority_improvements.append(
                f"🚨 **Pass Risk in {s['subject_name']}**: Projected total is {s['percentage']:.1f}% (Grade F). "
                f"You need at least **{s['marks_to_pass']:.1f} additional external marks** "
                f"to reach the passing cutoff ({passing_percentage:.0f}%)."
            )
    else:
        positive_highlights.append(
            f"🎉 **All Subjects Passing**: Every enrolled subject is projected at or above the {passing_percentage:.0f}% passing threshold."
        )

    # 3. Next Grade Close Calls / Quick Win Opportunities
    for s in subject_results:
        if s["is_pass"]:
            next_info = s.get("next_grade_info", {})
            next_grade = next_info.get("next_grade")
            marks_needed = s.get("marks_to_next_grade")
            can_reach = s.get("can_reach_next_grade", False)

            if next_grade and marks_needed is not None and marks_needed <= 5.0 and can_reach:
                grade_opportunities.append(
                    f"🚀 **Near Grade Boundary in {s['subject_name']}**: You are only **{marks_needed:.1f} marks** away "
                    f"from upgrading from **{s['grade']}** to **Grade {next_grade}**!"
                )

    # 4. Weakest Subject In-Depth Diagnostics
    weakest = overall_summary.get("weakest_subject")
    weakest_analysis = None
    if weakest:
        weakest_analysis = {
            "subject_name": weakest["subject_name"],
            "percentage": weakest["percentage"],
            "grade": weakest["grade"],
            "is_pass": weakest["is_pass"],
            "internal_score": f"{weakest['internal_obtained']:.1f} / {weakest['internal_max']:.1f}",
            "simulated_external": f"{weakest['external_obtained']:.1f} / {weakest['external_max']:.1f}",
            "marks_to_pass": weakest["marks_to_pass"],
            "next_grade": weakest.get("next_grade_info", {}).get("next_grade"),
            "marks_to_next_grade": weakest.get("marks_to_next_grade"),
            "advice": (
                f"Concentrate your revision on '{weakest['subject_name']}'. "
                + (
                    f"Increase simulated external marks by at least {weakest['marks_to_pass']:.1f} marks to avoid a backlog."
                    if not weakest["is_pass"]
                    else (
                        f"Aim for {weakest.get('marks_to_next_grade', 0.0):.1f} extra marks to elevate to Grade {weakest.get('next_grade_info', {}).get('next_grade')}."
                        if weakest.get("marks_to_next_grade")
                        else "Consistent performance will preserve this standing."
                    )
                )
            ),
        }

    # 5. Overall Performance Tier
    ov_pct = overall_summary.get("overall_percentage", 0.0)
    if ov_pct >= 80.0:
        positive_highlights.append(
            f"🌟 **First Class with Distinction**: Projected aggregate of {ov_pct:.1f}% places you in the premier academic bracket."
        )
    elif ov_pct >= 60.0:
        positive_highlights.append(
            f"📘 **First Class Standing**: Projected aggregate of {ov_pct:.1f}% is solid. Targeted push in external exams can reach Distinction."
        )
    elif ov_pct >= 50.0:
        priority_improvements.append(
            f"📈 **Second Class Standing**: Current aggregate is {ov_pct:.1f}%. Increasing external scores by 5-10% will lift overall standing to First Class."
        )

    return {
        "critical_warnings": critical_warnings,
        "priority_improvements": priority_improvements,
        "grade_opportunities": grade_opportunities,
        "positive_highlights": positive_highlights,
        "weakest_subject_analysis": weakest_analysis,
    }
