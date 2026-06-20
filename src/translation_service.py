"""Lightweight prompt/result translation helpers for CLI and skill integrations."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agent_client import AgentExecutor
from .llm_client import DummyLLMTranslator, LLMTranslator, OllamaLLMTranslator
from .translator import SpecializedTranslator
from .validator import ValidationIssue, ValidationLayer


def _issue_to_dict(issue: ValidationIssue) -> Dict[str, str]:
    return {
        "stage": issue.stage,
        "severity": issue.severity,
        "message": issue.message,
        "user_message": issue.user_message,
        "fix_hint": issue.fix_hint,
    }


class TranslationService:
    """Translate Armenian prompts to English and English results to Armenian.

    Unlike `ArmenianAgentBridge`, this service does **not** run an agent; it is
    meant for integrations where the actual tool execution is performed by
    another system (e.g. Claude Code, OpenCode).
    """

    def __init__(
        self,
        llm_translator: Optional[LLMTranslator] = None,
        dictionaries: Optional[Dict[str, Dict[str, str]]] = None,
        dictionary_path: Optional[str] = None,
    ):
        if dictionaries is None:
            if dictionary_path is None:
                dictionary_path = str(Path(__file__).parent.parent / "config" / "dictionaries.json")
            with open(dictionary_path, "r", encoding="utf-8") as f:
                dictionaries = json.load(f)

        self.dictionaries = dictionaries
        self.translator = SpecializedTranslator(dictionaries)
        self.validator = ValidationLayer(dictionaries)
        self.llm = llm_translator or DummyLLMTranslator()

    async def translate_prompt(self, armenian_prompt: str) -> Dict[str, Any]:
        """Return {'english_prompt': ..., 'issues': [...]} for an Armenian prompt."""
        prepared = self.translator.pre_process(armenian_prompt)
        expected_terms = re.findall(r"\[\[(.*?)\]\]", prepared)

        english_prompt = await self.llm.translate_to_english(prepared)
        english_prompt = english_prompt.replace("[[", "").replace("]]", "")

        issues = self.validator.validate_english_prompt(english_prompt, expected_terms)

        return {
            "armenian_prompt": armenian_prompt,
            "english_prompt": english_prompt,
            "issues": [_issue_to_dict(i) for i in issues],
        }

    async def translate_result(self, english_result: str) -> Dict[str, Any]:
        """Return {'armenian_output': ..., 'issues': [...]} for an English result."""
        armenian_output = await self.llm.translate_to_armenian(
            english_result,
            instructions="Natural Armenian, keep code, paths, and identifiers unchanged.",
        )
        armenian_output = self.translator.post_process(armenian_output)

        issues = self.validator.validate_armenian_output(armenian_output)

        return {
            "english_result": english_result,
            "armenian_output": armenian_output,
            "issues": [_issue_to_dict(i) for i in issues],
        }

    @classmethod
    def from_env(cls) -> "TranslationService":
        """Create a TranslationService using environment variables for the LLM.

        Environment variables:
          - OLLAMA_MODEL: if set, use OllamaLLMTranslator with this model
          - OLLAMA_BASE_URL: optional, defaults to http://localhost:11434
          - HYAG_DICT_PATH: optional, path to a custom dictionaries.json
        """
        dictionary_path = None
        if "HYAG_DICT_PATH" in __import__("os").environ:
            dictionary_path = __import__("os").environ["HYAG_DICT_PATH"]

        llm = None
        if "OLLAMA_MODEL" in __import__("os").environ:
            llm = OllamaLLMTranslator(
                model=__import__("os").environ["OLLAMA_MODEL"],
                base_url=__import__("os").environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            )

        return cls(llm_translator=llm, dictionary_path=dictionary_path)
