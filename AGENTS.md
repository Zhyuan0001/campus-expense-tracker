# AGENTS.md - 校园消费记账系统

## 项目概述
大学生生活费记账桌面应用。支持记录消费、分类统计（含饼图可视化）、月度分析、预算提醒、自定义分类、数据导出 CSV、亮/暗主题切换。

**当前版本**：v3.0 - Electron 便携版（推荐）
**历史版本**：
- v2.0 - 现代 Web 技术栈版本（pywebview）
- v1.0 - PyQt5 版本（保留用于学习对比）

## 技术栈

### v3.0 Electron 便携版（当前推荐）
- **前端**：Vue 3 + TypeScript + Element Plus + ECharts
- **后端**：Python 3.10+ + FastAPI（PyInstaller 打包为独立可执行文件）
- **桌面包装**：Electron（内置 Chromium，无需安装浏览器）
- **数据存储**：SQLite3（便携数据库，与应用同目录）
- **构建工具**：electron-vite + Vite
- **打包工具**：electron-builder
- **样式方案**：Element Plus 组件库 + CSS3 动画
- **特点**：双击即运行，无需安装 Python/Node.js，真正的便携版

### v2.0 现代 Web 版本（历史版本）
- **前端**：Vue 3 + TypeScript + Element Plus + ECharts
- **后端**：Python 3.10+ + FastAPI
- **桌面包装**：pywebview
- **数据存储**：SQLite3
- **构建工具**：Vite
- **样式方案**：Element Plus 组件库 + CSS3 动画

### v1.0 PyQt5 版本（历史版本）
- Python 3.10+
- PyQt5（GUI 框架）
- SQLite3（数据存储）
- matplotlib（图表）
- pytest（测试框架）

## 构建与运行命令

### v3.0 Electron 便携版（当前推荐）

```bash
# 1. 安装后端依赖
cd campus_expense_web
pip install -r requirements.txt
pip install pyinstaller

# 2. 安装前端依赖
cd campus_expense_electron
npm install

# 3. 开发模式运行（热重载）
npm run dev

# 4. 打包后端为独立可执行文件
#    必须在 campus_expense_electron 下执行：backend.spec 里的源码路径是
#    ../campus_expense_web/backend/main.py，相对于该目录解析
pyinstaller backend.spec --clean --noconfirm
cp -r dist/backend/* resources/backend/

# 5. 构建生产版本（Linux AppImage）
npm run build:linux

# 6. 构建生产版本（Windows 安装包）
#    PyInstaller 不支持交叉编译，Linux 上无法产出 Windows exe，
#    需用 GitHub Actions（见下）或在 Windows 上执行
npm run build:win

# 7. 单独运行后端 API（调试用）
cd ../campus_expense_web/backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Windows exe 自动构建**：推送 `v*` 标签触发 `.github/workflows/build-windows.yml`，
产出便携版与 NSIS 安装包并挂到 Release；也可在 Actions 页面手动触发（workflow_dispatch）。

```bash
git push origin master
git tag v3.0.0 && git push origin v3.0.0
```

`resources/backend/` 与 `out/` 已 gitignore（体积大且平台相关），由 CI 重新生成。
详见 `WINDOWS_BUILD_GUIDE.md`。

### v2.0 现代 Web 版本（历史版本）

```bash
# 1. 安装后端依赖
cd campus_expense_web
pip install -r requirements.txt

# 2. 安装前端依赖
cd frontend
npm install

# 3. 开发模式运行（热重载）
cd ..
DEV_MODE=1 python3 app.py

# 4. 生产模式构建与运行
cd frontend
npm run build  # 构建前端
cd ..
python3 app.py  # 运行桌面应用

# 5. 单独运行后端 API（调试用）
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# 6. 单独运行前端开发服务器（调试用）
cd frontend
npm run dev
```

### v1.0 PyQt5 版本（历史版本）

```bash
# 安装依赖
pip install PyQt5 matplotlib

# 运行主程序
python3 campus_expense_tracker.py

