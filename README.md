# Helium 便携版

全自动构建的 [Helium](https://github.com/imputnet/helium) Windows x64 便携版，集成 Chrome++ 便携化组件。

[![build status](https://github.com/Piracola/Helium_Portable/actions/workflows/build.yml/badge.svg)](https://github.com/Piracola/Helium_Portable/actions/workflows/build.yml)

## 项目简介

本仓库通过 GitHub Actions 定时检查 [imputnet/helium-windows](https://github.com/imputnet/helium-windows) 的最新 Windows 构建，下载 x64 installer，解包其中的 `Helium-bin`，注入 Chrome++，再发布为可直接解压使用的便携版。

## 相关项目

- [ChromiumPortable](https://github.com/Piracola/ChromiumPortable)：Chromium 系便携版构建核心，提供可复用的自动构建、打包和发行流程。
- [Chrome-Portable](https://github.com/Piracola/Chrome-Portable)：同系列 Google Chrome 便携版子项目。
- [Edge_Portable](https://github.com/betacola/Edge_Portable)：同系列 Microsoft Edge 便携版子项目。

## 功能特性

- 用户数据与缓存保存在 `Helium\Data` 和 `Helium\Cache`
- 集成 Chrome++，可在 `chrome++\chrome++.ini` 中调整增强选项
- 跟随 Helium Windows x64 Release 自动检查和发布

## 快速开始

**安装**

1. 访问 [Releases](https://github.com/Piracola/Helium_Portable/releases/latest) 下载最新压缩包。
2. 解压到任意目录。
3. 运行 `开始.bat` 创建桌面快捷方式，或直接启动 `Helium\chrome.exe`。

**更新**

保留旧版 `Helium\Data` 后，删除旧版程序文件并解压新版即可。重要数据建议先备份。

**本地构建**

```powershell
python -m pip install requests
$env:PYTHONPATH="..\ChromiumPortable"
python -m portable_builder --config browser.json --target helium_stable --workdir . build
```

## 致谢

| 项目 | 说明 |
| --- | --- |
| [imputnet/helium](https://github.com/imputnet/helium) | Helium 浏览器源码 |
| [imputnet/helium-windows](https://github.com/imputnet/helium-windows) | Helium Windows 构建发布 |
| [Bush2021/chrome_plus](https://github.com/Bush2021/chrome_plus) | Chrome++ 便携化组件 |
| [Piracola/ChromiumPortable](https://github.com/Piracola/ChromiumPortable) | 通用便携版构建核心 |

## 许可证

本仓库构建脚本遵循 MIT 许可证。Helium、Chromium 与 Chrome++ 的版权归各自项目所有。
