#include "cc/calculator.hh"

#include <cassert>
#include <cmath>
#include <cstring>
#include <iostream>

void test_basic_operations() {
    assert(calculator::evaluate_expression("2 + 2") == 4.0);
    assert(calculator::evaluate_expression("5 - 3") == 2.0);
    assert(calculator::evaluate_expression("4 * 3") == 12.0);
    assert(calculator::evaluate_expression("10 / 2") == 5.0);
}

void test_operator_precedence() {
    assert(calculator::evaluate_expression("2 + 3 * 4") == 14.0);
    assert(calculator::evaluate_expression("(2 + 3) * 4") == 20.0);
}

void test_power_operations() {
    assert(calculator::evaluate_expression("2 ** 3") == 8.0);
    assert(calculator::evaluate_expression("2 ^ 3") == 8.0);
}

void test_unary_operations() {
    assert(calculator::evaluate_expression("-5 + 3") == -2.0);
    assert(calculator::evaluate_expression("-(3 * 2)") == -6.0);
}

void test_float_parsing() {
    assert(calculator::evaluate_expression("2.5 * 4") == 10.0);
}

void test_ffi_functions() {
    double result = 0.0;
    char err[64] = {0};

    // Successful evaluation
    int32_t status = cc_calculator_eval("3 * (4 + 5)", &result, err, sizeof(err));
    assert(status == 0);
    assert(result == 27.0);
    assert(err[0] == '\0');

    // Division by zero
    status = cc_calculator_eval("8 / 0", &result, err, sizeof(err));
    assert(status == 1);
    assert(std::strcmp(err, "division by zero") == 0);

    // Invalid syntax
    status = cc_calculator_eval("1 ++ 2 *", &result, err, sizeof(err));
    assert(status == 2);
    assert(std::strcmp(err, "invalid syntax") == 0);

    // Empty expression
    status = cc_calculator_eval("   ", &result, err, sizeof(err));
    assert(status == 3);
    assert(std::strcmp(err, "empty expression") == 0);

    // Direct helper functions
    assert(cc_calculator_add(10, 32) == 42);
    assert(cc_calculator_pow(3.0, 3.0) == 27.0);
    assert(std::strcmp(cc_calculator_version(), "1.0.0-cpp") == 0);
}

int main() {
    test_basic_operations();
    test_operator_precedence();
    test_power_operations();
    test_unary_operations();
    test_float_parsing();
    test_ffi_functions();

    std::cout << "All C++ calculator tests passed successfully!" << std::endl;
    return 0;
}
