# Code-Reviewer

An AI-powered code review web application built with Flask and OpenAI. Paste or upload your code files and receive structured feedback categorized by severity — including critical bugs, major issues, minor problems, and style suggestions.

---

## Overview

Code-Reviewer sends your code to an OpenAI language model configured as a strict senior code reviewer. The model analyzes each file and returns findings organized by:

- **Critical / Major / Minor** — bugs, logic errors, security issues, and functional problems.
- **Style** — non-critical suggestions for readability and conventions.

Results are displayed in a clean web UI per file, or returned as JSON via the REST API.

---

## Features

- **Web UI** — paste code directly into a text area or drag-and-drop / upload multiple files.
- **REST API** — integrate code review into your own toolchain via a simple HTTP endpoint.
- **Multi-file support** — upload several files at once and receive a review for each.
- **Configurable model** — point the app at any OpenAI-compatible endpoint (e.g. Azure OpenAI, a local proxy) and choose any model.

---

## Infrastructure

```
Code-Reviewer/
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not committed)
└── app/
    ├── __init__.py          # Flask application factory
    ├── config.py            # Configuration – reads .env variables
    ├── api/
    │   └── routes.py        # URL routes (web UI + REST API)
    ├── service/
    │   └── ai_service.py    # OpenAI integration & review logic
    ├── util/
    │   └── OpenAIUtil.py    # Helper utilities (API key validation)
    ├── templates/           # Jinja2 HTML templates
    │   ├── layout.html
    │   ├── index.html       # Upload / paste page
    │   └── review.html      # Results page
    └── static/              # CSS, JS, favicon
        ├── style.css
        ├── script.js
        └── icon.ico
```

### Tech stack

| Layer | Technology |
|---|---|
| Web framework | Flask 3 |
| AI backend | OpenAI Python SDK (`openai`) |
| Templating | Jinja2 |
| Frontend | Bootstrap 5 + Bootstrap Icons |
| Config | `python-dotenv` |

---

## Getting Started

### Prerequisites

- Python 3.10+
- An OpenAI API key (or a compatible API endpoint)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/DEVStynx/Code-Reviewer.git
cd Code-Reviewer

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file (see section below)
cp .env.example .env       # then fill in your values

# 5. Start the development server
python main.py
```

The application will be available at `http://127.0.0.1:5000`.

---

## Environment Variables (`.env`)

Create a `.env` file in the project root. Below is an example with all supported variables:

```env
# Required – your OpenAI API key
OPENAI_API_KEY=sk-...

# Optional – override the API base URL (useful for Azure OpenAI or a local proxy)
# Defaults to: https://api.openai.com/v1
OPENAI_BASE_URL=https://api.openai.com/v1

# Optional – the model to use for code review
# Defaults to: gpt-3.1-mini
OPENAI_API_MODEL=gpt-4o
```

> **Note:** The `.env` file is listed in `.gitignore` and will never be committed to version control.

---

## Usage

### Web UI

1. Open `http://127.0.0.1:5000` in your browser.
2. Either **paste code** into the text area or **drag-and-drop / click** to upload one or more source files.
3. Click **Send**.
4. The review page displays each file with its findings and style suggestions.

### REST API

**Endpoint:** `POST /api/review`

**Content-Type:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `code` | string | Raw code to review (plain text) |
| `file` | file | One or more files to review |

You can supply `code`, one or more `file` fields, or both.

**Example with `curl`:**

```bash
# Review code passed as a string
curl -X POST http://127.0.0.1:5000/api/review \
  -F 'code=def add(a, b): return a - b'

# Review an uploaded file
curl -X POST http://127.0.0.1:5000/api/review \
  -F 'file=@path/to/your/script.py'
```

**Example response:**

```json
{
  "files": [
    {
      "file": "script.py",
      "findings": [
        {
          "severity": "major",
          "line": 1,
          "issue": "Incorrect subtraction instead of addition",
          "suggestion": "Change `a - b` to `a + b` to match the function name."
        }
      ],
      "style": []
    }
  ]
}
```

---

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
