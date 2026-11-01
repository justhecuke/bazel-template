#include "cc/rust_calculator.hh"

#include <cassert>
#include <iostream>
#include <stdexcept>

void test_basic_operations() {
    assert(rust_interop::evaluate_expression("2 + 2") == 4.0);
    assert(rust_interop::evaluate_expression("5 - 3") == 2.0);
    assert(rust_interop::evaluate_expression("4 * 3") == 12.0);
    assert(rust_interop::evaluate_expression("10 / 2") == 5.0);
}

void test_operator_precedence() {
    assert(rust_interop::evaluate_expression("2 + 3 * 4") == 14.0);
    assert(rust_interop::evaluate_expression("(2 + 3) * 4") == 20.0);
}

void test_power_operations() {
    assert(rust_interop::evaluate_expression("2 ** 3") == 8.0);
    assert(rust_interop::evaluate_expression("2 ^ 3") == 8.0);
}

void test_unary_operations() {
    assert(rust_interop::evaluate_expression("-5 + 3") == -2.0);
    assert(rust_interop::evaluate_expression("-(3 * 2)") == -6.0);
}

void test_division_by_zero() {
    bool caught = false;
    try {
        rust_interop::evaluate_expression("10 / 0");
    } catch (const std::runtime_error& e) {
        caught = true;
        assert(std::string_view(e.what()) == "division by zero");
    }
    assert(caught);
}

void test_invalid_syntax() {
    bool caught = false;
    try {
        rust_interop::evaluate_expression("2 + * 3");
    } catch (const std::runtime_error&) {
        caught = true;
    }
    assert(caught);
}

void test_direct_helpers() {
    assert(rust_interop::add(15, 27) == 42);
    assert(rust_interop::pow(2.0, 10.0) == 1024.0);
    assert(rust_interop::version() == "1.0.0-rust");
}

int main() {
    test_basic_operations();
    test_operator_precedence();
    test_power_operations();
    test_unary_operations();
    test_division_by_zero();
    test_invalid_syntax();
    test_direct_helpers();

    std::cout << "All C++ calling Rust interop tests passed successfully!" << std::endl;
    return 0;
}
