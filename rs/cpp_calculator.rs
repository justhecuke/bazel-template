use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_int};

extern "C" {
    fn cc_calculator_eval(
        expr: *const c_char,
        out_result: *mut f64,
        err_buf: *mut c_char,
        err_buf_len: usize,
    ) -> c_int;

    fn cc_calculator_add(a: i32, b: i32) -> i32;
    fn cc_calculator_pow(base: f64, exp: f64) -> f64;
    fn cc_calculator_version() -> *const c_char;
}

/// Safely evaluates a mathematical string expression using the hermetic C++ engine.
///
/// Supported operators: +, -, *, /, ^, ** and parentheses.
/// Returns Ok(f64) on success, or Err(String) describing the parsing or runtime error.
pub fn evaluate_expression_cpp(expr: &str) -> Result<f64, String> {
    let c_expr = CString::new(expr).map_err(|e| format!("invalid C string: {e}"))?;
    let mut result = 0.0f64;
    let mut err_buf = [0u8; 256];

    let status = unsafe {
        cc_calculator_eval(
            c_expr.as_ptr(),
            &mut result,
            err_buf.as_mut_ptr() as *mut c_char,
            err_buf.len(),
        )
    };

    if status == 0 {
        Ok(result)
    } else {
        let err_msg = unsafe { CStr::from_ptr(err_buf.as_ptr() as *const c_char) }
            .to_str()
            .unwrap_or("unknown error");
        Err(err_msg.to_string())
    }
}

/// Invokes the C++ integer addition function via FFI.
pub fn add_cpp(a: i32, b: i32) -> i32 {
    unsafe { cc_calculator_add(a, b) }
}

/// Invokes the C++ power function via FFI.
pub fn pow_cpp(base: f64, exp: f64) -> f64 {
    unsafe { cc_calculator_pow(base, exp) }
}

/// Returns the C++ calculator engine version string via FFI.
pub fn version_cpp() -> &'static str {
    unsafe {
        let ptr = cc_calculator_version();
        if ptr.is_null() {
            "unknown"
        } else {
            CStr::from_ptr(ptr).to_str().unwrap_or("unknown")
        }
    }
}
