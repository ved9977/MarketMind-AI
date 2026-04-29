"""
ui/app.py
=========
MarketMind AI – Streamlit Web Interface

A polished, feature-rich UI with:
  - Campaign input form (goal, audience, platform)
  - Animated progress indicators during generation
  - Tabbed output display (Plan, Timeline, Dependency Graph, Content)
  - Copy-to-clipboard buttons for all generated content
  - Session-state management for persistent results

Run with:
  streamlit run ui/app.py
  (from the project root)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is importable when launched from ui/ directory
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env", override=True)


@st.cache_resource
def get_tool_registry():
    from tools.mock_tools import TOOL_REGISTRY

    return TOOL_REGISTRY


@st.cache_resource
def get_planner_agent():
    from agents.planner_agent import PlannerAgent

    return PlannerAgent(tools=get_tool_registry())


@st.cache_resource
def get_knowledge_base():
    from vector_db.knowledge_base import MarketingKnowledgeBase

    return MarketingKnowledgeBase(
        persist_path=str(PROJECT_ROOT / "vector_db" / "faiss_index")
    )


@st.cache_resource
def get_content_generator():
    from generator.content_generator import ContentGenerator

    return ContentGenerator(knowledge_base=get_knowledge_base())

# ---------------------------------------------------------------------------
# Page config (MUST be the first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="MarketMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS – premium dark theme with gradient accents
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Background ── */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 40%, #0a0f1a 100%);
        color: #e2e8f0;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d1f 0%, #111128 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }

    /* ── Hero title ── */
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #818cf8, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
        line-height: 1.2;
    }

    .hero-sub {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }

    /* ── Cards ── */
    .mm-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(99, 102, 241, 0.18);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(12px);
        transition: box-shadow 0.3s ease;
    }
    .mm-card:hover {
        box-shadow: 0 0 30px rgba(129, 140, 248, 0.12);
        border-color: rgba(99, 102, 241, 0.35);
    }

    .mm-card-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        font-weight: 600;
        color: #a5b4fc;
        margin-bottom: 0.75rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    /* ── Step badge ── */
    .step-badge {
        display: inline-block;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        line-height: 28px;
        text-align: center;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 10px;
        flex-shrink: 0;
    }

    .step-row {
        display: flex;
        align-items: flex-start;
        margin-bottom: 0.75rem;
        padding: 0.6rem 0.8rem;
        border-radius: 10px;
        background: rgba(99, 102, 241, 0.06);
        border: 1px solid rgba(99, 102, 241, 0.1);
    }

    .step-text {
        font-size: 0.9rem;
        color: #cbd5e1;
        line-height: 1.5;
    }

    .dep-tag {
        font-size: 0.72rem;
        color: #818cf8;
        margin-top: 2px;
    }

    /* ── Content output boxes ── */
    .content-box {
        background: rgba(15, 15, 30, 0.7);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 1.25rem;
        white-space: pre-wrap;
        font-size: 0.88rem;
        line-height: 1.7;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
        margin-bottom: 1rem;
    }

    /* ── Timeline row ── */
    .timeline-row {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        padding: 0.5rem 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.4rem;
        background: rgba(99, 102, 241, 0.06);
        border-left: 3px solid #6366f1;
    }
    .timeline-step-num {
        font-weight: 600;
        color: #818cf8;
        min-width: 60px;
        font-size: 0.82rem;
    }
    .timeline-days {
        color: #94a3b8;
        min-width: 140px;
        font-size: 0.82rem;
    }
    .timeline-task {
        color: #e2e8f0;
        font-size: 0.88rem;
    }

    /* ── Stat chip ── */
    .stat-chip {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 8px;
        padding: 0.4rem 0.9rem;
        margin: 0.25rem;
        font-size: 0.82rem;
        color: #a5b4fc;
    }

    /* ── Sidebar label ── */
    .sidebar-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        margin-bottom: 0.3rem;
    }

    /* ── Streamlit overrides ── */
    .stTextArea textarea {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(99,102,241,0.3) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-size: 0.9rem !important;
    }
    .stTextInput input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(99,102,241,0.3) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(99,102,241,0.3) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }
    div[data-testid="stTabs"] button {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 500;
        color: #94a3b8;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #818cf8 !important;
        border-bottom-color: #818cf8 !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1rem !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 28px rgba(99, 102, 241, 0.6) !important;
    }
    div[data-testid="stMetric"] {
        background: rgba(99,102,241,0.08);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 12px;
        padding: 0.8rem;
    }
    div[data-testid="stMetricValue"] {
        color: #818cf8 !important;
    }
    hr { border-color: rgba(99,102,241,0.2) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

def init_session() -> None:
    defaults = {
        "plan": None,
        "plan_dict": None,
        "content": None,
        "goal": "Launch Instagram campaign for skincare product",
        "audience": "Women aged 22-35 interested in clean beauty",
        "platform": "Instagram",
        "budget": "medium",
        "tone": "casual",
        "calendar": None,
        "generated": False,
        "error": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()


# ---------------------------------------------------------------------------
# Sidebar – configuration
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div style='text-align:center; padding: 1rem 0 1.5rem;'>
            <div style='font-size:2.5rem'>🧠</div>
            <div style='font-family:"Space Grotesk",sans-serif; font-size:1.3rem;
                        font-weight:700; color:#818cf8; margin-top:0.3rem;'>
                MarketMind AI
            </div>
            <div style='color:#64748b; font-size:0.78rem; margin-top:0.2rem;'>
                Autonomous Marketing Engine
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown('<div class="sidebar-label">🎯 Campaign Goal</div>', unsafe_allow_html=True)
    goal_input = st.text_area(
        label="Campaign Goal",
        label_visibility="collapsed",
        value=st.session_state.goal,
        height=80,
        placeholder="e.g. Launch Instagram campaign for skincare product",
        key="goal_input",
    )

    st.markdown('<div class="sidebar-label" style="margin-top:1rem">👥 Target Audience</div>', unsafe_allow_html=True)
    audience_input = st.text_input(
        label="Target Audience",
        label_visibility="collapsed",
        value=st.session_state.audience,
        placeholder="e.g. Women aged 22-35 interested in clean beauty",
        key="audience_input",
    )

    st.markdown('<div class="sidebar-label" style="margin-top:1rem">📱 Platform</div>', unsafe_allow_html=True)
    platform_input = st.selectbox(
        label="Platform",
        label_visibility="collapsed",
        options=[
            "Instagram",
            "TikTok",
            "LinkedIn",
            "Twitter / X",
            "Facebook",
            "YouTube",
            "Multi-platform",
        ],
        index=0,
        key="platform_input",
    )


    st.markdown('<div class="sidebar-label" style="margin-top:1rem">💸 Budget</div>', unsafe_allow_html=True)
    budget_input = st.selectbox(
        label="Budget",
        label_visibility="collapsed",
        options=["low", "medium", "high"],
        index=["low", "medium", "high"].index(st.session_state.get("budget", "medium")),
        key="budget_input",
    )

    st.markdown('<div class="sidebar-label" style="margin-top:1rem">🎤 Tone</div>', unsafe_allow_html=True)
    tone_input = st.selectbox(
        label="Tone",
        label_visibility="collapsed",
        options=["formal", "casual", "premium"],
        index=["formal", "casual", "premium"].index(st.session_state.get("tone", "casual")),
        key="tone_input",
    )

    st.markdown("<br>", unsafe_allow_html=True)


    st.markdown("""
    <style>
    .mm-btn-row {
        display: flex;
        gap: 0.7rem;
        margin-bottom: 0.5rem;
        justify-content: center;
    }
    .mm-btn-row .stButton > button {
        min-width: 160px;
        border-radius: 10px !important;
        font-size: 1.02rem !important;
        padding: 0.55rem 0 !important;
        margin-bottom: 0 !important;
        box-shadow: 0 2px 12px rgba(129,140,248,0.10) !important;
    }
    .mm-btn-row .stButton > button.regen {
        background: linear-gradient(135deg, #818cf8, #a5b4fc) !important;
        color: #18181b !important;
    }
    .mm-btn-row .stButton > button.clear {
        background: linear-gradient(135deg, #f472b6, #818cf8) !important;
        color: #fff !important;
    }
    .mm-btn-row .stButton > button.download {
        background: linear-gradient(135deg, #34d399, #818cf8) !important;
        color: #fff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="mm-btn-row">', unsafe_allow_html=True)
    generate_btn = st.button("✨ Generate Campaign", key="gen_btn", use_container_width=False)
    regen_btn = st.button("🔄 Regenerate", key="regen_btn", use_container_width=False)
    clear_btn = st.button("🧹 Clear Output", key="clear_btn", use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(
        """
        <div style='font-size:0.75rem; color:#475569; line-height:1.6;'>
            <b style='color:#64748b;'>Powered by</b><br>
            🔗 LangChain · OpenAI<br>
            🗄 FAISS Vector DB<br>
            🤖 GPT-4o-mini
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main content area
# ---------------------------------------------------------------------------

# Hero header
st.markdown(
    """
    <div class="hero-title">MarketMind AI</div>
    <div class="hero-sub">
        Autonomous Marketing Planner & Content Engine — powered by Agentic + Generative AI
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Run pipeline on button click ─────────────────────────────────────────────

if generate_btn or 'regen_btn' in locals() and regen_btn:
    st.session_state.goal = goal_input.strip() or st.session_state.goal
    st.session_state.audience = audience_input.strip() or st.session_state.audience
    st.session_state.platform = platform_input
    st.session_state.budget = budget_input
    st.session_state.tone = tone_input
    st.session_state.generated = False
    st.session_state.error = None

    progress_placeholder = st.empty()

    try:
        # Step 1: Tools
        with progress_placeholder.status("⚙️  Loading tools & agents …", expanded=True) as status:
            st.write("🔧 Initialising mock tools …")
            st.write("🧠 Starting Planner Agent …")
            planner = get_planner_agent()

            # Step 2: Plan (with personalization and memory)
            st.write("📐 Generating marketing plan …")
            plan = planner.create_plan(
                goal=st.session_state.goal,
                audience=st.session_state.audience,
                platform=st.session_state.platform,
                budget=st.session_state.budget,
                tone=st.session_state.tone,
                user_input={
                    "audience": st.session_state.audience,
                    "platform": st.session_state.platform,
                    "budget": st.session_state.budget,
                    "tone": st.session_state.tone,
                },
            )
            st.session_state.plan = plan

            # Step 3: Execution planner
            st.write("📅 Building execution timeline …")
            from agents.execution_planner import ExecutionPlanner

            ep = ExecutionPlanner(days_per_step=3)
            st.session_state.plan_dict = ep.to_dict(
                plan, goal=st.session_state.goal
            )

            # Step 4: Knowledge base
            st.write("🗄 Connecting to Knowledge Base …")
            kb = get_knowledge_base()

            # Step 5: Content generation (with personalization and memory)
            st.write("✍️  Generating marketing content …")
            gen = get_content_generator()
            st.session_state.content = gen.generate_all(
                goal=st.session_state.goal,
                audience=st.session_state.audience,
                platform=st.session_state.platform,
                budget=st.session_state.budget,
                tone=st.session_state.tone,
                user_input={
                    "audience": st.session_state.audience,
                    "platform": st.session_state.platform,
                    "budget": st.session_state.budget,
                    "tone": st.session_state.tone,
                },
            )

            # Step 6: Campaign calendar
            st.write("📆 Generating campaign calendar …")
            from campaign_calendar_pkg.campaign_calendar import generate_campaign_calendar
            st.session_state.calendar = generate_campaign_calendar(
                duration_days=30,
                platform=st.session_state.platform,
            )

            st.session_state.generated = True
            status.update(
                label="✅ Campaign generated successfully!", state="complete"
            )

    except Exception as exc:
        st.session_state.error = str(exc)
        progress_placeholder.error(
            f"❌ Generation failed: {exc}\n\n"
            "**Troubleshooting:** Ensure your `OPENAI_API_KEY` is set in the `.env` file "
            "and you have a valid internet connection."
        )

# Clear output button
if 'clear_btn' in locals() and clear_btn:
    for k in ["plan", "plan_dict", "content", "generated", "error"]:
        st.session_state[k] = None if k != "generated" else False
    st.experimental_rerun()

# ── Display results ───────────────────────────────────────────────────────────

# Display results, including campaign calendar
if st.session_state.generated and st.session_state.plan and st.session_state.content:

    plan = st.session_state.plan
    pd = st.session_state.plan_dict
    content = st.session_state.content

    # ── Top metrics ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("📋 Plan Steps", len(plan.steps))
    with m2:
        import math
        total_days = len(plan.steps) * 3  # approximate
        st.metric("📅 Est. Duration", f"~{math.ceil(total_days / 7)} weeks")
    with m3:
        st.metric("✍️ Content Pieces", "6")
    with m4:
        st.metric("🗄 KB Docs Used", "3")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────

    tab_plan, tab_timeline, tab_deps, tab_captions, tab_ads, tab_email, tab_calendar = st.tabs([
        "📋 Plan", "📅 Timeline", "🔗 Dependencies",
        "📸 Instagram", "📢 Ads", "📧 Email", "📆 Calendar"
    ])

    # ═══════════════════════════════════════════════════════
    # TAB 7 – Campaign Calendar
    # ═══════════════════════════════════════════════════════
    with tab_calendar:
        st.markdown('<div class="mm-card-title">📆 30-Day Campaign Calendar</div>', unsafe_allow_html=True)
        calendar = st.session_state.get("calendar", [])
        if calendar:
            import pandas as pd
            df = pd.DataFrame(calendar)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Download Calendar (JSON)", pd.Series(calendar).to_json(orient="values"), file_name="campaign_calendar.json", use_container_width=True, help="Download the campaign calendar as JSON")
        else:
            st.info("No campaign calendar generated.")


    # ═══════════════════════════════════════════════════════
    # TAB 1 – Structured Plan
    # ═══════════════════════════════════════════════════════
    with tab_plan:
        st.markdown(
            f'<div class="mm-card-title">📋 Marketing Execution Plan</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"**Goal:** {st.session_state.goal}  \n"
            f"**Audience:** {st.session_state.audience}  \n"
            f"**Platform:** {st.session_state.platform}"
        )
        st.markdown("---")

        plan_text = ""
        for s in plan.steps:
            dep_html = (
                f'<div class="dep-tag">↳ Depends on Step {s.dependency}</div>'
                if s.dependency
                else '<div class="dep-tag">↳ No dependency (start anytime)</div>'
            )
            st.markdown(
                f"""
                <div class="step-row">
                    <span class="step-badge">{s.step}</span>
                    <div>
                        <div class="step-text">{s.task}</div>
                        {dep_html}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            plan_text += f"Step {s.step}: {s.task}\n"
        st.download_button("⬇️ Download Plan", plan_text, file_name="marketing_plan.txt", key="dl_plan", use_container_width=True, help="Download the plan as a text file")

    # ═══════════════════════════════════════════════════════
    # TAB 2 – Timeline
    # ═══════════════════════════════════════════════════════
    with tab_timeline:
        st.markdown('<div class="mm-card-title">📅 Day-Wise Execution Timeline</div>', unsafe_allow_html=True)

        # Recompute finish days
        finish_day: dict[int, int] = {}
        for s in plan.steps:
            dep_f = finish_day.get(s.dependency, 0) if s.dependency else 0
            finish_day[s.step] = dep_f + 3

        # Header row
        hcol1, hcol2, hcol3 = st.columns([1, 2, 4])
        with hcol1:
            st.markdown("**Step**")
        with hcol2:
            st.markdown("**Duration**")
        with hcol3:
            st.markdown("**Task**")
        st.markdown("---")


        timeline_text = ""
        for s in plan.steps:
            dep_f = finish_day.get(s.dependency, 0) if s.dependency else 0
            start = dep_f + 1
            end = finish_day[s.step]
            c1, c2, c3 = st.columns([1, 2, 4])
            with c1:
                st.markdown(
                    f'<span class="stat-chip" style="background:rgba(129,140,248,0.15);">'
                    f'Step {s.step}</span>',
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(f"Day **{start}** → **{end}**")
            with c3:
                st.markdown(s.task)
            timeline_text += f"Step {s.step}: Day {start} → {end}: {s.task}\n"
        st.download_button("⬇️ Download Timeline", timeline_text, file_name="timeline.txt", key="dl_timeline", use_container_width=True, help="Download the timeline as a text file")

        total_days = max(finish_day.values(), default=0)
        st.markdown("---")
        st.success(f"🗓 **Total estimated duration:** {total_days} days (~{math.ceil(total_days/7)} weeks)")

    # ═══════════════════════════════════════════════════════
    # TAB 3 – Dependency Graph
    # ═══════════════════════════════════════════════════════
    with tab_deps:
        st.markdown('<div class="mm-card-title">🔗 Task Dependency Graph</div>', unsafe_allow_html=True)

        # Re-render the text dependency graph
        from collections import defaultdict
        children_map = defaultdict(list)
        for s in plan.steps:
            children_map[s.dependency].append(s)

        lines: list[str] = []

        def render_tree(parent_id, depth=0):
            for child in children_map.get(parent_id, []):
                indent = "　" * depth
                arrow = "└─ " if depth > 0 else "●  "
                lines.append(f"{indent}{arrow}[Step {child.step}] {child.task}")
                render_tree(child.step, depth + 1)


        render_tree(None)
        dep_graph_text = "\n".join(lines)
        st.code(dep_graph_text, language=None)
        st.download_button("⬇️ Download Dependency Graph", dep_graph_text, file_name="dependency_graph.txt", key="dl_deps", use_container_width=True, help="Download the dependency graph as a text file")

        st.info(
            "📌 **How to read:** Root nodes (●) have no prerequisites. "
            "Indented nodes (└─) depend on their parent step."
        )

    # ═══════════════════════════════════════════════════════
    # TAB 4 – Instagram Captions
    # ═══════════════════════════════════════════════════════
    with tab_captions:
        st.markdown('<div class="mm-card-title">📸 Instagram Captions</div>', unsafe_allow_html=True)
        st.markdown("*3 distinct caption styles generated for your campaign.*")

        captions_raw = content["instagram_captions"]
        # Split on the separator pattern
        import re as _re
        caption_blocks = _re.split(r"---CAPTION \d+ \([^)]+\)---", captions_raw)
        caption_labels = _re.findall(r"---CAPTION \d+ \(([^)]+)\)---", captions_raw)


        if len(caption_labels) >= 3:
            for idx, (label, block) in enumerate(zip(caption_labels, caption_blocks[1:]), start=1):
                caption_text = block.strip()
                with st.expander(f"📌 {label}", expanded=True):
                    st.markdown(
                        f'<div class="content-box">{caption_text}</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(f"📋 Copy {label}", key=f"copy_caption_{idx}"):
                        st.code(caption_text)
        else:
            st.markdown(
                f'<div class="content-box">{captions_raw}</div>',
                unsafe_allow_html=True,
            )

        if st.button("📋 Copy All Captions", key="copy_captions"):
            st.code(captions_raw)
        st.download_button("⬇️ Download Captions", captions_raw, file_name="instagram_captions.txt", key="dl_captions", use_container_width=True, help="Download all captions as a text file")

    # ═══════════════════════════════════════════════════════
    # TAB 5 – Ad Copies
    # ═══════════════════════════════════════════════════════
    with tab_ads:
        st.markdown('<div class="mm-card-title">📢 Ad Copies</div>', unsafe_allow_html=True)
        st.markdown("*2 framework-based high-converting ad copies.*")

        ads_raw = content["ad_copies"]
        ad_blocks = _re.split(r"---AD \d+ \([^)]+\)---", ads_raw)
        ad_labels = _re.findall(r"---AD \d+ \(([^)]+)\)---", ads_raw)


        if len(ad_labels) >= 2:
            for idx, (label, block) in enumerate(zip(ad_labels, ad_blocks[1:]), start=1):
                ad_text = block.strip()
                with st.expander(f"🎯 {label}", expanded=True):
                    st.markdown(
                        f'<div class="content-box">{ad_text}</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(f"📋 Copy {label}", key=f"copy_ad_{idx}"):
                        st.code(ad_text)
        else:
            st.markdown(
                f'<div class="content-box">{ads_raw}</div>',
                unsafe_allow_html=True,
            )

        if st.button("📋 Copy All Ads", key="copy_ads"):
            st.code(ads_raw)
        st.download_button("⬇️ Download Ads", ads_raw, file_name="ad_copies.txt", key="dl_ads", use_container_width=True, help="Download all ads as a text file")

    # ═══════════════════════════════════════════════════════
    # TAB 6 – Email Campaign
    # ═══════════════════════════════════════════════════════
    with tab_email:
        st.markdown('<div class="mm-card-title">📧 Email Campaign</div>', unsafe_allow_html=True)
        st.markdown("*Full structured email campaign ready for your ESP.*")

        email_raw = content["email_campaign"]

        # Try to extract subject line for preview
        subj_match = _re.search(r"SUBJECT:\s*(.+)", email_raw)
        if subj_match:
            st.info(f"✉️ **Subject Line:** {subj_match.group(1).strip()}")


        st.markdown(
            f'<div class="content-box">{email_raw.strip()}</div>',
            unsafe_allow_html=True,
        )

        if st.button("📋 Copy Email", key="copy_email"):
            st.code(email_raw)
        st.download_button("⬇️ Download Email", email_raw, file_name="email_campaign.txt", key="dl_email", use_container_width=True, help="Download the email campaign as a text file")


elif not st.session_state.error:
    # ── Welcome state ─────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="mm-card" style="text-align:center; padding: 3rem 2rem;">
            <div style="font-size:4rem; margin-bottom:1rem;">🚀</div>
            <div style="font-family:'Space Grotesk',sans-serif; font-size:1.4rem;
                        font-weight:600; color:#a5b4fc; margin-bottom:0.75rem;">
                Ready to launch your campaign?
            </div>
            <div style="color:#64748b; font-size:0.95rem; max-width:500px; margin:0 auto;">
                Enter your campaign goal in the sidebar and click
                <b style="color:#818cf8;">✨ Generate Campaign</b> to get your
                full AI-powered marketing plan and content in seconds.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Feature tiles
    c1, c2, c3 = st.columns(3)
    features = [
        ("🤖", "Agentic Planning", "Decomposes goals into dependency-aware step-by-step plans using LangChain reasoning."),
        ("🗄", "RAG-Enhanced Writing", "Retrieves relevant templates and tone guides from a FAISS vector database before generating."),
        ("✍️", "6 Content Pieces", "Generates 3 Instagram captions, 2 ad copies, and a full email campaign automatically."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3], features):
        with col:
            st.markdown(
                f"""
                <div class="mm-card" style="text-align:center; min-height:180px;">
                    <div style="font-size:2.2rem; margin-bottom:0.75rem;">{icon}</div>
                    <div class="mm-card-title" style="text-transform:none; font-size:0.95rem;">
                        {title}
                    </div>
                    <div style="color:#64748b; font-size:0.82rem; line-height:1.6;">
                        {desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
