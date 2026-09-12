# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Helium Portable — automated portable build of the [Helium](https://github.com/imputnet/helium) browser for Windows x64, bundled with Chrome++ portability features. The build pipeline runs on GitHub Actions and tracks the latest **stable** release from `imputnet/helium-windows`. Upstream currently publishes only regular (non-prerelease) Releases; the former Preview/prerelease channel has been removed. Every upstream version upgrade creates a new GitHub Release (`create_new_release_on: upgrade`) so history stays downloadable.

## Local Build

```powershell
python -m pip install requests
$env:PYTHONPATH="..\ChromiumPortable"
$env:HELIUM_EXTRACT_INNER="true"
python -m portable_builder --config browser.json --target helium_stable --workdir . build
```

The `HELIUM_EXTRACT_INNER=true` env var is required — it triggers `helium_package.py` to download the upstream Helium zip, restructure it into a builder archive matching the expected `Helium-bin` version_root layout, and pass the local archive path to the builder instead of a direct download URL.

Other CLI commands (all need `$env:PYTHONPATH` and may need `$env:GITHUB_TOKEN`):

```powershell
# Check if upstream has a newer stable version
python -m portable_builder --config browser.json --target helium_stable --workdir . check-targets

# Build and archive any updated targets
python -m portable_builder --config browser.json --target helium_stable --workdir . build-targets

# Verify the finished archives (extract, check the import table, launch the browser)
python -m portable_builder --config browser.json --target helium_stable --workdir . verify-targets

# Render release metadata
python -m portable_builder --config browser.json --target helium_stable --workdir . render-release-targets
```

`verify-targets` skips targets whose `{PREFIX}_UPDATE` env var is `false`, so after a local single-target build use `verify` instead. It needs no `HELIUM_EXTRACT_INNER`.

## Key Files

- **`browser.json`** — Build target config. Defines the single `helium_stable` target and a top-level `release` section with `create_new_release_on: upgrade`, so every upstream version upgrade mints a new GitHub Release instead of replacing assets on the existing one. Asset matching is inferred from `archive_name`. `helium_package.py --channel prerelease` still exists for local experiments but is no longer wired into CI.
- **`scripts/helium_package.py`** — The script provider. Queries `imputnet/helium-windows` releases, selects the latest stable release via `--channel stable` (prerelease is unused in CI), finds the x64 zip asset, and either returns its URL or (with `--extract-inner` / `HELIUM_EXTRACT_INNER`) restructures the zip into a builder-compatible 7z archive. Key behavior: `chrome.exe` goes to `Helium-bin/chrome.exe`, everything else to `Helium-bin/<chromium_version>/...`. It refuses to emit a result unless the GitHub release asset carries a `digest`, verifies the downloaded zip against it, and reports a `sha256` for whatever it hands the builder (the repacked archive in extract-inner mode, the upstream digest otherwise).
- **`chrome++/chrome++.override.ini`** — Only this browser's deviations from the shared baseline. Its command line disables the profile lock, points Helium's browser-only WinSparkle appcast at the reserved `updates.invalid` domain, and disables the default-browser check. The appcast override is required because upstream's updater silently launches a per-user installer under `%LOCALAPPDATA%\imput\Helium\Application`; it does not disable Chromium component updates. The builder merges core's `setdll/chrome++.ini` (upstream baseline) → `setdll/chrome++.defaults.ini` (project-wide defaults) → this file. The effective `data_dir` is `%app%\..\Data` from the baseline: `%app%` is chrome.exe's directory (`Helium/`), so the profile lands one level up, next to the `Helium` folder in the extracted archive. See *chrome++.ini layering* in the workspace `CLAUDE.md`.
- **`chrome++/injectpe.bat`** — Manual DLL injection helper, unused by the automated build (which calls `setdll` directly). It still targets `helium.exe`, a name upstream no longer ships — the executable is `chrome.exe`.
- **`开始.bat`** — Creates a desktop shortcut pointing to `Helium\chrome.exe`, with the WinSparkle appcast and default-browser protections repeated as defense in depth. Do not restore the old broad `--disable-background-networking` switch: it does not stop WinSparkle and may also suppress extension and component updates.
- **`清理Helium安装版注册表.bat`** — Self-contained recovery tool for removing stale installed-Helium Default Apps registrations and resetting only associations that currently point to Helium. Its ASCII PowerShell payload is embedded after a marker and executed directly from memory, so users only need this one file. It backs up touched keys, supports `--dry-run`, never registers the portable build, and leaves browser files/data alone. Keep the entire file ASCII-only with CRLF line endings because localized `cmd.exe` versions may corrupt UTF-8 batch text. The current builder only copies `start_script`, so this recovery tool is not automatically included in release archives.

## Helium-Specific Build Details

- The upstream zip from `imputnet/helium-windows` contains a single root directory with `chrome.exe` at root and versioned files beside it. `helium_package.py` restructures this into `Helium-bin/chrome.exe` + `Helium-bin/<version>/...` to match the builder's expected `version_root` layout.
- The builder's `inject_dll` stage uses `setdll` to inject `version.dll` into `chrome.exe` with a portable relative path. Since `version_dll_location` is `app_root`, the DLL lands next to chrome.exe (not in the version subdirectory). Injection is asserted by parsing the PE import table and requiring `version.dll` to be the *first* import — Chromium natively imports the system `VERSION.dll`, so a weaker check would pass even with no injection at all.
- `exe_name` is `..\\chrome.exe` (relative path from the version subdirectory back to the app root).
- GitHub Releases are keyed to the Helium package version. With `create_new_release_on: upgrade`, every upstream version upgrade creates a new Release; assets on older Releases are left intact.
- Archive filenames and release metadata use the Helium package version, while the internal `Helium-bin/<version>` directory continues to follow the bundled Chromium version required by the upstream layout.
- Upstream `imputnet/helium-windows` currently marks new Releases as regular (not prerelease). Do not reintroduce a Preview target unless upstream starts publishing prereleases again.
