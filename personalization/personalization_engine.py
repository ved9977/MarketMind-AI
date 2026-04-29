"""
Personalization Engine for dynamic prompt and strategy adjustment.
"""
from typing import Dict, Any

class PersonalizationEngine:
    def __init__(self):
        pass

    def personalize_prompt(self, base_prompt: str, user_input: Dict[str, Any]) -> str:
        # Adjust prompt based on user input
        prompt = base_prompt
        if user_input.get("platform"):
            prompt += f"\nPlatform: {user_input['platform']}"
        if user_input.get("audience"):
            prompt += f"\nTarget Audience: {user_input['audience']}"
        if user_input.get("budget"):
            prompt += f"\nBudget: {user_input['budget']}"
        if user_input.get("tone"):
            prompt += f"\nTone: {user_input['tone']}"
        return prompt

    def adjust_strategy(self, strategy: Dict[str, Any], user_input: Dict[str, Any]) -> Dict[str, Any]:
        # Modify strategy dict based on personalization
        strategy = strategy.copy()
        for key in ["platform", "audience", "budget", "tone"]:
            if user_input.get(key):
                strategy[key] = user_input[key]
        return strategy

# Usage example:
# engine = PersonalizationEngine()
# prompt = engine.personalize_prompt(base_prompt, user_input)
