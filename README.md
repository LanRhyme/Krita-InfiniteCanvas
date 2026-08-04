<div align="center">

# Krita Infinite Canvas

<p>
  <a href="https://qm.qq.com/q/mtg1yNCi1q"><img alt="QQ" src="https://img.shields.io/badge/QQ-729283213-12B7F5?style=for-the-badge&logo=qq&logoColor=white"></a>
  <a href="https://afdian.com/a/LanRhyme" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/afdian-@LanRhyme-946ce6?style=for-the-badge&logo=afdian&logoColor=white" alt="afdian"></a>
</p>

为 Krita 提供类似 MyPaint 的无限画布无感扩充功能，顶层独立菜单、四向手动扩充与图层紧贴裁切

</div>

## 功能特性

- **顶层导航栏主菜单**：启动后在 Krita 顶部菜单栏追加独立的 **无限画布** 菜单项，快速开启与配置
- **动态无感扩充**：实时检测画师笔触包围盒，贴近边缘（默认 150px）时自动无感向外扩展画布空间
- **四向定向扩展**：提供向左、向右、向上、向下独立的扩展动作，支持单独绑定快捷键
- **精准紧贴图层裁切**：自动过滤背景图层与填充层，仅识别实际线条并精细缩减画布至紧贴绘制内容
- **安全扩展上限保护**：内置最大尺寸上限（默认 20000px），防止无限扩充导致内存溢出
- **用户首选项配置**：支持自定义防线阈值、扩充步长、检测频率及新建文档自动激活

## 兼容性

| 操作系统 | Krita 版本 | Qt 引擎 | 状态 |
| ---------- | ------------ | --------- | ------ |
| Linux x86_64 | 5.x / 6.x | Qt5 / Qt6 | 完全支持 |
| Windows x64 | 5.x / 6.x | Qt5 / Qt6 | 完全支持 |
| macOS | 5.x / 6.x | Qt5 / Qt6 | 完全支持 |

插件为纯 Python 实现，兼容 PyQt5 与 PyQt6 双版本环境

## 安装说明

### Linux

```bash
cp -r infinite_canvas ~/.local/share/krita/pykrita/
cp infinite_canvas.desktop ~/.local/share/krita/pykrita/infinite_canvas.desktop
```

重启 Krita，进入 **设置 → 配置 Krita → Python 插件管理器**，勾选 **Infinite Canvas**

### Windows

1. 将 `infinite_canvas` 文件夹复制到 `%APPDATA%\krita\pykrita\`
2. 将 `infinite_canvas.desktop` 复制到 `%APPDATA%\krita\pykrita\infinite_canvas.desktop`
3. 重启 Krita 并开启 **Infinite Canvas**

## 目录结构

- `infinite_canvas`：插件核心 Python 源码
  - `config.py`：首选项 JSON 持久化管理
  - `settings_dialog.py`：图形化设置对话框
  - `infinite_canvas.py`：顶层菜单挂载、边缘检测与裁剪逻辑
- `infinite_canvas.desktop`：插件元数据清单
