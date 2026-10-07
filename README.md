# TabFlow

[简体中文](README.md) | [English](README_EN.md)

![Coded by Gemini 3.8 Flash](https://img.shields.io/badge/Coded%20by-Gemini%203.8%20Flash-4285F4?style=flat-square&logo=google&logoColor=white)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

Windows 轻量级鼠标手势工具：**按住鼠标右键 + 滚动滚轮** 快速切换浏览器或应用标签页。

---

## 功能特性

- **右键 + 滚轮切标签**：向上滚向前切换，向下滚向后切换，支持随滚动刻度连续切换。
- **防误触处理**：
  - 手势触发时不触发页面滚动，松开时不误弹右键菜单。
  - 普通右键单击正常弹出上下文菜单。
  - 手势结束后自动释放修饰键，避免拖选文字粘滞。
- **低延迟**：基于 Win32 鼠标低级钩子（`WH_MOUSE_LL`），指针移动事件直接透传，资源占用极低。
- **多应用支持**：
  - 默认支持 Chrome、Edge、Firefox 等主流浏览器。
  - 支持自定义添加目标进程（如 VS Code `code.exe`），或开启全局模式。
- **系统集成**：
  - 适配 Windows 任务栏应用组（任务栏与任务管理器图标一致）及高分屏 DPI 缩放。
  - 单实例运行限制（防止多开）、最小化到系统托盘、开机自启。
- **多语言支持**：内置中文与英文（English），支持跟随系统语言或在界面一键实时切换。

---

## 运行方式

### 1. 独立 EXE（推荐）
直接运行 `dist\TabFlow.exe`（无需安装 Python 环境）。

### 2. 源码运行
```bash
pip install -r requirements.txt
python main.py
```
或直接双击根目录下的 `run.bat`（静默启动无控制台黑框）。

---

## 打包

双击运行根目录下的 `build.bat` 即可生成单文件 EXE。

产物位于 `dist/TabFlow.exe`；编译临时目录 `build/` 可随时删除。

---

## 快捷键模式

主界面可在“手势与快捷键”中切换：

| 模式 | 左切 (上一标签) | 右切 (下一标签) | 适用 |
| :--- | :--- | :--- | :--- |
| **标准模式 (默认)** | `Ctrl + Shift + Tab` | `Ctrl + Tab` | 大多数浏览器及编辑器 |
| **翻页模式** | `Ctrl + PageUp` | `Ctrl + PageDown` | 部分特定应用 |

---

## 目录结构

```text
tab/
├── main.py             # 主界面及生命周期管理
├── gesture_engine.py   # 鼠标钩子与手势状态机
├── tray_manager.py     # 托盘菜单与状态图标
├── config_manager.py   # 配置读写与开机自启
├── i18n.py             # 中英双语国际化
├── app.ico             # 应用图标
├── build.bat           # 打包脚本
├── run.bat             # 源码静默启动脚本
├── requirements.txt    # 依赖声明
├── .gitignore          # Git 忽略配置
├── LICENSE             # GPL-3.0 开源协议
├── README.md           # 中文文档
├── README_EN.md        # 英文文档
└── dist/TabFlow.exe    # 打包产物
```

---

## 常见问题

- **杀软报毒/拦截？**
  程序使用了全局鼠标钩子捕获滚轮事件，且由 PyInstaller 单文件打包，可能触发部分杀软误报，添加信任即可。
- **某些应用中无效？**
  如果目标程序（如以管理员身份打开的编辑器）具有管理员权限，TabFlow 也需以管理员身份运行才能注入按键。

---

## 开源协议

本项目采用 [GNU General Public License v3.0 (GPL-3.0)](LICENSE) 开源协议。
