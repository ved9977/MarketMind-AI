"""
tools/mock_tools.py
===================
Mock API tools used by the PlannerAgent.

These simulate external integrations (competitor analysis APIs, audience
analytics platforms, platform optimization services) with realistic
structured data so the project works without real API subscriptions.

Each tool function:
  * Accepts keyword arguments (goal, audience, platform).
  * Returns a structured dict mimicking a real API response.
  * Is registered in TOOL_REGISTRY for plug-and-play use by the agent.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def competitor_analysis_tool(
    goal: str = "",
    audience: str = "",
    platform: str = "",
    **kwargs: Any,
) -> dict:
    """
    Simulate a competitor analysis API.

    Returns a snapshot of mock competitor positioning data that the planner
    agent uses to inform strategy.
    """
    competitors = [
        {
            "brand": "GlowLab",
            "market_share_pct": 34,
            "primary_platform": "Instagram",
            "avg_engagement_rate_pct": 4.8,
            "top_content_types": ["before/after Reels", "UGC reposts", "tutorials"],
            "pricing_strategy": "premium",
            "estimated_monthly_ad_spend_usd": 85_000,
        },
        {
            "brand": "PureSkin Co.",
            "market_share_pct": 22,
            "primary_platform": "TikTok",
            "avg_engagement_rate_pct": 7.2,
            "top_content_types": ["short-form videos", "influencer collabs"],
            "pricing_strategy": "mid-range",
            "estimated_monthly_ad_spend_usd": 45_000,
        },
        {
            "brand": "DermEssence",
            "market_share_pct": 18,
            "primary_platform": "YouTube",
            "avg_engagement_rate_pct": 3.1,
            "top_content_types": ["long-form tutorials", "dermatologist endorsements"],
            "pricing_strategy": "luxury",
            "estimated_monthly_ad_spend_usd": 120_000,
        },
    ]

    market_gaps = [
        "Educational skincare content targeting Gen-Z males is underserved.",
        "Sustainable/eco-friendly messaging is rarely used by top competitors.",
        "Personalized skincare routines presented via interactive content have low adoption.",
    ]

    return {
        "status": "success",
        "analysis_date": "2026-04-25",
        "goal_context": goal[:80] if goal else "N/A",
        "competitors": competitors,
        "market_gaps": market_gaps,
        "recommendation": (
            "Focus on authentic UGC and educational Reels. "
            "Differentiate with eco-friendly messaging and personalization angles."
        ),
    }


def audience_analysis_tool(
    goal: str = "",
    audience: str = "",
    platform: str = "",
    **kwargs: Any,
) -> dict:
    """
    Simulate an audience analytics/segmentation API.

    Returns demographic breakdown, psychographic traits, and content-
    preference data for the inferred target audience.
    """
    segments = [
        {
            "segment": "Primary – Young Professionals (F, 25-34)",
            "size_estimate": "2.4 M",
            "interests": ["skincare routines", "wellness", "sustainability"],
            "peak_activity_times": ["07:00–09:00", "12:00–13:00", "20:00–22:00"],
            "preferred_content": ["short tutorials", "ingredient spotlights", "reviews"],
            "avg_purchase_intent_score": 78,
        },
        {
            "segment": "Secondary – Beauty Enthusiasts (All genders, 18-24)",
            "size_estimate": "3.1 M",
            "interests": ["makeup", "aesthetics", "trend-following"],
            "peak_activity_times": ["15:00–17:00", "21:00–23:00"],
            "preferred_content": ["viral challenges", "'Get Ready With Me' videos"],
            "avg_purchase_intent_score": 62,
        },
    ]

    return {
        "status": "success",
        "audience_input": audience[:80] if audience else "N/A",
        "segments": segments,
        "top_pain_points": [
            "Confusion around ingredient safety.",
            "Overwhelmed by too many product choices.",
            "Trust deficit — want clinical proof or real testimonials.",
        ],
        "messaging_recommendations": [
            "Lead with 'clean' and 'dermatologist-tested' claims.",
            "Use before/after social proof prominently.",
            "Offer a 'Find Your Routine' quiz to drive engagement.",
        ],
    }


def platform_selection_tool(
    goal: str = "",
    audience: str = "",
    platform: str = "",
    **kwargs: Any,
) -> dict:
    """
    Simulate a platform intelligence / media-mix API.

    Returns a ranked list of marketing platforms with justifications and
    recommended budget allocations.
    """
    platforms = [
        {
            "platform": "Instagram",
            "rank": 1,
            "best_for": ["visual storytelling", "Reels", "influencer marketing"],
            "recommended_budget_pct": 40,
            "expected_cpm_usd": 8.50,
            "estimated_reach": "1.8 M – 2.6 M",
            "content_cadence": "5–7 posts/week (mix of Feed + Stories + Reels)",
        },
        {
            "platform": "TikTok",
            "rank": 2,
            "best_for": ["viral reach", "Gen-Z", "trend hijacking"],
            "recommended_budget_pct": 30,
            "expected_cpm_usd": 5.20,
            "estimated_reach": "2.2 M – 4.0 M",
            "content_cadence": "1–2 videos/day",
        },
        {
            "platform": "Google Display / Search",
            "rank": 3,
            "best_for": ["intent capture", "retargeting"],
            "recommended_budget_pct": 20,
            "expected_cpm_usd": 3.80,
            "estimated_reach": "500 K – 800 K",
            "content_cadence": "Always-on ads with A/B rotation every 2 weeks",
        },
        {
            "platform": "Email",
            "rank": 4,
            "best_for": ["retention", "loyalty", "nurturing"],
            "recommended_budget_pct": 10,
            "expected_cpm_usd": 1.20,
            "estimated_reach": "Existing list + 15% growth",
            "content_cadence": "2 newsletters/week + 1 promotional email/week",
        },
    ]

    suggested = platform.strip() if platform and platform.lower() != "multi-platform" else "Instagram"
    top = next((p for p in platforms if p["platform"].lower() == suggested.lower()), platforms[0])

    return {
        "status": "success",
        "query_platform": platform or "multi-platform",
        "top_recommendation": top,
        "all_platforms": platforms,
        "total_estimated_reach": "4.5 M – 7.4 M (combined)",
        "suggested_launch_window": "Tuesday–Thursday, 09:00–11:00 local time",
    }


# ---------------------------------------------------------------------------
# Tool registry – keyed by descriptive name
# ---------------------------------------------------------------------------

TOOL_REGISTRY: dict[str, Any] = {
    "Competitor Analysis": competitor_analysis_tool,
    "Audience Analysis": audience_analysis_tool,
    "Platform Selection": platform_selection_tool,
}
