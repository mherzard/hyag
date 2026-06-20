---
name: hyag
description: Armenian-to-English agent bridge for the hyag project
---

# hyag Armenian Agent Bridge

This skill lets you handle user prompts written in Armenian by translating them
to English agent commands, executing them with your own tools, and translating
the result back into Armenian.

## When to use

Use this skill whenever the user writes in Armenian, especially for:
- Reading files and analyzing code
- Running commands and explaining results
- Searching, editing, or summarizing project files

## Required setup

The project must have a local LLM configured. By default the bridge uses a dummy
translator that only works for testing. For real Armenian translation set the
environment variable before running any commands:

```bash
export OLLAMA_MODEL=llama3.1  # or qwen2.5, mixtral, etc.
# optional:
# export OLLAMA_BASE_URL=http://localhost:11434
```

Make sure the model is pulled in Ollama:

```bash
ollama pull $OLLAMA_MODEL
```

## Workflow

For every Armenian user request, follow these steps exactly.

### Step 1 — Translate the prompt

Run the prompt through the hyag CLI:

```bash
export OLLAMA_MODEL=llama3.1
python3 /Users/macbook/myai/hyag/tools/hyag_cli.py translate-prompt "ՀԱՅԵՐԵՆ ՊՐՈՄՊՏ"
```

Parse the JSON output. The key field is `english_prompt`. If the JSON contains
`issues` with severity `error`, explain the problem to the user in Armenian and
stop. Otherwise continue.

### Step 2 — Execute the English command

Use your own Claude Code tools (Read, Bash, Edit, Search, etc.) to fulfill the
`english_prompt`. Do exactly what the English command says, as if the user had
asked in English.

Keep file paths, code snippets, identifiers, and technical names unchanged.

### Step 3 — Translate the result back to Armenian

After you have the final English result, write it to a temp file and translate
it back:

```bash
export OLLAMA_MODEL=llama3.1
python3 /Users/macbook/myai/hyag/tools/hyag_cli.py translate-result --input-file /tmp/result.txt
```

Or pipe the result directly:

```bash
printf '%s' "$ENGLISH_RESULT" | python3 /Users/macbook/myai/hyag/tools/hyag_cli.py translate-result -
```

### Step 4 — Respond to the user

Present only the `armenian_output` to the user. If `issues` with severity
`warning` exist, you may mention them briefly in Armenian, but keep the main
answer focused on the actual result.

## Example

User says:

> կարդա app.py ֆայլը, գտիր main ֆունկցիան

Step 1:

```bash
python3 /Users/macbook/myai/hyag/tools/hyag_cli.py translate-prompt "կարդա app.py ֆայլը, գտիր main ֆունկցիան"
```

Assume the JSON says:

```json
{
  "english_prompt": "read the app.py file and find the main function"
}
```

Step 2:

Use Read on `app.py`, locate `main`, summarize.

Step 3:

```bash
python3 /Users/macbook/myai/hyag/tools/hyag_cli.py translate-result --input-file /tmp/result.txt
```

Step 4:

Reply in Armenian, e.g.:

> app.py ֆայլում գտնվում է main ֆունկցիան, որը ...

## Rules

- Always translate the Armenian prompt first; do not guess the English command.
- Preserve protected names (`app.py`, `main`, identifiers) exactly.
- Run the result through the result translator before presenting it.
- Keep all code snippets, paths, and identifiers unchanged in the final Armenian
  output.
