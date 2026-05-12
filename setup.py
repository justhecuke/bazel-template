#!/usr/bin/env python3
"""
Setup script to provision global system dependencies: bazelisk and mise.
Cross-platform support for Windows, macOS, and Linux.
"""

import os
import sys
import shutil
import urllib.request
import platform
import argparse
import subprocess
import hashlib
import json
import zipfile
import tarfile
import re

BAZELISK_VERSION = "v1.29.0"
MISE_VERSION = "v2025.1.0"
PREK_VERSION = "v0.3.13"

BAZELISK_HASHES = {
    "bazelisk-darwin-amd64": "16c3d7aa15323a9fb69f56c7ec5733ed18bedb786680d0ba13bb12a3c8083007",
    "bazelisk-darwin-arm64": "cee851f726789227d5561004e9904a52be45c3efb56f8b38b6993d6adbaa0409",
    "bazelisk-linux-amd64": "5a408715e932c0250d28bd84555f12edbf70117de42f9181691c736eacc4a992",
    "bazelisk-linux-arm64": "e20e8b0f4f240091b7a55bf17b9398bd4f40ee70ae0208dff95dd4c445fb4010",
    "bazelisk-windows-amd64.exe": "092a8738d5b41aae7a85c42cc961b1034e3389aba43ffc20c0fabda7b43e095b",
    "bazelisk-windows-arm64.exe": "8bc42bd5d7857f18a21440b906469bb6c7cf91a7c72364d4b1e5ec56a76fe94f"
}

PREK_HASHES = {
    "prek-x86_64-pc-windows-msvc.zip": "ca32a6451cfdd22a27d99313b3a2f91eb0ce6d191eb8e35e2467f1551252ebbb",
    "prek-aarch64-pc-windows-msvc.zip": "892cb69e81c5c77c8af23dd930d4bcf578b8f62765ee00e3ba8fb76d2035eb34",
    "prek-x86_64-apple-darwin.tar.gz": "2bbfdf15cfe6e954b98cb27094828f5c55a8bec0a02cf55041f783c71e3b8955",
    "prek-aarch64-apple-darwin.tar.gz": "0b3b3dd0fbab7b95217280248196bde741b47b8de7bf60de50b4a12a9cc17b1f",
    "prek-x86_64-unknown-linux-gnu.tar.gz": "40898b110cdb0d70d3b7461c9e468d5821ce144c8ba890eedf22bf49e4817274",
    "prek-aarch64-unknown-linux-gnu.tar.gz": "0112ffa44a0aaa869aa9da45393b7a4d7c30c24abd6e540bac0494db24844c79",
}

# On Windows, install to C:\dev\bin — a conventional, space-free developer tools directory.
# This avoids a known bug in `mise activate pwsh` that breaks when the path contains spaces
# (common for Windows user profiles like C:\Users\John Doe\...).
WINDOWS_LOCAL_BIN = r"C:\dev\bin"
SETUP_START_MARKER = "# <bazel-template-setup-start>"
SETUP_END_MARKER = "# <bazel-template-setup-end>"

def get_local_bin(os_name=None):
    """Returns the platform-appropriate binary install directory."""
    if os_name is None:
        os_name, _, _ = get_platform_info()
    if os_name == "windows":
        return WINDOWS_LOCAL_BIN
    return os.path.join(os.path.expanduser("~"), ".local", "bin")

def get_platform_info():
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "windows":
        os_name = "windows"
        ext = ".exe"
    elif system == "darwin":
        os_name = "darwin"
        ext = ""
    else:
        os_name = "linux"
        ext = ""
        
    if machine in ["x86_64", "amd64"]:
        arch = "amd64"
    elif machine in ["aarch64", "arm64"]:
        arch = "arm64"
    else:
        arch = "amd64" # fallback
        
    return os_name, arch, ext

def check_command(cmd):
    return shutil.which(cmd) is not None

def verify_sha256(filepath, expected_hash):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest() == expected_hash, sha256_hash.hexdigest()

