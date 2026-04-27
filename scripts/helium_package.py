import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

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
    pattern = re.compile(rf"^helium_(?P<version>\d+\.\d+\.\d+(?:\.\d+)?)_{re.escape(arch)}-windows\.zip$", re.I)
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        match = pattern.match(name)
        if match and asset.get("browser_download_url"):
            return match.group("version"), asset
    raise RuntimeError(f"No Helium {arch} Windows zip asset found in release {release.get('tag_name')}.")


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


def remove_path(path):
    path = Path(path)
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


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
            remove_path(local_7zr)

    raise RuntimeError(f"Unable to locate or download 7-Zip. Last error: {last_error}")


def archive_root(entries):
    roots = {entry.split("/", 1)[0] for entry in entries if "/" in entry}
    if len(roots) != 1:
        raise RuntimeError("Unable to determine Helium zip root directory.")
    return roots.pop()


def chromium_version(entries, root):
    pattern = re.compile(rf"^{re.escape(root)}/(?P<version>\d+\.\d+\.\d+\.\d+)\.manifest$", re.I)
    for entry in entries:
        match = pattern.match(entry)
        if match:
            return match.group("version")
    raise RuntimeError("Unable to determine Chromium version from Helium zip.")


def prepare_builder_archive(asset, version, arch, workdir):
    workdir = Path(workdir)
    downloads_dir = workdir / "downloads"
    builder_archive = downloads_dir / f"helium_{version}_{arch}_builder.7z"
    if builder_archive.exists():
        return builder_archive

    source_zip = downloads_dir / asset["name"]
    download_file(asset["browser_download_url"], source_zip)
    stage_dir = downloads_dir / f"helium_{version}_{arch}_builder_stage"
    remove_path(stage_dir)
    stage_dir.mkdir(parents=True, exist_ok=True)

    with ZipFile(source_zip, "r") as source:
        entries = [name for name in source.namelist() if name and not name.endswith("/")]
        root = archive_root(entries)
        browser_version = chromium_version(entries, root)
        root_prefix = f"{root}/"

        for entry in entries:
            if not entry.startswith(root_prefix):
                continue

            relative = entry[len(root_prefix):]
            if not relative:
                continue

            if relative.lower() == "chrome.exe":
                target_path = stage_dir / "Helium-bin" / "chrome.exe"
            else:
                target_path = stage_dir / "Helium-bin" / browser_version / Path(relative)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with source.open(entry) as src, target_path.open("wb") as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)

    seven_zip = find_7z_tool(workdir)
    remove_path(builder_archive)
    result = subprocess.run(
        [str(seven_zip), "a", "-t7z", "-mx=0", str(builder_archive.resolve()), "Helium-bin"],
        cwd=stage_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise RuntimeError("Failed to create Helium builder archive.")

    remove_path(stage_dir)

    return builder_archive


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
        result["installer_path"] = str(prepare_builder_archive(asset, version, args.arch, Path.cwd()))
    else:
        result["url"] = asset["browser_download_url"]
        result["file_name"] = asset["name"]

    print(json.dumps(result))


if __name__ == "__main__":
    sys.exit(main())
