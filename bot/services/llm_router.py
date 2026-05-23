import json
import os
import sys
from typing import Any

import requests
from dotenv import load_dotenv

from services.backend_client import BackendClient


load_dotenv("../.env.bot.secret")
load_dotenv(".env.bot.secret")


TOOLS = [
    {"type": "function", "function": {"name": "get_items", "description": "List labs and tasks", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_learners", "description": "List enrolled students and groups", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_scores", "description": "Get score distribution for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_pass_rates", "description": "Get per-task pass rates for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_timeline", "description": "Get submissions timeline for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_groups", "description": "Get per-group scores for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_top_learners", "description": "Get top learners for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_completion_rate", "description": "Get completion rate for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "trigger_sync", "description": "Refresh backend data", "parameters": {"type": "object", "properties": {}}}},
]


def call_tool(name: str, args: dict[str, Any]) -> Any:
    client = BackendClient()

    if name == "get_items":
        return client.get("/items/")
    if name == "get_learners":
        return client.get("/learners/")
    if name == "get_scores":
        return client.get("/analytics/scores", {"lab": args.get("lab", "lab-08")})
    if name == "get_pass_rates":
        return client.get("/analytics/pass-rates", {"lab": args.get("lab", "lab-08")})
    if name == "get_timeline":
        return client.get("/analytics/timeline", {"lab": args.get("lab", "lab-08")})
    if name == "get_groups":
        return client.get("/analytics/groups", {"lab": args.get("lab", "lab-08")})
    if name == "get_top_learners":
        return client.get("/analytics/top-learners", {"lab": args.get("lab", "lab-08"), "limit": args.get("limit", 5)})
    if name == "get_completion_rate":
        return client.get("/analytics/completion-rate", {"lab": args.get("lab", "lab-08")})
    if name == "trigger_sync":
        return client.post("/pipeline/sync")

    return {"error": f"Unknown tool: {name}"}


def route_with_llm(user_text: str) -> str:
    api_key = os.getenv("LLM_API_KEY", "")
    base_url = os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1").rstrip("/")
    model = os.getenv("LLM_API_MODEL", "coder-model")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a software engineering course analytics bot. "
                "Use tools to answer questions about labs, scores, learners, groups, pass rates, and completion. "
                "For gibberish or greetings, answer helpfully. "
                "Always mention concrete lab ids and percentages when available."
            ),
        },
        {"role": "user", "content": user_text},
    ]

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    for _ in range(4):
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json={"model": model, "messages": messages, "tools": TOOLS, "tool_choice": "auto"},
            timeout=60,
        )
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]

        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            return message.get("content") or "I can help with labs, scores, pass rates, groups, and learners."

        messages.append(message)

        for tool_call in tool_calls:
            function = tool_call["function"]
            name = function["name"]
            args = json.loads(function.get("arguments") or "{}")

            print(f"[tool] LLM called: {name}({args})", file=sys.stderr)

            result = call_tool(name, args)
            print(f"[tool] Result: {str(result)[:300]}", file=sys.stderr)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": name,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    return "I could not finish the analysis. Try asking about labs, scores, pass rates, or groups."