def install_bazelisk(force=False):
    existing = shutil.which("bazelisk")
    if existing and not force:
        print(f"[ok] Bazelisk is already installed at {existing}")
        return

    os_name, arch, ext = get_platform_info()
    local_bin = get_local_bin(os_name)
    os.makedirs(local_bin, exist_ok=True)
    
    filename = f"bazelisk-{os_name}-{arch}{ext}"
    url = f"https://github.com/bazelbuild/bazelisk/releases/download/{BAZELISK_VERSION}/{filename}"
    out_path = os.path.join(local_bin, f"bazelisk{ext}")
    
    print(f"Installing bazelisk {BAZELISK_VERSION} to {out_path}... ", end="", flush=True)
    
    expected_hash = BAZELISK_HASHES.get(filename)
    if not expected_hash:
        print(f"\nError: No known SHA256 hash for {filename}. Aborting for security.")
        sys.exit(1)
        
    try:
        urllib.request.urlretrieve(url, out_path)
        is_valid, actual_hash = verify_sha256(out_path, expected_hash)
        
        if not is_valid:
            print(f"\nSECURITY ERROR: Hash mismatch for {filename}!")
            print(f"Expected: {expected_hash}")
            print(f"Actual:   {actual_hash}")
            os.remove(out_path)
            sys.exit(1)
            
        if os_name != "windows":
            os.chmod(out_path, 0o755)
        print("Done.")
    except Exception as e:
        print(f"\nFailed to install bazelisk: {e}")
        sys.exit(1)

