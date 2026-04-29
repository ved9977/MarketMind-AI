"""
generator/content_generator.py
================================
ContentGenerator – Generative AI module of MarketMind AI.

Produces campaign-ready marketing content:
  * 3 Instagram captions  (diverse styles: benefit-led, storytelling, UGC)
  * 2 Ad copies           (AIDA and PAS frameworks)
  * 1 Email campaign      (full structure: subject, preview, body, CTA)

Architecture
------------
Each content type has its own rigorously engineered PromptTemplate that:
  - Specifies output format explicitly.
  - Injects retrieved knowledge-base context for stylistic grounding.
  - Enforces professional, consistent marketing tone.
  - Provides campaign-specific details (goal, audience, platform, product).

The generator also offers a `generate_all()` convenience method that returns
a typed dict with all content in one call.
"""

from __future__ import annotations

import logging
import os

import json
from pathlib import Path


from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from memory.agent_memory import AgentMemory
from personalization.personalization_engine import PersonalizationEngine

load_dotenv(Path(__file__).parent.parent / ".env", override=True)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# System prompt (shared across all generation tasks)
# ---------------------------------------------------------------------------

CONTENT_SYSTEM_PROMPT = """You are MarketMind Content Engine — an elite AI copywriter
specialising in performance marketing and brand storytelling.

Core principles you always follow:
  1. Every word earns its place — ruthless brevity.
  2. Lead with the customer benefit, not the product feature.
  3. Match the tone and register of the target platform precisely.
  4. Use strong, active verbs. Avoid passive voice.
  5. Close every piece with one clear, compelling call-to-action.
  6. Maintain brand consistency across all deliverables.

You will receive extracted knowledge-base context. Use it to inform your
writing style, templates, and messaging pillars — do not ignore it.
"""


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

INSTAGRAM_PROMPT = PromptTemplate(
    input_variables=["goal", "audience", "platform", "product_hint", "kb_context"],
    template="""
TASK: Write 3 distinct Instagram captions for the following campaign.

Campaign Goal   : {goal}
Target Audience : {audience}
Platform        : {platform}
Product Context : {product_hint}

Knowledge Base Context (use for tone and template guidance):
{kb_context}

Requirements:
  - Caption 1: Benefit-Led — open with the #1 customer benefit, close with CTA + 3 hashtags.
  - Caption 2: Storytelling — open with a relatable problem, reveal the product as the solution.
  - Caption 3: UGC / Community — feature a fictional customer voice, invite community participation.

Format your response EXACTLY as:
---CAPTION 1 (Benefit-Led)---
[caption text]

---CAPTION 2 (Storytelling)---
[caption text]

---CAPTION 3 (UGC / Community)---
[caption text]
""",
)

AD_COPY_PROMPT = PromptTemplate(
    input_variables=["goal", "audience", "platform", "product_hint", "kb_context"],
    template="""
TASK: Write 2 high-converting ad copies for the following campaign.

Campaign Goal   : {goal}
Target Audience : {audience}
Platform        : {platform}
Product Context : {product_hint}

Knowledge Base Context (use for frameworks and tone):
{kb_context}

Requirements:
  - Ad 1: AIDA Framework — Headline (<8 words), Sub-headline, Body (2-3 bullet benefits + social proof), CTA.
  - Ad 2: PAS Framework  — Problem statement, Agitation paragraph, Solution + CTA.

Format your response EXACTLY as:
---AD 1 (AIDA Framework)---
HEADLINE: [text]
SUB-HEADLINE: [text]
BODY:
• [benefit 1]
• [benefit 2]
• [social proof]
CTA: [text]

---AD 2 (PAS Framework)---
PROBLEM: [text]
AGITATE: [text]
SOLVE: [text]
CTA: [text]
""",
)

