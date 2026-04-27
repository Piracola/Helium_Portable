import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import requests


DEFAULT_REPO = "imputnet/helium-windows"
SEVEN_ZIP_URLS = (
    "https://www.7-zip.org/a/7zr.exe",
    "https://raw.githubusercontent.com/develar/7zip-bin/master/win/x64/7za.exe",
)
SYSTEM_7Z_PATHS = (
    r"C:\Program Files\7-Zip\7z.exe",
    r"C:\Program Files (x86)\7-Zip\7z.exe",
)


def github_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Helium_Portable builder",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def latest_release(repo):
    response = requests.get(
        f"https://api.github.com/repos/{repo}/releases/latest",
        headers=github_headers(),
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def find_asset(release, arch):
    pattern = re.compile(rf"^helium_(?P<version>\d+\.\d+\.\d+(?:\.\d+)?)_{re.escape(arch)}-installer\.exe$", re.I)
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        match = pattern.match(name)
        if match and asset.get("browser_download_url"):
            return match.group("version"), asset
    raise RuntimeError(f"No Helium {arch} installer asset found in release {release.get('tag_name')}.")


def download_file(url, path, verify_ssl=True):
    path = Path(path)
    if path.exists():
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, verify=verify_ssl, headers=github_headers(), timeout=120) as response:
        response.raise_for_status()
        with path.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)
    return path


def find_7z_tool(workdir):
    for path in SYSTEM_7Z_PATHS:
        if Path(path).exists():
            return path

    path_7z = shutil.which("7z") or shutil.which("7za") or shutil.which("7zr")
    if path_7z:
        return path_7z

    local_7zr = Path(workdir) / "7zr.exe"
    if local_7zr.exists():
        return str(local_7zr)

    last_error = None
    for url in SEVEN_ZIP_URLS:
        try:
            download_file(url, local_7zr)
            return str(local_7zr)
        except Exception as exc:
            last_error = exc
            if local_7zr.exists():
                local_7zr.unlink()

    raise RuntimeError(f"Unable to locate or download 7-Zip. Last error: {last_error}")


def extract_archive(seven_zip, archive, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [str(seven_zip), "x", str(archive), "-y", f"-o{output_dir}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Extraction failed: {archive}")


def prepare_inner_archive(asset, version, arch, workdir):
    workdir = Path(workdir)
    downloads_dir = workdir / "downloads"
    inner_archive = downloads_dir / f"helium_{version}_{arch}.7z"
    if inner_archive.exists():
        return inner_archive

    installer_path = downloads_dir / asset["name"]
    download_file(asset["browser_download_url"], installer_path)

    extract_dir = downloads_dir / f"helium_installer_{version}_{arch}"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_archive(find_7z_tool(workdir), installer_path, extract_dir)

    matches = sorted(extract_dir.rglob("helium.7z"))
    if not matches:
        raise FileNotFoundError(f"helium.7z not found after extracting {installer_path}")

    shutil.copy2(matches[0], inner_archive)
    return inner_archive


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--arch", default="x64", choices=("x64", "arm64"))
    parser.add_argument("--extract-inner", action="store_true")
    args = parser.parse_args()

    release = latest_release(args.repo)
    asset_version, asset = find_asset(release, args.arch)
    tag_version = str(release.get("tag_name") or "").lstrip("v")
    version = tag_version or asset_version
    extract_inner = args.extract_inner or os.getenv("HELIUM_EXTRACT_INNER", "").lower() in ("1", "true", "yes")

    result = {
        "version": version,
        "verify_ssl": True
    }

    if extract_inner:
        result["installer_path"] = str(prepare_inner_archive(asset, version, args.arch, Path.cwd()))
    else:
        result["url"] = asset["browser_download_url"]
        result["file_name"] = asset["name"]

    print(json.dumps(result))


if __name__ == "__main__":
    sys.exit(main())
