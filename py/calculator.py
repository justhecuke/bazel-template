import ast
import operator

BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.BitXor: operator.pow,
}

UNARY_OPERATORS = {
    ast.USub: operator.neg,
}


def eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Num):  # for python < 3.8
        val = node.value
        if isinstance(val, (int, float)):
            return float(val)
        raise TypeError(f"Unexpected numeric value type: {type(val)}")
    elif isinstance(node, ast.Constant):
        val = node.value
        if isinstance(val, (int, float)):
            return float(val)
        raise TypeError(f"Unexpected constant value type: {type(val)}")
    elif isinstance(node, ast.BinOp):
        left = eval_node(node.left)
        right = eval_node(node.right)
        op_type = type(node.op)
        if op_type not in BINARY_OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        return float(BINARY_OPERATORS[op_type](left, right))
    elif isinstance(node, ast.UnaryOp):
        operand = eval_node(node.operand)
        op_type = type(node.op)
        if op_type not in UNARY_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        return UNARY_OPERATORS[op_type](operand)
    elif isinstance(node, ast.Expression):
        return eval_node(node.body)
    else:
        raise TypeError(f"Unsupported syntax: {type(node).__name__}")


def evaluate_expression(expr: str) -> float:
    """
    Safely evaluate a mathematical string expression using Python's AST.
    Supported operators: +, -, *, /, ^ (power)
    """
    try:
        parsed_ast = ast.parse(expr, mode="eval")
        return eval_node(parsed_ast)
    except (SyntaxError, TypeError, ValueError) as e:
        raise ValueError(f"Invalid mathematical expression '{expr}': {e}") from e
