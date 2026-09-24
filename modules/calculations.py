"""Calculations Module for Internal Marks 'What-If' Simulator.

Contains reusable, pure-logic mathematical and grading functions.
Provides strict division-by-zero protection and robust boundary handling.
"""

from typing import Any, Dict, List, Optional, Tuple

# Default university standard grading system (Common for MCA / Engineering programs)
DEFAULT_GRADE_SCALE: List[Tuple[str, float]] = [
    ("O", 90.0),    # Outstanding: 90.0% to 100%
    ("A+", 80.0),   # Excellent: 80.0% to 89.99%
    ("A", 70.0),    # Very Good: 70.0% to 79.99%
    ("B+", 60.0),   # Good: 60.0% to 69.99%
    ("B", 50.0),    # Above Average: 50.0% to 59.99%
    ("C", 40.0),    # Pass: 40.0% to 49.99%
    ("F", 0.0),     # Fail: Below 40.0%
]

GRADE_COLORS: Dict[str, str] = {
    "O": "#4F46E5",     # Deep Indigo
    "A+": "#16A34A",    # Rich Emerald Green
    "A": "#059669",     # Teal Green
    "B+": "#D97706",    # Warm Amber
    "B": "#EA580C",     # Orange
    "C": "#64748B",     # Slate Gray
    "F": "#DC2626",     # Crimson Red
}

GRADE_POINTS: Dict[str, int] = {
    "O": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C": 5,
    "F": 0,
}

GRADE_DESCRIPTIONS: Dict[str, str] = {
    "O": "Outstanding (10 Grade Points)",
    "A+": "Excellent (9 Grade Points)",
    "A": "Very Good (8 Grade Points)",
    "B+": "Good (7 Grade Points)",
    "B": "Above Average (6 Grade Points)",
    "C": "Pass (5 Grade Points)",
    "F": "Fail (Reappear Required)",
}


def get_grade(
    percentage: float,
    passing_percentage: float = 40.0,
    grade_scale: Optional[List[Tuple[str, float]]] = None
) -> str:
    """Determine letter grade based on percentage and passing threshold.

    Args:
        percentage: Calculated total score percentage.
        passing_percentage: Minimum percentage required to pass.
        grade_scale: Optional custom list of (grade, min_percentage) tuples descending.

    Returns:
        Letter grade string (e.g. 'O', 'A+', 'A', 'B+', 'B', 'C', 'F').
    """
    pct = round(max(0.0, min(100.0, float(percentage))), 2)

    if pct < passing_percentage:
        return "F"

    scale = grade_scale or DEFAULT_GRADE_SCALE
    for grade, min_pct in scale:
        if grade != "F" and pct >= min_pct:
            return grade

    return "F"


def get_next_grade_info(
    percentage: float,
    passing_percentage: float = 40.0,
    grade_scale: Optional[List[Tuple[str, float]]] = None
) -> Dict[str, Any]:
    """Calculate the target boundary and percentage points needed for the next grade.

    Args:
        percentage: Current subject or overall percentage.
        passing_percentage: Minimum passing percentage.
        grade_scale: Optional custom grading scale.

    Returns:
        Dict with keys:
            - current_grade (str)
            - next_grade (Optional[str])
            - next_grade_min_pct (Optional[float])
            - pct_needed (float)
            - is_highest (bool)
    """
    scale = grade_scale or DEFAULT_GRADE_SCALE
    pct = round(max(0.0, min(100.0, float(percentage))), 2)
    current_grade = get_grade(pct, passing_percentage, scale)

    # Sort descending by min_pct
    sorted_scale = sorted(
        [item for item in scale if item[0] != "F"],
        key=lambda x: x[1],
        reverse=True
    )

    # If already at top grade
    if current_grade == sorted_scale[0][0]:
        return {
            "current_grade": current_grade,
            "next_grade": None,
            "next_grade_min_pct": None,
            "pct_needed": 0.0,
            "is_highest": True,
        }

    # If failing, next target is passing grade 'C'
    if current_grade == "F":
        target_grade = "C"
        target_pct = passing_percentage
        pct_needed = round(max(0.0, target_pct - pct), 2)
        return {
            "current_grade": current_grade,
            "next_grade": target_grade,
            "next_grade_min_pct": target_pct,
            "pct_needed": pct_needed,
            "is_highest": False,
        }

    # Find the next higher grade threshold
    for i in range(len(sorted_scale) - 1, -1, -1):
        grade_name, min_pct = sorted_scale[i]
        if min_pct > pct:
            pct_needed = round(min_pct - pct, 2)
            return {
                "current_grade": current_grade,
                "next_grade": grade_name,
                "next_grade_min_pct": min_pct,
                "pct_needed": pct_needed,
                "is_highest": False,
            }

    return {
        "current_grade": current_grade,
        "next_grade": None,
        "next_grade_min_pct": None,
        "pct_needed": 0.0,
        "is_highest": True,
    }


