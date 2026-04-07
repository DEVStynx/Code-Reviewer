import os
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

class Config:
    DEBUG = True

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")