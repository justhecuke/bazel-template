#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <string_view>

namespace rust_interop {

/// Evaluates a mathematical string expression using the hermetic Rust engine.
/// Supported operators: +, -, *, /, ^, ** and parentheses.
/// Throws std::runtime_error on failure (syntax error, division by zero, etc.).
double evaluate_expression(std::string_view expr);

/// Adds two 32-bit integers via the Rust implementation.
int32_t add(int32_t a, int32_t b);

/// Computes base raised to exponent via the Rust implementation.
double pow(double base, double exp);

/// Returns the version string of the Rust calculator engine.
std::string_view version();

}  // namespace rust_interop
