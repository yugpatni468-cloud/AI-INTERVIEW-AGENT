import json
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from google import genai

load_dotenv()


class GeminiService:
    """Small Gemini wrapper used by question, evaluation, and scoring flows."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        self.client = genai.Client(api_key=self.api_key)

    def ask(self, prompt: str) -> str:
        """Keep the existing /interview/start integration compatible."""
        return self.generate_text(prompt)

    def generate_text(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        text = getattr(response, "text", None)
        if not text or not text.strip():
            raise RuntimeError("Gemini returned an empty response")

        return text.strip()

    def generate_with_context(
        self,
        system_instruction: str,
        user_prompt: str,
    ) -> str:
        """
        Generate a response using explicit interview context.

        This gives later question-generation and feedback calls a stable,
        reusable way to supply system rules and turn-specific instructions.
        """
        prompt = (
            f"{system_instruction.strip()}\n\n"
            f"--- Current task ---\n"
            f"{user_prompt.strip()}"
        )
        return self.generate_text(prompt)

    def generate_json(
        self,
        prompt: str,
    ) -> Dict[str, Any]:
        """
        Request a JSON object and safely decode Gemini's response.

        The prompt must instruct Gemini to return one JSON object only.
        This method will be used later for answer classification and scoring.
        """
        raw_response = self.generate_text(prompt)
        cleaned_response = self._remove_markdown_fence(raw_response)

        try:
            result = json.loads(cleaned_response)
        except json.JSONDecodeError as error:
            raise ValueError(
                "Gemini did not return valid JSON"
            ) from error

        if not isinstance(result, dict):
            raise ValueError("Gemini must return a JSON object")

        return result

    @staticmethod
    def _remove_markdown_fence(text: str) -> str:
        text = text.strip()

        if text.startswith("```"):
            lines = text.splitlines()

            if lines:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        return text