def handle_start() -> str:
    return "Hello! I am your SE Toolkit bot. Use /help to see available commands."

def handle_help() -> str:
    return "Available commands: /start, /help, /health, /labs, /scores <lab-id>"

def handle_health() -> str:
    return "Backend health check is not implemented yet."

def handle_labs() -> str:
    return "Labs list is not implemented yet."

def handle_scores(command: str) -> str:
    return "Scores command is not implemented yet."
