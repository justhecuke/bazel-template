use std::env;
use std::process;

fn print_usage() {
    println!("Usage: main <command> [arguments]");
    println!("Commands:");
    println!("  info               Display information about the Rust environment.");
    println!("  calc <expression>  Evaluate a mathematical expression securely.");
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        print_usage();
        process::exit(1);
    }

    match args[1].as_str() {
        "info" => {
            println!("OS: {}, Arch: {}", env::consts::OS, env::consts::ARCH);
            println!("Bazel hermetic Rust template is working!");
        }
        "calc" => {
            if args.len() < 3 {
                eprintln!("Error: calc command requires a mathematical expression.");
                process::exit(1);
            }
            let expression = &args[2];
            match calculator::evaluate_expression(expression) {
                Ok(result) => println!("{expression} = {result}"),
                Err(err) => {
                    eprintln!("Error: {err}");
                    process::exit(1);
                }
            }
        }
        unknown => {
            eprintln!("Error: Unknown command '{unknown}'");
            print_usage();
            process::exit(1);
        }
    }
}
