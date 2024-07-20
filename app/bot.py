from features.calculator import ALLOWED_CONSTANTS, CalculationError, evaluate_expression
from interactions import Client, Intents, OptionType, SlashCommandOption, SlashContext, listen, slash_command

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


@slash_command(
    name="calculate",
    description="Calculate a mathematical expression",
    options=[
        SlashCommandOption(
            name="expression",
            description="The mathematical expression to calculate",
            type=OptionType.STRING,
            required=True,
        ),
    ],
)
async def calculate_function(ctx: SlashContext, expression: str) -> None:
    """Calculate the given mathematical expression.

    This function takes a string expression, evaluates it, and returns the result.
    It handles potential calculation errors and unexpected exceptions.

    Args:
    ----
        ctx (SlashContext): The context of the slash command.
        expression (str): The mathematical expression to evaluate.

    """
    await ctx.defer()

    expression_without_spaces = expression.replace(" ", "")

    try:
        result = evaluate_expression(expression_without_spaces)
        await ctx.send(f"The result of `{expression}` is: {result}", ephemeral=True)
    except CalculationError as calc_error:
        await ctx.send(f"Calculation error: {calc_error}", ephemeral=True)
    except Exception as unexpected_error:  # noqa: BLE001
        await ctx.send(f"An unexpected error occurred: {unexpected_error}", ephemeral=True)


@slash_command(
    name="calculate_info",
    description="Get the list of allowed functions, constants, and operators",
)
async def info_function(ctx: SlashContext) -> None:
    """Provide information about allowed functions, constants, and operators."""
    functions_info = [
        "`root(x, n)` - nth root of x",
        "`log(x, base)` - logarithm of x with given base (default is e)",
        "`ln(x)` - natural logarithm of x",
        "`exp(x)` or `e^x` - exponential of x",
        "`sin(x)`, `cos(x)`, `tan(x)` - trigonometric functions",
        "`asin(x)`, `acos(x)`, `atan(x)` - inverse trigonometric functions",
        "`sinh(x)`, `cosh(x)`, `tanh(x)` - hyperbolic functions",
        "`asinh(x)`, `acosh(x)`, `atanh(x)` - inverse hyperbolic functions",
        "`abs(x)` - absolute value of x",
        "`factorial(x)` or `fact(x)` or `x!` - factorial of x",
        "`round(x)` - round x to the nearest integer",
        "`ceil(x)` - ceiling of x",
        "`floor(x)` - floor of x",
        "`sec(x)` - secant of x",
        "`csc(x)` - cosecant of x",
        "`cot(x)` - cotangent of x",
        "`sqrt(x)` - square root of x",
    ]

    constants_list = ", ".join(f"`{const}`" for const in ALLOWED_CONSTANTS)

    operators_info = [
        "`+` (addition)",
        "`-` (subtraction)",
        "`*` (multiplication)",
        "`/` (division)",
        "`**` or `^` (exponentiation)",
        "`%` (modulo)",
        "`//` (floor division)",
    ]

    info_message = (
        "**Allowed Functions:**\n"
        + "\n".join(functions_info)
        + "\n\n**Allowed Constants:**\n"
        + constants_list
        + "\n\n**Allowed Operators:**\n"
        + "\n".join(operators_info)
        + "\n\n**Note:** Complex numbers are not supported.\n\n"
    )

    await ctx.send(info_message, ephemeral=True)


bot.start("Your token goes here")
