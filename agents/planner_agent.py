"""
agents/planner_agent.py
=======================
PlannerAgent – Agentic AI component of MarketMind AI.

Responsibilities
----------------
* Accept a high-level marketing goal plus optional context.
* Use an LLM (via LangChain) to reason step-by-step and decompose the goal
  into ordered, dependency-aware tasks.
* Optionally call mock tools (competitor analysis, audience analysis, etc.)
  to enrich the plan.
* Return a strict JSON plan that downstream modules consume.

Architecture
------------
The class is built on LangChain's ChatOpenAI + PromptTemplate paradigm with
an explicit JSON-extraction step so the output is always machine-parseable.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Optional, Dict


from memory.agent_memory import AgentMemory
from personalization.personalization_engine import PersonalizationEngine


from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

# Load .env from the project root, regardless of working directory
load_dotenv(Path(__file__).parent.parent / ".env", override=True)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Output schema (used for validation)
# ---------------------------------------------------------------------------

class PlanStep(BaseModel):
    """One atomic task in the marketing execution plan."""

    step: int = Field(..., description="Sequential step number, starting from 1.")
    task: str = Field(..., description="Short description of the marketing task.")
    dependency: Optional[int] = Field(
        None,
        description="Step number this task depends on, or null if none.",
    )


class MarketingPlan(BaseModel):
    """Full structured plan returned by the PlannerAgent."""

    steps: list[PlanStep]


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are MarketMind, an elite AI marketing strategist.
Your job is to decompose a high-level marketing goal into a structured,
dependency-aware execution plan.

Rules:
1. Return ONLY a JSON object matching the schema below — no prose, no markdown fences.
2. Steps must be numbered sequentially starting at 1.
3. Each step's "dependency" is the step number it must wait for, or null.
4. Include 6–10 actionable steps that cover research, strategy, content,
   distribution, and measurement.

JSON Schema:
{
  "steps": [
    {"step": <int>, "task": "<string>", "dependency": <int|null>},
    ...
  ]
}
"""

PLAN_TEMPLATE = PromptTemplate(
    input_variables=["goal", "audience", "platform", "tool_insights"],
    template="""
Marketing Goal  : {goal}
Target Audience : {audience}
Platform        : {platform}

Additional Research Insights (from analysis tools):
{tool_insights}

Decompose this goal into a structured marketing execution plan.
Return ONLY the JSON object — no additional text.
""",
)


# ---------------------------------------------------------------------------
# PlannerAgent
# ---------------------------------------------------------------------------

class PlannerAgent:
    """
    Agentic AI planner that decomposes marketing goals into structured plans.

    Parameters
    ----------
    model_name : str
        OpenAI model to use for reasoning (default: gpt-4o-mini).
    temperature : float
        Sampling temperature; 0.3 gives deterministic-ish plans.
    tools : dict[str, callable]
        Optional mapping of tool name → callable for enriching the plan.
        Each callable should accept keyword arguments and return a dict.
    """

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.3,
        tools: Optional[dict[str, Any]] = None,
    ) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")

        llm_kwargs: dict[str, Any] = {
            "model": model_name,
            "temperature": temperature,
            "api_key": api_key,
        }
        if base_url:
            llm_kwargs["base_url"] = base_url

        self.llm = ChatOpenAI(**llm_kwargs)
        self.tools: dict[str, Any] = tools or {}
        self.memory = AgentMemory()
        self.personalizer = PersonalizationEngine()
        logger.info("PlannerAgent initialised with model=%s", model_name)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_plan(
        self,
        goal: str,
        audience: str = "General audience",
        platform: str = "Multi-platform",
        budget: str = None,
        tone: str = None,
        user_input: Dict[str, str] = None,
    ) -> MarketingPlan:
        """
        Generate a structured marketing plan for the given goal, using memory and personalization.
        """
        logger.info("Creating plan for goal: '%s'", goal)

        # Compose user_input dict for personalization and memory
        user_input = user_input or {
            "audience": audience,
            "platform": platform,
            "budget": budget,
            "tone": tone,
        }

        # 1. Retrieve relevant memory (past campaigns, preferences)
        relevant_memory = self.memory.retrieve_relevant_memory(user_input)
        preferences = self.memory.get_preferences()

        # 2. Gather tool insights
        tool_insights = self._gather_tool_insights(goal, audience, platform)

        # 3. Build the prompt, injecting memory and preferences
        base_prompt = PLAN_TEMPLATE.format(
            goal=goal,
            audience=audience,
            platform=platform,
            tool_insights=tool_insights,
        )
        if relevant_memory:
            base_prompt += f"\n\nRelevant Past Campaigns (for context):\n{json.dumps(relevant_memory, indent=2)}"
        if preferences:
            base_prompt += f"\n\nUser Preferences:\n{json.dumps(preferences, indent=2)}"

        # Personalize the prompt
        personalized_prompt = self.personalizer.personalize_prompt(base_prompt, user_input)

        # 4. Call the LLM
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=personalized_prompt),
        ]
        response = self.llm.invoke(messages)
        raw_text: str = response.content
        logger.debug("Raw LLM response:\n%s", raw_text)

        # 5. Extract and validate JSON
        plan = self._parse_plan(raw_text)
        logger.info("Plan created with %d steps.", len(plan.steps))

        # 6. Save campaign to memory
        campaign_record = {
            "goal": goal,
            "audience": audience,
            "platform": platform,
            "budget": budget,
            "tone": tone,
            "plan": [s.dict() for s in plan.steps],
        }
        self.memory.save_campaign_to_memory(campaign_record)

        # Optionally save/update preferences
        if platform:
            self.memory.save_user_preference("platform", platform)
        if tone:
            self.memory.save_user_preference("tone", tone)
        if audience:
            self.memory.save_user_preference("audience", audience)
        if budget:
            self.memory.save_user_preference("budget", budget)

        return plan

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _gather_tool_insights(
        self,
        goal: str,
        audience: str,
        platform: str,
    ) -> str:
        """Run each registered tool and concatenate their summaries."""
        if not self.tools:
            return "No additional tool insights available."

        insights: list[str] = []
        for name, tool_fn in self.tools.items():
            try:
                result: dict = tool_fn(goal=goal, audience=audience, platform=platform)
                summary = json.dumps(result, indent=2)
                insights.append(f"[{name}]\n{summary}")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Tool '%s' failed: %s", name, exc)
                insights.append(f"[{name}] unavailable.")

        return "\n\n".join(insights)

    @staticmethod
    def _extract_json(text: str) -> str:
        """
        Extract the first JSON object from a string that may contain markdown
        fences or surrounding prose.
        """
        # Try to find a JSON block enclosed in triple backticks
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fence_match:
            return fence_match.group(1)

        # Fall back to the first raw { … }
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            return brace_match.group(0)

        raise ValueError("No JSON object found in LLM response.")

    def _parse_plan(self, raw_text: str) -> MarketingPlan:
        """Parse and validate the LLM output into a MarketingPlan."""
        try:
            json_str = self._extract_json(raw_text)
            data = json.loads(json_str)
            return MarketingPlan(**data)
        except Exception as exc:
            logger.error("Failed to parse plan: %s\nRaw text:\n%s", exc, raw_text)
            raise ValueError(
                f"PlannerAgent could not produce a valid plan: {exc}"
            ) from exc
