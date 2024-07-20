"""Module providing functions to evaluate mathematical expressions.

It supports various mathematical operations, functions, and constants,
allowing for complex calculations to be performed on user-provided expressions.
"""

import ast
import math
import operator
import re


class CalculationError(Exception):
    """Custom exception for calculation errors."""

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
    "root": calculate_root,
    "log": calculate_logarithm,
    "ln": math.log,
    "exp": calculate_exponential,
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
    "abs": abs,
    "factorial": calculate_factorial,
    "fact": calculate_factorial,
    "round": round,
    "ceil": math.ceil,
    "floor": math.floor,
    "sec": calculate_secant,
    "csc": calculate_cosecant,
    "cot": calculate_cotangent,
    "sqrt": math.sqrt,
}

ALLOWED_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}


def preprocess_expression(expression: str) -> str:
    """Preprocess the mathematical expression to handle various input formats.

    Args:
    ----
        expression: The input mathematical expression.

    Returns:
    -------
        The preprocessed expression.

    """
    expression = expression.replace("^", "**")
    expression = re.sub(r"fact\(", "factorial(", expression)
    return re.sub(r"(\d+)!", r"factorial(\1)", expression)


def check_for_complex_numbers(expression: str) -> None:
    """Check if the expression contains complex numbers.

    Args:
    ----
        expression: The input mathematical expression.

    Raises:
    ------
        CalculationError: If the expression contains complex numbers.

    """
    if "j" in expression or "i" in expression:
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
        check_for_complex_numbers(expression)
        preprocessed_expression = preprocess_expression(expression)
        node = ast.parse(preprocessed_expression, mode="eval").body
        return evaluate_node(node)
    except ZeroDivisionError:
        error_message = "Error: Division by zero."
        raise CalculationError(error_message) from None
    except CalculationError:
        raise
    except Exception as error:
        error_message = f"Syntax error: {error}"
        raise CalculationError(error_message) from error


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
        return ALLOWED_OPERATORS[operator_type](left, right)
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
    error_message = f"Function not allowed: {function_name}"
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
        return evaluate_binary_operation(node)
    if isinstance(node, ast.UnaryOp):
        return evaluate_unary_operation(node)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in ALLOWED_CONSTANTS:
            return ALLOWED_CONSTANTS[node.id]
        error_message = f"Constant not allowed: {node.id}"
        raise CalculationError(error_message)
    if isinstance(node, ast.Call):
        return evaluate_function_call(node)
    if isinstance(node, ast.Expression):
        return evaluate_node(node.body)
    error_message = "Unsupported expression type."
    raise CalculationError(error_message)
