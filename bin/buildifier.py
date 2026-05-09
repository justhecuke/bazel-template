#!/usr/bin/env python3
"""
Wrapper to run hermetic buildifier via Bazel.
"""

import os
import sys
import subprocess

def main():
    # Call our bazel.py wrapper to ensure it runs inside the venv
    bazel_py = os.path.join(os.path.dirname(__file__), "bazel.py")
    
    cmd = [sys.executable, bazel_py, "run", "//tools:buildifier", "--"] + sys.argv[1:]
    
    if sys.platform != "win32":
        os.execvp(sys.executable, cmd)
    else:
        sys.exit(subprocess.run(cmd).returncode)

if __name__ == "__main__":
    main()
