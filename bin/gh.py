#!/usr/bin/env python3
"""Hermetic GitHub CLI (gh) wrapper.

Pins a specific release of gh, provisions it into a local cache directory on
first use with SHA256 integrity verification, and forwards all arguments.

Usage Examples:
  gh --version
  gh auth login
  gh repo view
"""

from __future__ import annotations

import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

GH_VERSION = "2.103.0"

# Pinned SHA-256 hashes for GitHub CLI v2.103.0 release assets
GH_HASHES: dict[str, str] = {
    "gh_2.103.0_windows_amd64.zip": "80c846a5b8432672ca6373b34ce9de998c9686aaa1885c845f2e1ee81f713726",
    "gh_2.103.0_windows_arm64.zip": "bc8c27c396c683a7a823446fd0c16b923e60ec3fac5d26a875c646865d513a48",
    "gh_2.103.0_linux_amd64.tar.gz": "fdd768eb70f6409f80fcfa9f3a1c0adf0fc98d827ab3ce0bed2ac22762c5d786",
    "gh_2.103.0_linux_arm64.tar.gz": "7f322df34e624d14f5ec0c4acb121fd6dfa14392fdbbd1066aa8e0a05ac3721e",
    "gh_2.103.0_macOS_amd64.zip": "64d1734941f104f996271c820daa50e96902c2618f9b4c1e63c41519517a9c6b",
    "gh_2.103.0_macOS_arm64.zip": "54be566e9f614bea5de8021e95b9ad33dfee3b9d2ea120c9c294c00defaa5014",
}


def _get_platform_info() -> tuple[str, str, str]:
    """Returns normalized (os_name, arch, archive_ext)."""
    sys_name = platform.system().lower()
    machine = platform.machine().lower()

    if sys_name == "windows":
        os_name = "windows"
        archive_ext = ".zip"
    elif sys_name == "darwin":
        os_name = "macOS"
        archive_ext = ".zip"
    else:
        os_name = "linux"
        archive_ext = ".tar.gz"

    if machine in ("x86_64", "amd64"):
        arch = "amd64"
    elif machine in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        arch = "amd64"

    return os_name, arch, archive_ext


def _verify_sha256(filepath: Path, expected_hash: str) -> bool:
    """Computes SHA256 of filepath and compares against expected hash."""
    hasher = hashlib.sha256()
    with filepath.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest().lower() == expected_hash.lower()


def _extract_binary(archive_path: Path, archive_ext: str, out_bin: Path) -> None:
    """Extracts gh executable from the downloaded archive."""
    target_names = {"gh", "gh.exe"}
    if archive_ext == ".zip":
        with zipfile.ZipFile(archive_path, "r") as z:
            for member in z.namelist():
                member_path = Path(member)
                if member_path.name in target_names and "bin" in member_path.parts:
                    with z.open(member) as src, out_bin.open("wb") as dst:
                        shutil.copyfileobj(src, dst)
                    return
    else:
        with tarfile.open(archive_path, "r:gz") as tar:
            for member in tar.getmembers():
                member_path = Path(member.name)
                if member_path.name in target_names and "bin" in member_path.parts:
                    f_extracted = tar.extractfile(member)
                    if f_extracted is None:
                        raise ValueError(f"Failed to extract {member.name} from archive")
                    with out_bin.open("wb") as dst:
                        shutil.copyfileobj(f_extracted, dst)
                    return
    raise RuntimeError(f"Could not find gh binary in downloaded archive {archive_path.name}")


def ensure_gh_binary() -> Path:
    """Provisions and returns the path to the cached gh binary."""
    os_name, arch, archive_ext = _get_platform_info()
    ext = ".exe" if os_name == "windows" else ""

    cache_dir = Path.home() / ".cache" / "bazel_template" / "gh" / f"v{GH_VERSION}"
    cache_dir.mkdir(parents=True, exist_ok=True)
    bin_path = cache_dir / f"gh{ext}"

    if bin_path.is_file():
        return bin_path

    archive_filename = f"gh_{GH_VERSION}_{os_name}_{arch}{archive_ext}"
    expected_hash = GH_HASHES.get(archive_filename)
    if not expected_hash:
        print(f"Error: Unsupported platform/architecture combination: {archive_filename}", file=sys.stderr)
        sys.exit(1)

    url = f"https://github.com/cli/cli/releases/download/v{GH_VERSION}/{archive_filename}"
    temp_archive = cache_dir / f"temp_{archive_filename}"

    print(f"Provisioning hermetic gh v{GH_VERSION} ({archive_filename})...", file=sys.stderr)
    try:
        urllib.request.urlretrieve(url, str(temp_archive))
        if not _verify_sha256(temp_archive, expected_hash):
            print(f"SECURITY ERROR: SHA-256 hash mismatch for {archive_filename}!", file=sys.stderr)
            temp_archive.unlink(missing_ok=True)
            sys.exit(1)

        _extract_binary(temp_archive, archive_ext, bin_path)
        if os_name != "windows":
            bin_path.chmod(0o755)
    finally:
        temp_archive.unlink(missing_ok=True)

    return bin_path


def main() -> None:
    gh_bin = ensure_gh_binary()
    args = sys.argv[1:]

    # Forward arguments directly to the gh binary
    if sys.platform != "win32":
        os.execvp(str(gh_bin), [str(gh_bin), *args])
    else:
        sys.exit(subprocess.run([str(gh_bin), *args], check=False).returncode)


if __name__ == "__main__":
    main()
