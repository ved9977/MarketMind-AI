"""
Campaign Calendar Generator
Generates a structured multi-day marketing campaign plan.
"""
from typing import Dict, List, Optional
import random

CONTENT_TYPES = [
    ("Instagram Reel", "Instagram"),
    ("Story Post", "Instagram"),
    ("LinkedIn Article", "LinkedIn"),
    ("Email Newsletter", "Email"),
    ("Blog Post", "Blog"),
    ("Tweet", "Twitter"),
    ("Facebook Post", "Facebook"),
]

SHORT_DESCRIPTIONS = [
    "Engage your audience with trending topics.",
    "Share behind-the-scenes content.",
    "Announce a special offer.",
    "Educate with a how-to guide.",
    "Highlight customer testimonials.",
    "Promote a new product or service.",
]

def generate_campaign_calendar(
    duration_days: int = 30,
    platform: Optional[str] = None,
) -> List[Dict[str, str]]:
    normalized_platform = (platform or "").strip().lower()
    if normalized_platform in {"twitter / x", "x"}:
        normalized_platform = "twitter"

    available_content_types = CONTENT_TYPES
    if normalized_platform and normalized_platform != "multi-platform":
        filtered_content_types = [
            (content_type, content_platform)
            for content_type, content_platform in CONTENT_TYPES
            if content_platform.lower() == normalized_platform
        ]
        if filtered_content_types:
            available_content_types = filtered_content_types

    calendar = []
    for day in range(1, duration_days + 1):
        content_type, selected_platform = random.choice(available_content_types)
        description = random.choice(SHORT_DESCRIPTIONS)
        calendar.append({
            "day": day,
            "activity": content_type,
            "platform": selected_platform,
            "content": description
        })
    return calendar

# Usage example:
# calendar = generate_campaign_calendar(7, platform="Instagram")
