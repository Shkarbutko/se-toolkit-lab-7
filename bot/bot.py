import argparse
from handlers.basic import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)

def route_message(text: str) -> str:
    text = text.strip()

    if text == "/start":
        return handle_start()
    if text == "/help":
        return handle_help()
    if text == "/health":
        return handle_health()
    if text == "/labs":
        return handle_labs()
    if text.startswith("/scores"):
        return handle_scores(text)

    return "Unknown command. Use /help to see available commands."

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, help="Run one command in offline test mode")
    args = parser.parse_args()

    if args.test is not None:
        print(route_message(args.test))
        return

    print("Telegram mode is not implemented yet.")

if __name__ == "__main__":
    main()
