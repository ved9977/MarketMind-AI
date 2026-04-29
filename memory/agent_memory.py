"""
Memory module for persistent and contextual learning.
Stores and retrieves past campaigns, user preferences, and feedback.
Supports both FAISS and JSON-based memory.
"""
import os
import json
from typing import Any, Dict, List, Optional

MEMORY_FILE = os.path.join(os.path.dirname(__file__), 'agent_memory.json')

class AgentMemory:
    def __init__(self):
        self.memory = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"campaigns": [], "preferences": {}, "feedback": []}

    def save_campaign_to_memory(self, campaign: Dict[str, Any]):
        self.memory["campaigns"].append(campaign)
        self._persist()

    def save_user_preference(self, key: str, value: Any):
        self.memory["preferences"][key] = value
        self._persist()

    def save_feedback(self, feedback: Dict[str, Any]):
        self.memory["feedback"].append(feedback)
        self._persist()

    def retrieve_relevant_memory(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Simple relevance: match platform, audience, or tone
        relevant = []
        for camp in self.memory["campaigns"]:
            if any(
                camp.get(k) == v for k, v in query.items() if v is not None
            ):
                relevant.append(camp)
        return relevant

    def get_preferences(self) -> Dict[str, Any]:
        return self.memory["preferences"]

    def _persist(self):
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2)

# Usage example:
# memory = AgentMemory()
# memory.save_campaign_to_memory({...})
# relevant = memory.retrieve_relevant_memory({"platform": "Instagram"})
