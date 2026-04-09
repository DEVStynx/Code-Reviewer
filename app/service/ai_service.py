import openai
from openai import OpenAI, RateLimitError
from flask import Flask, jsonify
from werkzeug.utils import secure_filename
from app.util.OpenAIUtil import isvalidAPIKey
from json import dumps, loads

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


def review_code(files=None, code=None, api=True):
    data = list()

    if code and not code == "":
        data.append(
            {
                "name": "direct_code",
                "content": code
            }
        )

    if files and "file" in files:
        data = preprocess_files(files.getlist("file"))

    try:
        review = createResponse(dumps(data))
    except openai.RateLimitError:
        raise RuntimeWarning("Too fast api rate!")
    if api:
        return jsonify(review.output_text)
    else:
        return {"review": review.output_text, "input": data}


def review_code_frontend(files=None, code=None):
    # Prepare files
    data = []
    if files and "file" in files:
        data = preprocess_files(files.getlist("file"))

    # Add code if directly via text
    if code:
        data.append({"name": "direct_code", "content": code})

    # review code
    result = review_code(files=None, code=dumps(data), api=False)

    # parse json
    reviewed_code = result["review"]
    if isinstance(reviewed_code, str):
        reviewed_code = loads(reviewed_code)

    # Create list
    file_list = []
    for i, file in enumerate(data):
        review_entry = reviewed_code["files"][i] if i < len(reviewed_code["files"]) else {"findings": [], "style": []}
        file_list.append(
            {
                "file": file["name"],
                "content": file["content"],
                "reviews": review_entry
            }
        )

    return file_list
