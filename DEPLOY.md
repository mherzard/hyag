:-

# hyag — Մանրամասն տեղակայման և գործարկման հրահանգ

Այս փաստաթուղթը քայլ առ քայլ բացատրում է, թե ինչպես տեղակայել և աշխատեցնել **hyag** (Armenian Agent Bridge) համակարգը macOS / Linux / Windows-ում։

---

## Արխիտեկտուրա

```
Օգտատեր (հայերեն) 
    ↓
Claude Code / OpenCode / CLI
    ↓
hyag translate-prompt → անգլերեն հրաման
    ↓
Claude Code գործիքներ (Read / Bash / Edit / Search …)
    ↓
hyag translate-result → հայերեն պատասխան
    ↓
Օգտատեր
```

hyag-ը ինքը չի կատարում գործիքները։ Այն միայն **թարգմանչական շերտ է**, որը նստում է Օգտատիրոջ և Claude Code-ի գործիքների միջև։

---

## Քայլ 1. Պահանջվող ծրագրային ապահովում

### 1.1 Python 3.10+

Ստուգիր տեղադրված Python-ը.

```bash
python3 --version
```

Ցանկալի է **Python 3.10 կամ ավելի նոր**։

- **macOS**: Python սովորաբար արդեն տեղադրված է։ Եթե ոչ, տեղադրիր [python.org](https://www.python.org/downloads/)-ից կամ `brew install python3`։
- **Linux (Debian/Ubuntu)**:
  ```bash
  sudo apt update
  sudo apt install python3 python3-venv python3-pip
  ```
- **Windows**: Տեղադրիր [python.org](https://www.python.org/downloads/)-ից և ավելացրու PATH-ում։

### 1.2 Ollama (տեղական LLM)

hyag-ն աշխատում է Ollama-ով։

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows — ներբեռնիր և տեղադրիր https://ollama.com/download/windows
```

Ստուգիր, որ Ollama-ն աշխատում է.

```bash
ollama --version
ollama list
```

Եթե ցուցակը դատարկ է, ներբեռնիր մոդել.

```bash
ollama pull llama3.1
```

Այլ առաջարկվող մոդելներ.

- `qwen2.5` — բազմալեզու, հաճախ լավ է արևելյան լեզուների համար
- `mixtral` — ավելի խոշոր, ավելի լավ տեխնիկական խնդիրներում
- `llama3.1:70b` — եթե համակարգիչը բավարար հզոր է

### 1.3 Claude Code կամ OpenCode

Օգտագործիր Claude Code CLI-ն։ Տեղադրման մասին տեղեկություններ.

- Claude Code: https://claude.ai/code
- OpenCode (community fork): https://github.com/saiyamjain/Opencode

---

## Քայլ 2. Նախագծի տեղակայում

### 2.1 Պանակի պատճառում

```bash
cd /Users/macbook/myai
# կամ այն տեղ, որտեղ ցանկանում ես պահել hyag-ը
```

### 2.2 Ստեղծիր virtual environment (պարտադիր չէ, բայց խորհուրդ է տրվում)

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows
```

### 2.3 Տեղադրիր կախվածությունները

```bash
cd /Users/macbook/myai/hyag
pip install -r requirements.txt
```

`requirements.txt` պարունակում է.

```
openai>=1.0.0
pydantic>=2.0.0
requests>=2.28.0
pytest>=7.0.0
```

---

## Քայլ 3. Ստուգիր, որ ամեն ինչ աշխատում է առանց LLM-ի

hyag-ն ունի `DummyLLMTranslator`, որը թույլ է տալիս ստուգել կառուցվածքը առանց Ollama-ի։

```bash
cd /Users/macbook/myai/hyag
python3 tests/test_basic.py
```

Սպասվող արդյունք.

```
Running tests...
✓ test_pre_process_replaces_known_terms
✓ test_post_process_maps_back
✓ test_validation_leftover_brackets
...
All tests passed.
```

Փորձիր base օրինակը.

```bash
python3 examples/example_usage.py
```

Այստեղ պատասխանները հիմնականում հայերեն են մնում, որովհետև DummyLLMTranslator-ը իրական թարգմանություն չի անում։

---

## Քայլ 4. Ollama-ի կապում hyag-ին

### 4.1 Սահմանիր միջավայրի փոփոխականները

```bash
export OLLAMA_MODEL=llama3.1
export OLLAMA_BASE_URL=http://localhost:11434   # default, կարելի է չգրել
```

Որպեսզի ամեն անգամ չգրես, ավելացրու քո shell-ի կոնֆիգում։

**macOS/Linux — ~/.zshrc կամ ~/.bashrc**.

```bash
echo 'export OLLAMA_MODEL=llama3.1' >> ~/.zshrc
echo 'export OLLAMA_BASE_URL=http://localhost:11434' >> ~/.zshrc
source ~/.zshrc
```

**Windows — PowerShell**.

```powershell
[Environment]::SetEnvironmentVariable("OLLAMA_MODEL", "llama3.1", "User")
[Environment]::SetEnvironmentVariable("OLLAMA_BASE_URL", "http://localhost:11434", "User")
```

### 4.2 Ստուգիր Ollama-ի աշխատանքը

```bash
ollama run llama3.1 "Say hello in Armenian"
```

Եթե պատասխանում է, ամեն ինչ լավ է։

### 4.3 Փորձիր hyag CLI-ն Ollama-ով

```bash
cd /Users/macbook/myai/hyag

python3 tools/hyag_cli.py translate-prompt \
    "կարդա app.py ֆայլը, գտիր main ֆունկցիան"
```

Սպասվող արդյունք.

```json
{
  "armenian_prompt": "կարդա app.py ֆայլը, գտիր main ֆունկցիան",
  "english_prompt": "read the app.py file and find the main function",
  "issues": []
}
```

Եթե Ollama-ն դեռ բեռնում է մոդելը առաջին անգամ, կարող է մի քանի վայրկյան տևել։

### 4.4 Հետադարձ թարգմանություն

```bash
printf 'In app.py there is a main function. It uses config_path, user_count, and api_token.' | \
python3 tools/hyag_cli.py translate-result -
```

---

## Քայլ 5. Claude Code-ի հետ գործարկում

### 5.1 Skill-ի ակտիվացում

hyag-ի skill-ը գտնվում է.

```
/Users/macbook/myai/hyag/.claude/skills/hyag.md
```

Claude Code-ն ավտոմատ տեսնում է `.claude/skills/` պանակը, երբ աշխատում է այս պրոեկտի վրա։

### 5.2 Պատրաստություն

1. Մուտք գործիր պրոեկտի պանակ.
   ```bash
   cd /Users/macbook/myai/hyag
   ```

2. Սահմանիր OLLAMA_MODEL-ը։
   ```bash
   export OLLAMA_MODEL=llama3.1
   ```

3. Բացի Claude Code-ը.
   ```bash
   claude
   ```

### 5.3 Օգտագործում սեսիայի ընթացքում

Հետևիր այս քայլերին ամեն հայերեն հարցման համար։

#### Ա. Հայերեն պրոմպտի թարգմանություն

Claude Code-ն ինքնուրույն կարող է կանչել.

```bash
python3 tools/hyag_cli.py translate-prompt "ՔՈ ՀԱՅԵՐԵՆ ՀԱՐՑՈՒՄ"
```

Օրինակ.

```bash
python3 tools/hyag_cli.py translate-prompt \
    "կարդա app.py ֆայլը, գտիր main ֆունկցիան և ցույց տուր ինչ փոփոխականներ են օգտագործվում"
```

Արդյունքում կստանաս անգլերեն հրաման։

```json
{
  "english_prompt": "read the app.py file, find the main function and show what variables are used"
}
```

#### Բ. Հրամանի կատարում

Claude Code-ն այդ հրամանը պետք է կատարի իր գործիքներով.

- `Read` → ֆայլ կարդալ
- `Bash` → հրաման գործարկել
- `Search` → որոնել
- `Edit` → խմբագրել

#### Գ. Արդյունքի հետադարձ թարգմանություն

Արդյունքը պահիր ֆայլում կամ ուղղակի pipe արա.

```bash
printf '%s' "YOUR ENGLISH RESULT" | \
python3 tools/hyag_cli.py translate-result -
```

Օրինակ.

```bash
printf 'app.py contains a main function. It uses config_path, user_count, and api_token.' | \
python3 tools/hyag_cli.py translate-result -
```

#### Դ. Պատասխան օգտատիրոջը

Ցույց տուր միայն `armenian_output` դաշտը։

> app.py ֆայլում գտնվում է main ֆունկցիան, որը օգտագործում է config_path, user_count և api_token փոփոխականները։

---

## Քայլ 6. Claude Code skill-ի ավտոմատացում (արհեստականորեն)

Claude Code-ն չունի պաշտոնական «plugin lifecycle» բոլոր շրջանակներում, բայց կարելի է օգտագործել երկու մոտեցում։

### Մոտեցում Ա. Հիշողության միջոցով (Memory)

Claude Code-ի memory-ում կարելի է պահել հետևյալ հրահանգը.

```
Whenever the user writes in Armenian:
1. Run: python3 /Users/macbook/myai/hyag/tools/hyag_cli.py translate-prompt "USER_TEXT"
2. Execute the resulting english_prompt with Claude Code tools.
3. Run the result through: python3 /Users/macbook/myai/hyag/tools/hyag_cli.py translate-result -
4. Reply with the armenian_output only, preserving code/paths/identifiers.
```

Memory-ն պահելու համար ասիր Claude Code-ին.

> Remember this workflow for Armenian prompts.

### Մոտեցում Բ. Project-specific prompt (CLAUDE.md)

Ավելացրու `/Users/macbook/myai/hyag/CLAUDE.md` ֆայլ հետևյալ բովանդակությամբ.

```markdown
# Project instructions

When the user sends a prompt in Armenian:
1. Translate it using `python3 tools/hyag_cli.py translate-prompt "..."`.
2. Execute the resulting English command with Claude Code tools.
3. Translate the result using `python3 tools/hyag_cli.py translate-result -`.
4. Reply in Armenian, preserving all code snippets, file paths, and identifiers.
```

Claude Code-ն կարդում է `CLAUDE.md` պրոեկտի արմատից, երբ սկսում է սեսիա այդ պրոեկտում։

---

## Քայլ 7. Բառարանի հարմարեցում

### 7.1 Բառարանի ֆայլը

```
/Users/macbook/myai/hyag/config/dictionaries.json
```

### 7.2 Բառարանի կատեգորիաներ

- `general` — ընդհանուր ծրագրավորման տերմիններ
- `project` — նախագծային / դոմենային տերմիններ
- `protected` — անուններ, որոնք երբեք չպետք է թարգմանվեն (ֆայլեր, ֆունկցիաներ)
- `keep_english` — տերմիններ, որոնք հայերենում էլ անգլերեն են մնում (API, HTTP)

### 7.3 Օրինակ՝ նոր տերմին ավելացնել

```json
{
  "general": {
    "ֆայլ": "file",
    "ֆունկցիա": "function",
    "դաս": "class",
    "նոր բառ": "new_word"
  }
}
```

### 7.4 Թարմացնելուց հետո փորձարկիր

```bash
python3 tools/hyag_cli.py translate-prompt "գրիր նոր բառ"
```

---

## Քայլ 8. Սխալների վերացում

### 8.1 Ollama-ն չի արձագանքում

```bash
ollama list
ollama run llama3.1 "hello"
```

Եթե չի աշխատում, վերագործարկիր.

```bash
# macOS
launchctl unload ~/Library/LaunchAgents/com.ollama.app.plist
launchctl load ~/Library/LaunchAgents/com.ollama.app.plist

# Linux
sudo systemctl restart ollama
```

### 8.2 `ModuleNotFoundError: No module named 'requests'`

```bash
pip install requests
```

### 8.3 Թարգմանությունը վատ է

1. Փորձիր այլ մոդել.
   ```bash
   ollama pull qwen2.5
   export OLLAMA_MODEL=qwen2.5
   ```

2. Լավացրու բառարանը։
   - Ավելացրու հաճախ հանդիպող սխալ թարգմանված բառերը
   - Օգտագործիր ավելի երկար բառարանային արժեքներ

3. Փոփոխիր `temperature` արժեքը.
   ```python
   OllamaLLMTranslator(model="llama3.1", temperature=0.05)
   ```

### 8.4 Պահպանված անունները փչանում են

Ավելացրու `protected` բառարանում.

```json
{
  "protected": {
    "app.py": "app.py",
    "main": "main",
    "UserModel": "UserModel"
  }
}
```

### 8.5 Հայերեն պատասխանում անգլերեն տերմիններ են մնում

Ավելացրու `general` բառարանում և/կամ `keep_english`՝ եթե անգլերեն մնալը նորմալ է։

---

## Քայլ 9. Արտադրական (production) տեղակայման առաջարկություններ

### 9.1 LLM ընտրություն

| Տեսակ | Ե_cuando | Մեկնաբանություն |
|---|---|---|
| Ollama տեղական | Անձնական մեքենա | Գաղտնիություն, արագ փորձարկում |
| OpenAI API | Արտադրություն | Ավելի ճշգրիտ, բայց արժեք |
| Anthropic API | Արտադրություն | Claude-ի որակ |
| Ollama սերվեր | Թիմային | Մեկ Ollama, բազմաթիվ օգտատերեր |

### 9.2 Պրոցես որպես սերվեր

Եթե ցանկանում ես, որ hyag-ն աշխատի որպես API, կարելի է գրել FastAPI շերտ.

```python
# server.py
from fastapi import FastAPI
from pydantic import BaseModel
from src.translation_service import TranslationService

app = FastAPI()
service = TranslationService.from_env()

class PromptRequest(BaseModel):
    text: str

@app.post("/translate-prompt")
async def translate_prompt(req: PromptRequest):
    return await service.translate_prompt(req.text)

@app.post("/translate-result")
async def translate_result(req: PromptRequest):
    return await service.translate_result(req.text)
```

Ավելացնել `fastapi` և `uvicorn` `requirements.txt`-ում և գործարկել.

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

---

## Ամփոփում

| Քայլ | Գործողություն |
|---|---|
| 1 | Տեղադրիր Python, Ollama, Claude Code |
| 2 | Կլոնիր / պատճառիր hyag պրոեկտը |
| 3 | Տեղադրիր կախվածությունները |
| 4 | Սահմանիր `OLLAMA_MODEL` |
| 5 | Փորձիր `tools/hyag_cli.py translate-prompt` |
| 6 | Օգտագործիր Claude Code-ի հետ |
| 7 | Հարմարեցրու բառարանը |
| 8 | Պատրաստ է |

---

## Արագ փորձարկման համար

```bash
cd /Users/macbook/myai/hyag
export OLLAMA_MODEL=llama3.1
python3 tests/test_basic.py
python3 tools/hyag_cli.py translate-prompt "կարդա app.py ֆայլը, գտիր main ֆունկցիան"
```
