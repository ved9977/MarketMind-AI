"""
main.py
=======
MarketMind AI – Command-Line Entry Point

Orchestrates the full pipeline:
  1. Parse user input (goal, audience, platform).
  2. Initialise mock tools and PlannerAgent.
  3. Generate a structured marketing plan.
  4. Convert the plan to a human-readable execution timeline.
  5. Initialise the FAISS knowledge base.
  6. Generate all marketing content (captions, ads, email).
  7. Print the final consolidated report.

Usage
-----
  python main.py
  python main.py --goal "Launch Instagram campaign for skincare product"
  python main.py --goal "..." --audience "Women 25-35" --platform "Instagram"

Environment
-----------
Requires a valid OPENAI_API_KEY in .env (copy .env.example → .env).
"""

from __future__ import annotations

import argparse
import logging
import sys
import textwrap
from pathlib import Path

from dotenv import load_dotenv

# Ensure project root is on sys.path when running directly
sys.path.insert(0, str(Path(__file__).parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv(Path(__file__).parent / ".env", override=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("marketmind")


# ---------------------------------------------------------------------------
# Pipeline orchestration
# ---------------------------------------------------------------------------

def run_pipeline(goal: str, audience: str, platform: str) -> None:
    """Execute the full MarketMind AI pipeline and print results."""

    separator = "=" * 70
    section_bar = "-" * 70

    print(f"\n{separator}")
    print("  MarketMind AI - Autonomous Marketing Planner & Content Engine")
    print(separator)
    print(f"\n  Goal     : {goal}")
    print(f"  Audience : {audience}")
    print(f"  Platform : {platform}\n")

    # ── Step 1: Tools ────────────────────────────────────────────────────────
    logger.info("Loading mock tools...")
    from tools.mock_tools import TOOL_REGISTRY

    # ── Step 2: Planner agent ────────────────────────────────────────────────
    logger.info("Initialising PlannerAgent...")
    from agents.planner_agent import PlannerAgent

    planner = PlannerAgent(tools=TOOL_REGISTRY)

    print("\nRunning Planner Agent (this may take ~10-20 seconds)...\n")
    try:
        plan = planner.create_plan(goal=goal, audience=audience, platform=platform)
    except Exception as exc:
        logger.error("PlannerAgent failed: %s", exc)
        print(f"\nPlanning failed: {exc}")
        print("    Make sure your OPENAI_API_KEY is set in .env and is valid.")
        sys.exit(1)

    # ── Step 3: Execution planner ────────────────────────────────────────────
    from agents.execution_planner import ExecutionPlanner

    ep = ExecutionPlanner(days_per_step=3)
    readable_plan = ep.generate_readable_plan(plan, goal=goal)

    print(readable_plan)

    # ── Step 4: Knowledge base ───────────────────────────────────────────────
    logger.info("Initialising Knowledge Base...")
    from vector_db.knowledge_base import MarketingKnowledgeBase

    kb = MarketingKnowledgeBase(persist_path="./vector_db/faiss_index")

    # ── Step 5: Content generation ───────────────────────────────────────────
    from generator.content_generator import ContentGenerator

    gen = ContentGenerator(knowledge_base=kb)

    print(f"\n\n{separator}")
    print("  GENERATING MARKETING CONTENT...")
    print(separator)

    try:
        content = gen.generate_all(
            goal=goal,
            audience=audience,
            platform=platform,
        )
    except Exception as exc:
        logger.error("ContentGenerator failed: %s", exc)
        print(f"\nContent generation failed: {exc}")
        sys.exit(1)

    # ── Step 6: Print content ────────────────────────────────────────────────
    print(f"\n\n{'INSTAGRAM CAPTIONS':^70}")
    print(section_bar)
    print(content["instagram_captions"])

    print(f"\n\n{'AD COPIES':^70}")
    print(section_bar)
    print(content["ad_copies"])

    print(f"\n\n{'EMAIL CAMPAIGN':^70}")
    print(section_bar)
    print(content["email_campaign"])

    print(f"\n\n{separator}")
    print("  MarketMind AI pipeline complete.")
    print(separator + "\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MarketMind AI – Autonomous Marketing Planner & Content Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Examples:
              python main.py
              python main.py --goal "Launch Instagram campaign for skincare product"
              python main.py --goal "Grow email list for SaaS app" \\
                             --audience "Startup founders 25-45" \\
                             --platform "LinkedIn"
            """
        ),
    )
    parser.add_argument(
        "--goal",
        type=str,
        default="Launch Instagram campaign for skincare product",
        help="High-level marketing objective.",
    )
    parser.add_argument(
        "--audience",
        type=str,
        default="Women aged 22-35 interested in clean beauty",
        help="Target audience description.",
    )
    parser.add_argument(
        "--platform",
        type=str,
        default="Instagram",
        help="Primary marketing platform.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(
        goal=args.goal,
        audience=args.audience,
        platform=args.platform,
    )
