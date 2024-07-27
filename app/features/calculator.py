"""Module providing functions to evaluate mathematical expressions.

It supports various mathematical operations, functions, and constants,
allowing for complex calculations to be performed on user-provided expressions.

This module also includes a Calculator extension for a Discord bot,
enabling users to perform calculations directly within Discord.
"""

import ast
import decimal
import math
import operator
import re
from fractions import Fraction

import interactions


class CalculationError(Exception):
    """Custom exception for calculation errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class UnexpectedCalculationError(Exception):
    """Custom exception for unexpected calculation errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


def calculate_root(base: float, exponent: float = 2) -> float:
    """Calculate the nth root of a number.

    Args:
    ----
        base: The number to find the root of.
        exponent: The root exponent. Defaults to 2 (square root).

    Returns:
    -------
        The calculated root.

    """
    return base ** (1 / exponent)


def calculate_exponential(value: float, base: float = math.e) -> float:
    """Calculate the exponential of a value with a given base.

    Args:
    ----
        value: The exponent.
        base: The base. Defaults to e.

    Returns:
    -------
        The calculated exponential.

    """
    return base**value


def calculate_logarithm(value: float, base: float = math.e) -> float:
    """Calculate the logarithm of a value with a given base.

    Args:
    ----
        value: The value to calculate the logarithm of.
        base: The logarithm base. Defaults to e (natural log).

    Returns:
    -------
        The calculated logarithm.

    """
    return math.log(value) if base == math.e else math.log(value, base)


def calculate_secant(angle: float) -> float:
    """Calculate the secant of an angle.

    Args:
    ----
        angle: The angle in radians.

    Returns:
    -------
        The secant of the angle.

    """
    return 1 / math.cos(angle)


def calculate_cosecant(angle: float) -> float:
    """Calculate the cosecant of an angle.

    Args:
    ----
        angle: The angle in radians.

    Returns:
    -------
        The cosecant of the angle.

    """
    return 1 / math.sin(angle)


def calculate_cotangent(angle: float) -> float:
    """Calculate the cotangent of an angle.

    Args:
    ----
        angle: The angle in radians.

    Returns:
    -------
        The cotangent of the angle.

    """
    return 1 / math.tan(angle)


def calculate_factorial(number: int) -> int:
    """Calculate the factorial of a number.

    Args:
    ----
        number: The number to calculate the factorial of.

    Returns:
    -------
        The factorial of the number.

    Raises:
    ------
        CalculationError: If the number is not a non-negative integer.

    """
    if not isinstance(number, int) or number < 0:
        error_message = "Factorial is only defined for non-negative integers."
        raise CalculationError(error_message)
    return math.factorial(number)


ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

ALLOWED_FUNCTIONS = {
    "sqrt": math.sqrt,
    "root": calculate_root,
    "ln": math.log,
    "log": calculate_logarithm,
    "exp": calculate_exponential,
    "fact": calculate_factorial,
    "factorial": calculate_factorial,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "asinh": math.asinh,
    "acosh": math.acosh,
    "atanh": math.atanh,
    "sec": calculate_secant,
    "csc": calculate_cosecant,
    "cot": calculate_cotangent,
    "radians": math.radians,
    "degrees": math.degrees,
    "abs": abs,
    "round": round,
    "ceil": math.ceil,
    "floor": math.floor,
}

ALLOWED_CONSTANTS = {
    "PI": math.pi,
    "pi": math.pi,
    "E": math.e,
    "e": math.e,
}

TOLERANCE = 1e-10


def preprocess_expression(expression: str) -> str:
    """Preprocess the mathematical expression to handle various input formats.

    Args:
    ----
        expression: The input mathematical expression.

    Returns:
    -------
        The preprocessed expression.

    """
    expression = expression.replace("^", "**").replace(" ", "")
    expression = re.sub(r"fact\(", "factorial(", expression)
    expression = re.sub(r"(\d+)!", r"factorial(\1)", expression)
    expression = re.sub(r"(\d)(\()", r"\1*\2", expression)
    expression = re.sub(r"(\))(\d)", r"\1*\2", expression)
    expression = re.sub(r"rad\(", "radians(", expression)
    expression = re.sub(r"deg\(", "degrees(", expression)
    constant_pattern = r"|".join(re.escape(const) for const in ALLOWED_CONSTANTS)
    expression = re.sub(rf"(\d)({constant_pattern})", r"\1*\2", expression)
    expression = re.sub(rf"({constant_pattern})(\d)", r"\1*\2", expression)
    expression = re.sub(rf"(\))({constant_pattern})", r"\1*\2", expression)
    return re.sub(rf"({constant_pattern})(\()", r"\1*\2", expression)


