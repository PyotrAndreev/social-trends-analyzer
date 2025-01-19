import json
import os
from dotenv import load_dotenv

load_dotenv()


def load_messages_and_buttons(language: str):
    messages_path = os.getenv("MESSAGES_PATH")

    if not messages_path:
        print("Error: MESSAGES_PATH is not set in .env.")
        return {}

    file_path = os.path.join(messages_path, f"{language}.json")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file for language '{language}' was not found at {file_path}.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: The file for language '{language}' contains invalid JSON.")
        return {}


data = load_messages_and_buttons("ru")

MESSAGES = data.get("messages", {})
BUTTONS = data.get("buttons", {})
