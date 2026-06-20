"""Armenian Agent Bridge orchestrator."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agent_client import AgentExecutor, DummyAgentExecutor
from .llm_client import DummyLLMTranslator, LLMTranslator
from .translator import SpecializedTranslator
from .validator import ValidationLayer, ValidationIssue


class ArmenianAgentBridge:
    """End-to-end bridge: Armenian prompt -> agent execution -> Armenian result."""

    def __init__(
        self,
        llm_translator: Optional[LLMTranslator] = None,
        agent_executor: Optional[AgentExecutor] = None,
        dictionaries: Optional[Dict[str, Dict[str, str]]] = None,
        dictionary_path: Optional[str] = None,
        max_retries: int = 2,
    ):
        if dictionaries is None:
            if dictionary_path is None:
                dictionary_path = str(Path(__file__).parent / "config" / "dictionaries.json")
            with open(dictionary_path, "r", encoding="utf-8") as f:
                dictionaries = json.load(f)

        self.translator = SpecializedTranslator(dictionaries)
        self.validator = ValidationLayer(dictionaries, agent_executor)
        self.llm = llm_translator or DummyLLMTranslator()
        self.agent = agent_executor or DummyAgentExecutor()
        self.max_retries = max_retries
        self.dictionaries = dictionaries

    async def run(self, armenian_prompt: str) -> Dict[str, Any]:
        """Process an Armenian prompt and return an Armenian result."""
        history: List[Dict[str, str]] = []

        for attempt in range(1, self.max_retries + 2):
            # 1. Pre-processing with dictionaries
            prepared = self.translator.pre_process(armenian_prompt)

            # Extract expected terms that were introduced by pre-processing
            expected_terms = re.findall(r"\[\[(.*?)\]\]", prepared)

            # 2. Translate hy -> en
            english_prompt = await self.llm.translate_to_english(
                prepared,
                context="\n".join(f"{h['stage']}: {h['issue']}" for h in history) if history else None,
            )
            english_prompt = english_prompt.replace("[[", "").replace("]]", "")

            # 3. Validate English prompt
            en_issues = self.validator.validate_english_prompt(english_prompt, expected_terms)
            en_errors = [i for i in en_issues if i.severity == "error"]
            if en_errors:
                history.append(self._issue_to_history(en_errors[0]))
                if self._should_retry(en_errors[0]):
                    continue
                return self._failure(history, attempt)

            # 4. Execute agent
            agent_result = await self.agent.execute(english_prompt)

            # 5. Validate agent result
            result_issues = self.validator.validate_agent_result(agent_result, armenian_prompt)
            result_errors = [i for i in result_issues if i.severity == "error"]
            if result_errors:
                history.append(self._issue_to_history(result_errors[0]))
                if self._should_retry(result_errors[0]):
                    continue
                return self._failure(history, attempt)

            # 6. Translate en -> hy
            armenian_output = await self.llm.translate_to_armenian(
                agent_result,
                instructions="Natural Armenian, keep code, paths, and identifiers unchanged."
            )

            # 7. Post-processing
            armenian_output = self.translator.post_process(armenian_output)

            # 8. Validate Armenian output
            hy_issues = self.validator.validate_armenian_output(armenian_output)
            hy_errors = [i for i in hy_issues if i.severity == "error"]
            if hy_errors:
                history.append(self._issue_to_history(hy_errors[0]))
                if self._should_retry(hy_errors[0]):
                    continue
                return self._failure(history, attempt)

            all_warnings = [
                i.user_message
                for i in en_issues + result_issues + hy_issues
                if i.severity == "warning"
            ]

            return {
                "success": True,
                "armenian_prompt": armenian_prompt,
                "english_prompt": english_prompt,
                "armenian_output": armenian_output,
                "warnings": all_warnings,
                "attempts": attempt,
            }

        return self._failure(history, self.max_retries + 1)

    def _issue_to_history(self, issue: ValidationIssue) -> Dict[str, str]:
        return {
            "stage": issue.stage,
            "issue": issue.message,
            "user_message": issue.user_message,
            "fix_hint": issue.fix_hint,
        }

    def _should_retry(self, issue: ValidationIssue) -> bool:
        """Determine if an issue is worth retrying."""
        return issue.severity == "error" or (
            issue.stage in ("english", "armenian") and issue.severity == "warning"
        )

    def _failure(self, history: List[Dict[str, str]], attempts: int) -> Dict[str, Any]:
        return {
            "success": False,
            "error": "Չհաջողվեց ստանալ ճիշտ պատասխան մի քանի փորձերից հետո։",
            "last_issues": history,
            "attempts": attempts,
        }

    def add_correction(self, category: str, armenian: str, english: str):
        """Add a user correction to the dictionaries."""
        self.translator.add_correction(category, armenian, english)
        self.validator = ValidationLayer(self.dictionaries, self.agent)
