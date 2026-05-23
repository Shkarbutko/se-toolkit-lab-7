from services.backend_client import BackendClient


def handle_start() -> str:
    return (
        "Welcome to SE Toolkit Bot!\n"
        "Use /help to see available commands."
    )


def handle_help() -> str:
    return (
        "Available commands:\n"
        "/start — show welcome message\n"
        "/help — list available commands\n"
        "/health — check backend status\n"
        "/labs — list available labs\n"
        "/scores <lab> — show pass rates for a lab"
    )


def handle_health() -> str:
    client = BackendClient()

    try:
        items = client.get("/items/")
        count = len(items) if isinstance(items, list) else 0
        return f"Backend is healthy. {count} items available."
    except RuntimeError as error:
        return f"Backend error: {error}. Check that the services are running."


def handle_labs() -> str:
    client = BackendClient()

    try:
        items = client.get("/items/")
    except RuntimeError as error:
        return f"Backend error: {error}. Check that the services are running."

    labs = []
    for item in items:
        item_type = str(item.get("type", "")).lower()
        if item_type == "lab":
            lab_id = item.get("id", "unknown")
            title = item.get("title") or item.get("name") or lab_id
            labs.append((lab_id, title))

    if not labs:
        return "No labs found."

    lines = ["Available labs:"]
    for lab_id, title in labs:
        lines.append(f"- {lab_id} — {title}")

    return "\n".join(lines)


def handle_scores(command: str) -> str:
    parts = command.split()

    if len(parts) < 2:
        return "Usage: /scores <lab-id>, for example: /scores lab-04"

    lab_id = parts[1]
    client = BackendClient()

    try:
        data = client.get("/analytics/pass-rates", params={"lab": lab_id})
    except RuntimeError as error:
        return f"Backend error: {error}. Check that the services are running."

    if not data:
        return f"No scores found for {lab_id}."

    lines = [f"Pass rates for {lab_id}:"]

    if isinstance(data, dict):
        data = data.get("items") or data.get("tasks") or data.get("data") or []

    for item in data:
        task_name = item.get("task") or item.get("task_name") or item.get("name") or item.get("title") or "Unknown task"
        rate = item.get("pass_rate") or item.get("passRate") or item.get("rate") or item.get("percentage") or 0
        attempts = item.get("attempts") or item.get("total") or item.get("count")

        if isinstance(rate, float) and rate <= 1:
            rate = rate * 100

        if attempts is None:
            lines.append(f"- {task_name}: {rate:.1f}%")
        else:
            lines.append(f"- {task_name}: {rate:.1f}% ({attempts} attempts)")

    return "\n".join(lines)
