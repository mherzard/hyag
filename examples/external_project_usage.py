"""Example: using the installed hyag package from a different project.

This script is meant to be copied or referenced from another project.
It shows how to import hyag, load a project-specific dictionary, and run
the bridge against an arbitrary directory.
"""

import asyncio
import json
import os
from pathlib import Path

from hyag import ArmenianAgentBridge
from hyag.agent_client import EchoToolAgent
from hyag.llm_client import OllamaLLMTranslator


async def main():
    # 1. Optional: use a project-specific dictionary to extend the built-in one.
    project_dict_path = Path(__file__).parent / "my_project_dict.json"
    if project_dict_path.exists():
        with open(project_dict_path, "r", encoding="utf-8") as f:
            custom_dict = json.load(f)
    else:
        custom_dict = None

    # 2. Choose the LLM. Use Ollama if OLLAMA_MODEL is set; otherwise the demo
    # dummy translator, which does not require a running local model.
    if os.environ.get("OLLAMA_MODEL"):
        llm = OllamaLLMTranslator(
            model=os.environ["OLLAMA_MODEL"],
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
    else:
        print("Note: OLLAMA_MODEL is not set, using DummyLLMTranslator for demo.")
        from hyag.llm_client import DummyLLMTranslator
        llm = DummyLLMTranslator()

    # 3. Build the bridge. If no dictionary_path is passed, the built-in config
    # bundled with the package is used automatically.
    bridge_kwargs = {
        "llm_translator": llm,
        "agent_executor": EchoToolAgent(),
        "max_retries": 2,
    }
    if custom_dict:
        bridge_kwargs["dictionaries"] = custom_dict

    bridge = ArmenianAgentBridge(**bridge_kwargs)

    # 4. Translate an Armenian prompt and run it.
    armenian_prompt = "կարդա app.py ֆայլը, գտիր main ֆունկցիան"
    result = await bridge.run(armenian_prompt)

    print("English command:", result["english_prompt"])
    print("Armenian output:", result["armenian_output"])
    if result["warnings"]:
        print("Warnings:")
        for w in result["warnings"]:
            print("  -", w)


if __name__ == "__main__":
    asyncio.run(main())
