#include "cc/calculator.hh"

#include <cctype>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <string_view>

namespace calculator {
namespace {

enum class TokenType {
    Number,
    Plus,
    Minus,
    Star,
    Slash,
    Power,
    LParen,
    RParen,
    Invalid,
    End
};

struct Token {
    TokenType type;
    double value{0.0};
};

class Lexer {
public:
    explicit Lexer(std::string_view input) : input_(input), pos_(0) {}

    Token next_token() {
        skip_whitespace();
        if (pos_ >= input_.size()) {
            return {TokenType::End, 0.0};
        }

        char c = input_[pos_];
        if (std::isdigit(static_cast<unsigned char>(c)) || c == '.') {
            const char* start_ptr = input_.data() + pos_;
            char* end_ptr = nullptr;
            double val = std::strtod(start_ptr, &end_ptr);
            if (end_ptr == start_ptr) {
                pos_++;
                return {TokenType::Invalid, 0.0};
            }
            pos_ += static_cast<size_t>(end_ptr - start_ptr);
            return {TokenType::Number, val};
        }

        pos_++;
        switch (c) {
            case '+': return {TokenType::Plus, 0.0};
            case '-': return {TokenType::Minus, 0.0};
            case '*':
                if (pos_ < input_.size() && input_[pos_] == '*') {
                    pos_++;
                    return {TokenType::Power, 0.0};
                }
                return {TokenType::Star, 0.0};
            case '/': return {TokenType::Slash, 0.0};
            case '^': return {TokenType::Power, 0.0};
            case '(': return {TokenType::LParen, 0.0};
            case ')': return {TokenType::RParen, 0.0};
            default:  return {TokenType::Invalid, 0.0};
        }
    }

private:
    void skip_whitespace() {
        while (pos_ < input_.size() && std::isspace(static_cast<unsigned char>(input_[pos_]))) {
            pos_++;
        }
    }

    std::string_view input_;
    size_t pos_;
};

class Parser {
public:
    explicit Parser(std::string_view input) : lexer_(input), error_code_(0), error_msg_(nullptr) {
        advance();
    }

    bool parse(double* out_result) {
        if (current_token_.type == TokenType::End) {
            set_error(3, "empty expression");
            return false;
        }
        double res = expression();
        if (error_code_ != 0) {
            return false;
        }
        if (current_token_.type != TokenType::End) {
            set_error(4, "trailing unparsed tokens");
            return false;
        }
        if (out_result) {
            *out_result = res;
        }
        return true;
    }

    int32_t error_code() const { return error_code_; }
    const char* error_msg() const { return error_msg_ ? error_msg_ : ""; }

private:
    void set_error(int32_t code, const char* msg) {
        if (error_code_ == 0) {
            error_code_ = code;
            error_msg_ = msg;
        }
    }

    void advance() {
        current_token_ = lexer_.next_token();
    }

    double expression() {
        double result = term();
        if (error_code_ != 0) return 0.0;
        while (current_token_.type == TokenType::Plus || current_token_.type == TokenType::Minus) {
            bool is_plus = (current_token_.type == TokenType::Plus);
            advance();
            double rhs = term();
            if (error_code_ != 0) return 0.0;
            if (is_plus) {
                result += rhs;
            } else {
                result -= rhs;
            }
        }
        return result;
    }

    double term() {
        double result = unary();
        if (error_code_ != 0) return 0.0;
        while (current_token_.type == TokenType::Star || current_token_.type == TokenType::Slash) {
            bool is_mul = (current_token_.type == TokenType::Star);
            advance();
            double rhs = unary();
            if (error_code_ != 0) return 0.0;
            if (is_mul) {
                result *= rhs;
            } else {
                if (rhs == 0.0) {
                    set_error(1, "division by zero");
                    return 0.0;
                }
                result /= rhs;
            }
        }
        return result;
    }

    double unary() {
        if (current_token_.type == TokenType::Plus) {
            advance();
            return unary();
        }
        if (current_token_.type == TokenType::Minus) {
            advance();
            return -unary();
        }
        return power();
    }

    double power() {
        double base = primary();
        if (error_code_ != 0) return 0.0;
        if (current_token_.type == TokenType::Power) {
            advance();
            double exponent = unary();
            if (error_code_ != 0) return 0.0;
            return std::pow(base, exponent);
        }
        return base;
    }

    double primary() {
        if (current_token_.type == TokenType::Number) {
            double val = current_token_.value;
            advance();
            return val;
        }
        if (current_token_.type == TokenType::LParen) {
            advance();
            double result = expression();
            if (error_code_ != 0) return 0.0;
            if (current_token_.type != TokenType::RParen) {
                set_error(2, "invalid syntax");
                return 0.0;
            }
            advance();
            return result;
        }
        set_error(2, "invalid syntax");
        return 0.0;
    }

    Lexer lexer_;
    Token current_token_;
    int32_t error_code_;
    const char* error_msg_;
};

}  // namespace

double evaluate_expression(std::string_view expr) {
    Parser parser(expr);
    double result = 0.0;
    if (!parser.parse(&result)) {
        return 0.0;
    }
    return result;
}

}  // namespace calculator

extern "C" {

int32_t cc_calculator_eval(
    const char* expr,
    double* out_result,
    char* err_buf,
    size_t err_buf_len
) {
    if (!expr || !out_result) {
        if (err_buf && err_buf_len > 0) {
            std::strncpy(err_buf, "null pointer argument", err_buf_len - 1);
            err_buf[err_buf_len - 1] = '\0';
        }
        return -1;
    }

    calculator::Parser parser(expr);
    if (!parser.parse(out_result)) {
        if (err_buf && err_buf_len > 0) {
            std::strncpy(err_buf, parser.error_msg(), err_buf_len - 1);
            err_buf[err_buf_len - 1] = '\0';
        }
        return parser.error_code();
    }

    if (err_buf && err_buf_len > 0) {
        err_buf[0] = '\0';
    }
    return 0;
}

int32_t cc_calculator_add(int32_t a, int32_t b) {
    return a + b;
}

double cc_calculator_pow(double base, double exp) {
    return std::pow(base, exp);
}

const char* cc_calculator_version(void) {
    return "1.0.0-cpp";
}

}  // extern "C"
