"""Example: Armenian agent bridge backed by a local Ollama model."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bridge import ArmenianAgentBridge
from src.agent_client import EchoToolAgent
from src.llm_client import OllamaLLMTranslator


async def main():
    # Make sure the model is available in Ollama, e.g.:
    #   ollama pull llama3.1
    #   ollama pull qwen2.5
    llm = OllamaLLMTranslator(
        model="llama3.1",  # change to your preferred local model
        base_url="http://localhost:11434",
        temperature=0.1,
    )

    bridge = ArmenianAgentBridge(
        llm_translator=llm,
        agent_executor=EchoToolAgent(),
        max_retries=2,
    )

    prompts = [
        "կարդա app.py ֆայլը, գտիր main ֆունկցիան և ցույց տուր ինչ փոփոխականներ են օգտագործվում",
        "ցուցակիր բոլոր ֆունկցիաները",
    ]

    for prompt in prompts:
        print("=" * 60)
        print(f"Հարցում: {prompt}")
        result = await bridge.run(prompt)
        print(f"Անգլերեն հրաման: {result.get('english_prompt', 'N/A')}")
        print(f"Պատասխան: {result.get('armenian_output', result.get('error'))}")
        if result.get("warnings"):
            print("Զգուշացումներ:")
            for w in result["warnings"]:
                print(f"  - {w}")


if __name__ == "__main__":
    asyncio.run(main())
