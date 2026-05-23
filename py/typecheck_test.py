import os
import runpy
import sys
from pathlib import Path


def setup_bin_path():
    # Locate the runfiles directory of the Bazel test sandbox
    runfiles_dir = os.environ.get("RUNFILES_DIR")
    if runfiles_dir:
        base_dir = Path(runfiles_dir)
    else:
        base_dir = Path(__file__).parent.parent

    exe_name = "pyrefly.exe" if sys.platform == "win32" else "pyrefly"

    found_bin_dir = None
    for root, _dirs, files in os.walk(base_dir):
        if exe_name in files:
            p = Path(root)
            if p.name == "bin":
                found_bin_dir = p
                break
            elif not found_bin_dir:
                found_bin_dir = p

    if found_bin_dir:
        os.environ["PATH"] = str(found_bin_dir.resolve()) + os.pathsep + os.environ.get("PATH", "")


def generate_sandbox_config():
    # Gather all import paths from sys.path
    search_paths = []
    for p in sys.path:
        if not p.strip():
            continue
        path_obj = Path(p).resolve()
        if path_obj.exists() and path_obj.is_dir():
            # Include all valid search paths so Pyrefly can resolve imports hermetically
            search_paths.append(path_obj.as_posix())

    # Write a temporary pyrefly.toml in the current working directory of the test
    toml_paths = ",\n".join(f'    "{p}"' for p in search_paths)
    pyrefly_content = f"search-path = [\n{toml_paths}\n]\ninfer-with-first-use = false\n"

    config_path = Path("pyrefly.toml")
    config_path.write_text(pyrefly_content, encoding="utf-8")
    print(f"Generated sandbox pyrefly.toml with {len(search_paths)} search paths.")


def main():
    setup_bin_path()
    generate_sandbox_config()

    # Find the specific target Python files under 'py/' to avoid checking
    # Bazel's generated runner and bootstrap scripts (which start with '_')
    py_dir = Path("py")
    files_to_check = []
    for p in py_dir.glob("*.py"):
        if not p.name.startswith("_") and p.name != "typecheck_test.py":
            files_to_check.append(str(p))

    print(f"Type-checking source files: {files_to_check}")

    # Pass the resolved source files to Pyrefly check
    sys.argv = ["pyrefly", "check", *files_to_check]
    try:
        runpy.run_module("pyrefly", run_name="__main__")
        sys.exit(0)
    except SystemExit as e:
        sys.exit(e.code)


if __name__ == "__main__":
    main()
