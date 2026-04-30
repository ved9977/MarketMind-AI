# 🧠 MarketMind AI — Autonomous Marketing Planner & Content Engine

> An intelligent, modular Python system that combines **Agentic AI** (planning & reasoning) with **Generative AI** (content creation) to automate complete marketing campaigns end-to-end.

---

## 🚀 Features

| Module            | Technology              | What it does                                      |
| ----------------- | ----------------------- | ------------------------------------------------- |
| Planner Agent     | LangChain + GPT-4o-mini | Decomposes a marketing goal into structured steps |
| Mock Tools        | Python                  | Competitor, audience, platform analysis           |
| Execution Planner | Python                  | Converts plan → timeline & tasks                  |
| Knowledge Base    | FAISS + OpenAI          | Stores templates & retrieves context              |
| Content Generator | GPT-4o-mini             | Generates captions, ads, emails                   |
| Streamlit UI      | Streamlit               | Web interface                                     |

---

## 🚀 Enhanced Features

* Memory System (stores past campaigns)
* Personalization Engine (custom strategies)
* Campaign Calendar Generator

---

## 🧠 Example Input

```json
{
  "audience": "Gen Z",
  "platform": "Instagram",
  "budget": "low",
  "tone": "casual"
}
```

---

## 🎯 Example Output

```json
[
  {"day": 1, "activity": "Instagram Reel"},
  {"day": 2, "activity": "Story Post"}
]
```

---

## 📁 Project Structure

```
MarketMind-AI/
├── agents/
├── tools/
├── generator/
├── vector_db/
├── ui/
├── main.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

```bash
git clone https://github.com/ved9977/MarketMind-AI.git
cd MarketMind-AI

python -m venv venv
source venv/bin/activate   # Linux
pip install -r requirements.txt
```

---

## 🔑 Add API Key

```bash
export OPENAI_API_KEY=your_key_here
```

---

## ▶️ Run App

```bash
streamlit run main.py
```

Open:

```
http://localhost:8501
```

---

## 🚀 Deployment

CI/CD enabled using **GitHub Actions + EC2**

Push to main → auto deploy 🚀

---

## 🧠 Tech Stack

* Python
* LangChain
* OpenAI
* FAISS
* Streamlit

---

## 👨‍💻 Author

Ved Meena
