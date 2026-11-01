use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_int};

/// Evaluates a mathematical string expression using the Rust calculator engine.
///
/// Returns 0 on success, or a non-zero error code:
///   1: Division by zero
///   2: Invalid syntax
///   3: Empty expression
///   4: Trailing unparsed tokens
///   -1: Null pointer or unexpected error
///
/// # Safety
/// Caller must ensure that `expr` is a valid null-terminated C string and
/// that `out_result` and `err_buf` point to valid memory if non-null.
#[no_mangle]
pub unsafe extern "C" fn rs_calculator_eval(
    expr: *const c_char,
    out_result: *mut f64,
    err_buf: *mut c_char,
    err_buf_len: usize,
) -> c_int {
    if expr.is_null() || out_result.is_null() {
        if !err_buf.is_null() && err_buf_len > 0 {
            let msg = b"null pointer argument\0";
            let copy_len = msg.len().min(err_buf_len);
            std::ptr::copy_nonoverlapping(msg.as_ptr() as *const c_char, err_buf, copy_len);
            *err_buf.add(copy_len - 1) = 0;
        }
        return -1;
    }

    let c_str = CStr::from_ptr(expr);
    let expr_str = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => {
            if !err_buf.is_null() && err_buf_len > 0 {
                let msg = b"invalid utf-8 string\0";
                let copy_len = msg.len().min(err_buf_len);
                std::ptr::copy_nonoverlapping(msg.as_ptr() as *const c_char, err_buf, copy_len);
                *err_buf.add(copy_len - 1) = 0;
            }
            return 2;
        }
    };

    match calculator::evaluate_expression(expr_str) {
        Ok(val) => {
            *out_result = val;
            if !err_buf.is_null() && err_buf_len > 0 {
                *err_buf = 0;
            }
            0
        }
        Err(err) => {
            let code = match err.as_str() {
                "division by zero" => 1,
                "empty expression" => 3,
                "trailing unparsed tokens" => 4,
                _ => 2,
            };
            if !err_buf.is_null() && err_buf_len > 0 {
                let c_err = CString::new(err).unwrap_or_default();
                let bytes = c_err.as_bytes_with_nul();
                let copy_len = bytes.len().min(err_buf_len);
                std::ptr::copy_nonoverlapping(bytes.as_ptr() as *const c_char, err_buf, copy_len);
                *err_buf.add(copy_len - 1) = 0;
            }
            code
        }
    }
}

/// Evaluates integer addition in Rust.
#[no_mangle]
pub extern "C" fn rs_calculator_add(a: i32, b: i32) -> i32 {
    a + b
}

/// Evaluates floating point exponentiation in Rust.
#[no_mangle]
pub extern "C" fn rs_calculator_pow(base: f64, exp: f64) -> f64 {
    base.powf(exp)
}

/// Returns the Rust calculator engine version string.
#[no_mangle]
pub extern "C" fn rs_calculator_version() -> *const c_char {
    static VERSION: &[u8] = b"1.0.0-rust\0";
    VERSION.as_ptr() as *const c_char
}
