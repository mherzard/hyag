"""Validation layer for the Armenian agent bridge."""

import re
from dataclasses import dataclass
from typing import Dict, List, Set


@dataclass
class ValidationIssue:
    stage: str          # e.g. "english", "agent_result", "armenian"
    severity: str       # "warning" | "error"
    message: str        # internal English description
    user_message: str     # Armenian message shown to the user
    fix_hint: str       # hint for retry/fix


class ValidationLayer:
    """Validates prompts, agent results, and Armenian output."""

    def __init__(self, dictionaries: Dict[str, Dict[str, str]], agent_executor=None):
        self.dictionaries = dictionaries
        self.agent = agent_executor
        self.error_markers = [
            "error", "exception", "traceback", "failed",
            "permission denied", "not found", "invalid"
        ]

    def validate_english_prompt(self, prompt: str, expected_terms: List[str] = None) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        leftover = re.findall(r"\[\[.*?\]\]", prompt)
        if leftover:
            issues.append(ValidationIssue(
                stage="english",
                severity="error",
                message=f"Leftover markers: {leftover}",
                user_message="Որոշ տեխնիկական տերմիններ չեն վերամշակվել ճիշտ։",
                fix_hint="Հեռացնել [[...]] փակագծերը և թողնել միայն անգլերեն արժեքը։"
            ))

        stripped = prompt.strip()
        if len(stripped) < 10:
            issues.append(ValidationIssue(
                stage="english",
                severity="error",
                message="Prompt is too short",
                user_message="Անգլերեն հրամանը չափազանց կարճ է և կարող է լինել սխալ։",
                fix_hint="Ավելացնել ավելի մանրամասն նկարագրություն։"
            ))

        # Only check terms that were actually introduced by the pre-processor
        expected_terms = expected_terms or []
        protected_names = set(self.dictionaries.get("protected", {}).values())
        for term in expected_terms:
            if not re.search(rf"\b{re.escape(term)}\b", stripped):
                if term in protected_names:
                    issues.append(ValidationIssue(
                        stage="english",
                        severity="error",
                        message=f"Protected name missing: {term}",
                        user_message=f"{term} պաշտպանված անունը բացակայում է կամ փոփոխվել է։",
                        fix_hint="Վերադարձնել սկզբնական անունը անփոփոխ։"
                    ))
                else:
                    issues.append(ValidationIssue(
                        stage="english",
                        severity="warning",
                        message=f"Expected term possibly altered: {term}",
                        user_message=f"{term} տերմինը կարող է լինել փոփոխված։",
                        fix_hint="Պահպանել բառարանի արժեքը թարգմանության ընթացքում։"
                    ))

        return issues

    def validate_agent_result(self, result: str, original_armenian_prompt: str) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        if not result or not result.strip():
            issues.append(ValidationIssue(
                stage="agent_result",
                severity="error",
                message="Agent returned empty result",
                user_message="Ագենտը դատարկ արդյունք է վերադարձրել։",
                fix_hint="Ստուգել հրամանի հասկանալիությունը կամ փորձել այլ եղանակով։"
            ))

        lowered = result.lower()
        for marker in self.error_markers:
            if marker in lowered:
                issues.append(ValidationIssue(
                    stage="agent_result",
                    severity="warning",
                    message=f"Error marker detected: {marker}",
                    user_message=f"Արդյունքում հայտնաբերվել է հնարավոր սխալ՝ «{marker}»։",
                    fix_hint="Ստուգել սխալը և ուղղել հրամանը։"
                ))

        if len(result) > 15000:
            issues.append(ValidationIssue(
                stage="agent_result",
                severity="warning",
                message="Result is very long",
                user_message="Արդյունքը շատ երկար է, կարող է պարունակել ավելորդ տեղեկություն։",
                fix_hint="Հարցնել ավելի կոնկրետ հարցում կամ սահմանափակել երկարությունը։"
            ))

        return issues

    def validate_armenian_output(self, text: str) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []

        reverse_map: Dict[str, str] = {}
        for d in self.dictionaries.values():
            for hy, en in d.items():
                reverse_map[en] = hy

        keep_english = set(self.dictionaries.get("keep_english", {}).values())
        protected_names = set(self.dictionaries.get("protected", {}).values())

        # Do not flag protected names or keep-english terms
        for en, hy in reverse_map.items():
            if en in keep_english or en in protected_names:
                continue
            if re.search(rf"\b{re.escape(en)}\b", text):
                issues.append(ValidationIssue(
                    stage="armenian",
                    severity="warning",
                    message=f"English term left untranslated: {en}",
                    user_message=f"Պատասխանում մնացել է անգլերեն տերմին՝ «{en}»։ Ավելի լավ կլինի՝ «{hy}»։",
                    fix_hint="Օգտագործել բառարանային հետամշակում՝ այս տերմինը հայերենացնելու համար։"
                ))

        armenian_chars = len(re.findall(r"[ա-֏]", text))
        total_chars = len(re.sub(r"\s", "", text))
        if total_chars > 20 and armenian_chars / total_chars < 0.3:
            issues.append(ValidationIssue(
                stage="armenian",
                severity="warning",
                message="Output seems mostly non-Armenian",
                user_message="Պատասխանը թվում է անգլերեն կամ չափազանց տեխնիկական, քիչ հայերեն տեքստ կա։",
                fix_hint="Հետադարձ թարգմանությունը լավացնել կամ բացատրել տեխնիկական մասերը։"
            ))

        return issues
