import json
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class GeminiService:
    """
    AI provider wrapper.

    The class name is preserved so existing route imports keep working,
    but requests are now sent to Groq.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv(
            "GROQ_MODEL",
            "llama-3.3-70b-versatile",
        )

        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is missing from the .env file")

        self.client = Groq(api_key=self.api_key)

    def ask(self, prompt: str) -> str:
        return self.generate_text(prompt)

    def generate_text(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.3,
        )

        text = completion.choices[0].message.content

        if not text or not text.strip():
            raise RuntimeError("Groq returned an empty response")

        return text.strip()

    def generate_with_context(
        self,
        system_instruction: str,
        user_prompt: str,
    ) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_instruction.strip(),
                },
                {
                    "role": "user",
                    "content": user_prompt.strip(),
                },
            ],
            temperature=0.3,
        )

        text = completion.choices[0].message.content

        if not text or not text.strip():
            raise RuntimeError("Groq returned an empty response")

        return text.strip()

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )

        text = completion.choices[0].message.content

        if not text or not text.strip():
            raise RuntimeError("Groq returned an empty JSON response")

        try:
            result = json.loads(text)
        except json.JSONDecodeError as error:
            raise ValueError("Groq did not return valid JSON") from error

        if not isinstance(result, dict):
            raise ValueError("Groq must return a JSON object")

        return result