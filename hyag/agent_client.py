"""Agent executor interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AgentExecutor(ABC):
    """Abstract interface for the tool/agent layer."""

    @abstractmethod
    async def execute(self, english_prompt: str) -> str:
        """Execute the English command and return a textual result."""
        pass


class DummyAgentExecutor(AgentExecutor):
    """Mock agent that echoes the prompt as a fake result."""

    async def execute(self, english_prompt: str) -> str:
        return f"Agent executed: {english_prompt}"


class EchoToolAgent(AgentExecutor):
    """A slightly smarter mock that recognizes a few simple read/list commands."""

    async def execute(self, english_prompt: str) -> str:
        lowered = english_prompt.lower()
        if "read" in lowered and "file" in lowered:
            return "File content: example content with a main function and variables."
        if "list" in lowered and ("function" in lowered or "functions" in lowered):
            return "Functions: main, helper, process_data."
        if "error" in lowered or "fail" in lowered:
            return "Error: simulated failure for testing validation."
        return f"Executed command: {english_prompt}"


class ClaudeCodeAgentExecutor(AgentExecutor):
    """Placeholder executor for Claude Code / OpenCode integrations.

    The actual tool execution is performed by Claude Code itself. This executor
    only returns a structured marker so the bridge can be used within Python
    scripts or skills that delegate execution to Claude Code.

    Example of what Claude Code should do after receiving this marker:
      1. Parse the English prompt from the marker.
      2. Use its own tools (Read, Bash, Edit, Search, ...) to fulfill it.
      3. Pass the English result to `tools/hyag_cli.py translate-result`.
      4. Present the Armenian output to the user.
    """

    async def execute(self, english_prompt: str) -> str:
        return f"[CLAUDE_CODE_EXECUTE] {english_prompt}"

    @staticmethod
    def parse_marker(text: str) -> str:
        """Extract the English prompt from a Claude Code execute marker."""
        prefix = "[CLAUDE_CODE_EXECUTE] "
        if text.startswith(prefix):
            return text[len(prefix):]
        return text
