import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


@app.post("/")
async def main(request: Request):
    body = await request.json()
    # Extract user text from the request payload
    try:
        user_text = body["request"]["original_utterance"]
    except Exception:
        user_text = ""

    answer = None
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": user_text}],
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices")
        if choices and isinstance(choices, list):
            message = choices[0].get("message", {})
            answer = message.get("content")
    except Exception:
        answer = None

    if not answer:
        answer = "Извините, произошла ошибка. Попробуйте позже."

    return {
        "version": body.get("version"),
        "session": body.get("session"),
        "response": {
            "end_session": False,
            "text": answer
        }
    }
