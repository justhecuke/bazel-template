#include "cc/rust_calculator.hh"

#include <stdexcept>
#include <string>

extern "C" {
int32_t rs_calculator_eval(
    const char* expr,
    double* out_result,
    char* err_buf,
    size_t err_buf_len
);
int32_t rs_calculator_add(int32_t a, int32_t b);
double rs_calculator_pow(double base, double exp);
const char* rs_calculator_version(void);
}

namespace rust_interop {

double evaluate_expression(std::string_view expr) {
    std::string null_term_expr(expr);
    double result = 0.0;
    char err_buf[256] = {0};

    int32_t status = rs_calculator_eval(
        null_term_expr.c_str(),
        &result,
        err_buf,
        sizeof(err_buf)
    );

    if (status != 0) {
        throw std::runtime_error(err_buf[0] != '\0' ? err_buf : "Rust evaluation failed");
    }

    return result;
}

int32_t add(int32_t a, int32_t b) {
    return rs_calculator_add(a, b);
}

double pow(double base, double exp) {
    return rs_calculator_pow(base, exp);
}

std::string_view version() {
    const char* v = rs_calculator_version();
    return v ? std::string_view(v) : "unknown";
}

}  // namespace rust_interop
