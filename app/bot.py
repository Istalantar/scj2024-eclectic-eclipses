import sys
from pathlib import Path

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

    token = ""
    with Path.open(env_path) as f:
        for line in f:
            if line.startswith("TOKEN"):
                token = line.split("=")[1].strip()

    bot.load_extension("features.todo_list")
    bot.start(token)
