"""Specialized Armenian-English translator with dictionary support."""

import json
from pathlib import Path
from typing import Dict, List


class SpecializedTranslator:
    """Pre- and post-processes text using dictionaries."""

    def __init__(self, dictionaries: Dict[str, Dict[str, str]]):
        self.dictionaries = dictionaries
        # Build combined map (longest keys first to avoid partial replacements)
        self.combined: Dict[str, str] = {}
        for d in dictionaries.values():
            self.combined.update(d)
        self.sorted_keys = sorted(self.combined.keys(), key=len, reverse=True)

    @classmethod
    def from_json(cls, path: str) -> "SpecializedTranslator":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(data)

    def pre_process(self, text: str) -> str:
        """Replace known Armenian terms with protected English equivalents."""
        for hy in self.sorted_keys:
            en = self.combined[hy]
            # Use markers so the LLM keeps them intact during translation
            text = text.replace(hy, f"[[{en}]]")
        return text

    def post_process(self, text: str) -> str:
        """Map protected English terms back to Armenian."""
        # Reverse map: English -> Armenian
        reverse: Dict[str, str] = {}
        for d in self.dictionaries.values():
            for hy, en in d.items():
                reverse[en] = hy

        # Keep English terms as-is for keep_english dictionary
        keep_english = set(self.dictionaries.get("keep_english", {}).values())

        # Longest first to avoid partial replacements
        for en in sorted(reverse.keys(), key=len, reverse=True):
            if en in keep_english:
                continue
            text = text.replace(en, reverse[en])
        return text

    def add_correction(self, category: str, armenian: str, english: str):
        """Add a user correction to the dictionaries."""
        if category not in self.dictionaries:
            self.dictionaries[category] = {}
        self.dictionaries[category][armenian] = english
        self.combined[armenian] = english
        # Re-sort keys
        self.sorted_keys = sorted(self.combined.keys(), key=len, reverse=True)
