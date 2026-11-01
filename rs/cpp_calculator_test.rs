use cpp_calculator::{add_cpp, evaluate_expression_cpp, pow_cpp, version_cpp};

#[test]
fn test_cpp_basic_operations() {
    assert_eq!(evaluate_expression_cpp("2 + 2"), Ok(4.0));
    assert_eq!(evaluate_expression_cpp("5 - 3"), Ok(2.0));
    assert_eq!(evaluate_expression_cpp("4 * 3"), Ok(12.0));
    assert_eq!(evaluate_expression_cpp("10 / 2"), Ok(5.0));
}

#[test]
fn test_cpp_operator_precedence() {
    assert_eq!(evaluate_expression_cpp("2 + 3 * 4"), Ok(14.0));
    assert_eq!(evaluate_expression_cpp("(2 + 3) * 4"), Ok(20.0));
}

#[test]
fn test_cpp_power_operations() {
    assert_eq!(evaluate_expression_cpp("2 ** 3"), Ok(8.0));
    assert_eq!(evaluate_expression_cpp("2 ^ 3"), Ok(8.0));
}

#[test]
fn test_cpp_unary_operations() {
    assert_eq!(evaluate_expression_cpp("-5 + 3"), Ok(-2.0));
    assert_eq!(evaluate_expression_cpp("-(3 * 2)"), Ok(-6.0));
}

#[test]
fn test_cpp_division_by_zero() {
    let result = evaluate_expression_cpp("10 / 0");
    assert!(result.is_err());
    assert_eq!(result.unwrap_err(), "division by zero");
}

#[test]
fn test_cpp_invalid_syntax() {
    assert!(evaluate_expression_cpp("2 + * 3").is_err());
}

#[test]
fn test_cpp_unsupported_operations() {
    assert!(evaluate_expression_cpp("import os").is_err());
}

#[test]
fn test_cpp_float_parsing() {
    assert_eq!(evaluate_expression_cpp("2.5 * 4"), Ok(10.0));
}

#[test]
fn test_cpp_direct_helpers() {
    assert_eq!(add_cpp(15, 27), 42);
    assert_eq!(pow_cpp(2.0, 10.0), 1024.0);
    assert_eq!(version_cpp(), "1.0.0-cpp");
}
