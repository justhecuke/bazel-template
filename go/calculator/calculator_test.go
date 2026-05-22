package main

import (
	"math"
	"testing"
)

func TestBasicOperations(t *testing.T) {
	tests := []struct {
		expr     string
		expected float64
	}{
		{"2 + 2", 4.0},
		{"5 - 3", 2.0},
		{"4 * 3", 12.0},
		{"10 / 2", 5.0},
	}

	for _, tc := range tests {
		res, err := EvaluateExpression(tc.expr)
		if err != nil {
			t.Errorf("EvaluateExpression(%q) failed: %v", tc.expr, err)
			continue
		}
		if res != tc.expected {
			t.Errorf("EvaluateExpression(%q) = %f; want %f", tc.expr, res, tc.expected)
		}
	}
}

func TestOperatorPrecedence(t *testing.T) {
	tests := []struct {
		expr     string
		expected float64
	}{
		{"2 + 3 * 4", 14.0},
		{"(2 + 3) * 4", 20.0},
	}

	for _, tc := range tests {
		res, err := EvaluateExpression(tc.expr)
		if err != nil {
			t.Errorf("EvaluateExpression(%q) failed: %v", tc.expr, err)
			continue
		}
		if res != tc.expected {
			t.Errorf("EvaluateExpression(%q) = %f; want %f", tc.expr, res, tc.expected)
		}
	}
}

func TestPowerOperations(t *testing.T) {
	// In our Go parser, ^ is token.XOR which evaluates left ^ right as math.Pow(left, right)
	res, err := EvaluateExpression("2 ^ 3")
	if err != nil {
		t.Fatalf("EvaluateExpression(\"2 ^ 3\") failed: %v", err)
	}
	if res != 8.0 {
		t.Errorf("EvaluateExpression(\"2 ^ 3\") = %f; want 8.0", res)
	}
}

func TestUnaryOperations(t *testing.T) {
	tests := []struct {
		expr     string
		expected float64
	}{
		{"-5 + 3", -2.0},
		{"-(3 * 2)", -6.0},
	}

	for _, tc := range tests {
		res, err := EvaluateExpression(tc.expr)
		if err != nil {
			t.Errorf("EvaluateExpression(%q) failed: %v", tc.expr, err)
			continue
		}
		if res != tc.expected {
			t.Errorf("EvaluateExpression(%q) = %f; want %f", tc.expr, res, tc.expected)
		}
	}
}

func TestDivisionByZero(t *testing.T) {
	_, err := EvaluateExpression("10 / 0")
	if err == nil {
		t.Error("Expected error for division by zero, got nil")
	}
}

func TestInvalidSyntax(t *testing.T) {
	_, err := EvaluateExpression("2 + * 3")
	if err == nil {
		t.Error("Expected error for invalid syntax, got nil")
	}
}

func TestUnsupportedOperations(t *testing.T) {
	_, err := EvaluateExpression("import os")
	if err == nil {
		t.Error("Expected error for unsupported operations, got nil")
	}
}

func TestFloatParsing(t *testing.T) {
	res, err := EvaluateExpression("2.5 * 4")
	if err != nil {
		t.Fatalf("EvaluateExpression(\"2.5 * 4\") failed: %v", err)
	}
	if math.Abs(res-10.0) > 1e-9 {
		t.Errorf("EvaluateExpression(\"2.5 * 4\") = %f; want 10.0", res)
	}
}
