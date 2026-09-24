"""Charts Module for Internal Marks 'What-If' Simulator.

Generates responsive, interactive Plotly visualizations for academic metrics,
grade distributions, internal-external split, grade boundaries, and multi-scenario comparisons.
"""

from typing import Any, Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go
from modules.calculations import GRADE_COLORS, DEFAULT_GRADE_SCALE

# Visual Theme Constants
FONT_FAMILY = "Plus Jakarta Sans, sans-serif"
COLOR_PASS = "#16A34A"     # Green
COLOR_FAIL = "#DC2626"     # Red
COLOR_WARNING = "#F59E0B"  # Amber
COLOR_PRIMARY = "#4F46E5"  # Indigo
COLOR_SECONDARY = "#6366F1"


def create_subject_percentage_chart(
    results: List[Dict[str, Any]],
    passing_percentage: float = 40.0
) -> go.Figure:
    """Create interactive bar chart showing projected percentage per subject with pass/fail indicators."""
    subjects = [r["subject_name"] for r in results]
    percentages = [r["percentage"] for r in results]
    colors = [COLOR_PASS if r["is_pass"] else COLOR_FAIL for r in results]
    status_text = ["PASS" if r["is_pass"] else "FAIL" for r in results]
    grades = [r["grade"] for r in results]

    hover_text = [
        f"<b>{subj}</b><br>"
        f"Projected Score: <b>{pct:.1f}%</b><br>"
        f"Grade: <b>{gr}</b> ({st})<br>"
        f"Total: {r['total_obtained']:.1f} / {r['total_max']:.1f}"
        for subj, pct, gr, st, r in zip(subjects, percentages, grades, status_text, results)
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=subjects,
            y=percentages,
            text=[f"{p:.1f}% ({g})" for p, g in zip(percentages, grades)],
            textposition="outside",
            marker=dict(
                color=colors,
                line=dict(color="rgba(0,0,0,0.1)", width=1),
                opacity=0.9,
            ),
            hoverinfo="text",
            hovertext=hover_text,
            name="Subject %",
        )
    )

    # Reference line for Passing Cutoff
    fig.add_hline(
        y=passing_percentage,
        line_dash="dot",
        line_color="#E11D48",
        line_width=2,
        annotation_text=f"Passing Cutoff ({passing_percentage:.0f}%)",
        annotation_position="top right",
        annotation_font=dict(size=11, color="#BE123C", family=FONT_FAMILY),
    )

    fig.update_layout(
        title=dict(
            text="<b>Subject-Wise Projected Percentage & Status</b>",
            font=dict(size=16, family=FONT_FAMILY, color="#1E293B"),
            x=0.0,
        ),
        xaxis=dict(
            title="",
            tickfont=dict(size=12, family=FONT_FAMILY, color="#334155"),
            gridcolor="#F1F5F9",
        ),
        yaxis=dict(
            title="Percentage (%)",
            range=[0, 110],
            tickfont=dict(size=11, family=FONT_FAMILY),
            gridcolor="#E2E8F0",
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=40, r=30, t=60, b=40),
        font=dict(family=FONT_FAMILY),
        showlegend=False,
    )

    return fig


def create_grade_distribution_chart(results: List[Dict[str, Any]]) -> go.Figure:
    """Create interactive Donut chart showing distribution across letter grades."""
    grade_counts: Dict[str, int] = {}
    for r in results:
        g = r["grade"]
        grade_counts[g] = grade_counts.get(g, 0) + 1

    # Order grades according to standard hierarchy
    all_grades = ["O", "A+", "A", "B+", "B", "C", "F"]
    labels = [g for g in all_grades if g in grade_counts]
    values = [grade_counts[g] for g in labels]
    colors = [GRADE_COLORS.get(g, "#64748B") for g in labels]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
                textinfo="label+value",
                textfont=dict(size=13, family=FONT_FAMILY, color="#FFFFFF"),
                hoverinfo="label+percent+value",
                hovertemplate="<b>Grade %{label}</b><br>Count: %{value} subjects<br>Share: %{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="<b>Projected Grade Distribution</b>",
            font=dict(size=16, family=FONT_FAMILY, color="#1E293B"),
            x=0.0,
        ),
        font=dict(family=FONT_FAMILY),
        paper_bgcolor="#FFFFFF",
        margin=dict(l=30, r=30, t=50, b=30),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=11, family=FONT_FAMILY),
        ),
        annotations=[
            dict(
                text=f"<b>{len(results)}</b><br><span style='font-size:10px; color:#64748B;'>Subjects</span>",
                x=0.5,
                y=0.5,
                font=dict(size=18, family=FONT_FAMILY, color="#1E293B"),
                showarrow=False,
            )
        ],
    )

    return fig


