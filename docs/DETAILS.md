# Helium 便携版：设置与构建细节

本文收录安装版清理、自动更新阻断与仓库关系说明。安装、更新、功能配置见仓库根目录的 [README](../README.md)，使用说明与常见问题见 [下载页面](https://piracola.github.io/ChromiumPortable/helium/)。

## C 盘已出现 Helium 安装版怎么办

Helium Windows 自带的 WinSparkle 更新器会把官方安装器安装到 `%LOCALAPPDATA%\imput\Helium\Application`。

安装版和便携版使用同一组浏览器注册名，所以安装过程会把原本指向便携版的默认浏览器路径覆盖成 C 盘路径。

1. 先关闭所有 Helium 窗口。
2. 在 Windows「设置 > 应用 > 已安装的应用」中卸载 Helium。
3. 下载并双击 `清理Helium安装版注册表.bat`，然后允许管理员权限。它是一个完整的单文件工具，只清理 Helium 的默认应用注册与关联，不会删除浏览器文件、用户数据或注册便携版。
4. 如果卸载后 `%LOCALAPPDATA%\imput\Helium\Application` 仍存在，确认里面没有需要的数据后再删除 `Helium` 文件夹。
5. 启动 Helium 便携版，在浏览器内部点击“设为默认浏览器”。

清理前，脚本会把涉及的注册表项备份到 `%LOCALAPPDATA%\HeliumPortable\RegistryBackups`。它不依赖同目录下的其他文件，可以单独下载到任意位置运行。如需只查看计划清理的项目，可在命令行运行 `清理Helium安装版注册表.bat --dry-run`，演练模式不会修改注册表。

2026-07-28 之后构建的便携版会在 Chrome++ 层和快捷方式层同时把整体更新清单指向保留的无效域名，从而阻断安装器下载。旧版用户可在 `Helium\chrome++.ini` 的 `command_line=` 末尾追加：

```text
--custom-update-server-url=https://updates.invalid/ --no-default-browser-check
```

## 本地构建

本地构建由 [ChromiumPortable](https://github.com/Piracola/ChromiumPortable) 的图形构建器完成，操作步骤见其 [开发文档](https://github.com/Piracola/ChromiumPortable/blob/main/docs/DEVELOPMENT.md)。

## 相关仓库

- [ChromiumPortable](https://github.com/Piracola/ChromiumPortable)：通用构建核心
- [Chrome-Portable](https://github.com/Piracola/Chrome-Portable)：同系列 Google Chrome 便携版
- [Edge_Portable](https://github.com/Piracola/Edge_Portable)：同系列 Microsoft Edge 便携版
