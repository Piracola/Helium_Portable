import argparse
import json
import os
import re
import sys

import requests


DEFAULT_REPO = "imputnet/helium-windows"


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--arch", default="x64", choices=("x64", "arm64"))
    args = parser.parse_args()

    release = latest_release(args.repo)
    asset_version, asset = find_asset(release, args.arch)
    tag_version = str(release.get("tag_name") or "").lstrip("v")
    version = tag_version or asset_version

    print(json.dumps({
        "version": version,
        "url": asset["browser_download_url"],
        "file_name": asset["name"],
        "verify_ssl": True
    }))


if __name__ == "__main__":
    sys.exit(main())
