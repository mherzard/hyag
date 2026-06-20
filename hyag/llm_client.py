"""LLM client interface for translation."""

import re
from abc import ABC, abstractmethod
from typing import Optional


class LLMTranslator(ABC):
    """Abstract interface for a translator LLM."""

    @abstractmethod
    async def translate_to_english(self, text: str, context: Optional[str] = None) -> str:
        """Translate prepared Armenian/English marker text into clean English agent command."""
        pass

    @abstractmethod
    async def translate_to_armenian(self, text: str, instructions: str = "") -> str:
        """Translate English agent result into natural Armenian."""
        pass


class DummyLLMTranslator(LLMTranslator):
    """A mock translator for testing and offline demos.

    Strips markers and removes Armenian suffixes that may stick to protected
    English terms. For a real deployment, use OpenAILLMTranslator or another
    production LLM client.
    """

    _SUFFIX_RE = re.compile(r"([a-zA-Z0-9_.]+)(ներ|ների|ից|ով|ում|ն|ը)")

    async def translate_to_english(self, text: str, context: Optional[str] = None) -> str:
        text = text.replace("[[", "").replace("]]", "")
        # Repeatedly remove Armenian suffixes attached to English terms so validators see clean words
        while self._SUFFIX_RE.search(text):
            text = self._SUFFIX_RE.sub(r"\1", text)
        return text.strip()

    async def translate_to_armenian(self, text: str, instructions: str = "") -> str:
        # Identity for testing; a real LLM would produce natural Armenian here
        return text.strip()


class OllamaLLMTranslator(LLMTranslator):
    """LLM translator that talks to Ollama via its native HTTP API.

    Requires the `requests` package (or any HTTP client). You can also point
    Ollama's OpenAI-compatible endpoint to the existing OpenAILLMTranslator.
    """

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        temperature: float = 0.1,
        timeout: float = 120.0,
        client=None,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.timeout = timeout
        self.client = client or self._default_client()

    @staticmethod
    def _default_client():
        import requests
        return requests

    def _chat(self, system: str, user: str) -> str:
        """Send a chat request to Ollama and return the assistant's content."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {
                "temperature": self.temperature,
            },
            "stream": False,
        }
        response = self.client.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "").strip()

    async def translate_to_english(self, text: str, context: Optional[str] = None) -> str:
        system = (
            "You translate Armenian agent prompts into clear, imperative English commands. "
            "Preserve all [[...]] markers exactly as they are. "
            "Output only the translated command, no extra text."
        )
        if context:
            system += f"\nPrevious correction context: {context}"
        return self._chat(system, text)

    async def translate_to_armenian(self, text: str, instructions: str = "") -> str:
        system = (
            "You translate English text into natural Armenian. "
            "Keep code snippets, file paths, identifiers, and technical names unchanged. "
            "Output only the translation, no extra text."
        )
        if instructions:
            system += f" {instructions}"
        return self._chat(system, text)

    @classmethod
    def openai_compatible(
        cls,
        model: str,
        base_url: str = "http://localhost:11434/v1",
        temperature: float = 0.1,
    ):
        """Return an OpenAILLMTranslator pointed at Ollama's OpenAI-compatible endpoint."""
        import openai
        client = openai.OpenAI(base_url=base_url, api_key="ollama")
        return OpenAILLMTranslator(client, model=model)


class OpenAILLMTranslator(LLMTranslator):
    """Example OpenAI-based translator. Requires openai package."""

    def __init__(self, client, model: str = "gpt-4o-mini"):
        self.client = client
        self.model = model

    async def translate_to_english(self, text: str, context: Optional[str] = None) -> str:
        system = (
            "You translate Armenian agent prompts into clear, imperative English commands. "
            "Preserve all [[...]] markers exactly as they are. "
            "Output only the translated command, no extra text."
        )
        if context:
            system += f"\nPrevious correction context: {context}"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": text},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()

    async def translate_to_armenian(self, text: str, instructions: str = "") -> str:
        system = (
            "You translate English text into natural Armenian. "
            "Keep code snippets, file paths, identifiers, and technical names unchanged. "
            "Output only the translation, no extra text."
        )
        if instructions:
            system += f" {instructions}"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": text},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
