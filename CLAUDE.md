# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Helium Portable — automated portable build of the [Helium](https://github.com/imputnet/helium) browser for Windows x64, bundled with Chrome++ portability features. The build pipeline runs on GitHub Actions, tracks both the latest stable release and the latest prerelease from `imputnet/helium-windows`, and publishes both portable 7z archives into the same GitHub Release keyed by the stable version.

## Local Build

```powershell
python -m pip install requests
$env:PYTHONPATH="..\ChromiumPortable"
$env:HELIUM_EXTRACT_INNER="true"
python -m portable_builder --config browser.json --target helium_stable --workdir . build
python -m portable_builder --config browser.json --target helium_prerelease --workdir . build
```

The `HELIUM_EXTRACT_INNER=true` env var is required — it triggers `helium_package.py` to download the upstream Helium zip, restructure it into a builder archive matching the expected `Helium-bin` version_root layout, and pass the local archive path to the builder instead of a direct download URL.

Other CLI commands (all need `$env:PYTHONPATH` and may need `$env:GITHUB_TOKEN`):

```powershell
# Check if upstream has a newer stable or prerelease version
python -m portable_builder --config browser.json --target helium_stable,helium_prerelease --workdir . check-targets

# Build and archive any updated targets
python -m portable_builder --config browser.json --target helium_stable,helium_prerelease --workdir . build-targets

# Render release metadata for the shared release
python -m portable_builder --config browser.json --target helium_stable,helium_prerelease --workdir . render-release-targets
```

## Key Files

- **`browser.json`** — Build target config. It defines `helium_stable` and `helium_prerelease`, both using the same packaging layout, and a shared top-level `release` section so one GitHub Release carries both assets. The stable target controls the release tag/title.
- **`scripts/helium_package.py`** — The script provider. Queries `imputnet/helium-windows` releases, selects either the latest stable or latest prerelease based on `--channel`, finds the x64 zip asset, and either returns its URL or (with `--extract-inner` / `HELIUM_EXTRACT_INNER`) restructures the zip into a builder-compatible 7z archive. Key behavior: `chrome.exe` goes to `Helium-bin/chrome.exe`, everything else to `Helium-bin/<chromium_version>/...`.
- **`chrome++/chrome++.ini`** — Chrome++ config with `data_dir=%app%\Data` and `cache_dir=%app%\Cache` (relative to chrome.exe's directory, since `ini_location` is `app_root`).
- **`chrome++/injectpe.bat`** — Manual DLL injection script (targets `helium.exe`; the automated builder uses `setdll` directly).
- **`开始.bat`** — Creates a desktop shortcut pointing to `Helium\chrome.exe` with `--disable-background-networking` flag.

## Helium-Specific Build Details

- The upstream zip from `imputnet/helium-windows` contains a single root directory with `chrome.exe` at root and versioned files beside it. `helium_package.py` restructures this into `Helium-bin/chrome.exe` + `Helium-bin/<version>/...` to match the builder's expected `version_root` layout.
- The builder's `inject_dll` stage uses `setdll` to inject `version.dll` into `chrome.exe` with a portable relative path. Since `version_dll_location` is `app_root`, the DLL lands next to chrome.exe (not in the version subdirectory).
- `exe_name` is `..\\chrome.exe` (relative path from the version subdirectory back to the app root).
- New GitHub Releases are still keyed to the stable version tag. If only the upstream prerelease changes, the workflow updates the existing latest release body and replaces only the preview asset.
- Archive filenames and release metadata should use the Helium package version, while the internal `Helium-bin/<version>` directory continues to follow the bundled Chromium version required by the upstream layout.
