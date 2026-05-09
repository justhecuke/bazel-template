#!/usr/bin/env python3
"""
Wrapper to ensure Bazel runs inside an isolated Python venv.
Prevents system-level Python packages from leaking into Bazel's bootstrap process.
"""

import os
import sys
import subprocess
import shutil

def main():
    venv_dir = ".venv"
    if not os.path.isdir(venv_dir):
        print("Bootstrapping isolated Python venv...")
        python_exe = "python3" if shutil.which("python3") else "python"
        subprocess.run([python_exe, "-m", "venv", venv_dir], check=True)
    
    # Activate venv environment in our current process copy
    env = os.environ.copy()
    if sys.platform == "win32":
        venv_bin = os.path.join(venv_dir, "Scripts")
    else:
        venv_bin = os.path.join(venv_dir, "bin")
        
    env["VIRTUAL_ENV"] = os.path.abspath(venv_dir)
    env["PATH"] = f"{os.path.abspath(venv_bin)}{os.pathsep}{env.get('PATH', '')}"
    
    # Locate the real bazelisk or bazel on the global PATH
    bazel_exe = shutil.which("bazelisk", path=env["PATH"]) or shutil.which("bazel", path=env["PATH"])
    if not bazel_exe:
        print("Error: Could not find bazelisk or bazel in PATH.")
        sys.exit(1)
        
    cmd = [bazel_exe] + sys.argv[1:]
    
    # Execute the real bazel
    if sys.platform != "win32":
        os.execvpe(bazel_exe, cmd, env)
    else:
        sys.exit(subprocess.run(cmd, env=env).returncode)

if __name__ == "__main__":
    main()
