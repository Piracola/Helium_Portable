<div align="center">

# Helium 便携版

集成 Chrome++ 的 [Helium](https://github.com/imputnet/helium) Windows 便携版，由 GitHub Actions 自动构建，提供 x64 与 ARM64 压缩包。

[![最新版本][badge-release]][link-release]
[![总下载量][badge-downloads]][link-release]
[![构建状态][badge-build]][link-actions]
[![许可证][badge-license]][link-license]

**语言 / Language:** **简体中文** · [English](README.en.md)

**[⬇ 下载最新版本][link-release]** · **[📖 使用说明与常见问题][link-site]**

</div>

## 项目简介

本仓库通过 GitHub Actions 定时检查 [imputnet/helium-windows](https://github.com/imputnet/helium-windows) 的 Windows 构建，跟踪最新正式版，下载对应架构的 zip（x64 / ARM64），重组为 `Helium-bin` 布局，注入 Chrome++，再发布为可直接解压使用的便携版。

目前每个上游版本升级都会创建一条新的 GitHub Release。

构建系统由 [ChromiumPortable](https://github.com/Piracola/ChromiumPortable) 提供，本仓库只保存构建配置；本地构建步骤见核心仓的[开发文档](https://github.com/Piracola/ChromiumPortable/blob/main/docs/DEVELOPMENT.md)。

## 快速开始

1. 从 [Releases](https://github.com/Piracola/Helium_Portable/releases/latest) 下载最新压缩包（`Helium_<版本>_<日期>.7z` 为 x64，`Helium_arm64_<版本>_<日期>.7z` 为 Windows on Arm），解压到任意位置。
2. 运行 `开始.bat` 在解压根目录生成 `Helium.lnk` 快捷方式，之后从快捷方式启动。

## 更新

1. 关闭浏览器（重要数据建议先备份 `Data` 目录）。
2. 删除 `Helium` 文件夹或重命名为 `Helium old` 以便回退。
3. 解压新版压缩包内的 `Helium` 文件夹，`Data`、`Cache` 保持不动。

<details>
<summary>C 盘已出现 Helium 安装版怎么办</summary>

Helium Windows 自带的 WinSparkle 更新器会把官方安装器装到 `%LOCALAPPDATA%\imput\Helium\Application`。安装版和便携版使用同一组浏览器注册名，所以安装过程会把原本指向便携版的默认浏览器路径覆盖成 C 盘路径。

1. 先关闭所有 Helium 窗口。
2. 在 Windows「设置 > 应用 > 已安装的应用」中卸载 Helium。
3. 从本仓库下载 [清理Helium安装版注册表.bat](清理Helium安装版注册表.bat)，双击运行并允许管理员权限。它是一个完整的单文件工具，只清理 Helium 的默认应用注册与关联，不会删除浏览器文件、用户数据，也不会注册便携版。
4. 如果卸载后 `%LOCALAPPDATA%\imput\Helium\Application` 仍然存在，确认里面没有需要的数据后再删除 `Helium` 文件夹。
5. 启动 Helium 便携版，在浏览器内部点击「设为默认浏览器」。

清理前，脚本会把涉及的注册表项备份到 `%LOCALAPPDATA%\HeliumPortable\RegistryBackups`。它不依赖同目录下的其他文件，可以单独下载到任意位置运行。只想看看会清理哪些项，可以在命令行运行 `清理Helium安装版注册表.bat --dry-run`，演练模式不会改动注册表。

2026-07-28 之后构建的便携版会在 Chrome++ 层和快捷方式层同时把整体更新清单指向保留的无效域名，从而阻断安装器下载。旧版用户可以在 `Helium\chrome++.ini` 的 `command_line=` 末尾追加：

```text
--custom-update-server-url=https://updates.invalid/ --no-default-browser-check
```

</details>

## 功能特性

- 用户数据与缓存保存在与 `Helium` 文件夹同级的 `Data` 和 `Cache` 文件夹（解压根目录下）
- 集成 Chrome++；以下增强除注明外默认启用，可在 `chrome++\chrome++.ini` 中调整或关闭：
  - 双击关闭标签页、保留最后一个标签页
  - 悬停标签栏时滚轮切换标签页
  - 新建前台标签页打开地址栏内容或书签
  - 免验证系统登录密码即可查看已保存密码
  - 支持右键关闭标签、老板键、翻译快捷键、按键映射、启动/退出钩子等扩展（默认未启用，详见 `chrome++.ini`）
- 阻断 Helium Windows 的整体自动更新，防止官方安装器在 C 盘创建另一份 Helium

<details>
<summary>更改数据目录位置</summary>

数据目录的位置由 `Helium\chrome++.ini` 里的 `data_dir` 和 `cache_dir` 两行决定，默认值是 `%app%\..\Data` 和 `%app%\..\Cache`（`%app%` 代表 `chrome.exe` 所在目录，所以默认落在 `Helium` 文件夹旁边）。值支持绝对路径，目录会自动创建。注意这个文件是 **UTF-16 编码**（记事本另存时选「Unicode」）。

默认路径相对于主程序目录，移动整个文件夹不需要修改。需要将数据存放到程序目录之外时，可改用绝对路径。

</details>

## 卸载

删除解压根目录即可，便携版不写注册表。

## 相关项目

- [ChromiumPortable](https://github.com/Piracola/ChromiumPortable)：通用构建核心
- [Chrome-Portable](https://github.com/Piracola/Chrome-Portable)：同系列 Google Chrome 便携版
- [Edge_Portable](https://github.com/Piracola/Edge_Portable)：同系列 Microsoft Edge 便携版

<details>
<summary>致谢</summary>

| 项目 | 说明 |
| --- | --- |
| [imputnet/helium](https://github.com/imputnet/helium) | Helium 浏览器源码 |
| [Bush2021/chrome_plus](https://github.com/Bush2021/chrome_plus) | Chrome++ 便携化组件 |
| [Piracola/ChromiumPortable](https://github.com/Piracola/ChromiumPortable) | 通用便携版构建核心 |

</details>

## 许可证

本仓库构建脚本遵循 MIT 许可证。

---

<div align="center">

<sub>Built and maintained by</sub>

**Piracola**

</div>

<!-- 徽标定义：中文标签需 percent-encode，否则 shields.io 无法解析。 -->
<!-- 修改标签文字时请一并更新编码，例如 最新版本 -> %E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC -->
[badge-release]: https://img.shields.io/github/v/release/Piracola/Helium_Portable?display_name=tag&style=flat-square&color=5b5bd6&label=%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC
[badge-downloads]: https://img.shields.io/github/downloads/Piracola/Helium_Portable/total?style=flat-square&color=2ea043&label=%E6%80%BB%E4%B8%8B%E8%BD%BD%E9%87%8F
[badge-build]: https://img.shields.io/github/actions/workflow/status/Piracola/Helium_Portable/build.yml?branch=main&style=flat-square&label=%E6%9E%84%E5%BB%BA%E7%8A%B6%E6%80%81
[badge-license]: https://img.shields.io/github/license/Piracola/Helium_Portable?style=flat-square&color=6e7681&label=%E8%AE%B8%E5%8F%AF%E8%AF%81

[link-release]: https://github.com/Piracola/Helium_Portable/releases/latest
[link-site]: https://piracola.github.io/ChromiumPortable/helium/
[link-actions]: https://github.com/Piracola/Helium_Portable/actions/workflows/build.yml
[link-license]: https://github.com/Piracola/Helium_Portable/blob/main/LICENSE
