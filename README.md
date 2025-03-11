# 喝水提醒

一个基于 PyQt5 的喝水提醒软件，帮助用户保持良好的饮水习惯。

## 功能特点

- 定时弹出喝水提醒（可设置间隔时间）
- 可视化喝水记录统计
- 支持自定义提醒文案
- 系统托盘图标常驻
- 静音/恢复提醒功能
- 启动时可选择最小化到托盘

## 安装要求

- Python 3.12 或更高版本
- Poetry（依赖管理工具）

## 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/B-ug/heshui.git
cd heshui
```

2. 安装依赖：

```bash
poetry install
```

## 使用方法

1. 启动应用程序：

```bash
poetry run python run.py
```

2. 使用系统托盘图标：
   - 左键单击：显示/隐藏主窗口
   - 右键单击：显示菜单（包含显示主窗口、静音提醒和退出选项）

3. 配置设置：
   - 点击主窗口的"设置"按钮
   - 可以设置提醒间隔、每日目标、提醒文本等

## 打包
1. 执行打包程序

```bash
poetry run python build_exe.py
```

## 开发说明

- 使用 Poetry 管理依赖
- 遵循 PEP 8 编码规范
- 使用 Google 风格的文档字符串
- 实现了单例模式（配置和数据库管理）

## 许可证

MIT License
