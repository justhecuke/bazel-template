# bazel-template
Skeleton to get started with bazel quickly, enforcing strict hermeticity and cross-platform compatibility.

## Initial Setup

This repository uses a completely hermetic Bazel setup. You should **not** install global tools like linters or formatters via your system package manager. Instead, all tools are provisioned by Bazel and transparently exposed to your shell via wrapper scripts in the `./bin/` directory.

To bootstrap this environment, we use `mise` to automatically manage your `PATH`. 

### 1. Provision System Dependencies
Run the initial setup script to download the required global bootstrappers (`bazelisk` and `mise`).
```shell
python setup.py
```
*Note: On Windows, binaries are installed to `C:\dev\bin` and that directory is automatically added to your Windows User `PATH` via the registry. On Mac/Linux, they are installed to `~/.local/bin`.*

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
This injects `./bin` into your `PATH` so you can use `bazel`, `buildifier`, etc. transparently.

**Windows (PowerShell):** Run the included `Activate.ps1` script. The leading `. ` (dot-space) is critical — it [dot-sources](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_scripts#script-scope-and-dot-sourcing) the script so environment changes apply to your current session:
```powershell
. .\Activate.ps1
```

> **Why not `mise activate pwsh | Invoke-Expression`?** PowerShell evaluates piped input **line-by-line**, which splits multi-line function bodies in the activation script across separate `Invoke-Expression` calls, causing a syntax error. `Activate.ps1` works around this by writing the full script to a temp file and dot-sourcing it as a whole.

To activate automatically on every new terminal, add it to your PowerShell profile:
```powershell
Add-Content $PROFILE "`n. D:\code\bazel-template\Activate.ps1"
```

**Mac/Linux:**
```bash
eval "$(mise activate bash)" # or zsh
```
*(Add this to `~/.zshrc` or `~/.bashrc` to activate automatically.)*
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
bazel run //:main
```

To format Bazel files:
```shell
buildifier BUILD.bazel
```

All commands are automatically routed through the local `bin/` directory and executed hermetically by Bazel!
