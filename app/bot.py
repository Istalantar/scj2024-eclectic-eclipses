import os

import interactions
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")

bot = interactions.Client(intents=interactions.Intents.DEFAULT, sync_interactions=True)


def setup(bot: interactions.Client) -> None:
    """Add the extensions before running the Bot."""
    bot.load_extension("features.Dictionary")


def main() -> None:
    """Initialize the bot."""
    bot.start(bot_token)


if __name__ == "__main__":
    setup(bot)
    main()