def calculate_subject_result(
    internal_obtained: float,
    internal_max: float,
    external_obtained: float,
    external_max: float,
    passing_percentage: float = 40.0,
    grade_scale: Optional[List[Tuple[str, float]]] = None
) -> Dict[str, Any]:
    """Calculate complete academic result for an individual subject under simulation.

    Args:
        internal_obtained: Marks scored in internal assessments.
        internal_max: Maximum internal marks possible.
        external_obtained: Simulated or actual external marks.
        external_max: Maximum external exam marks.
        passing_percentage: University passing cutoff (default 40%).
        grade_scale: Optional custom grading scale.

    Returns:
        Structured dictionary of marks, percentage, grade, pass status, and targets.
    """
    int_obt = float(internal_obtained)
    int_max = float(internal_max)
    ext_obt = float(external_obtained)
    ext_max = float(external_max)

    total_obtained = round(int_obt + ext_obt, 2)
    total_max = round(int_max + ext_max, 2)

    percentage = round((total_obtained / total_max * 100.0) if total_max > 0 else 0.0, 2)
    grade = get_grade(percentage, passing_percentage, grade_scale)
    is_pass = percentage >= passing_percentage

    # Calculate marks needed to pass
    pass_marks_required = round((passing_percentage / 100.0) * total_max, 2)
    marks_to_pass = max(0.0, round(pass_marks_required - total_obtained, 2))

    # Next grade analysis
    next_info = get_next_grade_info(percentage, passing_percentage, grade_scale)
    marks_to_next_grade: Optional[float] = None
    can_reach_next_grade: bool = False

    if next_info["next_grade_min_pct"] is not None:
        target_total = round((next_info["next_grade_min_pct"] / 100.0) * total_max, 2)
        diff = round(target_total - total_obtained, 2)
        marks_to_next_grade = max(0.0, diff)
        # Check if remaining external marks capacity can accommodate this requirement
        remaining_ext_capacity = ext_max - ext_obt
        can_reach_next_grade = marks_to_next_grade <= remaining_ext_capacity

    return {
        "internal_obtained": int_obt,
        "internal_max": int_max,
        "external_obtained": ext_obt,
        "external_max": ext_max,
        "total_obtained": total_obtained,
        "total_max": total_max,
        "percentage": percentage,
        "grade": grade,
        "grade_point": GRADE_POINTS.get(grade, 0),
        "is_pass": is_pass,
        "pass_marks_required": pass_marks_required,
        "marks_to_pass": marks_to_pass,
        "next_grade_info": next_info,
        "marks_to_next_grade": marks_to_next_grade,
        "can_reach_next_grade": can_reach_next_grade,
    }


def calculate_overall_percentage(
    subject_results: List[Dict[str, Any]],
    passing_percentage: float = 40.0,
    grade_scale: Optional[List[Tuple[str, float]]] = None
) -> Dict[str, Any]:
    """Calculate overall aggregate performance across all subjects.

    Args:
        subject_results: List of subject result dictionaries (including 'attendance' if available).
        passing_percentage: Passing threshold.
        grade_scale: Optional custom grading scale.

    Returns:
        Comprehensive aggregate metrics dictionary.
    """
    total_subjects = len(subject_results)
    if total_subjects == 0:
        return {
            "total_subjects": 0,
            "total_internal_obtained": 0.0,
            "total_internal_max": 0.0,
            "total_external_obtained": 0.0,
            "total_external_max": 0.0,
            "total_obtained": 0.0,
            "total_max": 0.0,
            "overall_percentage": 0.0,
            "overall_grade": "N/A",
            "overall_cgpa": 0.0,
            "is_pass": False,
            "passing_count": 0,
            "failing_count": 0,
            "attendance_risk_count": 0,
            "average_internal_marks": 0.0,
            "average_external_marks": 0.0,
            "average_total_marks": 0.0,
            "weakest_subject": None,
            "strongest_subject": None,
        }

    total_int_obt = sum(r["internal_obtained"] for r in subject_results)
    total_int_max = sum(r["internal_max"] for r in subject_results)
    total_ext_obt = sum(r["external_obtained"] for r in subject_results)
    total_ext_max = sum(r["external_max"] for r in subject_results)

    total_obt = total_int_obt + total_ext_obt
    total_max = total_int_max + total_ext_max

    overall_percentage = round((total_obt / total_max * 100.0) if total_max > 0 else 0.0, 2)
    overall_grade = get_grade(overall_percentage, passing_percentage, grade_scale)

    passing_count = sum(1 for r in subject_results if r["is_pass"])
    failing_count = total_subjects - passing_count
    is_all_passed = (failing_count == 0) and (overall_percentage >= passing_percentage)

    # CGPA calculation (Average Grade Points)
    total_grade_points = sum(r.get("grade_point", GRADE_POINTS.get(r.get("grade", "F"), 0)) for r in subject_results)
    overall_cgpa = round(total_grade_points / total_subjects, 2)

    # Attendance risk count
    attendance_risk_count = sum(
        1 for r in subject_results if r.get("attendance", 100.0) < 75.0
    )

    # Weakest and strongest subjects
    weakest = min(subject_results, key=lambda x: x["percentage"])
    strongest = max(subject_results, key=lambda x: x["percentage"])

    return {
        "total_subjects": total_subjects,
        "total_internal_obtained": round(total_int_obt, 2),
        "total_internal_max": round(total_int_max, 2),
        "total_external_obtained": round(total_ext_obt, 2),
        "total_external_max": round(total_ext_max, 2),
        "total_obtained": round(total_obt, 2),
        "total_max": round(total_max, 2),
        "overall_percentage": overall_percentage,
        "overall_grade": overall_grade,
        "overall_cgpa": overall_cgpa,
        "is_pass": is_all_passed,
        "passing_count": passing_count,
        "failing_count": failing_count,
        "attendance_risk_count": attendance_risk_count,
        "average_internal_marks": round(total_int_obt / total_subjects, 2),
        "average_external_marks": round(total_ext_obt / total_subjects, 2),
        "average_total_marks": round(total_obt / total_subjects, 2),
        "weakest_subject": weakest,
        "strongest_subject": strongest,
    }


