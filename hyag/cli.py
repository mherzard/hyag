#!/usr/bin/env python3
"""Command-line interface for the hyag Armenian agent bridge.

Typical Claude Code skill flow:

    1. Translate an Armenian prompt to English:
       python3 /Users/macbook/myai/hyag/tools/hyag_cli.py translate-prompt \
           "կարդա app.py ֆայլը, գտիր main ֆունկցիան"

    2. Translate an English tool result back to Armenian:
       echo "File content: example content" | \
       python3 /Users/macbook/myai/hyag/tools/hyag_cli.py translate-result -

Set OLLAMA_MODEL (and optionally OLLAMA_BASE_URL) to use a local Ollama model.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from hyag.llm_client import DummyLLMTranslator, OllamaLLMTranslator
from hyag.translation_service import TranslationService


def _default_dictionary_path() -> str:
    # When installed as a package, the config sits next to this module.
    return str(Path(__file__).resolve().parent / "config" / "dictionaries.json")


def _llm_from_env():
    if os.environ.get("OLLAMA_MODEL"):
        return OllamaLLMTranslator(
            model=os.environ["OLLAMA_MODEL"],
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
    return DummyLLMTranslator()


def _dictionary_path(args) -> str:
    if args.dictionary:
        return args.dictionary
    return _default_dictionary_path()


async def cmd_translate_prompt(args) -> None:
    service = TranslationService(
        llm_translator=_llm_from_env(),
        dictionary_path=_dictionary_path(args),
    )
    result = await service.translate_prompt(args.text)
    print(json.dumps(result, ensure_ascii=False, indent=2))


async def cmd_translate_result(args) -> None:
    service = TranslationService(
        llm_translator=_llm_from_env(),
        dictionary_path=_dictionary_path(args),
    )
    text = args.text
    if text == "-":
        text = sys.stdin.read()
    elif args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            text = f.read()

    result = await service.translate_result(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="CLI for the hyag Armenian-to-English agent bridge",
    )
    parser.add_argument(
        "--dictionary",
        type=str,
        default=str(Path(__file__).resolve().parent / "config" / "dictionaries.json"),
        help="Path to dictionaries.json",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_prompt = subparsers.add_parser(
        "translate-prompt",
        help="Translate an Armenian prompt into an English agent command",
    )
    p_prompt.add_argument("text", type=str, help="Armenian prompt text")

    p_result = subparsers.add_parser(
        "translate-result",
        help="Translate an English result into Armenian",
    )
    p_result.add_argument(
        "text",
        type=str,
        nargs="?",
        default="-",
        help="English result text, or '-' to read from stdin",
    )
    p_result.add_argument(
        "--input-file",
        type=str,
        help="Read the English result from a file instead of stdin/argument",
    )

    args = parser.parse_args()

    if args.command == "translate-prompt":
        asyncio.run(cmd_translate_prompt(args))
    elif args.command == "translate-result":
        asyncio.run(cmd_translate_result(args))


if __name__ == "__main__":
    main()
