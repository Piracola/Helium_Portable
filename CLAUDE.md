# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Helium Portable — automated portable build of the [Helium](https://github.com/imputnet/helium) browser for Windows x64, bundled with Chrome++ portability features. The build pipeline runs on GitHub Actions and tracks the latest **stable** release from `imputnet/helium-windows`. Upstream currently publishes only regular (non-prerelease) Releases; the former Preview/prerelease channel has been removed. Every upstream version upgrade creates a new GitHub Release (`create_new_release_on: upgrade`) so history stays downloadable.

The pipeline uses the prebuilt Rust engine from `Piracola/ChromiumPortable`'s `v2` Release (self-contained zip; the workflow downloads, sha256-verifies, and unpacks it into `_engine/`). This repo contains no builder code — only configuration (`browser.json`), Chrome++ overrides, and user-facing batch files.

## Local Build

```powershell
# Download the engine once (or reuse an existing copy)
gh release download v2 --repo Piracola/ChromiumPortable --pattern 'portable-builder-windows-x64.zip*' --dir _engine
Expand-Archive _engine/portable-builder-windows-x64.zip -DestinationPath _engine

$env:GITHUB_TOKEN = (gh auth token)   # release checks rate-limit without it
_engine\portable-builder-windows-x64\portable-builder.exe --config browser.json --target helium_stable --workdir . build
```

The engine auto-detects its own `setdll/` + `catalog/` (they ship inside the bundle, beside the exe). Other commands: `check`, `archive`, `verify` (single-target; `verify` is the meaningful one — it extracts the archive, re-checks the PE import table, launches the browser, and asserts the portable `Data/` directory lands inside the extracted tree), and the `*-targets` variants used by CI (`check-targets` etc. take the target list as a **positional** argument, not `--target`).

## Key Files

- **`browser.json`** — Build target config. The provider is the engine's builtin `github_release` channel (`imputnet/helium-windows`, channel `stable`, asset pattern with a named `version` group); it refuses to resolve an asset without a `digest`. `repack_layout: version_root` reshapes the upstream flat zip (`chrome.exe` beside DLLs) into `Helium-bin/chrome.exe` + `Helium-bin/<version>/...` during prepare — the version comes from the upstream zip's `<version>.manifest`, which currently carries the Helium release version. Top-level `release` section sets `create_new_release_on: upgrade`, so every upstream version upgrade mints a new GitHub Release instead of replacing assets on the existing one. Asset matching is inferred from `archive_name`.
- **`chrome++/chrome++.override.ini`** — Only this browser's deviations from the shared baseline. Its command line disables the profile lock, points Helium's browser-only WinSparkle appcast at the reserved `updates.invalid` domain, and disables the default-browser check. The appcast override is required because upstream's updater silently launches a per-user installer under `%LOCALAPPDATA%\imput\Helium\Application`; it does not disable Chromium component updates. The engine merges the bundle's `setdll/chrome++.ini` (upstream baseline) → `setdll/chrome++.defaults.ini` (project-wide defaults) → this file. The effective `data_dir` is `%app%\..\Data` from the baseline: `%app%` is chrome.exe's directory (`Helium/`), so the profile lands one level up, next to the `Helium` folder in the extracted archive. See *chrome++.ini layering* in the workspace `CLAUDE.md`.
- **`chrome++/injectpe.bat`** — Manual DLL injection helper, unused by the automated build (which calls `setdll` directly). It still targets `helium.exe`, a name upstream no longer ships — the executable is `chrome.exe`.
- **`开始.bat`** — Creates a desktop shortcut pointing to `Helium\chrome.exe`, with the WinSparkle appcast and default-browser protections repeated as defense in depth. Do not restore the old broad `--disable-background-networking` switch: it does not stop WinSparkle and may also suppress extension and component updates.
- **`清理Helium安装版注册表.bat`** — Self-contained recovery tool for removing stale installed-Helium Default Apps registrations and resetting only associations that currently point to Helium. Its ASCII PowerShell payload is embedded after a marker and executed directly from memory, so users only need this one file. It backs up touched keys, supports `--dry-run`, never registers the portable build, and leaves browser files/data alone. Keep the entire file ASCII-only with CRLF line endings because localized `cmd.exe` versions may corrupt UTF-8 batch text. The current builder only copies `start_script`, so this recovery tool is not automatically included in release archives.

## Helium-Specific Build Details

- The upstream zip from `imputnet/helium-windows` contains a single root directory with `chrome.exe` at root and versioned files beside it. The engine's `repack_layout` (in `browser.json`) restructures this into `Helium-bin/chrome.exe` + `Helium-bin/<version>/...` to match the builder's expected `version_root` layout.
- The builder's `inject_dll` stage uses `setdll` to inject `version.dll` into `chrome.exe` with a portable relative path. Since `version_dll_location` is `app_root`, the DLL lands next to chrome.exe (not in the version subdirectory). Injection is asserted by parsing the PE import table and requiring `version.dll` to be the *first* import — Chromium natively imports the system `VERSION.dll`, so a weaker check would pass even with no injection at all.
- `exe_name` is `..\\chrome.exe` (relative path from the version subdirectory back to the app root).
- GitHub Releases are keyed to the Helium package version. With `create_new_release_on: upgrade`, every upstream version upgrade creates a new Release; assets on older Releases are left intact.
- Archive filenames and release metadata use the Helium package version; the internal `Helium-bin/<version>` directory name comes from the upstream zip's manifest, which upstream currently keys to the release version.
- Upstream `imputnet/helium-windows` currently marks new Releases as regular (not prerelease). Do not reintroduce a Preview target unless upstream starts publishing prereleases again. (The `github_release` provider's `channel` key still supports `prerelease` if that ever changes.)
