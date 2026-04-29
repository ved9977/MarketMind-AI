"""
agents/execution_planner.py
===========================
ExecutionPlanner – converts the structured JSON plan produced by PlannerAgent
into a rich, human-readable document that includes:

  1. Numbered task list with dependency annotations.
  2. Day-wise / week-wise timeline.
  3. ASCII dependency graph (topological text-tree).

This module is pure Python and has no LLM dependency, making it fast and
deterministic — ideal for downstream display in the Streamlit UI.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Optional

from agents.planner_agent import MarketingPlan, PlanStep


# ---------------------------------------------------------------------------
# ExecutionPlanner
# ---------------------------------------------------------------------------

class ExecutionPlanner:
    """
    Transforms a MarketingPlan into human-readable execution artefacts.

    Parameters
    ----------
    days_per_step : int
        Estimated calendar days required to complete each step (default: 3).
    """

    def __init__(self, days_per_step: int = 3) -> None:
        self.days_per_step = days_per_step

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_readable_plan(self, plan: MarketingPlan, goal: str = "") -> str:
        """
        Produce a full human-readable execution plan string.

        Parameters
        ----------
        plan : MarketingPlan
            Validated plan from PlannerAgent.
        goal : str
            Optional goal string shown in the header.

        Returns
        -------
        str
            Multi-section formatted plan ready for printing or display.
        """
        sections = [
            self._header(goal),
            self._task_list(plan),
            self._timeline(plan),
            self._dependency_graph(plan),
            self._summary_stats(plan),
        ]
        return "\n\n".join(sections)

    def to_dict(self, plan: MarketingPlan, goal: str = "") -> dict:
        """
        Return all plan components as a dictionary for programmatic access.

        Returns
        -------
        dict with keys: header, task_list, timeline, dependency_graph, stats
        """
        return {
            "header": self._header(goal),
            "task_list": self._task_list(plan),
            "timeline": self._timeline(plan),
            "dependency_graph": self._dependency_graph(plan),
            "stats": self._summary_stats(plan),
        }

    # ------------------------------------------------------------------
    # Section builders
    # ------------------------------------------------------------------

    @staticmethod
    def _header(goal: str) -> str:
        line = "=" * 60
        title = "  MARKETING EXECUTION PLAN"
        goal_line = f"  Goal: {goal}" if goal else ""
        return f"{line}\n{title}\n{goal_line}\n{line}"

    def _task_list(self, plan: MarketingPlan) -> str:
        lines = ["TASK BREAKDOWN\n" + "-" * 40]
        for s in plan.steps:
            dep_note = f"  (depends on Step {s.dependency})" if s.dependency else "  (no dependency)"
            lines.append(f"  Step {s.step:02d} | {s.task}{dep_note}")
        return "\n".join(lines)

    def _timeline(self, plan: MarketingPlan) -> str:
        """
        Build a day-wise timeline by propagating finish days through
        the dependency chain.
        """
        finish_day: dict[int, int] = {}  # step_number -> day it completes

        for step in plan.steps:
            dep_finish = finish_day.get(step.dependency, 0) if step.dependency else 0
            start = dep_finish + 1
            finish_day[step.step] = dep_finish + self.days_per_step

        lines = ["EXECUTION TIMELINE\n" + "-" * 40]
        lines.append(f"  {'Step':<6} {'Start Day':<12} {'End Day':<10}  Task")
        lines.append("  " + "-" * 56)

        for step in plan.steps:
            dep_finish = finish_day.get(step.dependency, 0) if step.dependency else 0
            start = dep_finish + 1
            end = finish_day[step.step]
            lines.append(
                f"  {step.step:<6} Day {start:<8} Day {end:<6}  {step.task}"
            )

        total_days = max(finish_day.values(), default=0)
        total_weeks = math.ceil(total_days / 7)
        lines.append("")
        lines.append(
            f"  Total duration: ~{total_days} days  ({total_weeks} week{'s' if total_weeks != 1 else ''})"
        )
        return "\n".join(lines)

    @staticmethod
    def _dependency_graph(plan: MarketingPlan) -> str:
        """
        Build a simple text-tree showing which steps unlock which.
        Root nodes (no dependency) are printed first; children are indented.
        """
        children: dict[Optional[int], list[PlanStep]] = defaultdict(list)
        for step in plan.steps:
            children[step.dependency].append(step)

        lines = ["DEPENDENCY GRAPH\n" + "-" * 40]

        def render(parent_id: Optional[int], indent: int = 0) -> None:
            for child in children.get(parent_id, []):
                prefix = "  " * indent + ("|- " if indent > 0 else "")
                lines.append(f"  {prefix}[Step {child.step}] {child.task}")
                render(child.step, indent + 1)

        render(None)
        return "\n".join(lines)

    @staticmethod
    def _summary_stats(plan: MarketingPlan) -> str:
        total = len(plan.steps)
        with_dep = sum(1 for s in plan.steps if s.dependency is not None)
        root = total - with_dep
        lines = [
            "PLAN STATISTICS\n" + "-" * 40,
            f"  Total steps     : {total}",
            f"  Root steps      : {root}",
            f"  Dependent steps : {with_dep}",
        ]
        return "\n".join(lines)
