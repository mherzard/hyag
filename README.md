# hyag - Armenian Agent Bridge

A middleware system that translates Armenian prompts into English agent commands,
executes them via an agent layer, and returns the results in Armenian.

## Structure

```
hyag/
├── config/
│   └── dictionaries.json    # Armenian ↔ English dictionaries
├── src/
│   ├── translator.py         # SpecializedTranslator with dictionary pre/post processing
│   ├── validator.py          # ValidationLayer for three-stage validation
│   ├── llm_client.py         # LLM translation client interface
│   ├── agent_client.py       # Agent execution client interface
│   └── bridge.py             # ArmenianAgentBridge orchestrator
├── .claude/
│   └── skills/
│       └── hyag.md          # Claude Code skill for Armenian prompts
├── examples/
│   ├── example_usage.py     # Usage example
│   └── claude_code_usage.py # Manual Claude Code hand-off demo
├── tests/
│   └── test_basic.py        # Basic unit tests
├── tools/
│   └── hyag_cli.py          # CLI for skill integrations
├── README.md
└── requirements.txt
```

## Quick Start

```bash
pip install -r requirements.txt
python3 examples/example_usage.py
python3 tests/test_basic.py
```

> **Note**: The default `DummyLLMTranslator` does not call an external LLM; it is
> included for offline testing and demonstration. To translate real Armenian text,
> plug in `OllamaLLMTranslator`, `OpenAILLMTranslator`, or your own implementation
> of the `LLMTranslator` interface.

## Using with Ollama

If you run local models with Ollama, use the included `OllamaLLMTranslator`:

```python
from src.bridge import ArmenianAgentBridge
from src.llm_client import OllamaLLMTranslator
from src.agent_client import EchoToolAgent

llm = OllamaLLMTranslator(model="llama3.1", base_url="http://localhost:11434")
bridge = ArmenianAgentBridge(llm_translator=llm, agent_executor=EchoToolAgent())
result = await bridge.run("կարդա app.py ֆայլը")
```

Or use the OpenAI-compatible endpoint:

```python
llm = OllamaLLMTranslator.openai_compatible(
    model="llama3.1",
    base_url="http://localhost:11434/v1",
)
```

Recommended models for this task: `llama3.1`, `qwen2.5`, or `mixtral`.

## Using with Claude Code

A Claude Code skill is included in `.claude/skills/hyag.md`. When the skill is
active, Claude Code will:

1. Detect Armenian prompts.
2. Run `tools/hyag_cli.py translate-prompt "..."` to get an English agent command.
3. Execute that command with its own tools.
4. Run `tools/hyag_cli.py translate-result` to translate the result back to Armenian.
5. Present the Armenian answer to the user.

Set the local model before using the skill:

```bash
export OLLAMA_MODEL=llama3.1
```

You can also try the manual hand-off flow:

```bash
python3 examples/claude_code_usage.py
```

## How it works

1. **Pre-processing**: known Armenian technical terms are replaced with protected
   English equivalents using dictionaries.
2. **Translation**: an LLM translates the prepared text into a clean English agent
   command.
3. **Validation (English)**: checks that protected terms are preserved and markers
   are removed.
4. **Agent execution**: the English command is passed to an agent/tool executor.
5. **Validation (Agent result)**: checks that the result is not empty and has no
   obvious error markers.
6. **Back-translation**: the result is translated into Armenian.
7. **Post-processing**: protected English terms are mapped back to Armenian.
8. **Validation (Armenian)**: checks that the output is natural Armenian and that
   technical terms are handled correctly.

## Dictionaries

Dictionaries live in `config/dictionaries.json`. They are split into:

- `general`: common programming terms (`ֆունկցիա` → `function`)
- `project`: project/domain specific terms
- `protected`: names that must never be translated (`app.py` → `app.py`)
- `keep_english`: terms that may remain in English in the final output (`API`, `HTTP`)

## Customization

Plug in your own LLM client by implementing the `LLMTranslator` interface and your
own agent client by implementing the `AgentExecutor` interface.

## License

MIT
