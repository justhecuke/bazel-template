use calculator::evaluate_expression;

#[test]
fn test_basic_operations() {
    assert_eq!(evaluate_expression("2 + 2"), Ok(4.0));
    assert_eq!(evaluate_expression("5 - 3"), Ok(2.0));
    assert_eq!(evaluate_expression("4 * 3"), Ok(12.0));
    assert_eq!(evaluate_expression("10 / 2"), Ok(5.0));
}

#[test]
fn test_operator_precedence() {
    assert_eq!(evaluate_expression("2 + 3 * 4"), Ok(14.0));
    assert_eq!(evaluate_expression("(2 + 3) * 4"), Ok(20.0));
}

#[test]
fn test_power_operations() {
    assert_eq!(evaluate_expression("2 ** 3"), Ok(8.0));
    assert_eq!(evaluate_expression("2 ^ 3"), Ok(8.0));
}

#[test]
fn test_unary_operations() {
    assert_eq!(evaluate_expression("-5 + 3"), Ok(-2.0));
    assert_eq!(evaluate_expression("-(3 * 2)"), Ok(-6.0));
}

#[test]
fn test_division_by_zero() {
    assert!(evaluate_expression("10 / 0").is_err());
}

#[test]
fn test_invalid_syntax() {
    assert!(evaluate_expression("2 + * 3").is_err());
}

#[test]
fn test_unsupported_operations() {
    assert!(evaluate_expression("import os").is_err());
}

#[test]
fn test_float_parsing() {
    assert_eq!(evaluate_expression("2.5 * 4"), Ok(10.0));
}