def create_internal_external_split_chart(results: List[Dict[str, Any]]) -> go.Figure:
    """Create grouped bar chart comparing Internal marks obtained vs Simulated External marks."""
    subjects = [r["subject_name"] for r in results]
    internal_scores = [r["internal_obtained"] for r in results]
    internal_maxes = [r["internal_max"] for r in results]
    external_scores = [r["external_obtained"] for r in results]
    external_maxes = [r["external_max"] for r in results]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Internal Marks Scored",
            x=subjects,
            y=internal_scores,
            text=[f"{s:.0f}/{m:.0f}" for s, m in zip(internal_scores, internal_maxes)],
            textposition="auto",
            marker=dict(color="#4F46E5", opacity=0.9),
            hovertemplate="<b>%{x}</b><br>Internal Scored: %{y:.1f} marks<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            name="Simulated External Marks",
            x=subjects,
            y=external_scores,
            text=[f"{s:.0f}/{m:.0f}" for s, m in zip(external_scores, external_maxes)],
            textposition="auto",
            marker=dict(color="#06B6D4", opacity=0.9),
            hovertemplate="<b>%{x}</b><br>Simulated External: %{y:.1f} marks<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="group",
        title=dict(
            text="<b>Internal vs. Simulated External Marks Comparison</b>",
            font=dict(size=16, family=FONT_FAMILY, color="#1E293B"),
            x=0.0,
        ),
        xaxis=dict(
            tickfont=dict(size=12, family=FONT_FAMILY),
            gridcolor="#F1F5F9",
        ),
        yaxis=dict(
            title="Marks",
            tickfont=dict(size=11, family=FONT_FAMILY),
            gridcolor="#E2E8F0",
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=40, r=30, t=60, b=40),
        font=dict(family=FONT_FAMILY),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, family=FONT_FAMILY),
        ),
    )

    return fig


def create_scenario_comparison_chart(
    comparison_data: List[Dict[str, Any]],
    scenario_names: List[str]
) -> go.Figure:
    """Create grouped bar chart comparing subject percentages across multiple scenarios."""
    subjects = [row["subject_name"] for row in comparison_data]
    fig = go.Figure()

    palette = ["#94A3B8", "#3B82F6", "#10B981", "#8B5CF6", "#F59E0B"]

    for i, sc_name in enumerate(scenario_names):
        color = palette[i % len(palette)]
        percentages = [row.get(f"{sc_name}_pct", 0.0) for row in comparison_data]
        grades = [row.get(f"{sc_name}_grade", "-") for row in comparison_data]

        fig.add_trace(
            go.Bar(
                name=sc_name,
                x=subjects,
                y=percentages,
                text=[f"{p:.1f}% ({g})" for p, g in zip(percentages, grades)],
                textposition="auto",
                marker=dict(color=color, opacity=0.9),
                hovertemplate=f"<b>%{{x}}</b> [{sc_name}]<br>Percentage: %{{y:.1f}}%<extra></extra>",
            )
        )

    fig.update_layout(
        barmode="group",
        title=dict(
            text="<b>Multi-Scenario Performance Comparison</b>",
            font=dict(size=16, family=FONT_FAMILY, color="#1E293B"),
            x=0.0,
        ),
        xaxis=dict(
            tickfont=dict(size=12, family=FONT_FAMILY),
            gridcolor="#F1F5F9",
        ),
        yaxis=dict(
            title="Projected Percentage (%)",
            range=[0, 115],
            tickfont=dict(size=11, family=FONT_FAMILY),
            gridcolor="#E2E8F0",
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=40, r=30, t=60, b=40),
        font=dict(family=FONT_FAMILY),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, family=FONT_FAMILY),
        ),
    )

    return fig


