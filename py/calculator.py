import ast
import operator

def evaluate_expression(expr: str) -> float:
    """
    Safely evaluate a mathematical string expression using Python's AST.
    Supported operators: +, -, *, /, ^ (power)
    """
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.BitXor: operator.pow,
        ast.USub: operator.neg
    }

    def eval_node(node):
        if isinstance(node, ast.Num): # for python < 3.8
            return node.n
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = eval_node(node.left)
            right = eval_node(node.right)
            if type(node.op) not in operators:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = eval_node(node.operand)
            if type(node.op) not in operators:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            return operators[type(node.op)](operand)
        elif isinstance(node, ast.Expression):
            return eval_node(node.body)
        else:
            raise TypeError(f"Unsupported syntax: {type(node).__name__}")

    try:
        parsed_ast = ast.parse(expr, mode='eval')
        return float(eval_node(parsed_ast))
    except (SyntaxError, TypeError, ValueError) as e:
        raise ValueError(f"Invalid mathematical expression '{expr}': {e}")