def check_for_complex_numbers(expression: str) -> None:
    """Check if the expression contains complex numbers.

    Args:
    ----
        expression: The input mathematical expression.

    Raises:
    ------
        CalculationError: If the expression contains complex numbers.

    """
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        error_message = "Syntax error in expression."
        raise CalculationError(error_message) from e

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, complex):
            error_message = "Complex numbers are not supported."
            raise CalculationError(error_message)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            left = node.left
            right = node.right
            if (isinstance(left, ast.Constant) and isinstance(left.value, complex)) or (
                isinstance(right, ast.Constant) and isinstance(right.value, complex)
            ):
                error_message = "Complex numbers are not supported."
                raise CalculationError(error_message)


def evaluate_expression(expression: str) -> float:
    """Evaluate a mathematical expression.

    Args:
    ----
        expression: The mathematical expression to evaluate.

    Returns:
    -------
        The result of the evaluation.

    Raises:
    ------
        CalculationError: If there's an error during the evaluation.

    """
    try:
        preprocessed_expression = preprocess_expression(expression)
        check_for_complex_numbers(preprocessed_expression)
        node = ast.parse(preprocessed_expression, mode="eval").body
        return smart_round(evaluate_node(node))
    except ZeroDivisionError:
        error_message = "Error: Division by zero."
        raise CalculationError(error_message) from None
    except CalculationError:
        raise
    except Exception as error:
        error_message = f"Syntax error: {error}"
        raise CalculationError(error_message) from error


def radians_to_pi_symbolic(angle: float) -> str:
    """Convert a radian value to a symbolic representation in terms of pi."""
    pi_fraction = Fraction(angle / math.pi).limit_denominator()
    numerator, denominator = pi_fraction.numerator, pi_fraction.denominator

    if numerator == 0:
        return "0"
    if denominator == 1:
        return f"{numerator}π"
    return f"{numerator}π/{denominator}"


def count_decimal_places(number: float) -> int:
    """Count the number of decimal places in a float."""
    decimal_number = decimal.Decimal(str(number))
    return max(0, -decimal_number.as_tuple().exponent)


def adjust_precision_for_multiplication(result: float, operands: list[float]) -> float:
    """Adjust the precision of the result based on the operands for multiplication."""
    total_decimal_places = sum(count_decimal_places(op) for op in operands)
    return round(result, total_decimal_places)


def smart_round(value: float, decimals: int = 10) -> float:
    """Intelligently rounds a float to an integer if close enough, otherwise to 'decimals' places."""
    if abs(round(value) - value) < TOLERANCE:
        return round(value)
    rounded = round(value, decimals)
    return int(rounded) if rounded.is_integer() else rounded


def evaluate_binary_operation(node: ast.BinOp) -> float:
    """Evaluate binary operations in the AST.

    Args:
    ----
        node: The binary operation node.

    Returns:
    -------
        The result of the binary operation.

    Raises:
    ------
        CalculationError: If the operator is not allowed.

    """
    left = evaluate_node(node.left)
    right = evaluate_node(node.right)
    operator_type = type(node.op)
    if operator_type in ALLOWED_OPERATORS:
        result = ALLOWED_OPERATORS[operator_type](left, right)
        if operator_type == ast.Mult:
            return adjust_precision_for_multiplication(result, [left, right])
        return result
    error_message = "Operator not allowed."
    raise CalculationError(error_message)


def evaluate_unary_operation(node: ast.UnaryOp) -> float:
    """Evaluate unary operations in the AST.

    Args:
    ----
        node: The unary operation node.

    Returns:
    -------
        The result of the unary operation.

    Raises:
    ------
        CalculationError: If the operator is not allowed.

    """
    operand = evaluate_node(node.operand)
    operator_type = type(node.op)
    if operator_type in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[operator_type](operand)
    error_message = "Operator not allowed."
    raise CalculationError(error_message)


