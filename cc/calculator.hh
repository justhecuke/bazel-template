#pragma once

#include <cstddef>
#include <cstdint>

#ifdef __cplusplus
#include <string>
#include <string_view>

namespace calculator {

/// Evaluates a mathematical string expression in C++.
/// Supported operators: +, -, *, /, ^ and ** (power), and parentheses.
/// Throws std::runtime_error on invalid syntax, empty expression, or division by zero.
double evaluate_expression(std::string_view expr);

}  // namespace calculator
#endif

#ifdef __cplusplus
extern "C" {
#endif

/// C-compatible FFI interface for evaluating expressions.
///
/// Returns 0 on success, or a non-zero error code:
///   1: Division by zero
///   2: Invalid syntax
///   3: Empty expression
///   4: Trailing tokens
///   -1: Unexpected internal error or null pointer
///
/// On success, *out_result contains the evaluated double.
/// If err_buf is non-null and err_buf_len > 0, an error description is written.
int32_t cc_calculator_eval(
    const char* expr,
    double* out_result,
    char* err_buf,
    size_t err_buf_len
);

/// Adds two 32-bit integers via C++ implementation.
int32_t cc_calculator_add(int32_t a, int32_t b);

/// Computes base raised to exp via C++ implementation.
double cc_calculator_pow(double base, double exp);

/// Returns the C++ calculator engine version string.
const char* cc_calculator_version(void);

#ifdef __cplusplus
}
#endif
