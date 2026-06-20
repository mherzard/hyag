"""Manual demonstration of the hyag + Claude Code integration.

This script does not call Claude Code tools directly (that is only possible
inside a Claude Code session). Instead it shows the exact hand-off flow:

    1. Armenian prompt -> English command via hyag
    2. English command is printed for Claude Code to execute
    3. User pastes the English result
    4. English result -> Armenian output via hyag
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm_client import DummyLLMTranslator, OllamaLLMTranslator
from src.translation_service import TranslationService


def _make_service():
    """Use OLLAMA_MODEL if set; otherwise the demo dummy translator."""
    import os

    llm = None
    if os.environ.get("OLLAMA_MODEL"):
        llm = OllamaLLMTranslator(
            model=os.environ["OLLAMA_MODEL"],
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
    return TranslationService(llm_translator=llm)


async def main():
    service = _make_service()

    prompt = "կարդա app.py ֆայլը, գտիր main ֆունկցիան և ցույց տուր ինչ փոփոխականներ են օգտագործվում"

    print("=" * 60)
    print(f"Հայերեն պրոմպտ: {prompt}")
    print()

    # Step 1: Armenian -> English
    step1 = await service.translate_prompt(prompt)
    english_command = step1["english_prompt"]

    print("1. Անգլերեն հրաման Claude Code-ի համար:")
    print(english_command)
    print()

    if step1["issues"]:
        print("Զգուշացումներ թարգմանության ժամանակ:")
        for issue in step1["issues"]:
            print(f"  [{issue['severity']}] {issue['user_message']}")
        print()

    # Step 2: simulate Claude Code running tools and returning a result
    print("2. Այժմ Claude Code-ը պետք է կատարի այս հրամանը իր գործիքներով։")
    print("   Օրինակ՝ կարդա app.py-ն, գտիր main-ը, վերլուծիր փոփոխականները։")
    print()

    simulated_result = (
        "In app.py there is a main function. It uses the variables "
        "config_path, user_count, and api_token."
    )
    user_input = input(
        "Մուտքագրիր անգլերեն արդյունքը (Enter՝ օգտագործել օրինակը)։\n"
    ).strip()
    english_result = user_input if user_input else simulated_result

    # Step 3: English result -> Armenian
    step2 = await service.translate_result(english_result)
    armenian_output = step2["armenian_output"]

    print()
    print("3. Հայերեն պատասխան:")
    print(armenian_output)
    print()

    if step2["issues"]:
        print("Զգուշացումներ հետադարձ թարգմանության ժամանակ:")
        for issue in step2["issues"]:
            print(f"  [{issue['severity']}] {issue['user_message']}")


if __name__ == "__main__":
    asyncio.run(main())
