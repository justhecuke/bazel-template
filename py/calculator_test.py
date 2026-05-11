import unittest
from py.calculator import evaluate_expression

class TestCalculator(unittest.TestCase):
    def test_basic_operations(self):
        self.assertEqual(evaluate_expression("2 + 2"), 4.0)
        self.assertEqual(evaluate_expression("5 - 3"), 2.0)
        self.assertEqual(evaluate_expression("4 * 3"), 12.0)
        self.assertEqual(evaluate_expression("10 / 2"), 5.0)

    def test_operator_precedence(self):
        self.assertEqual(evaluate_expression("2 + 3 * 4"), 14.0)
        self.assertEqual(evaluate_expression("(2 + 3) * 4"), 20.0)

    def test_power_operations(self):
        self.assertEqual(evaluate_expression("2 ** 3"), 8.0)
        self.assertEqual(evaluate_expression("2 ^ 3"), 8.0)

    def test_unary_operations(self):
        self.assertEqual(evaluate_expression("-5 + 3"), -2.0)
        self.assertEqual(evaluate_expression("-(3 * 2)"), -6.0)

    def test_invalid_syntax(self):
        with self.assertRaises(ValueError):
            evaluate_expression("2 + * 3")
            
    def test_unsupported_operations(self):
        with self.assertRaises(ValueError):
            evaluate_expression("import os")

if __name__ == '__main__':
    unittest.main()
