"""
IBM Granite LLM Service
Wraps ibm-watsonx-ai SDK to expose a clean generate() interface.
Falls back to a local mock when credentials are not configured (dev mode).
"""

import os
import re
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class GraniteLLMService:
    """
    Interface to IBM Granite via watsonx.ai.

    Usage:
        llm = GraniteLLMService()
        response = llm.generate("Tell me about Python decorators.")
    """

    def __init__(self):
        self.api_key    = os.getenv("IBM_API_KEY", "")
        self.project_id = os.getenv("IBM_PROJECT_ID", "")
        self.url        = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        self.model_id   = os.getenv("IBM_GRANITE_MODEL_ID", "ibm/granite-13b-instruct-v2")
        self._client    = None
        self._model     = None
        self._use_mock  = not (self.api_key and self.project_id)

        if self._use_mock:
            logger.warning(
                "⚠️  IBM credentials not set – running in MOCK mode. "
                "Set IBM_API_KEY and IBM_PROJECT_ID in .env to use real Granite."
            )
        else:
            self._init_client()

    # ── Initialise watsonx.ai client ─────────────────────────────────────────
    def _init_client(self):
        try:
            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

            credentials = Credentials(url=self.url, api_key=self.api_key)

            params = {
                GenParams.MAX_NEW_TOKENS: 1024,
                GenParams.MIN_NEW_TOKENS: 10,
                GenParams.TEMPERATURE:    0.7,
                GenParams.TOP_P:          0.9,
                GenParams.REPETITION_PENALTY: 1.1,
            }

            self._model = ModelInference(
                model_id=self.model_id,
                credentials=credentials,
                project_id=self.project_id,
                params=params,
            )
            logger.info(f"✅  IBM Granite model '{self.model_id}' initialised.")
        except Exception as exc:
            logger.error(f"❌  Failed to init IBM Granite: {exc}")
            self._use_mock = True

    # ── Public generate method ───────────────────────────────────────────────
    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """
        Send `prompt` to IBM Granite and return the generated text.
        Falls back to mock response in dev/test mode.
        """
        if self._use_mock:
            return self._mock_response(prompt)

        try:
            result = self._model.generate_text(prompt=prompt)
            return result.strip() if isinstance(result, str) else str(result)
        except Exception as exc:
            logger.error(f"Granite generate error: {exc}")
            return self._mock_response(prompt)

    # ── Mock responses for development without IBM credentials ───────────────
    def _mock_response(self, prompt: str) -> str:
        """
        Deterministic mock that returns plausible responses so the app
        works end-to-end without real credentials during development.
        """
        prompt_lower = prompt.lower()

        if "generate" in prompt_lower and "question" in prompt_lower:
            return json.dumps({
                "technical": [
                    "Explain the difference between REST and GraphQL APIs.",
                    "What is Big-O notation? Give examples.",
                    "How does garbage collection work in Python/Java?",
                    "Describe the SOLID principles with examples.",
                    "What is a database index and when should you use one?",
                ],
                "hr": [
                    "Tell me about yourself and your career journey.",
                    "Describe a situation where you had to meet a tight deadline.",
                    "Where do you see yourself in 5 years?",
                    "How do you handle conflict within a team?",
                    "What is your greatest professional achievement?",
                ],
            })

        if "feedback" in prompt_lower or "evaluate" in prompt_lower:
            return json.dumps({
                "score": 7,
                "strengths": [
                    "Clear and structured response",
                    "Good use of technical terminology",
                    "Demonstrated practical experience",
                ],
                "improvements": [
                    "Add a concrete code example to strengthen the answer",
                    "Mention trade-offs or edge cases",
                    "Quantify the impact of your work where possible",
                ],
                "model_tip": (
                    "A strong answer follows the STAR method (Situation, Task, Action, Result). "
                    "Always tie your response back to the job role requirements."
                ),
            })

        if "chat" in prompt_lower or "interviewer" in prompt_lower:
            return (
                "That's a great point! Could you elaborate on the specific technologies "
                "you used and the challenges you overcame? For example, how did you "
                "handle scalability concerns in that project?"
            )

        # Generic fallback
        return (
            "Thank you for sharing that. IBM Granite (mock mode) is active. "
            "Please configure IBM_API_KEY and IBM_PROJECT_ID in your .env file "
            "to enable full AI responses from the Granite-13b-instruct model."
        )

    # ── Utility ──────────────────────────────────────────────────────────────
    @property
    def is_mock(self) -> bool:
        return self._use_mock

    def health_check(self) -> dict:
        return {
            "status":   "mock" if self._use_mock else "live",
            "model_id": self.model_id,
            "endpoint": self.url,
        }


# ── Singleton instance ────────────────────────────────────────────────────────
_llm_instance: Optional[GraniteLLMService] = None


def get_llm() -> GraniteLLMService:
    """Return the singleton GraniteLLMService instance."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = GraniteLLMService()
    return _llm_instance