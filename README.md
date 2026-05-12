# Bazel Template
A skeleton to get started with Bazel quickly, enforcing strict hermeticity and cross-platform compatibility.

## Initial Setup

This repository uses a completely hermetic Bazel setup. You should **not** install global tools like linters or formatters via your system package manager. Instead, all tools are provisioned by Bazel and transparently exposed to your shell via wrapper scripts in the `./bin/` directory.

To bootstrap this environment, we use `mise` to automatically manage your `PATH`. 

### 1. Provision System Dependencies
Run the initial setup script to download the required global bootstrappers (`bazelisk` and `mise`). We recommend using the `--add-to-path` flag to update your system PATH, and the `--configure-shell` flag to automatically inject activation into your shell profile.

**On Windows (PowerShell):**
```powershell
python setup.py --add-to-path --configure-shell $PROFILE
```

**On macOS/Linux (Bash/Zsh):**
```bash
python setup.py --configure-shell ~/.bashrc # or ~/.zshrc
```
*Note: On Windows, binaries are installed to `C:\dev\bin` (this can be automatically added to your Windows User `PATH` via the `--add-to-path` flag). On Mac/Linux, they are installed to `~/.local/bin`.*

### 2. Restart Your IDE Completely
`setup.py` modifies your Windows User `PATH` in the registry. This change **will not be visible** to any terminal that was already open, including "new terminal" tabs inside your IDE — those inherit the IDE process's environment, which was frozen at launch time.

**You must completely close and reopen your IDE** (or open a fresh terminal outside the IDE, e.g. Windows Terminal / PowerShell directly) for the new `PATH` to take effect.

> **Tip:** You can verify the path is correct by running `where.exe mise` in a fresh terminal. It should print `C:\dev\bin\mise.exe`. If it prints a path containing spaces (like `C:\Users\...`), you have a stale terminal and need to restart your IDE.

### 3. Trust the Project
Open a new terminal in the root of the project and trust the `.mise.toml` configuration:
```shell
mise trust
```

### 4. Activate the Environment
This injects `./bin` into your `PATH` so you can use Bazel, Buildifier, etc. transparently.

**Persistent Activation:**
If you ran `setup.py` with the `--configure-shell <PATH>` flag, it configured the specified profile file to automatically activate the environment in every new terminal session.

**Current Session Activation:**
If you want to activate the environment in your *current* terminal without restarting, run the following command:

**Windows (PowerShell):**
```powershell
mise activate pwsh | Out-String | Invoke-Expression
```
*Note: We use `Out-String | Invoke-Expression` to ensure the multi-line activation script is evaluated as a single block, avoiding syntax errors caused by line-by-line execution.*

**Mac/Linux (Bash/Zsh):**
```bash
eval "$(mise activate bash)" # or zsh
```

### 5. Generate IDE Search Paths
Bazel manages Python dependencies in a hermetic cache, which IDEs (like VS Code/Pyright) cannot discover by default. To fix import resolution errors, run the following command once to generate a local `pyproject.toml` containing the necessary search paths:
```shell
python bin/update_ide_paths.py
```
*Note: This configuration is automatically updated by a pre-commit hook whenever `requirements.txt` changes.*


## Usage

Now that `mise` is active, you can use the transparent wrappers as if they were globally installed tools. 

To run the Python template test:
```shell
bazel run //py:main
```

To format Bazel files:
```shell
buildifier BUILD.bazel
```

All commands are automatically routed through the local `bin/` directory and executed hermetically by Bazel!
