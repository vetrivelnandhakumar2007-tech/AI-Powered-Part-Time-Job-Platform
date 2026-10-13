import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from . import services as ai

MAX_HISTORY_TURNS = 8


@require_POST
@csrf_protect
def chat_view(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid request."}, status=400)

    message = (payload.get("message") or "").strip()
    if not message:
        return JsonResponse({"error": "Message is required."}, status=400)
    if len(message) > 1000:
        message = message[:1000]

    raw_history = payload.get("history") or []
    history = []
    for turn in raw_history[-(MAX_HISTORY_TURNS * 2):]:
        role = turn.get("role")
        content = turn.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            history.append({"role": role, "content": content.strip()[:1000]})

    reply = ai.chat_reply(message, history=history)
    return JsonResponse({"reply": reply})
