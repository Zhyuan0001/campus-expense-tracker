# 校园消费记账系统 v3.0 - Electron 便携版

## 项目简介

大学生生活费记账桌面应用，采用 Electron + Vue3 + FastAPI 技术栈，实现真正的便携版——双击即运行，无需安装 Python 或 Node.js。

## 核心特性

- **便携运行**：PyInstaller 打包后端为独立可执行文件，Electron 内置 Chromium，无需安装任何依赖
- **现代界面**：Vue3 + Element Plus + Indigo 主题，支持亮/暗模式切换
- **数据可视化**：ECharts 饼图、折线图，直观展示消费统计
- **仪表盘**：新增 Dashboard 首页，一目了然查看月度概况
- **分类管理**：8 种默认分类 + 自定义分类
- **预算提醒**：月度预算设置与超支警告
- **数据导出**：CSV 格式导出，方便备份和分析
- **高 DPI 支持**：Web 技术自动适配 4K 屏幕

## 技术栈

### 前端
- Vue 3 + TypeScript
- Element Plus UI 组件库
- ECharts 图表库
- electron-vite 构建工具
- Axios HTTP 客户端

### 后端
- Python 3.10+
- FastAPI Web 框架
- SQLite3 数据库
- PyInstaller 打包工具

### 桌面包装
- Electron（内置 Chromium）
- electron-builder 打包工具

## 快速开始

### 开发模式

```bash
# 1. 安装后端依赖
cd ../campus_expense_web
pip install -r requirements.txt

# 2. 安装前端依赖
cd ../campus_expense_electron
npm install

# 3. 启动开发服务器（自动启动后端）
npm run dev
```

### 生产构建

```bash
# 1. 打包后端为独立可执行文件
pyinstaller backend.spec --clean --noconfirm
cp -r dist/backend/* resources/backend/

# 2. 构建 Linux AppImage
npm run build:linux

# 3. 构建 Windows 安装包
npm run build:win
```

构建完成后，在 `dist/` 目录下找到可分发文件。

## 项目结构

```
campus_expense_electron/
├── src/
│   ├── main/              # Electron 主进程
│   │   └── index.ts       # 后端生命周期管理、窗口创建
│   ├── preload/           # 预加载脚本
│   │   └── index.ts       # 安全的 API 暴露
│   └── renderer/          # 渲染进程（前端）
│       ├── src/
│       │   ├── api/       # 统一 API 层
│       │   ├── components/# Vue 组件
│       │   ├── App.vue    # 主应用
│       │   └── main.ts    # 入口文件
│       └── index.html
├── resources/
│   └── backend/           # PyInstaller 打包的后端可执行文件
├── backend.spec           # PyInstaller 配置
├── electron.vite.config.ts
└── package.json
```

## 架构设计

### 三层架构

1. **主进程（Main）**：管理后端进程生命周期、创建窗口、安全配置
2. **预加载脚本（Preload）**：暴露安全的 API 给渲染进程
3. **渲染进程（Renderer）**：Vue3 前端应用

### 后端生命周期

- Electron 启动时自动启动后端进程
- 通过 TCP socket 轮询健康检查端点 `/api/health`
- 后端就绪后创建窗口
- 窗口关闭时自动停止后端进程

### 数据库路径

- **开发模式**：`campus_expense_web/campus_expenses.db`
- **生产模式**：`用户数据目录/campus_expenses.db`（跨平台）
  - Windows: `%APPDATA%/校园消费记账/campus_expenses.db`
  - Linux: `~/.config/校园消费记账/campus_expenses.db`
  - macOS: `~/Library/Application Support/校园消费记账/campus_expenses.db`

## 功能模块

### 仪表盘（Dashboard）
- 月度总支出、剩余预算、记录数、日均消费
- 分类占比饼图
- 6 个月趋势折线图
- 最近 5 条记录

### 记账（Expense）
- 快速添加消费记录
- 金额、分类、描述、日期
- 实时验证

### 记录（Records）
- 查看所有消费记录
- 按月筛选
- 分页显示
- 删除记录

### 统计（Statistics）
- 月度分类统计
- 饼图可视化
- 金额占比

### 预算（Budget）
- 设置月度预算
- 进度条显示使用情况
- 超支警告

### 设置（Settings）
- 分类管理（添加/删除自定义分类）
- 数据导出 CSV
- 关于信息

## API 端点

### 消费记录
- `GET /api/expenses` - 获取记录列表
- `POST /api/expenses` - 创建记录
- `DELETE /api/expenses/{id}` - 删除记录

### 分类管理
- `GET /api/categories` - 获取所有分类
- `POST /api/categories` - 创建分类
- `DELETE /api/categories/{id}` - 删除分类

### 统计数据
- `GET /api/statistics/{year}/{month}` - 月度统计

### 预算管理
- `GET /api/budget` - 获取预算
- `PUT /api/budget` - 设置预算

### 数据导出
- `GET /api/export` - 导出 CSV

### 健康检查
- `GET /api/health` - 后端状态

## 主题定制

采用 Indigo 主题色（`#6366F1`），支持亮/暗模式：

```css
/* 主色调 */
--el-color-primary: #6366F1;
--el-border-radius-base: 10px;

/* 暗色模式 */
html.dark {
  --el-bg-color: #1a1a1a;
  --el-fill-color-blank: #2a2a2a;
}
```

## 安全特性

- `contextIsolation: true` - 上下文隔离
- `nodeIntegration: false` - 禁用 Node 集成
- `sandbox: true` - 沙箱模式
- `Menu.setApplicationMenu(null)` - 移除菜单栏
- 统一 API 层，避免硬编码

## 跨平台支持

- Windows 10/11（NSIS 安装包）
- Linux（AppImage）
- macOS（计划中）

## 开发团队

校园消费记账系统开发团队

## 许可证

MIT License