EMAIL_CAMPAIGN_PROMPT = PromptTemplate(
    input_variables=["goal", "audience", "platform", "product_hint", "kb_context"],
    template="""
TASK: Write a full email campaign for the following marketing goal.

Campaign Goal   : {goal}
Target Audience : {audience}
Platform        : {platform}
Product Context : {product_hint}

Knowledge Base Context (use for email structure and best practices):
{kb_context}

Requirements:
  - Subject line  : ≤45 characters, benefit-driven or curiosity-provoking.
  - Preview text  : ≤90 characters, complements (don't repeat) the subject.
  - Greeting      : Personalised opener.
  - Intro (2-3 sentences): Acknowledge a customer pain point, pivot to solution.
  - Benefits block: 3 concise bullet points (feature → benefit format).
  - Social proof  : One short fictional customer testimonial.
  - Primary CTA   : Bold action button label + supporting sentence.
  - Secondary CTA : Softer alternative ('Learn more about XYZ').
  - Sign-off      : Warm, on-brand closing.

Format your response EXACTLY as:
---EMAIL CAMPAIGN---
SUBJECT: [text]
PREVIEW: [text]

GREETING:
[text]

INTRO:
[text]

BENEFITS:
• [feature → benefit]
• [feature → benefit]
• [feature → benefit]

SOCIAL PROOF:
[testimonial]

PRIMARY CTA: [button text]
[supporting sentence]

SECONDARY CTA: [text]

SIGN-OFF:
[text]
""",
)


# ---------------------------------------------------------------------------
# ContentGenerator
# ---------------------------------------------------------------------------

