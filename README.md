# OCR Reader

Enterprise-grade OCR (optical character recognition) built on FastAPI and the
OpenAI Responses API vision models. Upload a photo, screenshot or scanned
document and get back clean, accurate text - with structured output,
streaming, multi-language support and a searchable history, all running
locally on your own machine.

> New to Python, VS Code or APIs? Skip straight to **[INSTRUCTION.md](INSTRUCTION.md)**
> for a complete, zero-assumptions, step-by-step setup guide.

---

## Table of contents

- [OCR overview](#ocr-overview)
- [Vision models](#vision-models)
- [Features](#features)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Installation](#installation)
- [Visual Studio Code setup](#visual-studio-code-setup)
- [Running the application](#running-the-application)
- [API reference](#api-reference)
- [Configuration reference](#configuration-reference)
- [Troubleshooting](#troubleshooting)
- [Future improvements](#future-improvements)
- [License](#license)

---

## OCR overview

Optical Character Recognition (OCR) is the process of converting an image
containing text - a photo, a scanned page, a screenshot - into machine
readable text. Traditional OCR engines (like Tesseract) work by detecting
individual glyphs and matching them against known character shapes. That
approach is fast and works offline, but it struggles with handwriting,
unusual fonts, low-quality photos, skewed layouts, and mixed languages.

OCR Reader takes a different approach: it sends the image directly to a
**multimodal large language model** (an OpenAI vision-capable model) and
asks it to read and transcribe the text. Because the model actually
*understands* images rather than pattern-matching glyphs, it tends to be
far more robust to:

- Handwriting and cursive text
- Skewed, rotated or partially obscured photos
- Low resolution or poorly lit images
- Mixed-language documents
- Tables, receipts, forms and structured layouts

The trade-off is that this approach requires an internet connection and an
OpenAI API key, and costs a small amount per request (see
[OpenAI's pricing page](https://openai.com/api/pricing/)).

## Vision models

OCR Reader calls the **OpenAI Responses API** (`client.responses.*`) with an
`input_image` content block, which is OpenAI's current interface for
multimodal (text + image) requests. The model used is controlled by the
`OPENAI_MODEL` environment variable - any current OpenAI model with vision
support will work. The project defaults to `gpt-4.1-mini`, a good balance of
cost, latency and accuracy for document-style OCR.

Three request modes are implemented in [`ocr_service.py`](ocr_service.py):

| Mode | API call | Used for |
|---|---|---|
| Plain text | `client.responses.create(...)` | Fast, simple transcription |
| Structured | `client.responses.parse(..., text_format=OCRStructuredExtraction)` | Text broken into headings, paragraphs, lists and tables |
| Streaming | `client.responses.stream(...)` | Live, token-by-token output in the UI |

Because model names and capabilities change over time, check
[OpenAI's model documentation](https://platform.openai.com/docs/models) if
you want to point the app at a newer or different vision model - no code
changes are required, only the `OPENAI_MODEL` value in `.env`.

## Features

**Upload**
- Drag & drop images anywhere on the dropzone
- Click to browse files, or capture directly from your device camera
- Live image preview with a scanning animation while text is being extracted

**Extraction**
- Plain-text OCR extraction
- Structured output (semantic blocks: heading, paragraph, list item, table, caption)
- Streaming output (text appears as it is generated)
- Multi-language hinting, or fully automatic language detection

**Results**
- Monospaced text preview panel
- One-click copy to clipboard
- Download as `.txt` or `.md`

**History**
- Every extraction is saved to a local SQLite database
- Browse, open, delete individual records, or clear all history
- Re-download any past result as `.txt` or `.md`

**Interface**
- Responsive layout (desktop sidebar / mobile top bar)
- Full dark mode, persisted in the browser
- Zero build step - plain HTML, CSS and JavaScript

## Architecture

OCR Reader follows **Clean Architecture** principles adapted for a small,
single-service Python project: dependencies point inward, the framework
(FastAPI) and I/O (SQLite, OpenAI) are kept at the edges, and business logic
lives in small, independently testable services. Rather than deep nested
folders, each concern gets its own flat module at the repository root -
easy to navigate, easy to reason about, easy to keep under the project's
25 MB budget.

```
┌─────────────────────────────────────────────────────────────────┐
│  Presentation                                                   │
│  router_pages.py   -> server-rendered HTML (Jinja2)             │
│  router_ocr.py      -> OCR HTTP endpoints (extract / stream)    │
│  router_history.py  -> history HTTP endpoints                   │
│  static/, templates/ -> HTML, CSS, JS                           │
├─────────────────────────────────────────────────────────────────┤
│  Application services                                           │
│  ocr_service.py      -> talks to the OpenAI Responses API       │
│  image_service.py    -> validates & encodes uploaded images     │
│  history_service.py  -> history CRUD operations                 │
├─────────────────────────────────────────────────────────────────┤
│  Domain                                                         │
│  schemas.py       -> Pydantic v2 models (the shared "contract") │
│  exceptions.py    -> typed application errors                   │
├─────────────────────────────────────────────────────────────────┤
│  Infrastructure                                                 │
│  database.py       -> SQLite connection + schema                │
│  config.py          -> environment-variable driven settings     │
│  logging_config.py  -> structured logging setup                 │
└─────────────────────────────────────────────────────────────────┘
```

Key design decisions:

- **No ORM.** The schema is a single table, so raw `sqlite3` (stdlib) keeps
  the dependency list short and the code easy to follow.
- **Images are never written to disk.** Uploads are validated and processed
  entirely in memory; only the *extracted text* and metadata are persisted.
  This keeps the app stateless with respect to user files and keeps the
  repository (and its runtime footprint) small.
- **One module, one job.** `ocr_service.py` is the only file that imports
  the OpenAI SDK; `database.py` is the only file that imports `sqlite3`.
  Swapping either dependency later only touches one file.
- **Typed errors, not string matching.** Services raise typed exceptions
  (`InvalidImageError`, `OCRProcessingError`, ...) which `exceptions.py`
  translates into consistent JSON responses.

## Project structure

```
ocr-reader/
├── main.py FastAPI app, lifespan, router wiring
├── config.py Environment-variable settings (Pydantic v2)
├── logging_config.py Console + rotating file logging
├── database.py SQLite connection + schema
├── schemas.py Pydantic v2 request/response models
├── exceptions.py Typed errors + FastAPI exception handlers
├── utils.py Small shared helpers
├── image_service.py Upload validation (magic-byte sniffing)
├── ocr_service.py OpenAI Responses API integration
├── history_service.py History CRUD
├── router_pages.py HTML page routes
├── router_ocr.py OCR extraction routes
├── router_history.py History routes
├── static/
│   ├── css/style.css All styling, incl. dark mode
│   ├── js/app.js All frontend behaviour
│   ├── icons/logo.svg
│   └── favicon.svg
├── templates/
│   ├── base.html Shared app shell
│   ├── index.html Upload / dashboard page
│   ├── history.html History page
│   └── settings.html Settings page
├── tests/
│   ├── conftest.py Test fixtures
│   ├── test_api.py Endpoint tests
│   └── test_ocr_service.py Service unit tests
├── requirements.txt Production dependencies
├── requirements-dev.txt + pytest, httpx
├── .env.example Environment variable template
├── .gitignore
├── .vscode/ Editor settings + extension picks
├── Start App.bat Windows one-click startup
├── Start App (Mac).command macOS one-click startup
├── LICENSE
├── README.md
└── INSTRUCTION.md
```

## Installation

**Prerequisites:** Python 3.12+, an OpenAI API key. See
[INSTRUCTION.md](INSTRUCTION.md) if you need help installing anything below.

```bash
# 1. Clone or download the repository, then enter it
cd ocr-reader

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it
#    Windows:
venv\Scripts\activate
#    macOS / Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create your .env file
cp .env.example .env # Windows: copy .env.example .env

# 6. Edit .env and set OPENAI_API_KEY to your real key
```

Get an API key at <https://platform.openai.com/api-keys>.

## Visual Studio Code setup

1. Open the `ocr-reader` folder in VS Code (**File -> Open Folder...**).
2. Install the recommended extensions when prompted, or open the Extensions
   panel and install:
   - **Python** (`ms-python.python`)
   - **Pylance** (`ms-python.vscode-pylance`)
3. Select the project's virtual environment as the interpreter:
   **Ctrl+Shift+P** / **Cmd+Shift+P** -> `Python: Select Interpreter` ->
   choose the one inside `./venv`.
4. Open the integrated terminal (**Ctrl+`**) - it should automatically
   activate `venv`. If it doesn't, activate it manually (see
   [Installation](#installation) step 3).
5. Run the app from the terminal with `python main.py`, or press **F5** and
   choose "Python File" to run `main.py` under the debugger.

`.vscode/settings.json` in this repository already points VS Code at
`venv`, enables `pytest`, and sets sensible formatting defaults.

## Running the application

```bash
# with the virtual environment activated:
python main.py
# or, for auto-reload during development:
uvicorn main:app --reload
```

Then open **<http://127.0.0.1:8000>** in your browser. Interactive API docs
are available at **<http://127.0.0.1:8000/docs>** (Swagger UI) and
**<http://127.0.0.1:8000/redoc>** (ReDoc).

Windows and macOS users can instead double-click **`Start App.bat`** or
**`Start App (Mac).command`**, which handle the virtual environment,
dependency installation and `.env` check automatically.

## API reference

| Method | Path | Description |
|---|---|---|
| `GET`  | `/` | Upload dashboard |
| `GET`  | `/history` | History page |
| `GET`  | `/settings` | Settings page |
| `GET`  | `/api/health` | Liveness/readiness probe |
| `POST` | `/api/ocr/extract` | Extract text from an uploaded image (JSON response) |
| `POST` | `/api/ocr/stream` | Extract text with a Server-Sent-Events stream |
| `GET`  | `/api/history` | List past extractions (`?limit=&offset=`) |
| `GET`  | `/api/history/{id}` | Get one extraction, including full text |
| `DELETE` | `/api/history/{id}` | Delete one extraction |
| `DELETE` | `/api/history` | Delete all history |
| `GET`  | `/api/history/{id}/download` | Download as `.txt` or `.md` (`?fmt=txt\|md`) |

Full interactive documentation, including request/response schemas, is
generated automatically by FastAPI at `/docs`.

## Configuration reference

All configuration lives in `.env` (copy it from `.env.example`). See that
file for the full list with inline comments; the most important variables:

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4.1-mini` | Vision-capable model to use |
| `MAX_UPLOAD_SIZE_MB` | `8` | Maximum accepted upload size |
| `HOST` / `PORT` | `127.0.0.1` / `8000` | Bind address for Uvicorn |
| `DATABASE_PATH` | `ocr_reader.db` | SQLite file location |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## Troubleshooting

**"OPENAI_API_KEY is not configured" / warning banner in the UI**
`.env` is missing, not loaded, or still contains the placeholder key.
Confirm `.env` exists next to `main.py`, contains a real
`OPENAI_API_KEY=sk-...` line, and restart the server after editing it.

**`ModuleNotFoundError` when running the app**
The virtual environment isn't activated, or dependencies weren't installed
into it. Activate `venv` and re-run `pip install -r requirements.txt`.

**"Unsupported or unrecognised image format"**
Only JPEG, PNG, WEBP, GIF and BMP are accepted, and the file's actual
content is checked (not just its extension). Re-export the image in one of
these formats.

**"File exceeds the X MB upload limit"**
Increase `MAX_UPLOAD_SIZE_MB` in `.env` and restart the server, or
compress/resize the image first.

**The page loads but extraction fails immediately**
Check the terminal running the server, and `logs/app.log`, for the full
error. Common causes: invalid/expired API key, no OpenAI account billing
configured, or no internet connection.

**Port 8000 is already in use**
Set a different `PORT` in `.env`, or stop whatever else is using port 8000.

**Streaming stalls or never finishes**
Some corporate proxies buffer Server-Sent-Events. Turn off "Stream results"
in the upload form to fall back to a single non-streamed request.

**Dark mode doesn't persist**
The theme is stored in `localStorage`, so it's specific to one browser and
is cleared if you clear site data for `127.0.0.1`.

## Future improvements

- Batch upload and extraction of multiple images at once
- PDF input support (page-by-page extraction)
- Exportable structured output as CSV/JSON for tabular documents
- Optional local OCR fallback (e.g. Tesseract) for offline use
- User accounts and per-user history when deployed for a team
- Rate limiting and request queuing for shared deployments
- Configurable retention policy for history records

## License

Released under the [MIT License](LICENSE).
