# 🐛 DebugGenius — AI Code Debugger

A premium, glassmorphism Streamlit app that reads **screenshots of code errors**
and returns a structured fix — error type, plain-English meaning, root cause, and
corrected code — streamed live from an **Ollama vision model**.

> Drop in a screenshot of any stack trace or error and get a streaming, copy-ready
> answer in seconds.

---

## ✨ Features

- 🖼️ **Screenshot in** — PNG / JPG / WEBP of an error or stack trace.
- 🎚️ **Two modes** — *Hints only* (guidance) or *Full solution* (corrected code).
- ⚡ **Streaming answers** — the explanation renders token-by-token.
- 📋 **Copy & export** — copy code blocks, download the whole answer as Markdown.
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

# 3. Configure (optional for a local daemon)
copy .env.example .env        # Windows  (cp on macOS/Linux)

# 4. Run
streamlit run app.py
```

The app opens at <http://localhost:8501>.

### You need an Ollama vision model

DebugGenius talks to [Ollama](https://ollama.com). The default model is the
vision model `gemma4:31b-cloud`. Any vision model works (e.g. `llava`,
`minicpm-v`, `moondream`) — set `OLLAMA_MODEL`.

```bash
ollama pull gemma4:31b-cloud   # or your preferred vision model
ollama signin                  # only required for "-cloud" models
```

**Local daemon** (default): no key needed — `ollama signin` authenticates the
daemon and it proxies cloud models for you.

**Remote / deployed** (no local daemon): point at the cloud endpoint and pass a key:

```bash
OLLAMA_HOST=https://ollama.com
OLLAMA_API_KEY=your_ollama_api_key
```

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
│   ├── ollama_service.py      # Ollama wrapper: streaming + retries + error mapping
│   ├── theme.py               # Glassmorphism design system (injected CSS)
│   ├── state.py               # Session-state + bounded history
│   ├── ui.py                  # Reusable presentation components
│   └── logging_setup.py       # Centralized logging
├── tests/                     # Unit tests (validation, prompts, models, config, ollama)
├── .streamlit/config.toml     # Base dark theme to match the CSS
├── requirements.txt           # Runtime dependencies (no AI vendor SDK — stdlib HTTP)
└── requirements-dev.txt       # + pytest
```

**Design principles:** separation of concerns, dependency direction inward
(UI → core → models), no framework imports in the testable core, DRY prompts,
typed errors that always surface an actionable hint, and zero AI-vendor SDK
(the Ollama client is plain `urllib`).

---

## ⚙️ Configuration

Every value resolves from the environment / `.env` first, then `st.secrets`, so the
same configuration works locally and on Streamlit Cloud.

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `OLLAMA_HOST` | ❌ | `http://localhost:11434` | Ollama server URL (`https://ollama.com` for remote). |
| `OLLAMA_MODEL` | ❌ | `gemma4:31b-cloud` | Ollama **vision** model. |
| `OLLAMA_API_KEY` | ⚠️ | — | Required only for the remote `https://ollama.com` endpoint. |
| `DEBUGGENIUS_LOG_LEVEL` | ❌ | `INFO` | Logging verbosity. |

---

## 🌐 Deploy to Streamlit Community Cloud

1. Push the repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **Create app** → pick this
   repo, branch `main`, main file `app.py`.
3. Open **Advanced settings → Secrets** and paste (TOML):

   ```toml
   OLLAMA_HOST    = "https://ollama.com"
   OLLAMA_MODEL   = "gemma4:31b-cloud"
   OLLAMA_API_KEY = "your_ollama_api_key"
   ```

   There is no local Ollama daemon in the cloud, so `OLLAMA_HOST` **must** point at
   `https://ollama.com` and `OLLAMA_API_KEY` is required.
4. Click **Deploy**. Never upload `.env` — secrets go only in the Secrets box.

> ⚠️ A public app uses *your* API key, so visitors spend your Ollama quota. Restrict
> viewers in the app settings if that's a concern.

---

## 🧪 Testing

```bash
pip install -r requirements-dev.txt
pytest
```

The core logic (validation, prompts, models, config, Ollama payload/auth) is
unit-tested without any network or Streamlit runtime.

---

## 🔒 Security notes

- `.env` is git-ignored — never commit keys. If a key was ever exposed, **rotate it**.
- Uploads are validated for type, size, dimensions, and decodability before any API call.

---

## 📄 License

Open source — fork and contribute.

---

**Made with ❤️ — DebugGenius, your AI debugging partner.**
