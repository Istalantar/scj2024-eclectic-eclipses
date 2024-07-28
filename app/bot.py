import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from interactions import (
    Client,
    Intents,
    listen,
)
from interactions.api.events import Ready

bot = Client(intents=Intents.DEFAULT)


@listen(Ready)
async def on_ready() -> None:
    """Doc string here."""
    print("Ready")
    print(f"This bot is owned by {bot.owner}")


if __name__ == "__main__":
    env_path = Path(".env")
    if not Path.exists(env_path):
        print("No .env file for the token found")
        sys.exit(1)

    load_dotenv()
    token = os.getenv("TOKEN")

    bot.load_extension("features.todo_list")
    bot.load_extension("features.database")
    bot.load_extension("features.dictionary")
    bot.load_extension("features.reminder")
    bot.load_extension("features.calculator")
    bot.start(token)