def evaluate_function_call(node: ast.Call) -> float:
    """Evaluate function calls in the AST.

    Args:
    ----
        node: The function call node.

    Returns:
    -------
        The result of the function call.

    Raises:
    ------
        CalculationError: If the function is not allowed.

    """
    function_name = node.func.id
    if function_name in ALLOWED_FUNCTIONS:
        args = [evaluate_node(arg) for arg in node.args]
        return ALLOWED_FUNCTIONS[function_name](*args)
    error_message = f"Function not allowed or syntax error: {function_name}"
    raise CalculationError(error_message)


def evaluate_node(node: ast.BinOp | ast.UnaryOp | ast.Constant | ast.Name | ast.Call | ast.Expression) -> float:
    """Recursively evaluate an AST node.

    Args:
    ----
        node: The AST node to evaluate.

    Returns:
    -------
        The result of the node evaluation.

    Raises:
    ------
        CalculationError: If the node type is not supported.

    """
    if isinstance(node, ast.BinOp):
        result = evaluate_binary_operation(node)
    elif isinstance(node, ast.UnaryOp):
        result = evaluate_unary_operation(node)
    elif isinstance(node, ast.Constant):
        result = node.value
    elif isinstance(node, ast.Name):
        if node.id in ALLOWED_CONSTANTS:
            result = ALLOWED_CONSTANTS[node.id]
        else:
            error_message = f"Constant not allowed or syntax error: {node.id}"
            raise CalculationError(error_message)
    elif isinstance(node, ast.Call):
        result = evaluate_function_call(node)
    elif isinstance(node, ast.Expression):
        result = evaluate_node(node.body)
    else:
        error_message = "Unsupported node type"
        raise CalculationError(error_message)
    return result