# 运行测试
pytest test_expense_tracker.py -v
```

## 代码风格规范

### 后端（Python）
- 遵循 PEP8
- 类名 PascalCase，函数/变量 snake_case
- 中文界面，中文注释
- FastAPI 路由使用 RESTful 风格

### 前端（Vue3 + TypeScript）
- 组件名 PascalCase（如 ExpenseTab.vue）
- 变量/函数 camelCase
- 使用 TypeScript 类型注解
- Element Plus 组件优先
- CSS 类名 kebab-case

## 项目结构

```
SofteareEnjineer/
├── campus_expense_electron/          # v3.0 Electron 便携版（推荐）
│   ├── package.json                  # Electron 项目配置
│   ├── electron.vite.config.ts       # electron-vite 构建配置
│   ├── backend.spec                  # PyInstaller 打包配置（路径相对于本目录）
│   ├── resources/
│   │   └── backend/                  # 打包后的后端可执行文件（gitignore，CI 生成）
│   ├── src/
│   │   ├── main/
│   │   │   └── index.ts              # Electron 主进程（后端生命周期管理）
│   │   ├── preload/
│   │   │   └── index.ts              # 预加载脚本
│   │   └── renderer/
│   │       ├── index.html            # 前端入口
│   │       └── src/
│   │           ├── main.ts           # Vue3 入口
│   │           ├── App.vue           # 主应用组件
│   │           ├── style.css         # 全局样式（Indigo主题）
│   │           ├── api/
│   │           │   └── index.ts      # 统一 API 层
│   │           └── components/
│   │               ├── DashboardTab.vue  # 仪表盘（新增）
│   │               ├── ExpenseTab.vue    # 记账 Tab
│   │               ├── RecordsTab.vue    # 记录 Tab
│   │               ├── StatisticsTab.vue # 统计 Tab
│   │               ├── BudgetTab.vue     # 预算 Tab
│   │               └── SettingsTab.vue   # 设置 Tab
│   └── dist/                         # 构建输出（electron-builder）
│
├── campus_expense_web/              # v2.0 现代 Web 版本（历史）
│   ├── app.py                       # pywebview 桌面启动器
│   ├── requirements.txt             # Python 依赖
│   ├── README.md                    # 项目说明
│   ├── backend/
│   │   └── main.py                  # FastAPI 后端（REST API）
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── App.vue              # 主应用组件
│   │   │   ├── main.ts              # 入口文件
│   │   │   └── components/
│   │   │       ├── ExpenseTab.vue   # 记账 Tab
│   │   │       ├── RecordsTab.vue   # 记录 Tab
│   │   │       ├── StatisticsTab.vue # 统计 Tab
│   │   │       ├── BudgetTab.vue    # 预算 Tab
│   │   │       └── SettingsTab.vue  # 设置 Tab
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   └── tsconfig.json
│   └── campus_expenses.db           # SQLite 数据库（运行时生成）
│
├── campus_expense_tracker.py        # v1.0 PyQt5 版本（历史）
├── test_expense_tracker.py          # v1.0 单元测试
├── .github/
│   └── workflows/
│       └── build-windows.yml        # 推 v* 标签时构建 Windows exe 并发布 Release
├── DESIGN.md                        # 设计文档
├── AGENTS.md                        # 本文件
├── iteration_log.md                 # 迭代记录
├── PLAN.md                          # 迭代计划
├── PPT_PREPARATION.md               # 答辩材料
├── WINDOWS_BUILD_GUIDE.md           # Windows 构建指南（CI + 本地）
└── .gitignore
```

## 数据库结构
- **expenses**: id, amount, category, description, date, created_at
- **categories**: id, name, icon, is_default
- **budget**: id, monthly_budget
- **settings**: key, value（存储主题等配置）

## REST API 端点（v2.0 / v3.0 共用同一后端）

以下清单与 `campus_expense_web/backend/main.py` 的实际路由逐条核对过（2026-09-30）。

### 系统
- `GET /` - 服务标识
- `GET /api/health` - 健康检查（Electron 主进程用它做启动探活）

### 消费记录
- `GET /api/expenses?year=&month=` - 获取消费记录列表；year/month 可单独或组合使用，month 必须在 1-12
- `POST /api/expenses` - 创建消费记录；amount 必须 >0 且为有限数，date 必须为严格补零的 YYYY-MM-DD 且真实存在
- `DELETE /api/expenses/{id}` - 删除消费记录，不存在返回 404

### 分类管理
- `GET /api/categories` - 获取所有分类（含 is_default 标记）
- `POST /api/categories` - 创建自定义分类；名称去空白后不可为空、不可与已有分类重名（400）
- `DELETE /api/categories/{id}` - 删除自定义分类；默认分类拒绝删除（400）

### 统计数据
- `GET /api/statistics/{year}/{month}` - 月度统计，返回 total 与按分类聚合的 categories 数组

### 预算管理
- `GET /api/budget` - 返回 monthly_budget（未设置时为 null）、spent、remaining、percentage
- `PUT /api/budget` - 设置月度预算（注意是 PUT，不是 POST）

### 数据导出
- `GET /api/export` - 导出全部记录为 CSV（内存生成，utf-8-sig 带 BOM，表头 ID,日期,分类,描述,金额）

### 关于主题
主题（亮/暗）**没有后端接口**，由渲染层 localStorage 持久化（见 F8）。
数据库中的 `settings` 表按设计保留但当前未使用。
历史上文档曾列出 `/api/statistics/monthly`、`/api/statistics/category`、
`/api/budget/status`、`/api/export/csv`、`/api/settings/theme`，这些端点从未实现，已于 2026-09-30 从文档中移除。

## 不变量（严禁修改）
- 数据库表名和字段名
- 默认 8 种分类：餐饮、交通、学习、娱乐、社交、购物、医疗、其他
- CSV 导出列顺序：ID,日期,分类,描述,金额
- API 端点路径和响应格式
- 文件命名约定

## 测试说明

### v3.0 Electron 便携版（当前）
- 后端 API 测试：`cd campus_expense_web/backend && python -m pytest tests/ -v`
  30 个用例（含 Infinity/NaN、非补零日期、空白分类名、CSV 字节内容、统计口径一致性等
  回归用例），覆盖率 97%
- 渲染层组件测试：`cd campus_expense_electron && npm run test:run`
  vitest + @vue/test-utils + jsdom，覆盖 6 个页面组件与主题 composable
- 类型检查：`cd campus_expense_electron && npm run typecheck`（node 与 web 两套 tsconfig）
- 以上三项由 `.github/workflows/ci.yml` 在每次 push 时自动执行
- 手工验证：Swagger UI（http://localhost:8000/docs）

### v2.0 现代 Web 版本
- 前端组件测试：`cd campus_expense_web/frontend && npm run test:run`（vitest，6 个用例）

### v1.0 PyQt5 版本
- 使用 pytest 运行 test_expense_tracker.py
- 测试覆盖：输入校验、数据库操作、统计计算、边界情况
- 测试使用临时数据库文件，不污染生产数据

## 安全注意事项
- 金额输入必须为正数且为有限数（后端 `Field(gt=0, allow_inf_nan=False)`，
  否则 Infinity 会污染数据库导致读接口永久 500）
- 日期格式严格校验（补零 YYYY-MM-DD 正则 + 真实日期双重校验）
- 删除操作需二次确认（前端弹窗）
- 分类名去空白后不可为空、不可重复
- CSV 导出在内存中生成，不落临时文件（固定可预测的临时路径可被符号链接劫持）
- CORS 配置限制（生产环境应限制 allow_origins；当前为 `*`，属已知取舍，见 iteration_log）

## 跨平台说明
v2.0 版本支持：
- Windows 10/11
- Ubuntu 20.04+
- Fedora 35+
- macOS 11+

高 DPI 支持：Web 技术自动适配 4K 屏幕，无需额外配置。

## 开发工作流

### 功能开发
1. 后端：在 backend/main.py 添加 API 端点
2. 前端：在 frontend/src/components/ 修改或新增组件
3. 测试：使用 Swagger UI 测试 API，浏览器测试前端
4. 打包：`cd frontend && npm run build` 构建前端

### Git 分支策略
- `master`：稳定版本
- `develop`：开发主线
- `feature/*`：功能分支

## 版本演进路线
- v1.0（已完成）：PyQt5 单文件版本
- v2.0（已完成）：现代 Web 技术栈版本（pywebview）
- v3.0（已完成）：Electron 便携版，PyInstaller 打包后端，真正的双击即运行
- v4.0（计划中）：移动端适配、云同步
