"""OpenAI helper service used by the application.

This module provides a thin wrapper around the OpenAI client used by the
application to request code reviews. It focuses on clear typing, better
error messages and small defensive checks.
"""

from __future__ import annotations

from json import dumps, loads
import logging
from typing import Any, Dict, List, Optional, cast

from flask import Flask, jsonify
from flask_jwt_extended import get_current_user
from openai import OpenAI, RateLimitError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.database.db import db
from app.util.OpenAIUtil import isvalidAPIKey
from app.models.query import Query

logger = logging.getLogger(__name__)


# Module-level OpenAI state (initialized via setup_openai_api)
OPENAI_CLIENT: Optional[OpenAI] = None
MODEL: str = "gpt-3.1-mini"
MASTER_PROMPT: Optional[Dict[str, Any]] = None

MAX_FILE_SIZE_BYTES = 250_000
MAX_FILE_CHARS = 50_000


def setup_openai_api(app: Flask) -> None:
    """Initialize the global OpenAI client using values from Flask config.

    Expected config keys:
      - OPENAI_API_KEY
      - OPENAI_BASE_URL (optional)
      - OPENAI_API_MODEL (optional)
      - MASTER_PROMPT (required)
    """

    global OPENAI_CLIENT, MODEL, MASTER_PROMPT, MAX_FILE_SIZE_BYTES, MAX_FILE_CHARS, MAX_FILE_CHARS

    with app.app_context():
        key = app.config.get("OPENAI_API_KEY")
        base_url = app.config.get("OPENAI_BASE_URL")
        MODEL = app.config.get("OPENAI_API_MODEL") or MODEL
        MASTER_PROMPT = app.config.get("MASTER_PROMPT")
        MAX_FILE_SIZE_BYTES = app.config.get("MAX_FILE_SIZE_BYTES")
        MAX_FILE_CHARS = app.config.get("MAX_FILE_CHARS")

    if not isvalidAPIKey(key):
        raise ValueError("Invalid or missing OpenAI API key; set OPENAI_API_KEY in configuration.")

    OPENAI_CLIENT = OpenAI(api_key=key, base_url=base_url)

    # quick validation call to fail fast if the key/base URL are invalid
    try:
        OPENAI_CLIENT.models.list()
    except Exception as exc:  # pragma: no cover - surface connection issues clearly
        logger.exception("Failed to validate OpenAI credentials")
        raise ConnectionError("Failed to validate OpenAI credentials; check API key and base URL") from exc


def _create_response(payload: str) -> Any:
    """Send a request to the OpenAI responses API and return the raw result.

    The function expects setup_openai_api to have been called previously.
    """

    if OPENAI_CLIENT is None:
        raise ConnectionError("OpenAI client is not initialized. Call setup_openai_api first.")

    if MASTER_PROMPT is None:
        raise ConnectionError("MASTER_PROMPT is not configured in application config.")

    request = [MASTER_PROMPT, {"role": "user", "content": payload}]
    return OPENAI_CLIENT.responses.create(model=MODEL, input=cast(Any, request))


def _extract_json_block(text: str) -> Optional[str]:
    """Try to extract a JSON object or array from free-form model output."""

    candidates = []

    object_start = text.find("{")
    object_end = text.rfind("}")
    if object_start != -1 and object_end > object_start:
        candidates.append(text[object_start : object_end + 1])

    array_start = text.find("[")
    array_end = text.rfind("]")
    if array_start != -1 and array_end > array_start:
        candidates.append(text[array_start : array_end + 1])

    for candidate in candidates:
        try:
            loads(candidate)
            return candidate
        except Exception:
            continue

    return None


def _normalize_review_output(review: Any) -> Dict[str, Any]:
    """Coerce different OpenAI response shapes into the expected review payload."""

    if isinstance(review, dict):
        return review

    if isinstance(review, list):
        return {"files": review}

    if isinstance(review, str):
        try:
            parsed = loads(review)
        except Exception:
            extracted = _extract_json_block(review)
            if extracted is not None:
                try:
                    parsed = loads(extracted)
                except Exception:
                    parsed = None
            else:
                parsed = None

        if isinstance(parsed, dict):
            return parsed

        if isinstance(parsed, list):
            return {"files": parsed}

        return {"files": [], "summary": review}

    return {"files": []}


