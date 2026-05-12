import subprocess
import os
import sys
import tempfile
import shlex
from pathlib import Path

def main():
    # Use the local bazel wrapper
    bin_dir = Path(__file__).parent
    bazel_py = bin_dir / "bazel.py"
    bazel_cmd = [sys.executable, str(bazel_py)]
    target = "//:requirements.update"
    
    if os.name != "nt":
        # On macOS/Linux, we don't have the UAC issue, so just use the official command.
        print("Running requirements update via Bazel...")
        sys.exit(subprocess.run([*bazel_cmd, "run", target]).returncode)

    # --- Windows UAC Bypass Logic ---
    print("Detected Windows: Using UAC-safe bypass...")

    # Ask Bazel to generate the execution script.
    with tempfile.NamedTemporaryFile(suffix=".cmd", delete=False) as tmp:
        tmp_name = Path(tmp.name)
        
    try:
        print("Generating execution script...")
        subprocess.run([*bazel_cmd, "run", target, f"--script_path={tmp_name}"], check=True, capture_output=True)
        
        lines = tmp_name.read_text().splitlines()
            
        new_lines = []
        for line in lines:
            # We want to find the line that executes the .update.exe
            # This is safer than regex: we split the line and check the first token.
            if not line.strip().startswith("cd") and ".update.exe" in line:
                # Use shlex to safely split the command line (handles quotes)
                try:
                    parts = shlex.split(line, posix=False)
                    if parts and parts[0].endswith(".update.exe"):
                        # Use pathlib to strip the extension
                        exe_path = Path(parts[0])
                        parts[0] = str(exe_path.with_suffix("")) # Removes .exe
                        
                        # Prepend the python executable
                        parts.insert(0, sys.executable)
                        
                        # Reconstruct the line with proper quoting for each part
                        line = " ".join(f'"{p}"' for p in parts)
                except ValueError as e:
                    print(f"Error: Failed to parse command line with shlex: {e}")
                    print(f"Offending line: {line}")
                    sys.exit(1)
            new_lines.append(line)
            
        tmp_name.write_text("\n".join(new_lines))
            
        print("Running requirements update...")
        # Run the modified script. It handles all environment variables and arguments.
        sys.exit(subprocess.run([str(tmp_name), *sys.argv[1:]] , shell=True).returncode)
        
    finally:
        if tmp_name.exists():
            tmp_name.unlink()

if __name__ == "__main__":
    main()
