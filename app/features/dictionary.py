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
        async with aiohttp.ClientSession() as session, session.get(request_url) as dict_response:
            json_content = dict_response.json()
            short_def = "".join(json_content[0]["shortdef"])
            await ctx.send(f"{search_word} : {short_def}")