class ContentGenerator:
    """
    Generates professional marketing content using an LLM + knowledge retrieval.

    Parameters
    ----------
    knowledge_base : MarketingKnowledgeBase | None
        Optional vector DB for RAG-enhanced generation.
    model_name : str
        OpenAI model to use (default: gpt-4o-mini).
    temperature : float
        Sampling temperature (0.7 balances creativity and consistency).
    """

    def __init__(
        self,
        knowledge_base=None,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.7,
    ) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")

        llm_kwargs: dict = {
            "model": model_name,
            "temperature": temperature,
            "api_key": api_key,
        }
        if base_url:
            llm_kwargs["base_url"] = base_url

        self.llm = ChatOpenAI(**llm_kwargs)
        self.kb = knowledge_base
        self.memory = AgentMemory()
        self.personalizer = PersonalizationEngine()
        self._kb_context_cache: dict[tuple[str, int], str] = {}
        logger.info("ContentGenerator initialised with model=%s", model_name)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_all(
        self,
        goal: str,
        audience: str = "General audience",
        platform: str = "Instagram",
        product_hint: str = "",
        budget: str = None,
        tone: str = None,
        user_input: dict = None,
    ) -> dict[str, str]:
        """
        Generate all content types in one call, using memory and personalization.
        """
        logger.info("Generating all content for goal: '%s'", goal)
        inferred_hint = product_hint or self._infer_product(goal)
        user_input = user_input or {
            "audience": audience,
            "platform": platform,
            "budget": budget,
            "tone": tone,
        }

        # Retrieve relevant memory and preferences
        relevant_memory = self.memory.retrieve_relevant_memory(user_input)
        preferences = self.memory.get_preferences()

        # Save campaign to memory after generation (see below)

        # Generate content with memory and personalization
        captions = self.generate_instagram_captions(goal, audience, platform, inferred_hint, budget, tone, user_input, relevant_memory, preferences)
        ads = self.generate_ad_copies(goal, audience, platform, inferred_hint, budget, tone, user_input, relevant_memory, preferences)
        email = self.generate_email_campaign(goal, audience, platform, inferred_hint, budget, tone, user_input, relevant_memory, preferences)

        # Save campaign content to memory
        campaign_record = {
            "goal": goal,
            "audience": audience,
            "platform": platform,
            "budget": budget,
            "tone": tone,
            "content": {
                "instagram_captions": captions,
                "ad_copies": ads,
                "email_campaign": email,
            },
        }
        self.memory.save_campaign_to_memory(campaign_record)

        return {
            "instagram_captions": captions,
            "ad_copies": ads,
            "email_campaign": email,
        }

    def generate_instagram_captions(
        self,
        goal: str,
        audience: str,
        platform: str,
        product_hint: str = "",
        budget: str = None,
        tone: str = None,
        user_input: dict = None,
        relevant_memory=None,
        preferences=None,
    ) -> str:
        """Generate 3 Instagram captions with memory and personalization."""
        kb_ctx = self._get_kb_context("instagram caption skincare social media")
        user_input = user_input or {"audience": audience, "platform": platform, "budget": budget, "tone": tone}
        prompt = INSTAGRAM_PROMPT.format(
            goal=goal,
            audience=audience,
            platform=platform,
            product_hint=product_hint or self._infer_product(goal),
            kb_context=kb_ctx,
        )
        # Inject memory and preferences
        if relevant_memory:
            prompt += f"\n\nRelevant Past Campaigns (for context):\n{json.dumps(relevant_memory, indent=2)}"
        if preferences:
            prompt += f"\n\nUser Preferences:\n{json.dumps(preferences, indent=2)}"
        # Personalize prompt
        prompt = self.personalizer.personalize_prompt(prompt, user_input)
        return self._call_llm(prompt)

    def generate_ad_copies(
        self,
        goal: str,
        audience: str,
        platform: str,
        product_hint: str = "",
        budget: str = None,
        tone: str = None,
        user_input: dict = None,
        relevant_memory=None,
        preferences=None,
    ) -> str:
        """Generate 2 ad copies (AIDA + PAS) with memory and personalization."""
        kb_ctx = self._get_kb_context("ad copy AIDA PAS framework marketing")
        user_input = user_input or {"audience": audience, "platform": platform, "budget": budget, "tone": tone}
        prompt = AD_COPY_PROMPT.format(
            goal=goal,
            audience=audience,
            platform=platform,
            product_hint=product_hint or self._infer_product(goal),
            kb_context=kb_ctx,
        )
        if relevant_memory:
            prompt += f"\n\nRelevant Past Campaigns (for context):\n{json.dumps(relevant_memory, indent=2)}"
        if preferences:
            prompt += f"\n\nUser Preferences:\n{json.dumps(preferences, indent=2)}"
        prompt = self.personalizer.personalize_prompt(prompt, user_input)
        return self._call_llm(prompt)

    def generate_email_campaign(
        self,
        goal: str,
        audience: str,
        platform: str,
        product_hint: str = "",
        budget: str = None,
        tone: str = None,
        user_input: dict = None,
        relevant_memory=None,
        preferences=None,
    ) -> str:
        """Generate a full email campaign with memory and personalization."""
        kb_ctx = self._get_kb_context("email campaign promotional structure best practices")
        user_input = user_input or {"audience": audience, "platform": platform, "budget": budget, "tone": tone}
        prompt = EMAIL_CAMPAIGN_PROMPT.format(
            goal=goal,
            audience=audience,
            platform=platform,
            product_hint=product_hint or self._infer_product(goal),
            kb_context=kb_ctx,
        )
        if relevant_memory:
            prompt += f"\n\nRelevant Past Campaigns (for context):\n{json.dumps(relevant_memory, indent=2)}"
        if preferences:
            prompt += f"\n\nUser Preferences:\n{json.dumps(preferences, indent=2)}"
        prompt = self.personalizer.personalize_prompt(prompt, user_input)
        return self._call_llm(prompt)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _call_llm(self, user_prompt: str) -> str:
        """Invoke the LLM and return the text content."""
        messages = [
            SystemMessage(content=CONTENT_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
        response = self.llm.invoke(messages)
        return response.content.strip()

    def _get_kb_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve relevant knowledge-base context, or return a placeholder."""
        if self.kb is None:
            return "No knowledge base connected."
        cache_key = (query, top_k)
        if cache_key not in self._kb_context_cache:
            self._kb_context_cache[cache_key] = self.kb.retrieve_as_context(
                query,
                top_k=top_k,
            )
        return self._kb_context_cache[cache_key]

    @staticmethod
    def _infer_product(goal: str) -> str:
        """
        Heuristically extract a product/category hint from the goal string.
        Falls back to a generic label if nothing useful is found.
        """
        keywords = [
            "skincare", "supplement", "app", "software", "clothing", "fashion",
            "food", "beverage", "tech", "device", "service", "platform",
            "course", "book", "pet", "fitness", "health",
        ]
        goal_lower = goal.lower()
        for kw in keywords:
            if kw in goal_lower:
                return kw.capitalize() + " product"
        return "product"
