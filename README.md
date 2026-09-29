# 校园消费记账系统

大学生生活费记账桌面应用，支持记录消费、分类统计、月度分析、预算提醒等功能。

## 📦 版本说明

### v2.0 - 现代 Web 版本（推荐）
位于 `campus_expense_web/` 目录

**技术栈**：Vue3 + TypeScript + Element Plus + FastAPI + pywebview

**特点**：
- 🎨 现代化 Material Design UI
- 📱 完美支持 4K/Retina 高 DPI 屏幕
- 🌓 亮/暗主题切换
- 📊 ECharts 数据可视化
- 🌐 跨平台（Windows/Linux/macOS）
- 🔧 前后端分离，易于维护和扩展

[查看详细文档 →](campus_expense_web/README.md)

### v1.0 - PyQt5 版本（历史版本）
位于项目根目录

**技术栈**：Python + PyQt5 + SQLite3 + matplotlib

**特点**：
- 单文件实现（约 810 行）
- 适合学习 PyQt5 桌面开发
- 功能完整但 UI 较传统

## 🚀 快速开始

### 使用现代 Web 版本（推荐）

```bash
# 1. 进入项目目录
cd campus_expense_web

# 2. 安装后端依赖
pip install -r requirements.txt

# 3. 安装前端依赖
cd frontend
npm install

# 4. 开发模式运行
cd ..
DEV_MODE=1 python3 app.py

# 5. 生产模式构建与运行
cd frontend
npm run build
cd ..
python3 app.py
```

### 使用 PyQt5 版本（历史版本）

```bash
# 安装依赖
pip install PyQt5 matplotlib

# 运行程序
python3 campus_expense_tracker.py

# 运行测试
pytest test_expense_tracker.py -v
```

## 📁 项目结构

```
SofteareEnjineer/
├── campus_expense_web/          # v2.0 现代 Web 版本（推荐）
│   ├── app.py                   # 桌面启动器
│   ├── backend/                 # FastAPI 后端
│   ├── frontend/                # Vue3 前端
│   └── README.md                # 详细文档
│
├── campus_expense_tracker.py    # v1.0 PyQt5 版本
├── test_expense_tracker.py      # v1.0 单元测试
├── DESIGN.md                    # 设计文档
├── AGENTS.md                    # AI 编程助手指南
├── iteration_log.md             # 迭代记录
└── README.md                    # 本文件
```

## ✨ 核心功能

- ✅ **记账**：添加消费记录（金额、分类、描述、日期）
- ✅ **查看记录**：表格展示，按月筛选，删除记录
- ✅ **分类统计**：饼图可视化，月度分析
- ✅ **预算提醒**：设置月预算，进度条显示，三色状态（绿/黄/红）
- ✅ **自定义分类**：添加/删除自定义分类
- ✅ **数据导出**：导出 CSV 文件
- ✅ **主题切换**：亮色/暗色主题

## 🛠️ 技术对比

| 特性 | v2.0 Web 版本 | v1.0 PyQt5 版本 |
|------|--------------|----------------|
| UI 美观度 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 高 DPI 支持 | 自动适配 | 需手动配置 |
| 跨平台 | 完整支持 | 需测试 |
| 代码量 | 前后端分离，易维护 | 单文件 810 行 |
| 扩展性 | 高（Web 技术栈） | 中 |
| 移动端适配 | 可复用前端代码 | 需重写 |
| 学习价值 | 现代 Web 开发 | 传统桌面开发 |

## 📚 文档

- [设计文档](DESIGN.md) - 需求分析与系统设计
- [AGENTS.md](AGENTS.md) - AI 编程助手指南
- [迭代记录](iteration_log.md) - 开发过程记录
- [现代版详细文档](campus_expense_web/README.md) - v2.0 使用说明

## 🎯 开发流程

本项目遵循课程教授的个人软件过程（PSP）：

1. **意图澄清**：明确需求，编写设计文档
2. **上下文准备**：编写 AGENTS.md，为 AI 提供项目背景
3. **分阶段生成**：使用 AI 辅助编码，小步快跑
4. **验证与验收**：单元测试 + 手动测试
5. **迭代修正**：≥2 轮迭代优化
6. **沉淀资产**：记录迭代过程和心得

## 📝 课程信息

- **课程**：软件工程
- **练习类型**：AI 辅助编程实践
- **完成日期**：2026-09-29

## 📄 License

MIT
