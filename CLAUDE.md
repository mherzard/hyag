# Project instructions for hyag

This project is an Armenian-to-English agent bridge (`hyag`).

When the user sends a prompt in Armenian inside this project:

1. Translate the Armenian prompt to an English agent command using:
   ```bash
   export OLLAMA_MODEL=llama3.1
   python3 /Users/macbook/myai/hyag/tools/hyag_cli.py translate-prompt "ARMENIAN_PROMPT"
   ```
2. Execute the resulting `english_prompt` with Claude Code tools (Read, Bash,
   Edit, Search, etc.). Keep file paths, identifiers, and code unchanged.
3. Translate the English result back to Armenian using:
   ```bash
   printf '%s' "ENGLISH_RESULT" | python3 /Users/macbook/myai/hyag/tools/hyag_cli.py translate-result -
   ```
4. Reply to the user with only the `armenian_output`, preserving all code
   snippets, file paths, and identifiers.

If the JSON from `translate-prompt` contains an issue with severity `error`,
stop and explain the problem to the user in Armenian.

If there are only warnings, you may mention them briefly but keep the main
answer focused on the actual result.
