"""
MarketMind AI – vector_db package.

Exposes the MarketingKnowledgeBase class that wraps FAISS for
storing and retrieving marketing templates, tone guides, and examples.
"""

from vector_db.knowledge_base import MarketingKnowledgeBase

__all__ = ["MarketingKnowledgeBase"]
