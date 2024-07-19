from interactions import Client, Intents, SlashContext, listen, slash_command

bot = Client(intents=Intents.DEFAULT)
# intents are what events we want to receive from discord, `DEFAULT` is usually fine


@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready() -> None:
    """Doc string here."""
    # This event is called when the bot is ready to respond to commands
    print("Ready")
    print(f"This bot is owned by {bot.owner}")


@listen()
async def on_message_create(event) -> None:  # noqa: ANN001
    """Doc string here."""
    # This event is called when a message is sent in a channel the bot can see
    print(f"message received: {event.message.jump_url}")


@slash_command(name="hello", description="Hello world")
async def hello_function(ctx: SlashContext) -> None:
    """Doc string here."""
    await ctx.defer()
    await ctx.send("Hello world")


bot.start("Your token goes here")
