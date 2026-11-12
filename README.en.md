<div align="center">

# Helium Portable

Portable Windows build of [Helium](https://github.com/imputnet/helium) with Chrome++ integrated, built automatically by GitHub Actions, in x64 and ARM64 archives.

[![Latest release][badge-release]][link-release]
[![Total downloads][badge-downloads]][link-release]
[![Build status][badge-build]][link-actions]
[![License][badge-license]][link-license]

**Language / 语言:** [简体中文](README.md) · **English**

**[⬇ Download the latest release][link-release]** · **[📖 Usage guide & FAQ][link-site]**

</div>

## About

GitHub Actions checks the Windows builds from [imputnet/helium-windows](https://github.com/imputnet/helium-windows) on a schedule, tracks the latest stable release, downloads the zip for each architecture (x64 / ARM64), reshapes it into the `Helium-bin` layout, injects Chrome++, and publishes it as an extract-and-run portable build.

For now, every upstream version upgrade creates a new GitHub Release.

The build system is provided by [ChromiumPortable](https://github.com/Piracola/ChromiumPortable); this repository only holds the build configuration. For a local build, see the core repository's [development docs](https://github.com/Piracola/ChromiumPortable/blob/main/docs/DEVELOPMENT.md).

## Quick start

1. Download the latest archive from [Releases](https://github.com/Piracola/Helium_Portable/releases/latest) — `Helium_<version>_<date>.7z` for x64, `Helium_arm64_<version>_<date>.7z` for Windows on Arm — and extract it anywhere.
2. Run `开始.bat` to create the `Helium.lnk` shortcut inside the extraction folder, then launch from that shortcut.

## Updating

1. Close the browser (back up the `Data` folder first if the data matters).
2. Delete the `Helium` folder, or rename it to `Helium old` for a rollback option.
3. Extract the `Helium` folder from the new archive; leave `Data` and `Cache` alone.

## What if an installed Helium shows up on my C: drive?

Helium's built-in WinSparkle updater on Windows installs the official installer into `%LOCALAPPDATA%\imput\Helium\Application`. The installed build and the portable build share the same browser registration names, so installing overwrites the default-browser path that pointed at the portable copy with a C: path.

1. Close every Helium window.
2. Uninstall Helium in Windows Settings > Apps > Installed apps.
3. Download [清理Helium安装版注册表.bat](清理Helium安装版注册表.bat) from this repository, double-click it, and allow administrator rights. It is a self-contained single-file tool that only clears Helium's Default Apps registrations and associations — it deletes no browser files or user data, and it does not register the portable build.
4. If `%LOCALAPPDATA%\imput\Helium\Application` survives the uninstall, make sure there is nothing you need in it before deleting the `Helium` folder.
5. Start the portable Helium and click "Set as default browser" inside the browser.

Before cleaning, the script backs up the registry keys involved to `%LOCALAPPDATA%\HeliumPortable\RegistryBackups`. It depends on no other file in its folder, so you can download it on its own and run it from anywhere. To preview what it would clean, run `清理Helium安装版注册表.bat --dry-run` from a command prompt — a dry run never touches the registry.

Portable builds made after 2026-07-28 point the whole update manifest at a reserved invalid domain, at both the Chrome++ layer and the shortcut layer, so the installer download is blocked. On older builds, append this to the end of `command_line=` in `Helium\chrome++.ini`:

```text
--custom-update-server-url=https://updates.invalid/ --no-default-browser-check
```

## Features

- Profile data and cache live in the `Data` and `Cache` folders next to `Helium` (at the extraction root)
- Chrome++ is included; everything below is enabled by default unless noted — adjust or switch it off in `chrome++\chrome++.ini`:
  - Double-click a tab to close it; the last tab stays open
  - Scroll the mouse wheel over the tab strip to switch tabs
  - Open whatever sits in the address bar, or a bookmark, in a new foreground tab
  - View saved passwords without going through the Windows sign-in prompt
  - Optional extras: close tabs with the right mouse button, boss key, translate shortcut, key remapping, start/exit hooks and more (off by default; see `chrome++.ini`)
- Helium's own auto-update is blocked, so the official installer never creates a second Helium on your C: drive

## Changing the data directory

The location is set by the `data_dir` and `cache_dir` lines in `Helium\chrome++.ini`. Defaults are `%app%\..\Data` and `%app%\..\Cache`, where `%app%` is the folder holding `chrome.exe`, so data lands next to `Helium`. Absolute paths are accepted and directories are created as needed. Note that the file is **UTF-16 encoded** (pick "Unicode" when saving from Notepad).

Because the defaults are relative to the program folder, moving the whole tree needs no edits. Switch to an absolute path if you want data stored outside the program folder.

## Uninstalling

Delete the extraction root. The portable build writes nothing to the registry.

## Related projects

- [ChromiumPortable](https://github.com/Piracola/ChromiumPortable): shared build core
- [Chrome-Portable](https://github.com/Piracola/Chrome-Portable): the Google Chrome portable build
- [Edge_Portable](https://github.com/Piracola/Edge_Portable): the Microsoft Edge portable build

## Credits

| Project | Role |
| --- | --- |
| [imputnet/helium](https://github.com/imputnet/helium) | Helium browser source |
| [Bush2021/chrome\_plus](https://github.com/Bush2021/chrome_plus) | Chrome++ portability components |
| [Piracola/ChromiumPortable](https://github.com/Piracola/ChromiumPortable) | Shared portable build core |

## License

The build scripts in this repository are MIT licensed.

---

<div align="center">

<sub>Built and maintained by</sub>

**Piracola**

</div>

<!-- Badge labels: percent-encode spaces, otherwise shields.io cannot parse the URL. -->
[badge-release]: https://img.shields.io/github/v/release/Piracola/Helium_Portable?display_name=tag&style=flat-square&color=5b5bd6&label=latest%20release
[badge-downloads]: https://img.shields.io/github/downloads/Piracola/Helium_Portable/total?style=flat-square&color=2ea043&label=total%20downloads
[badge-build]: https://img.shields.io/github/actions/workflow/status/Piracola/Helium_Portable/build.yml?branch=main&style=flat-square&label=build%20status
[badge-license]: https://img.shields.io/github/license/Piracola/Helium_Portable?style=flat-square&color=6e7681&label=license

[link-release]: https://github.com/Piracola/Helium_Portable/releases/latest
[link-site]: https://piracola.github.io/ChromiumPortable/en/helium/
[link-actions]: https://github.com/Piracola/Helium_Portable/actions/workflows/build.yml
[link-license]: https://github.com/Piracola/Helium_Portable/blob/main/LICENSE
