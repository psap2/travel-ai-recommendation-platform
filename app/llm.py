import json

from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)


def complete_json(system: str, user: str, model: str | None = None) -> dict:
    """One thin seam over the Chat API that always returns parsed JSON."""
    resp = client.chat.completions.create(
        model=model or settings.openai_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    return json.loads(resp.choices[0].message.content)
