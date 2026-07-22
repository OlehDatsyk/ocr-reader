# OCR Reader - Beginner's Installation & Usage Guide

Welcome! This guide assumes you have **never** used Python, Visual Studio
Code, Git, FastAPI, the OpenAI API, AI vision models, or OCR before. Every
step is spelled out - nothing is skipped. Just follow along from top to
bottom, in order.

Grab a coffee. This will take about 30-45 minutes the first time.

---

## Table of contents

1. [Installing Python](#1-installing-python)
2. [Installing Visual Studio Code](#2-installing-visual-studio-code)
3. [Installing Git](#3-installing-git)
4. [Required VS Code extensions](#4-required-vs-code-extensions)
5. [Opening the project](#5-opening-the-project)
6. [Creating a virtual environment](#6-creating-a-virtual-environment)
7. [Activating the virtual environment](#7-activating-the-virtual-environment)
8. [Installing dependencies](#8-installing-dependencies)
9. [Creating the .env file](#9-creating-the-env-file)
10. [Obtaining an OpenAI API key](#10-obtaining-an-openai-api-key)
11. [Running the application](#11-running-the-application)
12. [Uploading your first image](#12-uploading-your-first-image)
13. [Testing every feature](#13-testing-every-feature)
14. [Exporting results](#14-exporting-results)
15. [Common errors](#15-common-errors)
16. [Troubleshooting](#16-troubleshooting)
17. [FAQ](#17-faq)
18. [Security recommendations](#18-security-recommendations)
19. [Project architecture](#19-project-architecture)
20. [Next learning steps](#20-next-learning-steps)

---

## 1. Installing Python

Python is the programming language this project is written in. You need
version **3.12 or newer**.

### Windows

1. Go to <https://www.python.org/downloads/> in your web browser.
2. Click the yellow **Download Python 3.x.x** button.
3. Open the downloaded file (it will be named something like
   `python-3.12.x-amd64.exe`).
4. **This is the most important step:** on the first installer screen,
   check the box at the bottom that says **"Add python.exe to PATH"**
   before clicking anything else.

   ```
   [ Screenshot placeholder: Python installer first screen with the
     "Add python.exe to PATH" checkbox highlighted ]
   ```

5. Click **Install Now** and wait for it to finish.
6. Click **Close**.

### macOS

1. Go to <https://www.python.org/downloads/macos/> in your web browser.
2. Download the latest **macOS 64-bit universal2 installer**.
3. Open the downloaded `.pkg` file and follow the installer prompts
   (Continue -> Continue -> Agree -> Install).
4. Enter your Mac's password when asked.

### Verify the installation

Open a terminal:
- **Windows:** press the Windows key, type `cmd`, press Enter.
- **macOS:** press `Cmd+Space`, type `Terminal`, press Enter.

Type this command and press Enter:

```bash
python --version
```

If that prints something like `Python is not recognized`, try:

```bash
python3 --version
```

**Expected output:**

```
Python 3.12.4
```

Any `3.12.x` or higher is fine. If you see a version below 3.12, reinstall
using the steps above with the latest version from python.org.

---

## 2. Installing Visual Studio Code

Visual Studio Code (VS Code) is a free code editor.

1. Go to <https://code.visualstudio.com/>.
2. Click the big **Download** button - it detects your operating system
   automatically.
3. Run the downloaded installer:
   - **Windows:** accept the license, keep the default options, and it's
     recommended to check "Add to PATH" if offered.
   - **macOS:** drag the **Visual Studio Code** icon into your
     **Applications** folder.
4. Launch VS Code.

   ```
   [ Screenshot placeholder: VS Code welcome screen on first launch ]
   ```

---

## 3. Installing Git

Git tracks changes to code and lets you download (clone) this project from
GitHub. It's optional if you already have the project files as a `.zip`,
but it's recommended.

### Windows

1. Go to <https://git-scm.com/download/win>.
2. Download and run the installer.
3. Click **Next** through every screen, keeping the default options - the
   defaults are fine for beginners.
4. Click **Install**, then **Finish**.

### macOS

1. Open **Terminal**.
2. Type `git --version` and press Enter.
3. If Git isn't installed, macOS will prompt you to install the
   "Command Line Developer Tools" - click **Install** and wait.

### Verify

```bash
git --version
```

**Expected output:**

```
git version 2.43.0
```

(Exact numbers will vary - any version is fine.)

---

## 4. Required VS Code extensions

Extensions add extra functionality to VS Code.

1. Open VS Code.
2. Click the **Extensions** icon in the left sidebar (it looks like four
   squares, one detached).

   ```
   [ Screenshot placeholder: VS Code left sidebar with the Extensions
     icon highlighted ]
   ```

3. Search for and install each of the following (click **Install** on
   each):

| Extension | Publisher | Why you need it |
|---|---|---|
| Python | Microsoft (`ms-python.python`) | Python language support, running & debugging |
| Pylance | Microsoft (`ms-python.vscode-pylance`) | Fast autocompletion and error checking |

When you open this project's folder, VS Code will show a notification
offering to install these (and a couple of optional extras) automatically -
you can just click **Install All** there instead.

---

## 5. Opening the project

If you downloaded this project as a `.zip` file:

1. Right-click the `.zip` file and choose **Extract All...** (Windows) or
   double-click it (macOS) to unzip it.
2. Note the folder path where it was extracted (e.g.
   `C:\Users\YourName\Downloads\ocr-reader` or
   `/Users/YourName/Downloads/ocr-reader`).

If you're cloning with Git instead:

```bash
git clone <the repository URL>
cd ocr-reader
```

Now open the folder in VS Code:

1. In VS Code, go to **File -> Open Folder...** (macOS: **File -> Open...**).
2. Browse to and select the `ocr-reader` folder.
3. Click **Select Folder** (Windows) / **Open** (macOS).

You should now see all the project files in the **Explorer** panel on the
left: `main.py`, `config.py`, `templates/`, `static/`, and so on.

```
[ Screenshot placeholder: VS Code Explorer panel showing the ocr-reader
  project file tree ]
```

---

## 6. Creating a virtual environment

A **virtual environment** is an isolated folder that holds Python packages
just for this project, so they don't clash with anything else on your
computer. This is standard practice for every Python project.

1. Open the integrated terminal in VS Code: **Terminal -> New Terminal**
   (or the shortcut `` Ctrl+` ``).
2. Make sure the terminal's current folder is the project folder (the
   prompt should show `ocr-reader` somewhere in the path).
3. Run:

```bash
python -m venv venv
```

If `python` isn't recognized, try `python3` instead. This creates a new
folder named `venv` inside your project - that's your virtual environment.
It can take 10-20 seconds.

**Expected result:** a new `venv` folder appears in the VS Code Explorer
panel. Nothing is printed to the terminal if it succeeds.

---

## 7. Activating the virtual environment

"Activating" tells your terminal to use the Python and packages inside
`venv` instead of your computer's main Python installation.

### Windows (Command Prompt)

```bat
venv\Scripts\activate
```

### Windows (PowerShell)

```powershell
venv\Scripts\Activate.ps1
```

> If PowerShell shows a red "running scripts is disabled" error, run
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, type `Y` to
> confirm, then try activating again.

### macOS / Linux

```bash
source venv/bin/activate
```

**Expected result:** your terminal prompt now starts with `(venv)`, like:

```
(venv) C:\Users\YourName\ocr-reader>
```

or

```
(venv) yourname@MacBook ocr-reader %
```

You'll need to activate the virtual environment every time you open a new
terminal to work on this project. VS Code will often do this automatically
once it knows about `venv` (see [Section 4](#4-required-vs-code-extensions)).

---

## 8. Installing dependencies

With `(venv)` showing in your prompt, install the Python packages this
project needs:

```bash
pip install -r requirements.txt
```

This reads the `requirements.txt` file and downloads/installs FastAPI,
Uvicorn, the OpenAI SDK, and a handful of other small libraries. It takes
1-3 minutes depending on your internet connection.

**Expected output (last few lines):**

```
Successfully installed fastapi-... jinja2-... openai-... python-dotenv-... python-multipart-... uvicorn-...
```

If you plan to run the test suite later, also install:

```bash
pip install -r requirements-dev.txt
```

---

## 9. Creating the .env file

The `.env` file holds settings specific to your machine - most importantly,
your private OpenAI API key. It is never uploaded to GitHub (it's excluded
via `.gitignore`).

1. In the project folder, find the file named **`.env.example`**.
2. Make a copy of it named exactly **`.env`** (no `.example`):

   **Windows:**
   ```bat
   copy .env.example .env
   ```

   **macOS / Linux:**
   ```bash
   cp .env.example .env
   ```

3. Open `.env` in VS Code (click it in the Explorer panel).
4. You'll fill in `OPENAI_API_KEY` in the next section - leave everything
   else as-is for now.

```
[ Screenshot placeholder: .env file open in the VS Code editor, with the
  OPENAI_API_KEY line highlighted ]
```

---

## 10. Obtaining an OpenAI API key

An API key is a private password that lets this app make requests to
OpenAI's models on your behalf. OpenAI charges a small amount per request
based on usage - there is no separate subscription needed to use the API.

1. Go to <https://platform.openai.com/> and sign up or log in.
2. You may be asked to add a payment method under **Settings -> Billing**
   before the API will work - the OCR calls this app makes are inexpensive,
   but OpenAI requires billing to be set up for API access.
3. Go to <https://platform.openai.com/api-keys>.
4. Click **Create new secret key**.
5. Give it a name (e.g. "OCR Reader") and click **Create secret key**.
6. **Copy the key immediately** - it looks like `sk-proj-...` and is shown
   **only once**. If you lose it, just create a new one.

   ```
   [ Screenshot placeholder: OpenAI dashboard "Create new secret key"
     dialog with the generated key visible ]
   ```

7. Back in VS Code, open `.env` and replace the placeholder line:

   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```

   with your real key, for example:

   ```
   OPENAI_API_KEY=sk-proj-AbCdEf123...
   ```

8. Save the file (`Ctrl+S` / `Cmd+S`).

---

## 11. Running the application

With the virtual environment activated (`(venv)` visible in your prompt)
and dependencies installed, start the server:

```bash
python main.py
```

**Expected output:**

```
2026-07-22 10:00:00 | INFO     | logging_config | Logging configured (level=INFO, log_dir=logs)
2026-07-22 10:00:00 | INFO     | main            | Starting OCR Reader v1.0.0 (environment=development)
2026-07-22 10:00:00 | INFO     | database        | Database initialised at ocr_reader.db
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Open your web browser and go to:

```
http://127.0.0.1:8000
```

You should see the OCR Reader dashboard.

```
[ Screenshot placeholder: OCR Reader upload dashboard in the browser ]
```

To stop the server later, click into the terminal and press `Ctrl+C`.

> **Prefer one-click startup?** Instead of the steps above, you can
> double-click **`Start App.bat`** (Windows) or **`Start App (Mac).command`**
> (macOS) - after you've completed Section 9 and 10 once, these scripts
> handle the virtual environment, dependencies and launch automatically
> every time.

---

## 12. Uploading your first image

1. On the **Upload** page, either:
   - Drag an image file from your computer onto the dropzone, or
   - Click **Browse files** and choose an image, or
   - Click **Use camera** to take a photo (on a phone/laptop with a
     camera).
2. A preview of your image appears.
3. Leave **Language** as **Auto-detect** for now.
4. Click **Extract text**.
5. Within a few seconds, extracted text streams into the right-hand panel.

```
[ Screenshot placeholder: Upload page showing an image preview on the
  left and extracted text streaming into the panel on the right ]
```

**Expected result:** the text visible in your image appears in the
"Extracted text" panel, along with chips showing the detected language,
model used, and character/word counts.

---

## 13. Testing every feature

Work through this checklist to confirm everything works end-to-end:

| # | Feature | How to test | Expected result |
|---|---|---|---|
| 1 | Drag & drop | Drag an image onto the dropzone | Preview appears |
| 2 | Browse files | Click "Browse files", pick an image | Preview appears |
| 3 | Camera upload | Click "Use camera" | Camera opens (on supported devices) |
| 4 | Plain extraction | Untoggle "Structured output", click Extract | Text appears |
| 5 | Structured output | Toggle it on, click Extract | Text still appears (blocks used internally) |
| 6 | Streaming | Toggle "Stream results" on, click Extract | Text appears progressively, not all at once |
| 7 | Language hint | Change "Language" to a specific language, click Extract | "Language:" chip reflects your choice |
| 8 | Copy text | Click "Copy text" after an extraction | A toast says "Copied to clipboard"; paste elsewhere to confirm |
| 9 | Download .txt | Click "Download .txt" | A `.txt` file downloads with the extracted text |
| 10 | Download .md | Click "Download .md" | A `.md` file downloads with headers and metadata |
| 11 | History list | Go to **History** | Your past extractions are listed, newest first |
| 12 | History detail | Click a history row | A modal opens with the full text |
| 13 | Delete one item | Click the trash icon on a row | The item disappears from the list |
| 14 | Clear history | Click "Clear history", confirm | The list becomes empty |
| 15 | Dark mode | Click the "Dark mode" button in the sidebar | Colors invert; refreshing the page keeps your choice |
| 16 | Settings page | Go to **Settings** | Your `.env` values are shown (API key masked) |
| 17 | Responsive layout | Resize your browser window narrow, or open on a phone | Sidebar becomes a top bar |

---

## 14. Exporting results

There are two ways to export extracted text:

**From the Upload page**, immediately after an extraction:
- Click **Download .txt** for plain text.
- Click **Download .md** for a Markdown file with metadata (filename,
  detected language, model, timestamp) above the text.

**From the History page**, at any later time:
- Click a row to open it, then use the **Download .txt** / **Download .md**
  buttons in the modal footer.
- Or visit the download URL directly, e.g.
  `http://127.0.0.1:8000/api/history/1/download?fmt=md`.

---

## 15. Common errors

| Error message | What it means | Fix |
|---|---|---|
| `'python' is not recognized as an internal or external command` | Python isn't on your PATH | Reinstall Python and check "Add python.exe to PATH" (Section 1) |
| `ModuleNotFoundError: No module named 'fastapi'` | Dependencies aren't installed in the active environment | Activate `venv` (Section 7), then `pip install -r requirements.txt` |
| `OPENAI_API_KEY is not configured` (banner in the app) | `.env` is missing or still has the placeholder key | Complete Sections 9 and 10 |
| `AuthenticationError` / "OpenAI rejected the configured API key" | The key in `.env` is wrong, revoked, or has no billing set up | Generate a new key at platform.openai.com and update `.env` |
| `Unsupported or unrecognised image format` | The file isn't a JPEG/PNG/WEBP/GIF/BMP, or is corrupted | Re-export/save the image in a supported format |
| `File exceeds the 8.0 MB upload limit` | The image is too large | Compress the image, or raise `MAX_UPLOAD_SIZE_MB` in `.env` |
| `Address already in use` / port 8000 busy | Something else is using port 8000 | Set `PORT=8001` (or similar) in `.env` and restart |
| Blank page / cannot connect | The server isn't running, or you used the wrong URL | Confirm `python main.py` is running and you're visiting `http://127.0.0.1:8000` |

---

## 16. Troubleshooting

If something isn't working, work through these steps in order:

1. **Check the terminal.** Any error is printed there in plain language.
2. **Check `logs/app.log`** inside the project folder for a more detailed
   history of what happened.
3. **Confirm `(venv)` is showing** in your terminal prompt. If not, repeat
   Section 7.
4. **Confirm `.env` exists** (not just `.env.example`) and has a real API
   key with no extra spaces or quotation marks.
5. **Restart the server** after any change to `.env` - it's only read on
   startup.
6. **Try the health check** at `http://127.0.0.1:8000/api/health` - if
   `openai_configured` is `false`, your `.env` isn't being picked up.
7. **Reinstall dependencies**: deactivate, delete the `venv` folder, and
   repeat Sections 6-8 from scratch.
8. Still stuck? Re-read the exact error message in the
   [Common errors](#15-common-errors) table above - most issues map
   directly to one of those rows.

---

## 17. FAQ

**Do I need to know how to code to use this?**
No - Sections 1-12 get you to a working app with no coding required.
Sections 19-20 are for anyone who wants to go further.

**Does this work without an internet connection?**
No. Every extraction sends the image to OpenAI's servers, so an internet
connection and a valid, billed OpenAI account are required.

**Is my data private?**
Images are processed in memory and never saved to disk by this app; only
the extracted *text* is stored, locally, in the `ocr_reader.db` SQLite
file on your own computer. Images are sent to OpenAI for processing -
review OpenAI's API data usage policy (openai.com/enterprise-privacy) for
how they handle that data.

**How much does each extraction cost?**
It depends on the model and image size; see OpenAI's pricing page
(openai.com/api/pricing). Costs for typical document-sized images are
usually a small fraction of a cent to a few cents per image.

**Can I use a different AI provider?**
Not without code changes - `ocr_service.py` is written against the OpenAI
Python SDK specifically. It's the only file you'd need to change to
support a different provider.

**Can multiple people use this at once?**
The app has no built-in user accounts or authentication; it's designed for
individual/local use. See "Future improvements" in `README.md` for ideas
on extending it for shared/team use.

**Why SQLite instead of a "real" database?**
SQLite is a single file, needs no separate server to install or run, and
is more than capable for a personal history log. It's part of Python's
standard library, so it adds zero extra dependencies.

---

## 18. Security recommendations

- **Never commit your `.env` file** to Git or share it with anyone - it
  contains your private API key. This project's `.gitignore` already
  excludes it, but always double-check before pushing to a public
  repository.
- **Never paste your API key in chat, forums, or screenshots.** Treat it
  like a password.
- **Rotate your key if it's ever exposed**: go to your OpenAI dashboard's
  API keys page, delete the old key, and create a new one.
- **Set a usage limit** in your OpenAI account (Settings -> Billing ->
  Limits) so a bug or unexpected traffic can't run up a large bill.
- **Don't expose this app directly to the internet** without adding
  authentication first - as shipped, anyone who can reach the server can
  use your API key's quota. It's designed to run on `127.0.0.1`
  (your own machine only).
- **Keep dependencies up to date** periodically with
  `pip install --upgrade -r requirements.txt`, and re-run the test suite
  afterwards.

---

## 19. Project architecture

For a full breakdown of how the codebase is organised, see the
**Architecture** and **Project structure** sections of `README.md`. In
short:

- **`main.py`** wires everything together and starts the server.
- **Routers** (`router_pages.py`, `router_ocr.py`, `router_history.py`)
  handle incoming HTTP requests.
- **Services** (`ocr_service.py`, `image_service.py`, `history_service.py`)
  contain the actual logic - talking to OpenAI, validating images, reading
  and writing history.
- **`schemas.py`** defines the exact shape of every request and response
  using Pydantic v2, so mistakes are caught automatically before they reach
  your code.
- **`database.py`** is the only file that talks directly to SQLite.
- **`templates/` and `static/`** hold everything the browser sees: HTML
  pages, CSS styling, and JavaScript behaviour.

---

## 20. Next learning steps

If this project sparked your curiosity, here's a suggested path:

1. **Python basics** - if any of the code in `.py` files looked
   unfamiliar, try the free "Python for Everybody" course (py4e.com).
2. **FastAPI** - read the official tutorial at fastapi.tiangolo.com to
   understand `main.py` and the `router_*.py` files in depth.
3. **Pydantic** - docs.pydantic.dev explains the data validation library
   used throughout `schemas.py` and `config.py`.
4. **The OpenAI API** - platform.openai.com/docs covers the Responses API
   used in `ocr_service.py`, including other capabilities like function
   calling and structured outputs.
5. **HTML/CSS/JavaScript** - MDN's "Learn web development" section
   (developer.mozilla.org) covers everything used in `templates/` and
   `static/`.
6. **Git & GitHub** - docs.github.com/en/get-started if you want to track
   your own changes to this project or publish your fork.
7. **Try extending the app** - a great first project is picking one item
   from the "Future improvements" list in `README.md` and implementing it
   yourself.

Good luck, and enjoy exploring OCR Reader!
