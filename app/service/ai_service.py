from openai import OpenAI
from flask import Flask, jsonify
from werkzeug.utils import secure_filename
from app.util.OpenAIUtil import isvalidAPIKey
from json import dumps

openai_client: OpenAI
MODEL: str


def setupOpenAIAPI(app: Flask):
    global openai_client
    global MODEL

    with app.app_context():
        key = app.config.get("OPENAI_API_KEY", None)
        base_url = app.config.get("OPENAI_BASE_URL", None)
        MODEL = app.config.get("OPENAI_API_MODEL") or "gpt-3.1-mini"
    if not isvalidAPIKey(key):
        raise ValueError("Invalid OpenAI API key, check your .env file!")
    openai_client = OpenAI(api_key=key, base_url=base_url)

    # Check if api key is valid
    try:
        openai_client.models.list()
    except Exception as e:
        raise ConnectionError("Invalid OpenAI API Key, check if your key is still valid!") from e


def createResponse(diff):
    # Check if OpenAIAPI is setup already
    if not openai_client:
        raise ConnectionError("The OpenAI client isn't setup yet!")
    request = [
        {
            "role": "system",
            "content": """
                You are a strict code reviewer.

                Return findings as a list:
                    - severity: (critical|major|minor)
                    - file
                    - line
                    - issue
                    - suggestion
            """
        },
        {
            "role": "user",
            "content": diff
        }
    ]
    response = openai_client.responses.create(
        model=MODEL,
        input=request
    )
    return response


def preprocess_files(files) -> list:
    processed_files = list()
    for file in files:
        # If file exists
        if not file or file.filename == '':
            continue

        # Correct filename for safety reasons
        name = secure_filename(file.filename)

        # If decoding fails, skip file (e.g. binary files, ...)
        try:
            content = file.read().decode('utf-8')
        except UnicodeError as e:
            continue
        processed_files.append(
            {
                "name": name,
                "content": content
            }
        )

    return processed_files


def review_code(files=None, code=None):
    data = list()
    if files and "file" in files:
        data = preprocess_files(files.getlist("file"))
    if code and not code == "":
        data.append(
            {
                "name": "direct_code",
                "content": code
            }
        )

    review = createResponse(dumps(data))
    return jsonify(review.output_text)