def _preprocess_files(files: List[FileStorage]) -> List[Dict[str, str]]:
    """Convert uploaded FileStorage objects into a list of dicts with name/content.

    Files that cannot be decoded as UTF-8 are skipped.
    """

    processed: List[Dict[str, str]] = []

    for fs in files:
        if not fs or not getattr(fs, "filename", None):
            continue

        filename = secure_filename(fs.filename or "")
        if not filename:
            continue

        # FileStorage.read() may return bytes or str depending on how it was opened
        raw = fs.read()
        if raw is None:
            continue

        if isinstance(raw, (bytes, bytearray)) and len(raw) > MAX_FILE_SIZE_BYTES:
            logger.warning("Skipping file %s: exceeds %s bytes", filename, MAX_FILE_SIZE_BYTES)
            continue

        if isinstance(raw, (bytes, bytearray)) and b"\x00" in raw:
            logger.warning("Skipping file %s: appears to be binary data", filename)
            continue

        try:
            content = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
        except UnicodeError:
            logger.warning("Skipping file %s: unable to decode as UTF-8", filename)
            continue

        if len(content) > MAX_FILE_CHARS:
            logger.warning("Truncating file %s to %s characters", filename, MAX_FILE_CHARS)
            content = content[:MAX_FILE_CHARS] + f"\n\n[Truncated after {MAX_FILE_CHARS} characters for safety.]"

        processed.append({"name": filename, "content": content})

    return processed


def _build_input(files: Optional[Any] = None, code: Optional[str] = None) -> List[Dict[str, str]]:
    """Build a serializable input structure from either raw code or uploaded files.

    The `files` parameter is expected to be a Werkzeug MultiDict-like structure
    with a 'file' key that supports `.getlist('file')`.
    """

    data: List[Dict[str, str]] = []
    uploads: List[Dict[str, str]] = []

    if files:
        for key in ("file", "files"):
            if key in files:
                uploads.extend(_preprocess_files(cast(List[FileStorage], files.getlist(key))))

    normalized_code = code.strip() if code else ""

    if normalized_code:
        upload_contents = {item["content"].strip() for item in uploads}
        if normalized_code not in upload_contents:
            data.append({"name": "direct_code", "content": normalized_code})

    data.extend(uploads)

    return data
def _append_query_db(query: Query):
    """Append a query to the database."""
    print(f"query: {query.user_id} {query.review_json}")
    db.session.add(query)
    db.session.commit()
    pass

def review_code(files: Optional[Dict[str, Any]] = None, code: Optional[str] = None, api: bool = True):
    """Request a code review from OpenAI.

    If `api` is True the function returns a Flask `Response` (JSON), otherwise
    it returns a dict with the raw review and the input used.
    """

    payload = _build_input(files=files, code=code)

    logger.info("Code Review request: %s", payload)

    try:
        review = _create_response(dumps(payload))
    except RateLimitError as exc:
        logger.warning("OpenAI rate limit exceeded")
        raise RuntimeWarning("OpenAI rate limit exceeded; slow down requests") from exc

    # Many OpenAI response objects expose `output_text` - keep existing behaviour.
    output_text = getattr(review, "output_text", None)
    review_payload = _normalize_review_output(output_text if output_text is not None else review)

    logger.info("Code Review response: %s", review_payload)
    if api:
        return jsonify(review_payload)

    return {"review": review_payload, "input": payload}


def review_code_frontend(files: Optional[Dict[str, Any]] = None, code: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return a frontend-friendly list of reviewed files.

    Each entry contains: file, content, reviews (with default empty findings/style).
    """

    result = review_code(files=files, code=code, api=False)
    reviewed = _normalize_review_output(result.get("review"))

    input_files = cast(List[Dict[str, str]], result.get("input", []))
    reviewed_files = cast(List[Dict[str, Any]], reviewed.get("files", [])) if isinstance(reviewed, dict) else []
    summary = reviewed.get("summary", "") if isinstance(reviewed, dict) else ""

    out: List[Dict[str, Any]] = []
    for idx, infile in enumerate(input_files):
        review_entry = reviewed_files[idx] if idx < len(reviewed_files) and isinstance(reviewed_files[idx], dict) else {}
        normalized_review = {
            "findings": review_entry.get("findings", []),
            "style": review_entry.get("style", []),
            "summary": review_entry.get("summary", "") or (summary if len(input_files) == 1 else ""),
        }

        if not normalized_review["findings"] and not normalized_review["style"] and not normalized_review["summary"] and summary:
            normalized_review["summary"] = summary

        out.append({"file": infile["name"], "content": infile["content"], "reviews": normalized_review})

    if not out and summary:
        out.append({"file": "review", "content": "", "reviews": {"findings": [], "style": [], "summary": summary}})

    query = Query()
    query.review_json = out
    query.user_id = get_current_user().user_id
    _append_query_db(query)
    return out
