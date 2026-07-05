# Helium 便携版

全自动构建的 [Helium](https://github.com/imputnet/helium) Windows x64 便携版，集成 Chrome++ 便携化组件。

[![build status](https://github.com/Piracola/Helium_Portable/actions/workflows/build.yml/badge.svg)](https://github.com/Piracola/Helium_Portable/actions/workflows/build.yml)

> 想了解构建系统或新增浏览器？见 [ChromiumPortable](https://github.com/Piracola/ChromiumPortable)——本仓库仅是其构建配置之一。

## 仓库导航

- [ChromiumPortable（主仓库/构建核心）](https://github.com/Piracola/ChromiumPortable)：Chromium 系便携版构建核心，提供可复用的自动构建、打包和发行流程。
- [Chrome-Portable](https://github.com/Piracola/Chrome-Portable)：同系列 Google Chrome 便携版项目。
- [Edge_Portable](https://github.com/betacola/Edge_Portable)：同系列 Microsoft Edge 便携版项目。

## 项目简介

本仓库通过 GitHub Actions 定时检查 [imputnet/helium-windows](https://github.com/imputnet/helium-windows) 的 Windows 构建，分别跟踪最新正式版与最新预发行版，下载 x64 installer，解包其中的 `Helium-bin`，注入 Chrome++，再发布为可直接解压使用的便携版。

## 功能特性

- 用户数据与缓存保存在 `Helium\Data` 和 `Helium\Cache`
- 集成 Chrome++，以下功能均已默认启用，可在 `chrome++\chrome++.ini` 中调整或关闭：
  - 双击关闭标签页、保留最后一个标签页
  - 悬停标签栏时滚轮切换标签页
  - 新建前台标签页打开地址栏内容或书签
  - 免验证系统登录密码即可查看已保存密码
  - 支持右键关闭标签、老板键、翻译快捷键、按键映射、启动/退出钩子等扩展（默认未启用，详见 `chrome++.ini`）
- 跟随 Helium Windows x64 正式版自动检查和发布
- 同一个 GitHub Release 同时提供正式版便携包和最新预发行版便携包
- 当正式版创建新 release 而预发行版未更新时，会自动沿用上一版 preview 压缩包，保持同一个 release 下两个包都可下载

## 快速开始

**安装**

1. 访问 [Releases](https://github.com/Piracola/Helium_Portable/releases/latest) 下载最新压缩包。
2. `Helium_...` 为正式版，`Helium_Preview_...` 为预发行版。
3. 解压到任意目录。
4. 运行 `开始.bat` 创建桌面快捷方式，或直接启动 `Helium\chrome.exe`。

**更新**

保留旧版 `Helium\Data`（重要数据建议先备份），删除旧版 `Helium` 文件夹后解压新版到同级目录，再把 `Data` 放回新版 `Helium` 文件夹。

**卸载**

删除 `Helium` 文件夹即可完成卸载（便携，不写注册表）。

**本地构建**（Windows + Python 3，需将 `ChromiumPortable` 检出到同级目录）

`HELIUM_EXTRACT_INNER=true` 用于触发 `helium_package.py` 把上游 zip 重组为构建器兼容的 `Helium-bin` 布局；更多细节见 `CLAUDE.md`。

```powershell
python -m pip install requests
$env:PYTHONPATH="..\ChromiumPortable"
$env:HELIUM_EXTRACT_INNER="true"
python -m portable_builder --config browser.json --target helium_stable --workdir . build
python -m portable_builder --config browser.json --target helium_prerelease --workdir . build
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
