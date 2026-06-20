"""Example usage of the Armenian agent bridge."""

import asyncio
import sys
from pathlib import Path

# Allow running from the examples directory without installing
sys.path.insert(0, str(Path(__file__).parent.parent))

from hyag.bridge import ArmenianAgentBridge
from hyag.agent_client import EchoToolAgent


async def main():
    bridge = ArmenianAgentBridge(
        agent_executor=EchoToolAgent(),
        max_retries=2,
    )

    prompts = [
        "կարդա app.py ֆայլը, գտիր main ֆունկցիան և ցույց տուր ինչ փոփոխականներ են օգտագործվում",
        "ասա, թե ինչ սխալներ կան կոդում",
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
        print(f"Փորձեր: {result['attempts']}")


if __name__ == "__main__":
    asyncio.run(main())
