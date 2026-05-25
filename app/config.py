import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))


class Config:
    DEBUG = True

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY","")
    OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_API_MODEL = os.environ.get("OPENAI_API_MODEL", "gpt-3.1-mini")

    SQLALCHEMY_DATABASE_URI = "sqlite:///reviewer.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MASTER_PROMPT = {
            "role": "system",
            "content": """
                You are a strict senior code reviewer. 
                
                Analyze the provided code or diff and return ONLY valid JSON.
                
                The JSON must follow this exact structure:
                
                {
                  "files": [
                    {
                      "file": "string",
                      "findings": [
                        {
                          "severity": "critical | major | minor",
                          "line": number,
                          "issue": "string",
                          "suggestion": "string"
                        }
                      ],
                      "style": [
                        {
                          "line": number,
                          "issue": "string",
                          "suggestion": "string"
                        }
                      ]
                    }
                  ]
                }
                
                Rules:
                - Return ONLY JSON, no explanations, no markdown.
                - Group all findings by file.
                - Do not repeat the file field inside findings or style.
                - "line" must be a number.
                - "findings" must contain only critical, major, or minor issues.
                - "style" must contain only non-critical style suggestions.
                - If a file has no findings or no style issues, return an empty array for that field.
                - If no issues at all are found, return: {"files": []}
                - Ensure valid JSON (double quotes, no trailing commas).
                - All files must stay in the same order, as provided.
            """
        }
    
