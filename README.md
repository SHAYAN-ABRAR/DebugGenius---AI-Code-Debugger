# 🐛 DebugGenius — AI Code Debugger

A premium, glassmorphism Streamlit app that analyzes **screenshots of code errors**
and returns a structured explanation — error type, root cause, fix, and corrected
code — powered by **Google Gemini Vision**.

> Drop in a screenshot of any stack trace or error and get a streaming, copy-ready
> answer in seconds.

---

## ✨ Features

- 🖼️ **Screenshot in** — PNG / JPG / WEBP of an error or stack trace.
- 🎚️ **Two modes** — *Hints only* (guidance) or *Full solution* (corrected code).
- ⚡ **Streaming answers** — the explanation renders token-by-token.
- 📋 **One-click copy & export** — copy code blocks, download the whole answer as Markdown.
- 🕑 **Session history** — revisit earlier analyses without re-running them.
- 🎨 **Glassmorphism UI** — frosted panels, aurora backdrop, Inter type, micro-interactions.
- 🛡️ **Robust** — typed errors, input validation, retries with backoff, friendly messages.

---

## 🚀 Quick start

```bash
# 1. Create & activate a virtual environment
python -m venv venv
venv\Scripts\activate         # Windows
# source venv/bin/activate    # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your API key
copy .env.example .env        # Windows  (cp on macOS/Linux)
#   then edit .env and set GEMINI_API_KEY

# 4. Run
streamlit run app.py
```

The app opens at <http://localhost:8501>.
Get a free key from [Google AI Studio](https://aistudio.google.com/app/apikeys).

---

## 🧱 Architecture

A thin entrypoint (`app.py`) orchestrates a small, single-responsibility package:

```
AI Code Debugger App/
├── app.py                     # Entrypoint: page config + orchestration only
├── debuggenius/
│   ├── config.py              # Immutable settings + secret resolution (.env / st.secrets)
│   ├── models.py              # Typed domain models (DebugMode, DebugRequest, HistoryEntry)
│   ├── exceptions.py          # Typed error hierarchy with user-facing hints
│   ├── validation.py          # Pure, testable image validation
│   ├── prompts.py             # Single source of truth for model prompts
│   ├── ai_service.py          # Gemini wrapper: streaming + retries + error mapping
│   ├── theme.py               # Glassmorphism design system (injected CSS)
│   ├── state.py               # Session-state + bounded history
│   ├── ui.py                  # Reusable presentation components
│   └── logging_setup.py       # Centralized logging
├── tests/                     # Unit tests (validation, prompts, models, config)
├── .streamlit/config.toml     # Base dark theme to match the CSS
├── requirements.txt           # Runtime dependencies
└── requirements-dev.txt       # + pytest
```

**Design principles:** separation of concerns, dependency direction inward
(UI → core → models), no framework imports in the testable core, DRY prompts,
and typed errors that always surface an actionable hint.

---

## ⚙️ Configuration

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `GEMINI_API_KEY` | ✅ | — | Gemini API key (`.env` locally or Streamlit secrets in the cloud). |
| `GEMINI_MODEL` | ❌ | `gemini-2.0-flash` | Override the vision model. |
| `DEBUGGENIUS_LOG_LEVEL` | ❌ | `INFO` | Logging verbosity. |

On **Streamlit Cloud**, add `GEMINI_API_KEY` under *App → Settings → Secrets*
instead of committing a `.env` file.

---

## 🧪 Testing

```bash
pip install -r requirements-dev.txt
pytest
```

The core logic (validation, prompts, models, config) is unit-tested without any
network or Streamlit runtime.

---

## 🔒 Security notes

- `.env` is git-ignored — never commit your key. If a key was ever committed, **rotate it**.
- Uploads are validated for type, size, dimensions, and decodability before any API call.

---

## 📄 License

Open source — fork and contribute.

---

**Made with ❤️ — DebugGenius, your AI debugging partner.**
