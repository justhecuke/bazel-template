import subprocess
import sys
import re
import textwrap
from pathlib import Path


def toml_str(s: str) -> str:
    """Wrap a string in double quotes for TOML."""
    return f'"{s}"'


def main():
    # Use the local bazel wrapper
    bin_dir = Path(__file__).parent
    bazel_py = bin_dir / "bazel.py"
    bazel_cmd = [sys.executable, str(bazel_py)]
    
    print("Querying Bazel for external pip dependencies...")
    # Using deps(@pypi//..., 1) to reduce search space to just the direct packages and their py_library rules
    query = 'kind(py_library, deps(@pypi//..., 1))'
    
    try:
        # --keep_going gracefully ignores cross-platform wheel evaluation errors in external repos.
        # check=False because --keep_going causes Bazel to return exit code 1 even on partial success.
        result = subprocess.run(
            [*bazel_cmd, "query", "--keep_going", query, "--output=location"],
            capture_output=True, text=True, check=False
        )
    except Exception as e:
        print(f"Error executing bazel query: {e}")
        sys.exit(1)

    extra_paths = set()
    
    # Parse the output lines.
    # Format: <path>:<line>:<col>: py_library rule <label> ...
    # Example: D:/bazelout/.../BUILD.bazel:6:34: py_library rule @@rules_python++pip+pypi_...
    for line in result.stdout.splitlines():
        if not line.strip():
            continue

        # Step 1: split on ' py_library ' to isolate the '<path>:<line>:<col>:' prefix.
        # This avoids any platform-specific colon counting.
        halves = line.split(" py_library ", 1)
        if len(halves) < 2:
            continue

        # Step 2: strip the trailing ':' separator then rsplit to drop line+col numbers.
        location = halves[0].rstrip(": ")
        path_str = location.rsplit(":", 2)[0]

        build_file_path = Path(path_str)
        # We want the directory containing the BUILD file.
        pkg_dir = build_file_path.parent
        # rules_python pip packages expose Python code under a site-packages subdirectory.
        site_packages_dir = pkg_dir / "site-packages"

        # Trust Bazel's query output unconditionally — paths may not exist yet if
        # the cache hasn't been populated, but Pyright will pick them up once the
        # user fetches or builds the relevant targets.
        # Use as_posix() to ensure forward slashes are used on all platforms.
        extra_paths.add(site_packages_dir.as_posix())
                
    if not extra_paths:
        print("Warning: No pip dependency paths found.")

    sorted_paths = sorted(extra_paths)

    # Build the [tool.pyright] TOML block with markers.
    # We use 12 spaces in the join to match the indentation in the f-string
    # (8 space base + 4 space indent) so dedent works correctly.
    path_lines = ",\n            ".join(toml_str(p) for p in sorted_paths)
    
    start_marker = "# <pypi-site-package-pyright-start>"
    end_marker = "# <pypi-site-package-pyright-end>"
    
    pyright_block = textwrap.dedent(f"""\
        {start_marker}
        [tool.pyright]
        extraPaths = [
            {path_lines}
        ]
        {end_marker}
    """).strip()

    # Merge into pyproject.toml surgically.
    workspace_dir = bin_dir.parent
    config_path = workspace_dir / "pyproject.toml"

    original = config_path.read_text(encoding="utf-8") if config_path.exists() else ""

    if start_marker in original and end_marker in original:
        # Surgical replacement of the existing marked block.
        pattern = re.compile(
            rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}", 
            re.DOTALL
        )
        new_content = pattern.sub(pyright_block, original)
    else:
        # Nothing found, just append to the end.
        new_content = original.rstrip() + "\n\n" + pyright_block + "\n"

    config_path.write_text(new_content.lstrip(), encoding="utf-8")

    print(f"[OK] Updated [tool.pyright] in {config_path.name} with {len(extra_paths)} external search paths.")

if __name__ == "__main__":
    main()
