package main

import (
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"math"
	"strconv"
)

// EvaluateExpression safely evaluates a mathematical string expression using Go's AST.
// Supported operators: +, -, *, /, ^ (power)
func EvaluateExpression(expr string) (float64, error) {
	node, err := parser.ParseExpr(expr)
	if err != nil {
		return 0, fmt.Errorf("invalid expression: %w", err)
	}
	return eval(node)
}

func eval(expr ast.Expr) (float64, error) {
	switch n := expr.(type) {
	case *ast.BasicLit:
		if n.Kind == token.INT || n.Kind == token.FLOAT {
			val, err := strconv.ParseFloat(n.Value, 64)
			if err != nil {
				return 0, fmt.Errorf("invalid number '%s': %w", n.Value, err)
			}
			return val, nil
		}
		return 0, fmt.Errorf("unsupported basic literal kind: %v", n.Kind)

	case *ast.BinaryExpr:
		left, err := eval(n.X)
		if err != nil {
			return 0, err
		}
		right, err := eval(n.Y)
		if err != nil {
			return 0, err
		}
		switch n.Op {
		case token.ADD:
			return left + right, nil
		case token.SUB:
			return left - right, nil
		case token.MUL:
			return left * right, nil
		case token.QUO:
			if right == 0 {
				return 0, fmt.Errorf("division by zero")
			}
			return left / right, nil
		case token.XOR: // Treat ^ as power, mirroring Python's bitwise XOR replacement
			return math.Pow(left, right), nil
		default:
			return 0, fmt.Errorf("unsupported binary operator: %s", n.Op)
		}

	case *ast.UnaryExpr:
		val, err := eval(n.X)
		if err != nil {
			return 0, err
		}
		switch n.Op {
		case token.SUB:
			return -val, nil
		case token.ADD:
			return val, nil
		default:
			return 0, fmt.Errorf("unsupported unary operator: %s", n.Op)
		}

	case *ast.ParenExpr:
		return eval(n.X)

	default:
		return 0, fmt.Errorf("unsupported syntax: %T", expr)
	}
}
