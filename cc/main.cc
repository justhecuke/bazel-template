#include "cc/calculator.hh"
#include "cc/rust_calculator.hh"

#include <iostream>
#include <string>
#include <string_view>

void print_usage() {
    std::cout << "Usage: main <command> [arguments]\n"
              << "Commands:\n"
              << "  info                   Display information about the C++ environment.\n"
              << "  calc <expression>      Evaluate a mathematical expression using C++ engine.\n"
              << "  calc-rs <expression>   Evaluate a mathematical expression using Rust FFI engine.\n";
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        print_usage();
        return 1;
    }

    std::string_view command = argv[1];
    if (command == "info") {
        std::cout << "C++ Standard: " << __cplusplus << "\n"
                  << "Engine Version: " << cc_calculator_version() << "\n"
                  << "Rust Interop Engine Version: " << rust_interop::version() << "\n"
                  << "Bazel hermetic C++ toolchain is working!\n";
        return 0;
    }

    if (command == "calc") {
        if (argc < 3) {
            std::cerr << "Error: calc command requires a mathematical expression.\n";
            return 1;
        }
        std::string expression = argv[2];
        double result = 0.0;
        char err_buf[256] = {0};
        int32_t status = cc_calculator_eval(expression.c_str(), &result, err_buf, sizeof(err_buf));
        if (status == 0) {
            std::cout << expression << " = " << result << "\n";
            return 0;
        } else {
            std::cerr << "Error: " << (err_buf[0] != '\0' ? err_buf : "evaluation failed") << "\n";
            return 1;
        }
    }

    if (command == "calc-rs") {
        if (argc < 3) {
            std::cerr << "Error: calc-rs command requires a mathematical expression.\n";
            return 1;
        }
        std::string expression = argv[2];
        try {
            double result = rust_interop::evaluate_expression(expression);
            std::cout << expression << " = " << result << " (via Rust engine)\n";
            return 0;
        } catch (const std::exception& e) {
            std::cerr << "Error: " << e.what() << "\n";
            return 1;
        }
    }

    std::cerr << "Error: Unknown command '" << command << "'\n";
    print_usage();
    return 1;
}
