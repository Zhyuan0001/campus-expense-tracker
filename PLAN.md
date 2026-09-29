# v3.0 Electron 便携版 — 实施计划

## 一、需求分析（PPT 流程 Step 1）

### 1.1 核心需求
- **便携性**：双击即运行，无需安装 Python/Node.js，"哪里解压哪里运行哪里建立数据库"
- **跨平台**：优先 Windows .exe，兼顾 Linux
- **美观**：Web 技术栈天然支持现代 UI，比 PyQt5 更易美化
- **HiDPI**：Chromium 自动适配 4K 屏幕
- **数据隔离**：数据库跟随应用目录（便携版语义），非 AppData

### 1.2 功能清单（复用 v2.0 全部功能 + 新增）
| 功能 | 状态 | 说明 |
|------|------|------|
| 记账（增删查） | 已有 | 复用 ExpenseTab.vue |
| 记录列表 + 筛选 | 已有 | 复用 RecordsTab.vue，修复假分页 |
| 分类统计饼图 | 已有 | 复用 StatisticsTab.vue，优化配色 |
| 预算管理 | 已有 | 复用 BudgetTab.vue |
| 自定义分类 | 已有 | 复用 SettingsTab.vue |
| CSV 导出 | 已有 | 复用 SettingsTab.vue |
| 亮/暗主题 | 已有 | 优化暗色模式 |
| **Dashboard 仪表盘** | **新增** | 首页概览：本月支出、饼图缩略、趋势图、最近记录 |
| **趋势折线图** | **新增** | 近6个月消费趋势 |

---

## 二、系统设计（PPT 流程 Step 2）

### 2.1 技术架构

```
┌─────────────────────────────────────────────────┐
│                  Electron Shell                   │
│  ┌─────────────────────────────────────────────┐ │
│  │           BrowserWindow (Chromium)           │ │
│  │  ┌────────────────────────────────────────┐  │ │
│  │  │   Vue3 + Element Plus + ECharts        │  │ │
│  │  │   (renderer 进程, 打包为静态 HTML)      │  │ │
│  │  └──────────────┬─────────────────────────┘  │ │
│  │                 │ HTTP :8000                   │ │
│  │  ┌──────────────▼─────────────────────────┐  │ │
│  │  │   FastAPI 后端 (PyInstaller → exe)      │  │ │
│  │  │   SQLite3 数据库 (exe 同级目录)          │  │ │
│  │  └────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### 2.2 两层打包策略

| 层 | 工具 | 产物 | 说明 |
|----|------|------|------|
| 层1：后端 | PyInstaller (one-directory) | `backend/backend.exe` + `_internal/` | 纯 Python，无 GUI |
| 层2：桌面 | electron-builder | `校园消费记账.exe` + `resources/` | 内嵌 Chromium + 后端 exe |

### 2.3 项目结构（新建 `campus_expense_electron/`）

```
SofteareEnjineer/
├── campus_expense_electron/           # v3.0 Electron 版本（新建）
│   ├── package.json
│   ├── electron.vite.config.ts
│   ├── tsconfig.json / tsconfig.node.json / tsconfig.web.json
│   ├── src/
│   │   ├── main/
│   │   │   └── index.ts              # 主进程：窗口管理 + 后端生命周期
│   │   ├── preload/
│   │   │   └── index.ts              # 安全桥接
│   │   └── renderer/                 # Vue3 前端（从 campus_expense_web/frontend 迁移）
│   │       ├── index.html
│   │       └── src/
│   │           ├── main.ts
│   │           ├── App.vue           # 重写：添加 Dashboard
│   │           ├── style.css          # 重写：清理脚手架代码
│   │           ├── api/
│   │           │   └── index.ts       # 新增：统一 API 层，消除 API_BASE 重复
│   │           └── components/
│   │               ├── DashboardTab.vue  # 新增
│   │               ├── ExpenseTab.vue    # 迁移 + 优化
│   │               ├── RecordsTab.vue    # 迁移 + 修复分页
│   │               ├── StatisticsTab.vue # 迁移 + 优化配色
│   │               ├── BudgetTab.vue     # 迁移
│   │               └── SettingsTab.vue   # 迁移
│   ├── resources/
│   │   └── backend/                  # PyInstaller 产物放这里
│   └── build/                        # 图标等
│
├── campus_expense_web/                # v2.0（保留，作为参考）
├── campus_expense_tracker.py          # v1.0（保留）
└── AGENTS.md                          # 更新
```

### 2.4 后端改造（修改 `campus_expense_web/backend/main.py`）

| 改动 | 说明 |
|------|------|
| 数据库路径 | 优先读 `DB_PATH` 环境变量，fallback 到 `sys.executable` 同级目录 |
| 健康检查 | 新增 `GET /api/health` 端点 |
| 优雅关闭 | 添加 lifespan 事件关闭 SQLite 连接 |
| 端口可配 | 读 `PORT` 环境变量，默认 8000 |
| uvicorn 启动 | 传 app 对象（非字符串），兼容 PyInstaller |

### 2.5 UI 设计改进

| 改进项 | 方案 |
|--------|------|
| 主色调 | Indigo `#6366F1`（更有品牌感） |
| 圆角 | `--el-border-radius-base: 12px` |
| Dashboard | 新增首页：本月支出卡片 + 分类饼图 + 趋势折线图 + 最近5条记录 |
| 饼图 | 环形图，圆角边框，hover 放大 |
| 趋势图 | 折线图 + 面积填充，近6个月 |
| 暗色模式 | 引入 `element-plus/theme-chalk/dark/css-vars.css` |
| 分类配色 | 8色方案：红/青/蓝/绿/黄/紫/橙/灰 |
| API 层 | 统一 `api/index.ts`，消除 5 处重复的 API_BASE |
| style.css | 清理 297 行 Vite 脚手架代码，仅保留应用样式 |
| HelloWorld.vue | 删除 |

