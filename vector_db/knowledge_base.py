"""
vector_db/knowledge_base.py
============================
MarketingKnowledgeBase – FAISS-backed vector store for marketing templates,
tone guides, and example content.

Capabilities
------------
* Encodes a built-in corpus of marketing knowledge using OpenAI embeddings.
* Persists the index to disk so embeddings are only computed once.
* Retrieves the top-k most relevant documents for any query string.
* Provides formatted context strings ready for injection into LLM prompts.

Design decisions
----------------
* Uses FAISS (CPU) via langchain-community for zero-infrastructure setup.
* Falls back gracefully when no API key is available (returns empty context).
* The default knowledge corpus is hardcoded; extend KNOWLEDGE_CORPUS to add more.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env", override=True)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Built-in marketing knowledge corpus
# ---------------------------------------------------------------------------

KNOWLEDGE_CORPUS: list[dict[str, str]] = [
    # ── Tone guides ─────────────────────────────────────────────────────────
    {
        "id": "tone_professional",
        "category": "Tone Guide",
        "title": "Professional Marketing Tone",
        "content": (
            "Professional marketing copy is confident, clear, and benefit-focused. "
            "Use active voice, short sentences, and strong verbs. Avoid jargon unless "
            "the audience is expert-level. Lead with the customer benefit, not the feature. "
            "Always close with a single, compelling call-to-action."
        ),
    },
    {
        "id": "tone_conversational",
        "category": "Tone Guide",
        "title": "Conversational / Gen-Z Tone",
        "content": (
            "Address the reader directly ('you'). Use contractions and colloquial language "
            "that resonates with 18-24-year-olds. Embrace humour, authenticity, and "
            "imperfection. Short paragraphs or even sentence fragments are fine. "
            "Emojis can amplify emotion but should not exceed 3 per post."
        ),
    },
    {
        "id": "tone_luxury",
        "category": "Tone Guide",
        "title": "Luxury Brand Tone",
        "content": (
            "Luxury copy exudes exclusivity and aspiration. Use sensory language and "
            "evocative adjectives. Avoid discounts and urgency tactics — scarcity is "
            "implied, never shouted. Sentences can be longer and more lyrical. "
            "Minimalism is key: say more with less."
        ),
    },
    # ── Instagram templates ─────────────────────────────────────────────────
    {
        "id": "ig_caption_benefit",
        "category": "Instagram Template",
        "title": "Benefit-Led Caption",
        "content": (
            "Template: '[Transformation statement]. [Product name] delivers [key benefit] "
            "with [hero ingredient/feature]. No [pain point]. Just [desired outcome].\n"
            "Shop via the link in bio. 🛒\n#[Brand] #[Category] #[Trend]'\n\n"
            "Example: 'Glow that lasts all day. LumiGlow Serum delivers 72-hour hydration "
            "with hyaluronic acid. No more dry patches. Just luminous, healthy skin.'"
        ),
    },
    {
        "id": "ig_caption_storytelling",
        "category": "Instagram Template",
        "title": "Storytelling Caption",
        "content": (
            "Template: '[Relatable opening problem]. We've been there. That's why we "
            "created [product] — [mission statement]. [Social proof or result]. "
            "Ready to [desired outcome]? Try it risk-free. Link in bio.'\n\n"
            "Open with a question or surprising stat to maximise the 'More' click-through rate."
        ),
    },
    {
        "id": "ig_caption_ugc",
        "category": "Instagram Template",
        "title": "UGC / Testimonial Caption",
        "content": (
            "Lead with a customer quote in inverted commas. Follow with 2-3 lines "
            "reinforcing the product benefit. Tag the original poster where possible. "
            "End with a community CTA: 'Share your story – tag us with #[BrandHashtag].'"
        ),
    },
    # ── Ad copy templates ────────────────────────────────────────────────────
    {
        "id": "ad_aida",
        "category": "Ad Copy Template",
        "title": "AIDA Framework Ad",
        "content": (
            "AIDA = Attention → Interest → Desire → Action.\n"
            "Headline (Attention): Bold claim or provocative question (<8 words).\n"
            "Sub-headline (Interest): Expand with the key differentiator.\n"
            "Body (Desire): 2-3 bullet benefits + social proof.\n"
            "CTA (Action): Single, time-bound action ('Shop Now – Free Shipping Today Only')."
        ),
    },
    {
        "id": "ad_problem_agitate",
        "category": "Ad Copy Template",
        "title": "Problem-Agitate-Solve (PAS) Ad",
        "content": (
            "Step 1 – Problem: Clearly name the pain.\n"
            "Step 2 – Agitate: Amplify the emotional cost of inaction.\n"
            "Step 3 – Solve: Present the product as the relief.\n"
            "Example: 'Still hiding behind heavy foundation? Every failed skincare routine "
            "costs you confidence. Meet DermShield — 4-week clinical results, zero compromise.'"
        ),
    },
    # ── Email templates ──────────────────────────────────────────────────────
    {
        "id": "email_welcome",
        "category": "Email Template",
        "title": "Welcome / Launch Email Structure",
        "content": (
            "Subject: [Benefit or curiosity hook] | 45 chars max.\n"
            "Preview text: extends/contradicts the subject for higher open rate.\n"
            "Body structure:\n"
            "  1. Hero image (lifestyle, not product-only).\n"
            "  2. Warm greeting + one-sentence brand promise.\n"
            "  3. The 'Here's what's in it for you' section (3 bullet points).\n"
            "  4. Social proof block (star rating + one quote).\n"
            "  5. Primary CTA button (contrasting colour).\n"
            "  6. Secondary CTA (softer: 'Learn more').\n"
            "  7. Footer with unsubscribe link (legal requirement)."
        ),
    },
    {
        "id": "email_promotional",
        "category": "Email Template",
        "title": "Promotional / Offer Email",
        "content": (
            "Best practice: send Tuesday–Thursday, 09:00–11:00 local time.\n"
            "Subject line formula: '[Number]% off [product]? Yes, really.' or "
            "'Your exclusive [brand] offer expires [date]'.\n"
            "Body: Urgency first, value second, proof third.\n"
            "Always A/B test subject lines on at least 20% of your list before full send."
        ),
    },
    # ── Marketing strategy frameworks ────────────────────────────────────────
    {
        "id": "strategy_funnel",
        "category": "Strategy Framework",
        "title": "Full-Funnel Marketing Model",
        "content": (
            "TOFU (Top of Funnel): Awareness — broad-reach content (Reels, viral posts, PR).\n"
            "MOFU (Middle of Funnel): Consideration — educational content, testimonials, demos.\n"
            "BOFU (Bottom of Funnel): Conversion — offers, retargeting, urgency triggers.\n"
            "Retention: Post-purchase nurture — loyalty rewards, UGC encouragement, cross-sell."
        ),
    },
    {
        "id": "strategy_content_calendar",
        "category": "Strategy Framework",
        "title": "Content Calendar Best Practices",
        "content": (
            "Plan content in 4-week sprints. Allocate themes per week:\n"
            "  Week 1: Education / awareness.\n"
            "  Week 2: Social proof / UGC.\n"
            "  Week 3: Product spotlight.\n"
            "  Week 4: Promotional / offer.\n"
            "Maintain a 70/20/10 ratio: 70% value, 20% brand, 10% promotional."
        ),
    },
    # ── Skincare-specific ────────────────────────────────────────────────────
    {
        "id": "skincare_messaging",
        "category": "Vertical Knowledge",
        "title": "Skincare Marketing Messaging Pillars",
        "content": (
            "Trust pillars for skincare brands:\n"
            "  1. Clinical credibility — 'dermatologist-tested', 'clinically proven'.\n"
            "  2. Ingredient transparency — hero ingredient stories (hyaluronic acid, retinol).\n"
            "  3. Inclusivity — diverse skin tones, types, and concerns.\n"
            "  4. Sustainability — cruelty-free, vegan, minimal packaging.\n"
            "  5. Transformation — before/after imagery (with regulatory compliance).\n"
            "Regulatory note: avoid absolute claims ('cures', 'treats') unless medically certified."
        ),
    },
]


# ---------------------------------------------------------------------------
# MarketingKnowledgeBase
# ---------------------------------------------------------------------------

class MarketingKnowledgeBase:
    """
    FAISS-backed vector knowledge base for marketing content retrieval.

    Parameters
    ----------
    persist_path : str | None
        Directory to save/load the FAISS index and document store.
        If None, the index is held in memory only.
    embedding_model : str
        OpenAI embedding model name (default: text-embedding-3-small).
    corpus : list[dict] | None
        Knowledge documents to index. Defaults to KNOWLEDGE_CORPUS.
    """

    def __init__(
        self,
        persist_path: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small",
        corpus: Optional[list[dict]] = None,
    ) -> None:
        self.persist_path = persist_path
        self.embedding_model = embedding_model
        self.corpus = corpus or KNOWLEDGE_CORPUS
        self._vector_store = None  # lazy-init

        # Try to initialise; if API key is missing, operate in fallback mode
        try:
            self._init_vector_store()
        except Exception as exc:
            logger.warning(
                "KnowledgeBase could not initialise embeddings (%s). "
                "Retrieval will return empty context.",
                exc,
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Retrieve the top-k most relevant knowledge documents for a query.

        Parameters
        ----------
        query : str
            The search query (e.g. "Instagram caption skincare").
        top_k : int
            Number of documents to return (default: 3).

        Returns
        -------
        list[dict]
            Each dict has keys: title, category, content, score.
        """
        if self._vector_store is None:
            logger.warning("Vector store unavailable; returning empty results.")
            return []

        try:
            results = self._vector_store.similarity_search_with_score(query, k=top_k)
            retrieved = []
            for doc, score in results:
                retrieved.append(
                    {
                        "title": doc.metadata.get("title", "Untitled"),
                        "category": doc.metadata.get("category", ""),
                        "content": doc.page_content,
                        "score": round(float(score), 4),
                    }
                )
            return retrieved
        except Exception as exc:
            logger.error("Retrieval failed: %s", exc)
            return []

    def retrieve_as_context(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve documents and format them as an LLM-ready context block.

        Returns
        -------
        str
            Formatted context string, or a notice if nothing was found.
        """
        docs = self.retrieve(query, top_k=top_k)
        if not docs:
            return "No relevant marketing knowledge retrieved."

        parts = ["--- RETRIEVED MARKETING KNOWLEDGE ---"]
        for i, doc in enumerate(docs, 1):
            parts.append(
                f"\n[{i}] {doc['category']} | {doc['title']}\n{doc['content']}"
            )
        parts.append("--- END OF RETRIEVED KNOWLEDGE ---")
        return "\n".join(parts)

    def add_documents(self, documents: list[dict]) -> None:
        """
        Add new documents to the knowledge base at runtime.

        Parameters
        ----------
        documents : list[dict]
            Each dict must have a 'content' key; optional: 'title', 'category'.
        """
        if self._vector_store is None:
            logger.warning("Cannot add documents: vector store not initialised.")
            return

        from langchain_core.documents import Document

        lc_docs = [
            Document(
                page_content=d["content"],
                metadata={k: v for k, v in d.items() if k != "content"},
            )
            for d in documents
        ]
        self._vector_store.add_documents(lc_docs)
        logger.info("Added %d documents to the knowledge base.", len(lc_docs))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _init_vector_store(self) -> None:
        """Build or load the FAISS vector store."""
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import FAISS
        from langchain_core.documents import Document

        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")

        embed_kwargs: dict = {"model": self.embedding_model, "api_key": api_key}
        if base_url:
            embed_kwargs["base_url"] = base_url

        embeddings = OpenAIEmbeddings(**embed_kwargs)

        # Try loading from disk first
        if self.persist_path and Path(self.persist_path).exists():
            try:
                self._vector_store = FAISS.load_local(
                    self.persist_path,
                    embeddings,
                    allow_dangerous_deserialization=True,
                )
                logger.info("Loaded FAISS index from %s", self.persist_path)
                return
            except Exception as exc:
                logger.warning("Could not load persisted index: %s. Rebuilding.", exc)

        # Build from corpus
        docs = [
            Document(
                page_content=entry["content"],
                metadata={k: v for k, v in entry.items() if k != "content"},
            )
            for entry in self.corpus
        ]
        self._vector_store = FAISS.from_documents(docs, embeddings)
        logger.info("Built FAISS index with %d documents.", len(docs))

        # Persist if path provided
        if self.persist_path:
            Path(self.persist_path).mkdir(parents=True, exist_ok=True)
            self._vector_store.save_local(self.persist_path)
            logger.info("Saved FAISS index to %s", self.persist_path)