def create_grade_boundary_visualizer(
    percentage: float,
    subject_name: str = "Overall Aggregate",
    passing_percentage: float = 40.0
) -> go.Figure:
    """Create a bullet / gauge visual showing current score relative to university grade boundaries."""
    # Grade scale boundaries: F(<40), C(40-50), B(50-60), B+(60-70), A(70-80), A+(80-90), O(90-100)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=percentage,
            domain=dict(x=[0, 1], y=[0, 1]),
            title=dict(
                text=f"<b>{subject_name}</b><br><span style='font-size:12px; color:#64748B;'>Score vs. Grade Cutoffs</span>",
                font=dict(size=15, family=FONT_FAMILY, color="#1E293B"),
            ),
            delta=dict(
                reference=passing_percentage,
                increasing=dict(color="#16A34A"),
                decreasing=dict(color="#DC2626"),
                prefix="vs Pass: ",
                font=dict(size=12, family=FONT_FAMILY),
            ),
            gauge=dict(
                axis=dict(
                    range=[0, 100],
                    tickwidth=1,
                    tickcolor="#475569",
                    tickvals=[0, 40, 50, 60, 70, 80, 90, 100],
                    ticktext=["0", "Pass(40)", "B(50)", "B+(60)", "A(70)", "A+(80)", "O(90)", "100"],
                    tickfont=dict(size=9, family=FONT_FAMILY),
                ),
                bar=dict(color="#4F46E5", thickness=0.3),
                bgcolor="white",
                borderwidth=1,
                bordercolor="#E2E8F0",
                steps=[
                    dict(range=[0, 40], color="#FEE2E2"),    # F (Red)
                    dict(range=[40, 50], color="#F1F5F9"),   # C (Slate)
                    dict(range=[50, 60], color="#FEF3C7"),   # B (Amber light)
                    dict(range=[60, 70], color="#FDE68A"),   # B+ (Amber)
                    dict(range=[70, 80], color="#D1FAE5"),   # A (Emerald light)
                    dict(range=[80, 90], color="#A7F3D0"),   # A+ (Emerald)
                    dict(range=[90, 100], color="#C7D2FE"),  # O (Indigo light)
                ],
                threshold=dict(
                    line=dict(color="#DC2626", width=3),
                    thickness=0.8,
                    value=passing_percentage,
                ),
            ),
        )
    )

    fig.update_layout(
        height=260,
        margin=dict(l=25, r=25, t=50, b=25),
        paper_bgcolor="#FFFFFF",
        font=dict(family=FONT_FAMILY),
    )

    return fig


def create_attendance_overview_chart(
    subjects_data: List[Dict[str, Any]],
    min_attendance: float = 75.0
) -> go.Figure:
    """Create horizontal bar chart showing student attendance percentage and flagging risk subjects."""
    names = [s["subject_name"] for s in subjects_data]
    attendances = [s["attendance"] for s in subjects_data]
    colors = [COLOR_PASS if att >= min_attendance else COLOR_FAIL for att in attendances]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=names,
            x=attendances,
            orientation="h",
            text=[f"{att:.1f}% ({'Eligible' if att >= min_attendance else 'SHORTAGE'})" for att in attendances],
            textposition="auto",
            marker=dict(color=colors, opacity=0.9),
            hovertemplate="<b>%{y}</b><br>Attendance: %{x:.1f}%<extra></extra>",
        )
    )

    fig.add_vline(
        x=min_attendance,
        line_dash="dash",
        line_color="#DC2626",
        line_width=2,
        annotation_text=f"Eligibility Threshold ({min_attendance:.0f}%)",
        annotation_position="top right",
        annotation_font=dict(size=10, color="#DC2626", family=FONT_FAMILY),
    )

    fig.update_layout(
        title=dict(
            text="<b>Subject Attendance & Exam Eligibility</b>",
            font=dict(size=16, family=FONT_FAMILY, color="#1E293B"),
            x=0.0,
        ),
        xaxis=dict(
            title="Attendance (%)",
            range=[0, 110],
            tickfont=dict(size=11, family=FONT_FAMILY),
            gridcolor="#E2E8F0",
        ),
        yaxis=dict(
            tickfont=dict(size=12, family=FONT_FAMILY),
            autorange="reversed",
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=40, r=30, t=50, b=40),
        font=dict(family=FONT_FAMILY),
        showlegend=False,
    )

    return fig
