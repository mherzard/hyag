"""Basic unit tests for the Armenian agent bridge.

Can be run with pytest if installed, or directly with `python tests/test_basic.py`.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio

from src.translator import SpecializedTranslator
from src.validator import ValidationLayer, ValidationIssue
from src.agent_client import EchoToolAgent
from src.bridge import ArmenianAgentBridge


SAMPLE_DICT = {
    "general": {"ֆունկցիա": "function", "ֆայլ": "file"},
    "protected": {"app.py": "app.py"},
    "keep_english": {"API": "API"},
}


def test_pre_process_replaces_known_terms():
    st = SpecializedTranslator(SAMPLE_DICT)
    result = st.pre_process("կարդա app.py ֆայլը, գտիր main ֆունկցիան")
    assert "[[app.py]]" in result
    assert "[[file]]" in result
    assert "[[main]]" not in result  # not in dictionary
    assert "[[function]]" in result


def test_post_process_maps_back():
    st = SpecializedTranslator(SAMPLE_DICT)
    result = st.post_process("Read the app.py file and find the main function")
    assert "app.py" in result
    assert "ֆայլ" in result
    assert "ֆունկցիա" in result


def test_validation_leftover_brackets():
    vl = ValidationLayer(SAMPLE_DICT)
    issues = vl.validate_english_prompt("Read the [[app.py]] file")
    assert any(i.severity == "error" for i in issues)


def test_validation_missing_expected_term():
    vl = ValidationLayer(SAMPLE_DICT)
    # If the pre-processor introduced "file" and "function", they should be present
    issues = vl.validate_english_prompt(
        "Read the app.py file and find the main function",
        expected_terms=["file", "function"]
    )
    assert all(i.severity == "warning" or "missing" not in i.message for i in issues)


def test_validation_empty_agent_result():
    vl = ValidationLayer(SAMPLE_DICT)
    issues = vl.validate_agent_result("", "հարցում")
    assert any(i.severity == "error" for i in issues)


def test_validation_error_marker():
    vl = ValidationLayer(SAMPLE_DICT)
    issues = vl.validate_agent_result("Error: something failed", "հարցում")
    assert any(i.severity == "warning" for i in issues)


def test_validation_english_term_left_in_armenian():
    vl = ValidationLayer(SAMPLE_DICT)
    issues = vl.validate_armenian_output("Դիտեք function-ը")
    assert any("function" in i.message for i in issues)


def test_validation_protected_name_not_flagged():
    vl = ValidationLayer(SAMPLE_DICT)
    issues = vl.validate_armenian_output("Բացի app.py-ն")
    assert not any("app.py" in i.user_message for i in issues)


async def test_bridge_success():
    bridge = ArmenianAgentBridge(
        agent_executor=EchoToolAgent(),
        dictionaries=SAMPLE_DICT,
        max_retries=0,
    )
    result = await bridge.run("կարդա app.py ֆայլը, գտիր ֆունկցիան")
    assert result["success"] is True
    assert "app.py" in result["english_prompt"]
    assert "file" in result["english_prompt"]
    assert "function" in result["english_prompt"]
    assert result["armenian_output"] is not None


async def test_bridge_error_case():
    bridge = ArmenianAgentBridge(
        agent_executor=EchoToolAgent(),
        dictionaries=SAMPLE_DICT,
        max_retries=0,
    )
    # EchoToolAgent returns an error when "error" is in the prompt
    result = await bridge.run("ասա, թե ինչ սխալներ կան")
    assert result["success"] is True  # validation only warns on error markers
    assert "սխալ" in result["armenian_output"]


# Plain-Python test runner (no pytest required)
ALL_TESTS = [
    test_pre_process_replaces_known_terms,
    test_post_process_maps_back,
    test_validation_leftover_brackets,
    test_validation_missing_expected_term,
    test_validation_empty_agent_result,
    test_validation_error_marker,
    test_validation_english_term_left_in_armenian,
    test_validation_protected_name_not_flagged,
    test_bridge_success,
    test_bridge_error_case,
]


async def _run_all():
    for test in ALL_TESTS:
        if asyncio.iscoroutinefunction(test):
            await test()
        else:
            test()
        print(f"✓ {test.__name__}")


if __name__ == "__main__":
    print("Running tests...")
    asyncio.run(_run_all())
    print("All tests passed.")
