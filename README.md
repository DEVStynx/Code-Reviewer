# Code-Reviewer
#### Video Demo:  https://youtu.be/X68CM469pEU
#### Description:

An AI-powered code review web application built with Flask and OpenAI. Register an account, paste or upload your code files, and receive structured feedback categorized by severity — including critical bugs, major issues, minor problems, and style suggestions. Track review history and customize your review settings.

---

## Overview

Code-Reviewer sends your code to an OpenAI language model configured as a strict senior code reviewer. The model analyzes each file and returns findings organized by:

- **Critical / Major / Minor** — bugs, logic errors, security issues, and functional problems.
- **Style** — non-critical suggestions for readability and conventions.

Results are displayed in a clean web UI per file, accessible via REST API with JWT authentication, and stored in your review history for future reference.

---

## Features

- **User Authentication** — secure registration and login with JWT tokens stored in cookies.
- **Web UI** — paste code directly into a text area or drag-and-drop / upload multiple files.
- **Review History** — access past reviews and organize your code review workflow.
- **User Settings** — customize your code review preferences and configuration.
- **REST API** — integrate code review into your toolchain via authenticated HTTP endpoints.
- **Multi-file support** — upload several files at once and receive a review for each.
- **Configurable model** — point the app at any OpenAI-compatible endpoint (e.g. Azure OpenAI, a local proxy) and choose any model.
- **GitHub linking support** — coming soon!

---

## Tech stack

| Layer | Technology |
|---|---|
| Web framework | Flask 3 |
| AI backend | OpenAI Python SDK (`openai`) |
| Database | SQLAlchemy + SQLite |
| Migrations | Alembic / Flask-Migrate |
| Authentication | Flask-JWT-Extended (JWT cookies) |
| Password hashing | Argon2 |
| Templating | Jinja2 |
| Frontend | Bootstrap 5 + Bootstrap Icons |
| Config | `python-dotenv` |
| Data validation | Pydantic |

---

## Getting Started

### Prerequisites

- Python 3.10+
- An OpenAI API key (or a compatible API endpoint)
- SQLite (included with Python)

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

# 5. Initialize the database
flask db upgrade

# 6. Start the development server
python main.py
```

The application will be available at `http://127.0.0.1:5000`.

---

## First Time Setup

On first launch, you will be redirected to the login page. Create a new account by clicking **Register**, then log in with your credentials. Your account includes:

- A personal review history linked to your account
- Customizable settings per user
- Secure access to the review API via JWT tokens

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

#### Registration & Login

1. Navigate to `http://127.0.0.1:5000` in your browser.
2. You will be redirected to the **Login** page.
3. Click **Register** to create a new account with a username and password.
4. Log in with your credentials.

#### Code Review

1. Once logged in, paste code into the text area or drag-and-drop / click to upload one or more source files.
2. Click **Send**.
3. The review page displays each file with its findings and style suggestions.
4. Access your **Review History** from the nav menu to revisit past reviews.
5. Adjust **Settings** to customize your review preferences.

### REST API

**Authentication:** All API endpoints require JWT authentication via Bearer token or cookie.

**Endpoint:** `POST /api/review`

**Content-Type:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `code` | string | Raw code to review (plain text) |
| `file` | file | One or more files to review |

You can supply `code`, one or more `file` fields, or both.

**Example with `curl` (using JWT Bearer token):**

```bash
# First, obtain a JWT token (or use the cookie from login)
# Then review code with the token

curl -X POST http://127.0.0.1:5000/api/review \
  -H "Authorization: Bearer <your-jwt-token>" \
  -F 'code=def add(a, b): return a - b'

# Or upload a file
curl -X POST http://127.0.0.1:5000/api/review \
  -H "Authorization: Bearer <your-jwt-token>" \
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
          "code": "def add(a, b): return a - b",
          "issue": "Incorrect subtraction instead of addition",
          "suggestion": "Change `a - b` to `a + b` to match the function name."
        }
      ],
      "style": []
    }
  ]
}
```

### User Endpoints

**Get current user info:**

```bash
curl -X GET http://127.0.0.1:5000/api/me \
  -H "Authorization: Bearer <your-jwt-token>"
```

**Response:**

```json
{
  "id": "user-id",
  "username": "your-username"
}
```

---

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