def calculate_required_external_marks(
    internal_obtained: float,
    internal_max: float,
    external_max: float,
    target_percentage: float
) -> Dict[str, Any]:
    """Calculate the exact minimum external marks required to secure a target percentage.

    Formula:
        Total Max = internal_max + external_max
        Target Total Marks = (target_percentage / 100) * Total Max
        Required External Marks = Target Total Marks - internal_obtained

    Args:
        internal_obtained: Internal marks already scored.
        internal_max: Maximum internal marks.
        external_max: Maximum external exam marks.
        target_percentage: Desired overall percentage.

    Returns:
        Dict with status, required_external, shortfall, and descriptive message.
    """
    int_obt = float(internal_obtained)
    int_max = float(internal_max)
    ext_max = float(external_max)
    target_pct = float(target_percentage)

    total_max = int_max + ext_max
    if total_max <= 0:
        return {
            "status": "Invalid",
            "required_external": 0.0,
            "target_total_marks": 0.0,
            "shortfall": 0.0,
            "message": "Maximum marks cannot be zero.",
            "is_achievable": False,
        }

    target_total = round((target_pct / 100.0) * total_max, 2)
    raw_required_ext = round(target_total - int_obt, 2)

    if raw_required_ext <= 0:
        # Already secured without external marks!
        return {
            "status": "Already Achieved",
            "required_external": 0.0,
            "raw_required_external": raw_required_ext,
            "target_total_marks": target_total,
            "shortfall": 0.0,
            "message": f"Your internal score of {int_obt:.1f} alone already satisfies the {target_pct:.1f}% threshold!",
            "is_achievable": True,
        }
    elif raw_required_ext <= ext_max:
        return {
            "status": "Achievable",
            "required_external": raw_required_ext,
            "raw_required_external": raw_required_ext,
            "target_total_marks": target_total,
            "shortfall": 0.0,
            "message": f"You need at least {raw_required_ext:.1f} / {ext_max:.0f} in the external exam.",
            "is_achievable": True,
        }
    else:
        shortfall = round(raw_required_ext - ext_max, 2)
        max_possible_total = int_obt + ext_max
        max_possible_pct = round((max_possible_total / total_max) * 100.0, 2)
        return {
            "status": "Impossible",
            "required_external": raw_required_ext,
            "raw_required_external": raw_required_ext,
            "target_total_marks": target_total,
            "shortfall": shortfall,
            "max_possible_percentage": max_possible_pct,
            "message": (
                f"Requires {raw_required_ext:.1f} marks, but maximum external marks is only {ext_max:.0f}. "
                f"Highest possible score is {max_possible_pct:.1f}%."
            ),
            "is_achievable": False,
        }


def check_attendance_risk(
    attendance: float,
    minimum_attendance: float = 75.0
) -> Dict[str, Any]:
    """Check whether a student's attendance meets the university eligibility criteria.

    Args:
        attendance: Current student attendance percentage.
        minimum_attendance: Minimum threshold (default 75%).

    Returns:
        Dict with is_risk, shortfall, status, and formal warning message.
    """
    att = round(float(attendance), 1)
    min_att = round(float(minimum_attendance), 1)

    if att < min_att:
        shortfall = round(min_att - att, 1)
        return {
            "is_risk": True,
            "attendance": att,
            "minimum_attendance": min_att,
            "shortfall": shortfall,
            "status": "Shortage Warning",
            "warning_message": (
                f"Attendance shortage detected ({att}% vs required {min_att}%). "
                f"You are short by {shortfall}%. Your examination eligibility may be affected according to university rules."
            ),
        }
    return {
        "is_risk": False,
        "attendance": att,
        "minimum_attendance": min_att,
        "shortfall": 0.0,
        "status": "Eligible",
        "warning_message": f"Attendance satisfactory ({att}% >= {min_att}%). Eligible to appear for examinations.",
    }
