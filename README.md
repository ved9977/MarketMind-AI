# 🧠 MarketMind AI — Autonomous Marketing Planner & Content Engine

> An intelligent, modular Python system that combines **Agentic AI** (planning & reasoning) with **Generative AI** (content creation) to automate complete marketing campaigns end-to-end.

---

## 🚀 Features

| Module | Technology | What it does |
|---|---|---|
| **Planner Agent** | LangChain + GPT-4o-mini | Decomposes a marketing goal into a structured, dependency-aware step plan |
| **Mock Tools** | Pure Python | Competitor, audience, and platform analysis tools used by the agent |
| **Execution Planner** | Pure Python | Converts JSON plan → timeline, dependency graph, task list |
| **Knowledge Base** | FAISS + OpenAI Embeddings | Stores marketing templates & tone guides; retrieves context via RAG |
| **Content Generator** | GPT-4o-mini + PromptTemplates | Produces 3 Instagram captions, 2 ad copies, 1 email campaign |
| **Streamlit UI** | Streamlit | Premium dark-themed web interface with tabbed output |

---

## 🚀 Enhanced Features

- **Memory System:** Remembers past campaigns, user preferences, and feedback. Uses FAISS or JSON for persistent memory.
- **Personalization Engine:** Generates highly customized marketing plans based on structured user input (audience, platform, budget, tone).
- **Campaign Calendar Generator:** Produces a structured, multi-day campaign plan with exportable calendar.

## 🧠 Example Inputs

```json
{
  "audience": "Gen Z",
  "platform": "Instagram",
  "budget": "low",
  "tone": "casual"
}
```

## 🎯 Example Output (Calendar)

```json
[
  {"day": 1, "activity": "Instagram Reel", "platform": "Instagram", "content": "Engage your audience with trending topics."},
  {"day": 2, "activity": "Story Post", "platform": "Instagram", "content": "Share behind-the-scenes content."}
]
```

## 🧪 Testing

- Try different combinations of audience, platform, budget, and tone in the UI.
- Verify that:
  - Memory influences output (e.g., repeated Instagram preference).
  - Personalization changes the strategy and content.
  - Calendar is generated and exportable.

## 🗂️ Modular Structure

- `memory/agent_memory.py` – Persistent/contextual memory
- `personalization/personalization_engine.py` – Personalization logic
- `calendar/campaign_calendar.py` – Calendar generator
- `agents/planner_agent.py` – Planning agent (integrates memory/personalization)
- `generator/content_generator.py` – Content generation (integrates memory/personalization)
- `ui/app.py` – Streamlit UI (integrates all features)

## 📝 Comments

- Each module and function is commented for clarity.
- See code for usage examples and integration points.

---

## 📁 Project Structure

```
MAJOR PROJECT/
├── agents/
│   ├── __init__.py
│   ├── planner_agent.py      # LangChain-based reasoning agent
│   └── execution_planner.py  # Timeline & dependency graph generator
├── tools/
│   ├── __init__.py
│   └── mock_tools.py         # Simulated competitor/audience/platform APIs
├── generator/
│   ├── __init__.py
│   └── content_generator.py  # GPT-powered marketing content generator
├── vector_db/
│   ├── __init__.py
│   └── knowledge_base.py     # FAISS knowledge base with RAG retrieval
├── ui/
│   └── app.py                # Streamlit web interface
├── main.py                   # CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Setup

### 1. Clone / navigate to the project
```bash
cd "f:\MAJOR PROJECT"
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux / Mac
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your API key
Copy `.env.example` to `.env` and fill in your OpenAI API key:
```bash
copy .env.example .env
# then edit .env:
OPENAI_API_KEY=sk-your-actual-key-here
```

> **Alternative:** Use [OpenRouter](https://openrouter.ai) as a drop-in proxy:
> ```
> OPENAI_API_KEY=sk-or-your-openrouter-key
> OPENAI_BASE_URL=https://openrouter.ai/api/v1
> ```

---

## ▶️ Running the App

### Streamlit Web UI (recommended)
```bash
streamlit run ui/app.py
```
Open http://localhost:8501 in your browser.

### Command-Line (CLI)
```bash
# Default demo input
python main.py

# Custom input
python main.py --goal "Launch Instagram campaign for skincare product" \
               --audience "Women aged 22-35" \
               --platform "Instagram"
```

---

## 🧪 Example Output

**Input:** `"Launch Instagram campaign for skincare product"`

**Output:**
1. ✅ 8-10 step marketing plan with task dependencies
2. 📅 Day-wise execution timeline
3. 🔗 ASCII dependency graph
4. 📸 3 Instagram captions (benefit-led, storytelling, UGC)
5. 📢 2 Ad copies (AIDA + PAS frameworks)
6. 📧 Full email campaign (subject, body, CTAs)

---

## 🧠 Architecture Overview

```
User Input
    │
    ▼
PlannerAgent ──► TOOL_REGISTRY (mock APIs)
    │               ├─ competitor_analysis_tool()
    │               ├─ audience_analysis_tool()
    │               └─ platform_selection_tool()
    │
    ▼
MarketingPlan (JSON)
    │
    ▼
ExecutionPlanner ──► Readable plan + timeline + dep graph
    │
    ▼
MarketingKnowledgeBase (FAISS)
    │   ▲ RAG retrieval
    ▼   │
ContentGenerator ──► Instagram captions
                 └──► Ad copies
                 └──► Email campaign
```

---

## 📚 Tech Stack

- **Python 3.10+**
- **LangChain** — agent orchestration & prompt templates
- **OpenAI GPT-4o-mini** — reasoning + generation
- **FAISS** — vector database for knowledge retrieval
- **Streamlit** — web interface
- **Pydantic v2** — data validation
- **python-dotenv** — environment management

---

## ▶️ How to Run

Activate your Python environment, then run:

```
streamlit run ui/app.py
```

Open the displayed local URL in your browser to use the MarketMind AI interface.
