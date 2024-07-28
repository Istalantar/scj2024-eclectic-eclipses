import json
import os

import aiohttp
from dotenv import load_dotenv
from interactions import Extension, OptionType, SlashContext, slash_command, slash_option

load_dotenv()
DICTIONARY_KEY = os.getenv("DICTIONARY_KEY")


class Dictionary(Extension):
    """Dictionary slash command, returns a short definition of the word provided by User."""

    @slash_command(
        name="dictionary",
        description="Tells a short definition from dictionary",
    )
    @slash_option(
        name="search_word",
        description="Word to be searched in the dictionary",
        required=True,
        opt_type=OptionType.STRING,
    )
    async def dictionary(self, ctx: SlashContext, search_word: str) -> None:
        """Provide a short definition of the word passed by User."""
        request_url = f"https://dictionaryapi.com/api/v3/references/collegiate/json/{search_word}?key={DICTIONARY_KEY}"
        async with aiohttp.ClientSession() as session, session.get(request_url) as response:
            try:
                short_def = "\n"
                text_content = await response.text()
                json_content = json.loads(text_content)
                for num, short_defs in enumerate(json_content[0]["shortdef"], start=1):
                    short_def += f"{num} : {short_defs}\n"
            except TypeError as e:
                print(f"Could not find short definition of {search_word} : Exception {e}")
                short_def = "We could not find the meaning of this word in the dictionary"
                if json_content:
                    short_def += "\nDid you mean any of these ? "
                    short_def += ", ".join(json_content)
            await ctx.send(f"{search_word} : {short_def}")