---

## 三、实施步骤（PPT 流程 Step 3-5）

### Phase 1：后端改造（修复 + 增强）
1. 修改 `main.py`：数据库路径环境变量化、健康检查端点、lifespan、端口可配
2. 修复测试 fixture：让 `TEST_DB_PATH` 环境变量生效
3. 运行测试确认全部通过

### Phase 2：创建 Electron 项目骨架
1. 使用 `npm create @quick-start/electron` 创建 electron-vite + Vue3 + TS 项目
2. 配置 `electron.vite.config.ts`
3. 安装依赖：element-plus, echarts, axios, @element-plus/icons-vue

### Phase 3：前端迁移 + UI 升级
1. 迁移 5 个 Vue 组件到 renderer
2. 创建统一 API 层 `api/index.ts`
3. 重写 `style.css`（清理脚手架代码 + Element Plus 主题定制）
4. 重写 `App.vue`（添加 Dashboard 导航项）
5. 新建 `DashboardTab.vue`
6. 优化 StatisticsTab 配色
7. 修复 RecordsTab 假分页
8. 删除 HelloWorld.vue

### Phase 4：Electron 主进程
1. 实现后端进程启动（开发模式 vs 生产模式）
2. 实现健康检查轮询（TCP socket，用 127.0.0.1）
3. 实现优雅关闭（SIGTERM / taskkill）
4. 窗口配置（无菜单、ready-to-show、minWidth/minHeight）
5. 安全配置（contextIsolation、sandbox、nodeIntegration:false）

### Phase 5：PyInstaller 打包后端
1. 编写 `backend.spec`（hidden imports、one-directory、console=False）
2. 打包并测试独立运行

### Phase 6：集成测试 + 打包
1. 开发模式完整测试（Electron + 后端）
2. 配置 electron-builder（extraResources 包含后端）
3. 构建 Linux 版本测试
4. 更新 AGENTS.md、README.md

---

## 四、关键风险与对策

| 风险 | 对策 |
|------|------|
| PyInstaller hidden imports 遗漏 | 使用 backend-agent 提供的完整列表 |
| 端口 8000 被占用 | 支持 PORT 环境变量，可动态切换 |
| 后端进程残留 | Electron 注册所有退出路径的 cleanup |
| 数据库路径错误 | 环境变量优先，fallback 到 sys.executable 同级 |
| localhost IPv6 问题 | 统一使用 127.0.0.1 |
| Windows 跨平台打包 | PyInstaller 不支持交叉编译，需 Windows 机器最终打包 |

---

## 五、验收标准

1. `npm run dev` 启动 Electron 窗口，所有功能正常
2. 后端 API 测试全部通过（pytest）
3. Dashboard 显示本月概览 + 饼图 + 趋势图
4. 亮/暗主题切换正常
5. CSV 导出正常
6. PyInstaller 打包的后端可独立运行
7. electron-builder 打包后可正常启动（Linux 先测）
