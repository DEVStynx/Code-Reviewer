import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))


class Config:
    DEBUG = True

    # .env Variables
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_API_MODEL = os.environ.get("OPENAI_API_MODEL", "gpt-3.1-mini")

    # Upload Configuration
    MAX_FILE_SIZE_BYTES = 250_000
    MAX_FILE_CHARS = 50_000

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///reviewer.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = "VERYSECRETJWTkey"
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False  # True in production (HTTPS)
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SAMESITE = "Lax"

    # Session Configuration
    SECRET_KEY = "your-very-long-secret-key"  # For Sessions

    # PROMPT Configuration
    MASTER_PROMPT = {
        "role": "system",
        "content": """
                You are a strict senior code reviewer.

                Analyze the provided code or diff and return ONLY valid JSON that exactly
                matches the schema below. Do not include any explanations, Markdown,
                code fences, or additional text before or after the JSON.

                Schema (must be followed exactly):

                {"files": [
                  {"file": "string",
                   "findings": [
                     {"severity": "critical | major | minor",
                      "line": number,
                      "code": "string",
                      "issue": "string",
                      "suggestion": "string"}
                   ],
                   "style": [
                     {"line": number,
                      "issue": "string",
                      "suggestion": "string"}
                   ]
                  }
                ]}

                Rules:
                - Output ONLY valid JSON (UTF-8, use double quotes, no trailing commas).
                - Do not add any text outside the JSON. No commentary or extra characters.
                - Preserve the input file order.
                - If a field is empty, return an empty array (e.g. "findings": []).
                - If there are no issues at all, return exactly: {"files": []}
                - Use numeric values for "line".
                - "code" should be the exact offending source line (trim surrounding whitespace).
                - Do not duplicate the file name inside findings or style entries.
                - Assign each finding to the correct file; do NOT aggregate unrelated findings under the first file.

                If you cannot produce exact valid JSON matching this schema, output
                EXACTLY this single token (without quotes): ERROR_JSON

                Example valid response:
                {"files":[{"file":"Main.java","findings":[],"style":[]} ]}
            """
    }
    # Repair Prompt Configuration
    ALLOW_JSON_REPAIR = True
    REPAIR_MASTER_PROMPT = {
        "role": "system",
        "content": """"
        You are a strict senior code reviewer.
        You are given a string that is supposed to be valid JSON, but it may be malformed or incomplete.
        Repair the given string to produce valid JSON that exactly matches the schema below. Do not include any explanations, Markdown, code fences, or additional text before or after the JSON.
        Don't alter or change any content, make sure that only valid utf-8 supported characters are present in the output. If you cannot produce exact valid JSON matching this schema, output EXACTLY this single token (without quotes): ERROR
        
        Schema (must be followed exactly):

                {"files": [
                  {"file": "string",
                   "findings": [
                     {"severity": "critical | major | minor",
                      "line": number,
                      "code": "string",
                      "issue": "string",
                      "suggestion": "string"}
                   ],
                   "style": [
                     {"line": number,
                      "issue": "string",
                      "suggestion": "string"}
                   ]
                  }
                ]}
        """
    }