def install_mise(force=False):
    existing = shutil.which("mise")
    if existing and not force:
        print(f"[ok] Mise is already installed at {existing}")
        return

    os_name, _, _ = get_platform_info()
    
    env = os.environ.copy()
    env["MISE_VERSION"] = MISE_VERSION.lstrip('v')
    
    if os_name == "windows":
        local_bin = get_local_bin(os_name)
        os.makedirs(local_bin, exist_ok=True)
        out_path = os.path.join(local_bin, "mise.exe")
        
        print(f"Installing mise {MISE_VERSION} to {out_path}... ", end="", flush=True)
        url = f"https://api.github.com/repos/jdx/mise/releases/tags/{MISE_VERSION}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
            asset_url = None
            for asset in data.get('assets', []):
                if 'windows' in asset['name'].lower() and 'x64' in asset['name'].lower() and asset['name'].endswith('.zip'):
                    asset_url = asset['browser_download_url']
                    break
                    
            if not asset_url:
                print("\nCould not find Windows x64 zip archive in release assets.")
                sys.exit(1)
                
            zip_path = os.path.join(local_bin, "mise_temp.zip")
            
            urllib.request.urlretrieve(asset_url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as z:
                exe_name = None
                for name in z.namelist():
                    if name.endswith('mise.exe') or name == 'mise.exe':
                        exe_name = name
                        break
                if exe_name:
                    with z.open(exe_name) as zf, open(out_path, 'wb') as f:
                        shutil.copyfileobj(zf, f)
                else:
                    print("\nError: Could not find mise.exe inside the zip file.")
                    os.remove(zip_path)
                    sys.exit(1)
                    
            os.remove(zip_path)
            print("Done.")
        except Exception as e:
            print(f"\nFailed to install mise on Windows: {e}")
            sys.exit(1)
    else:
        print(f"Installing mise {MISE_VERSION} via official script... ", end="", flush=True)
        try:
            subprocess.run("curl https://mise.run | sh > /dev/null 2>&1", shell=True, check=True, env=env)
            print("Done.")
        except subprocess.CalledProcessError as e:
            print(f"\nFailed to install mise: {e}")
            sys.exit(1)

def install_prek(force=False):
    existing = shutil.which("prek")
    if existing and not force:
        print(f"[ok] Prek is already installed at {existing}")
    else:
        os_name, arch, ext = get_platform_info()
        local_bin = get_local_bin(os_name)
        os.makedirs(local_bin, exist_ok=True)
        
        if os_name == "windows":
            platform_str = "pc-windows-msvc"
            archive_ext = ".zip"
        elif os_name == "darwin":
            platform_str = "apple-darwin"
            archive_ext = ".tar.gz"
        else:
            platform_str = "unknown-linux-gnu"
            archive_ext = ".tar.gz"
            
        # mapping architectures to prek formats
        prek_arch = "x86_64" if arch == "amd64" else "aarch64"
        
        filename = f"prek-{prek_arch}-{platform_str}{archive_ext}"
        url = f"https://github.com/j178/prek/releases/download/{PREK_VERSION}/{filename}"
        archive_path = os.path.join(local_bin, filename)
        out_path = os.path.join(local_bin, f"prek{ext}")
        
        print(f"Installing prek {PREK_VERSION} to {out_path}... ", end="", flush=True)
        
        expected_hash = PREK_HASHES.get(filename)
        if not expected_hash:
            print(f"\nError: No known SHA256 hash for {filename}. Aborting for security.")
            sys.exit(1)
            
        try:
            urllib.request.urlretrieve(url, archive_path)
            is_valid, actual_hash = verify_sha256(archive_path, expected_hash)
            
            if not is_valid:
                print(f"\nSECURITY ERROR: Hash mismatch for {filename}!")
                print(f"Expected: {expected_hash}")
                print(f"Actual:   {actual_hash}")
                os.remove(archive_path)
                sys.exit(1)
                
            if archive_ext == ".zip":
                with zipfile.ZipFile(archive_path, 'r') as z:
                    for name in z.namelist():
                        if name.endswith('prek.exe') or name == 'prek.exe':
                            with z.open(name) as zf, open(out_path, 'wb') as f:
                                shutil.copyfileobj(zf, f)
                            break
            else:
                with tarfile.open(archive_path, "r:gz") as tar:
                    for member in tar.getmembers():
                        if member.name.endswith('prek') or member.name.split('/')[-1] == 'prek':
                            member.name = os.path.basename(member.name)
                            f = tar.extractfile(member)
                            with open(out_path, 'wb') as out_f:
                                shutil.copyfileobj(f, out_f)
                            break
                            
            os.remove(archive_path)
            if os_name != "windows":
                os.chmod(out_path, 0o755)
            print("Done.")
        except Exception as e:
            print(f"\nFailed to install prek: {e}")
            sys.exit(1)
            
    # Always try to install hooks into the repo
    print("Setting up git hooks with prek... ", end="", flush=True)
    try:
        subprocess.run(["prek", "install"], check=True, capture_output=True)
        print("Done.")
    except Exception as e:
        print(f"Failed to run prek install: {e}")


def configure_shell_profile(profile_path, local_bin):
    """Injects mise activation into a specific shell profile or RC file.
    Detects shell type based on file extension or OS fallback.
    Returns True if the profile was modified."""
    profile_path = os.path.expanduser(profile_path)
    os_name, _, _ = get_platform_info()
    
    # Detect shell type
    ext = os.path.splitext(profile_path)[1].lower()
    if ext in ('.ps1', '.psm1'):
        shell_type = 'pwsh'
    elif ext in ('.bashrc', '.zshrc', '.sh') or profile_path.endswith('rc'):
        shell_type = 'unix'
    else:
        # Fallback to OS-level detection
        shell_type = 'pwsh' if os_name == 'windows' else 'unix'

    print(f"Configuring shell profile at {profile_path} (detected type: {shell_type})... ", end="", flush=True)

    if shell_type == 'pwsh':
        mise_exe = os.path.join(local_bin, 'mise.exe').replace('\\', '\\\\')
        activation_block = f'{SETUP_START_MARKER}\n& "{mise_exe}" activate pwsh | Out-String | Invoke-Expression\n{SETUP_END_MARKER}\n'
    else:
        # For Unix, we assume mise is in the path or we use the ~/.local/bin/mise if it exists
        mise_cmd = "mise"
        # If we installed to a specific local_bin, try to use that
        mise_path = os.path.join(local_bin, "mise")
        if os.path.exists(mise_path):
            mise_cmd = mise_path
            
        activation_block = f'{SETUP_START_MARKER}\neval "$("{mise_cmd}" activate bash)"\n{SETUP_END_MARKER}\n'

    try:
        content = ""
        if os.path.exists(profile_path):
            with open(profile_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        
        # 1. Surgical replacement of existing block if found
        pattern = re.compile(
            rf"{re.escape(SETUP_START_MARKER)}.*?{re.escape(SETUP_END_MARKER)}(\r?\n|$)", 
            re.DOTALL
        )
        if SETUP_START_MARKER in content:
            new_content = pattern.sub(activation_block, content)
        else:
            # 2. Append to the end
            new_content = content.rstrip() + "\n\n" + activation_block

        if new_content != content:
            with open(profile_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Done.")
            return True
        else:
            print("Already up-to-date.")
            return False
    except Exception as e:
        print(f"\nError: Could not modify {profile_path}: {e}")
        return False



def ensure_windows_path(*paths):
    """Automatically adds one or more directories to the Windows User PATH if not already present.
    Returns True if any modification was made."""
    modified = False
    for path in paths:
        cmd = f"""
        $currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
        if ($currentPath -eq $null) {{
            $currentPath = ''
        }}
        if (-not $currentPath.Contains('{path}')) {{
            $newPath = $currentPath
            if ($newPath -and -not $newPath.EndsWith(';')) {{
                $newPath += ';'
            }}
            $newPath += '{path}'
            [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
            Write-Output "Added to PATH"
        }}
        """
        try:
            result = subprocess.run(['powershell', '-NoProfile', '-Command', cmd], check=True, capture_output=True, text=True)
            if "Added to PATH" in result.stdout:
                modified = True
        except Exception:
            pass
    return modified

def main():
    parser = argparse.ArgumentParser(description="Provision global system dependencies for bazel-template.")
    parser.add_argument("--force", action="store_true", help="Force reinstall of pinned versions.")
    parser.add_argument("--add-to-path", action="store_true", help="Automatically add install directory to User PATH.")
    parser.add_argument("--configure-shell", metavar="PATH", help="Path to the shell profile/rc file to modify (e.g., $PROFILE or ~/.bashrc).")
    args = parser.parse_args()
    
    os_name, _, _ = get_platform_info()
    local_bin = get_local_bin(os_name)
    
    # Ensure local_bin is in the current process PATH so shutil.which finds our installs
    # even if the user hasn't restarted their terminal yet.
    if local_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = local_bin + os.pathsep + os.environ.get("PATH", "")
        
    install_bazelisk(force=args.force)
    install_mise(force=args.force)
    install_prek(force=args.force)
    
    path_modified = False
    profile_modified = False
    
    if args.add_to_path and os_name == "windows":
        path_modified = ensure_windows_path(local_bin)
        
    if args.configure_shell:
        profile_modified = configure_shell_profile(args.configure_shell, local_bin)
    
    print("\n[ok] Setup complete!")
    if os_name != "windows":
        print("Ensure ~/.local/bin (and ~/.local/share/mise/bin if using mise) is in your PATH.")
        
    needs_restart = path_modified or profile_modified
    if needs_restart:
        print("\n" + "="*60)
        print("!! ACTION REQUIRED !!".center(60))
        print("="*60)
        if path_modified:
            print(f"Your Windows User PATH was modified to include {local_bin}.")
        if profile_modified:
            print(f"Mise activation was added to {args.configure_shell}.")
            print("This means any NEW terminal using that profile will be automatically activated.")
        print("You MUST completely close your IDE and reopen it for changes")
        print("to take effect in integrated terminals.")
        print("="*60 + "\n")
    else:
        print("\n" + "-"*60)
        print("Next Steps:".center(60))
        print("-"*60)
        if not path_modified and os_name == "windows":
            print(f"1. Add {local_bin} to your PATH manually, or run with --add-to-path")
        print("2. Activate the environment in your shell:")
        if os_name == "windows":
            print("   mise activate pwsh | Out-String | Invoke-Expression")
        else:
            print('   eval "$(mise activate bash)" # or zsh')
        print(f"3. (Optional) Run with --configure-shell for automatic activation.")
        print("-"*60 + "\n")

if __name__ == "__main__":
    main()

