import logging
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import requests

app = FastAPI()

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY_ENV = "DEEPSEEK_API_KEY"

DEFAULT_VERSION = "1.0"
WELCOME_TEXT = "Привет! Я Дипсик помощник. Задайте мне вопрос."
MISSING_API_KEY_TEXT = "Ошибка настройки: не найден ключ DeepSeek API."
DEEPSEEK_ERROR_TEXT = (
    "Извините, сейчас не смог получить ответ от DeepSeek. Попробуйте позже."
)
INTERNAL_ERROR_TEXT = "Извините, произошла внутренняя ошибка. Попробуйте позже."


@app.get("/", response_class=PlainTextResponse)
async def healthcheck():
    return "OK"


def build_yandex_response(text, body=None, end_session=False):
    if not isinstance(body, dict):
        body = {}

    session = body.get("session")
    if not isinstance(session, dict):
        session = {}

    if not isinstance(text, str):
        text = str(text) if text is not None else ""

    return {
        "version": body.get("version") or DEFAULT_VERSION,
        "session": session,
        "response": {
            "text": text,
            "tts": text,
            "end_session": end_session,
        },
    }


def extract_user_text(body):
    if not isinstance(body, dict):
        return ""

    request_payload = body.get("request")
    if not isinstance(request_payload, dict):
        return ""

    original_utterance = (request_payload.get("original_utterance") or "").strip()
    if original_utterance:
        return original_utterance

    command = (request_payload.get("command") or "").strip()
    return command


def ask_deepseek(user_text):
    deepseek_api_key = os.getenv(DEEPSEEK_API_KEY_ENV)
    if not deepseek_api_key:
        logger.error("DeepSeek API key is not configured in %s", DEEPSEEK_API_KEY_ENV)
        return MISSING_API_KEY_TEXT

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Ты голосовой помощник в навыке Алисы. "
                            "Отвечай кратко, понятно и по-русски."
                        ),
                    },
                    {
                        "role": "user",
                        "content": user_text,
                    },
                ],
                "temperature": 0.7,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        choices = data.get("choices") if isinstance(data, dict) else None
        if choices and isinstance(choices, list) and isinstance(choices[0], dict):
            message = choices[0].get("message")
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()

        logger.error("DeepSeek API response has unexpected structure")

    except Exception:
        logger.exception("DeepSeek API request failed")

    return DEEPSEEK_ERROR_TEXT


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled application error", exc_info=(type(exc), exc, exc.__traceback__))
    if request.method == "POST":
        return JSONResponse(build_yandex_response(INTERNAL_ERROR_TEXT), status_code=200)
    return PlainTextResponse("OK", status_code=200)


@app.post("/")
async def main(request: Request):
    body = {}
    try:
        try:
            body = await request.json()
        except Exception:
            logger.warning("Failed to parse Yandex Dialogs request JSON", exc_info=True)
            body = {}

        if not isinstance(body, dict):
            logger.warning("Yandex Dialogs request body is not a JSON object")
            body = {}

        user_text = extract_user_text(body)
        if not user_text:
            return build_yandex_response(WELCOME_TEXT, body)

        answer = ask_deepseek(user_text)
        return build_yandex_response(answer, body)
    except Exception:
        logger.exception("Failed to handle Yandex Dialogs webhook request")
        return build_yandex_response(INTERNAL_ERROR_TEXT, body)
