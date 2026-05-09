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

BAZELISK_VERSION = "v1.29.0"
MISE_VERSION = "v2025.1.0"

BAZELISK_HASHES = {
    "bazelisk-darwin-amd64": "16c3d7aa15323a9fb69f56c7ec5733ed18bedb786680d0ba13bb12a3c8083007",
    "bazelisk-darwin-arm64": "cee851f726789227d5561004e9904a52be45c3efb56f8b38b6993d6adbaa0409",
    "bazelisk-linux-amd64": "5a408715e932c0250d28bd84555f12edbf70117de42f9181691c736eacc4a992",
    "bazelisk-linux-arm64": "e20e8b0f4f240091b7a55bf17b9398bd4f40ee70ae0208dff95dd4c445fb4010",
    "bazelisk-windows-amd64.exe": "092a8738d5b41aae7a85c42cc961b1034e3389aba43ffc20c0fabda7b43e095b",
    "bazelisk-windows-arm64.exe": "8bc42bd5d7857f18a21440b906469bb6c7cf91a7c72364d4b1e5ec56a76fe94f"
}

# On Windows, install to C:\dev\bin — a conventional, space-free developer tools directory.
# This avoids a known bug in `mise activate pwsh` that breaks when the path contains spaces
# (common for Windows user profiles like C:\Users\John Doe\...).
WINDOWS_LOCAL_BIN = r"C:\dev\bin"

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
        print(f"[✓] Bazelisk is already installed at {existing}")
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
        print(f"[✓] Mise is already installed at {existing}")
        return

    os_name, _, _ = get_platform_info()
    
    env = os.environ.copy()
    env["MISE_VERSION"] = MISE_VERSION.lstrip('v')
    
    if os_name == "windows":
        local_bin = get_local_bin(os_name)
        os.makedirs(local_bin, exist_ok=True)
        out_path = os.path.join(local_bin, "mise.exe")
        
        print(f"Installing mise {MISE_VERSION} to {out_path}... ", end="", flush=True)
        import json
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
                
            import zipfile
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

def setup_pwsh_profile(local_bin):
    """Injects mise activation into the user's PowerShell profile.
    Uses ScriptBlock dot-sourcing to evaluate the multi-line activation script
    as a whole unit, bypassing the line-by-line Invoke-Expression limitation.
    Also ensures the PowerShell execution policy allows the profile to load.
    Returns True if the profile was modified."""
    # First, ensure the execution policy allows scripts to run.
    # 'RemoteSigned' is the standard developer policy: local scripts run freely,
    # downloaded scripts must be signed. This is required for $PROFILE to load.
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-ExecutionPolicy -Scope CurrentUser'],
            capture_output=True, text=True, check=True
        )
        policy = result.stdout.strip()
        if policy in ('Undefined', 'Restricted'):
            print("Setting PowerShell execution policy to RemoteSigned for current user... ", end="", flush=True)
            subprocess.run(
                ['powershell', '-Command', 'Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force'],
                check=True, capture_output=True
            )
            print("Done.")
        else:
            print(f"[✓] PowerShell execution policy is already '{policy}'.")
    except Exception as e:
        print(f"Could not set execution policy: {e}")

    try:
        result = subprocess.run(
            ['powershell', '-Command', 'echo $PROFILE'],
            capture_output=True, text=True, check=True
        )
        profile_path = result.stdout.strip()
    except Exception as e:
        print(f"Could not determine PowerShell profile path: {e}")
        return False

    # The activation line:
    # We use '&' to call the executable and pipe the full output to Out-String
    # then Invoke-Expression. This ensures multi-line scripts are evaluated
    # as a single block, avoiding the line-by-line syntax error.
    mise_exe = os.path.join(local_bin, 'mise.exe').replace('\\', '\\\\')
    activation_marker = '# mise activate'
    activation_line = f'{activation_marker}\n& "{mise_exe}" activate pwsh | Out-String | Invoke-Expression\n'

    try:
        content = ""
        if os.path.exists(profile_path):
            with open(profile_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        if activation_marker in content:
            # Replace the old activation block with the new one
            import re
            # Regex to find the marker and the following line(s)
            pattern = re.escape(activation_marker) + r".*?(\r?\n|$)"
            new_content = re.sub(pattern, activation_line, content, flags=re.DOTALL)
            if new_content == content:
                # If regex didn't find a clean match to replace, just append (safe fallback)
                new_content = content + "\n" + activation_line
        else:
            new_content = content + "\n" + activation_line

        with open(profile_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[✓] Updated mise activation in PowerShell profile at {profile_path}")
        return True
    except Exception as e:
        print(f"Could not modify PowerShell profile: {e}")
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
            result = subprocess.run(['powershell', '-Command', cmd], check=True, capture_output=True, text=True)
            if "Added to PATH" in result.stdout:
                modified = True
        except Exception:
            pass
    return modified

def main():
    parser = argparse.ArgumentParser(description="Provision global system dependencies for bazel-template.")
    parser.add_argument("--force", action="store_true", help="Force reinstall of pinned versions.")
    args = parser.parse_args()
    
    os_name, _, _ = get_platform_info()
    local_bin = get_local_bin(os_name)
    
    # Ensure local_bin is in the current process PATH so shutil.which finds our installs
    # even if the user hasn't restarted their terminal yet.
    if local_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = local_bin + os.pathsep + os.environ.get("PATH", "")
        
    install_bazelisk(force=args.force)
    install_mise(force=args.force)
    
    profile_modified = False
    if os_name == "windows":
        path_modified = ensure_windows_path(local_bin)
        profile_modified = setup_pwsh_profile(local_bin)
    
    print("\n[✓] Setup complete!")
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
            print("Mise activation was added to your PowerShell profile.")
            print("This means any NEW terminal will be automatically activated.")
        print("You MUST completely close your IDE and reopen it for changes")
        print("to take effect in integrated terminals.")
        print("="*60 + "\n")

if __name__ == "__main__":
    main()

