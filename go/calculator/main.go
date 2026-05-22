package main

import (
	"fmt"
	"net/http"
	"os"
	"runtime"
	"time"
)

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	command := os.Args[1]
	switch command {
	case "info":
		fmt.Printf("Go version: %s\n", runtime.Version())
		fmt.Printf("OS: %s, Arch: %s\n", runtime.GOOS, runtime.GOARCH)
		fmt.Println("Bazel hermetic Go template is working!")

	case "fetch":
		if len(os.Args) < 3 {
			fmt.Println("Error: fetch command requires a URL.")
			os.Exit(1)
		}
		url := os.Args[2]
		fetchURL(url)

	case "calc":
		if len(os.Args) < 3 {
			fmt.Println("Error: calc command requires a mathematical expression.")
			os.Exit(1)
		}
		expression := os.Args[2]
		evaluate(expression)

	default:
		fmt.Printf("Error: Unknown command '%s'\n", command)
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Println("Usage: go_demo <command> [arguments]")
	fmt.Println("Commands:")
	fmt.Println("  info               Display information about the Go environment.")
	fmt.Println("  fetch <url>        Fetch the status code from a given URL.")
	fmt.Println("  calc <expression>  Evaluate a mathematical expression securely using AST parsing.")
}

func fetchURL(url string) {
	client := http.Client{
		Timeout: 5 * time.Second,
	}
	resp, err := client.Get(url)
	if err != nil {
		fmt.Printf("Failed to fetch %s: %v\n", url, err)
		os.Exit(1)
	}
	defer resp.Body.Close()

	fmt.Printf("Fetched %s - Status Code: %d\n", url, resp.StatusCode)
}

func evaluate(expression string) {
	result, err := EvaluateExpression(expression)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("%s = %g\n", expression, result)
}