class Calculator(interactions.Extension):
    """Calculator extension."""

    def __init__(self, bot: interactions.Client) -> None:
        self.bot = bot
        print("Calculator extension loaded")

    @interactions.slash_command(
        name="calculate",
        description="Calculate a mathematical expression",
        options=[
            interactions.SlashCommandOption(
                name="expression",
                description="The mathematical expression to calculate",
                required=True,
                type=interactions.OptionType.STRING,
            ),
        ],
    )
    async def calculate_expression(
        self,
        ctx: interactions.SlashContext,
        expression: str,
    ) -> None:
        """Calculate the given mathematical expression."""
        try:
            result = evaluate_expression(expression)
            await ctx.send(f"The result of `{expression}` is: {result}")
        except CalculationError as calc_error:
            await ctx.send(f"Calculation error: {calc_error}", ephemeral=True)
        except (ValueError, TypeError) as specific_error:
            await ctx.send(f"An error occurred: {specific_error}", ephemeral=True)
        except UnexpectedCalculationError as unexpected_error:
            await ctx.send(f"An unexpected error occurred: {unexpected_error}", ephemeral=True)

    @interactions.slash_command(name="calc", description="Calculator functions")
    async def calc(self, ctx: interactions.SlashContext) -> None:
        """Provide base command for calculator functions."""

    @calc.subcommand(sub_cmd_name="sqrt", sub_cmd_description="Calculate the square root")
    @interactions.slash_option(
        name="x",
        description="Number to calculate the square root of",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    async def calc_sqrt(self, ctx: interactions.SlashContext, x: str) -> None:
        """Calculate the square root of a number."""
        try:
            expression = f"sqrt({x})"
            result = evaluate_expression(expression)
            await ctx.send(f"The square root of {x} is: {result}")
        except (CalculationError, ValueError, TypeError) as e:
            await ctx.send(f"An error occurred: {e!s}", ephemeral=True)

    @calc.subcommand(sub_cmd_name="root", sub_cmd_description="Calculate the nth root of a number")
    @interactions.slash_option(
        name="x",
        description="The number to find the root of",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    @interactions.slash_option(
        name="n",
        description="The root exponent",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    async def calc_root(self, ctx: interactions.SlashContext, x: str, n: str) -> None:
        """Calculate the nth root of a number."""
        try:
            expression = f"root({x},{n})"
            result = evaluate_expression(expression)
            await ctx.send(f"The {n}th root of {x} is: {result}")
        except (CalculationError, ValueError, TypeError) as e:
            await ctx.send(f"An error occurred: {e!s}", ephemeral=True)

    @calc.subcommand(sub_cmd_name="ln", sub_cmd_description="Calculate the natural logarithm")
    @interactions.slash_option(
        name="x",
        description="The number to calculate the natural logarithm of",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    async def calc_ln(self, ctx: interactions.SlashContext, x: str) -> None:
        """Calculate the natural logarithm of a number."""
        try:
            expression = f"ln({x})"
            result = evaluate_expression(expression)
            await ctx.send(f"The natural logarithm of {x} is: {result}")
        except (CalculationError, ValueError, TypeError) as e:
            await ctx.send(f"An error occurred: {e!s}", ephemeral=True)

    @calc.subcommand(sub_cmd_name="log", sub_cmd_description="Calculate the logarithm with a specified base")
    @interactions.slash_option(
        name="x",
        description="The number to calculate the logarithm of",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    @interactions.slash_option(
        name="base",
        description="The base of the logarithm",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    async def calc_log(self, ctx: interactions.SlashContext, x: str, base: str) -> None:
        """Calculate the logarithm of a number with a specified base."""
        try:
            expression = f"log({x},{base})"
            result = evaluate_expression(expression)
            await ctx.send(f"The logarithm of {x} with base {base} is: {result}")
        except (CalculationError, ValueError, TypeError) as e:
            await ctx.send(f"An error occurred: {e!s}", ephemeral=True)

    @calc.subcommand(sub_cmd_name="exp", sub_cmd_description="Calculate the exponential of a number")
    @interactions.slash_option(
        name="x",
        description="The exponent",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    async def calc_exp(self, ctx: interactions.SlashContext, x: str) -> None:
        """Calculate the exponential of a number."""
        try:
            expression = f"exp({x})"
            result = evaluate_expression(expression)
            await ctx.send(f"e^{x} = {result}")
        except (CalculationError, ValueError, TypeError) as e:
            await ctx.send(f"An error occurred: {e!s}", ephemeral=True)

    @calc.subcommand(sub_cmd_name="fact", sub_cmd_description="Calculate the factorial of a number")
    @interactions.slash_option(
        name="x",
        description="The number to calculate factorial",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    async def calc_fact(self, ctx: interactions.SlashContext, x: str) -> None:
        """Calculate the factorial of a number."""
        try:
            expression = f"factorial({x})"
            result = evaluate_expression(expression)
            await ctx.send(f"{x}! = {result}")
        except (CalculationError, ValueError, TypeError) as e:
            await ctx.send(f"An error occurred: {e!s}", ephemeral=True)

    @calc.subcommand(sub_cmd_name="rad", sub_cmd_description="Convert a degree value into radians")
    @interactions.slash_option(
        name="x",
        description="Angle in degree",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    async def calc_rad(self, ctx: interactions.SlashContext, x: str) -> None:
        """Convert a degree value into radians."""
        try:
            expression = f"radians({x})"
            result = evaluate_expression(expression)
            result_pi = radians_to_pi_symbolic(result)
            await ctx.send(f"{x}° in radians:\nDecimal: {result:.6f}\nIn terms of π: {result_pi}")
        except (CalculationError, ValueError, TypeError) as e:
            await ctx.send(f"An error occurred: {e!s}", ephemeral=True)

    @calc.subcommand(sub_cmd_name="deg", sub_cmd_description="Convert a radians value into degrees")
    @interactions.slash_option(
        name="x",
        description="Angle in radians",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    async def calc_deg(self, ctx: interactions.SlashContext, x: str) -> None:
        """Convert a radians value into degrees."""
        try:
            expression = f"degrees({x})"
            result = evaluate_expression(expression)
            await ctx.send(f"{x} in degrees: {result}")
        except (CalculationError, ValueError, TypeError) as e:
            await ctx.send(f"An error occurred: {e!s}", ephemeral=True)

    @interactions.slash_command(name="calc_trig", description="Trigonometric functions")
    async def calc_trig(self, ctx: interactions.SlashContext) -> None:
        """Provide base command for trigonometric functions."""

    @calc_trig.subcommand(sub_cmd_name="basic", sub_cmd_description="Basic trigonometric functions")
    @interactions.slash_option(
        name="function",
        description="Choose the trigonometric function",
        required=True,
        opt_type=interactions.OptionType.STRING,
        choices=[
            {"name": "sin", "value": "sin"},
            {"name": "cos", "value": "cos"},
            {"name": "tan", "value": "tan"},
        ],
    )
    @interactions.slash_option(
        name="angle",
        description="Angle in radians",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    async def trig_basic(self, ctx: interactions.SlashContext, function: str, angle: str) -> None:
        """Calculate basic trigonometric functions."""
        try:
            expression = f"{function}({angle})"
            result = evaluate_expression(expression)
            await ctx.send(f"The {function} of {angle} radians is: {result}")
        except (CalculationError, ValueError, TypeError) as e:
            await ctx.send(f"An error occurred: {e!s}", ephemeral=True)

    @calc_trig.subcommand(sub_cmd_name="hyperbolic", sub_cmd_description="Hyperbolic trigonometric functions")
    @interactions.slash_option(
        name="function",
        description="Choose the hyperbolic trigonometric function",
        required=True,
        opt_type=interactions.OptionType.STRING,
        choices=[
            {"name": "sinh", "value": "sinh"},
            {"name": "cosh", "value": "cosh"},
            {"name": "tanh", "value": "tanh"},
        ],
    )
    @interactions.slash_option(
        name="value",
        description="Input value",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    async def trig_hyperbolic(self, ctx: interactions.SlashContext, function: str, value: str) -> None:
        """Calculate hyperbolic trigonometric functions."""
        try:
            expression = f"{function}({value})"
            result = evaluate_expression(expression)
            await ctx.send(f"The {function} of {value} is: {result}")
        except (CalculationError, ValueError, TypeError) as e:
            await ctx.send(f"An error occurred: {e!s}", ephemeral=True)

    @calc_trig.subcommand(sub_cmd_name="inverse", sub_cmd_description="Inverse trigonometric functions")
    @interactions.slash_option(
        name="function",
        description="Choose the inverse of basic and hyperbolic trigonometric function",
        required=True,
        opt_type=interactions.OptionType.STRING,
        choices=[
            {"name": "asin", "value": "asin"},
            {"name": "acos", "value": "acos"},
            {"name": "atan", "value": "atan"},
            {"name": "asinh", "value": "asinh"},
            {"name": "acosh", "value": "acosh"},
            {"name": "atanh", "value": "atanh"},
        ],
    )
    @interactions.slash_option(
        name="value",
        description="Input value",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    async def trig_inverse(self, ctx: interactions.SlashContext, function: str, value: str) -> None:
        """Calculate inverse trigonometric functions."""
        try:
            expression = f"{function}({value})"
            result = evaluate_expression(expression)
            await ctx.send(f"The {function} of {value} is: {result} radians")
        except (CalculationError, ValueError, TypeError) as e:
            await ctx.send(f"An error occurred: {e!s}", ephemeral=True)

    @calc_trig.subcommand(sub_cmd_name="other", sub_cmd_description="Other trigonometric functions")
    @interactions.slash_option(
        name="function",
        description="Choose the trigonometric function",
        required=True,
        opt_type=interactions.OptionType.STRING,
        choices=[
            {"name": "sec", "value": "sec"},
            {"name": "csc", "value": "csc"},
            {"name": "cot", "value": "cot"},
        ],
    )
    @interactions.slash_option(
        name="angle",
        description="Angle in radians",
        required=True,
        opt_type=interactions.OptionType.STRING,
    )
    async def trig_other(self, ctx: interactions.SlashContext, function: str, angle: str) -> None:
        """Calculate other trigonometric functions."""
        try:
            expression = f"{function}({angle})"
            result = evaluate_expression(expression)
            await ctx.send(f"The {function} of {angle} radians is: {result}")
        except (CalculationError, ValueError, TypeError) as e:
            await ctx.send(f"An error occurred: {e!s}", ephemeral=True)

    @interactions.slash_command(
        name="calc_info",
        description="Get information about the calculator",
    )
    async def calculate_info(self, ctx: interactions.SlashContext) -> None:
        """Provide information about allowed functions, constants, and operators."""
        functions_info = [
            "`sqrt(x)` - square root of x",
            "`root(x, n)` - nth root of x",
            "`ln(x)` - natural logarithm of x",
            "`log(x, base)` - logarithm of x with given base (default is e)",
            "`exp(x)` or `e^x` - exponential of x",
            "`factorial(x)` or `fact(x)` or `x!` - factorial of x",
            "`sin(x)`, `cos(x)`, `tan(x)` - trigonometric functions",
            "`asin(x)`, `acos(x)`, `atan(x)` - inverse trigonometric functions",
            "`sinh(x)`, `cosh(x)`, `tanh(x)` - hyperbolic functions",
            "`asinh(x)`, `acosh(x)`, `atanh(x)` - inverse hyperbolic functions",
            "`sec(x)` - secant of x",
            "`csc(x)` - cosecant of x",
            "`cot(x)` - cotangent of x",
            "`radians(x)` or `rad(x)` - convert a degree value into radians",
            "`abs(x)` - absolute value of x",
            "`round(x)` - round x to the nearest integer",
            "`ceil(x)` - ceiling of x",
            "`floor(x)` - floor of x",
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

        embed = interactions.Embed(
            title="Calculator Information",
            description="Here is the list of allowed functions, constants, and operators for the calculator.",
            color=0x1E1F22,
        )

        embed.add_field(name="Allowed Functions", value="\n".join(functions_info), inline=False)
        embed.add_field(name="Allowed Constants", value=constants_list, inline=False)
        embed.add_field(name="Allowed Operators", value="\n".join(operators_info), inline=False)
        embed.set_footer(
            text="Note: \n- Complex numbers are not supported and angle unit is radians."
            "\n- Use points for decimals; commas are not supported"
            "\n- Use radians unit for angles (or use rad() function to convert degrees angle)",
        )

        await ctx.send(embeds=[embed], ephemeral=True)

    @interactions.slash_command(name="calc_help", description="Get a list of available calculator commands")
    async def calc_help(self, ctx: interactions.SlashContext) -> None:
        """Provide a list of available calculator commands."""
        commands_info = [
            "`/calc_help` - Get a list of available calculator commands",
            "`/calc_info` - Get information about the calculator",
            "`/calculator` - Open the interactive calculator",
        ]

        commands_calc = [
            "`/calculate expression [expression]` - Calculate a mathematical expression",
            "`/calc sqrt [x]` - Calculate the square root of x",
            "`/calc root [x] [n]` - Calculate the nth root of x",
            "`/calc ln [x]` - Calculate the natural logarithm of x",
            "`/calc log [x] [base]` - Calculate the logarithm of x with a specified base",
            "`/calc exp [x]` - Calculate the exponential of x",
            "`/calc fact [x]` - Calculate the factorial of x",
            "`/calc rad [x] - Convert a degree value into radians",
            "`/calc deg [x] - Convert a radians value into degree",
            "`/calc_trig basic [function] [angle]` - Calculate basic trigonometric functions",
            "`/calc_trig inverse [function] [value]` - Calculate inverse of basic and hyperbolic "
            "trigonometric functions",
            "`/calc_trig hyperbolic [function] [value]` - Calculate hyperbolic trigonometric functions",
            "`/calc_trig other [function] [angle]` - Calculate other trigonometric functions",
        ]

        embed = interactions.Embed(
            title="Calculator Commands",
            description="Here is the list of available calculator commands.",
            color=0x1E1F22,
        )

        embed.add_field(name="Info commands", value="\n".join(commands_info), inline=False)
        embed.add_field(name="Calculate commands", value="\n".join(commands_calc), inline=False)

        await ctx.send(embeds=[embed], ephemeral=True)


def setup(bot: interactions.Client) -> None:
    """Set up the Calculator extension."""
    Calculator(bot)
