# AGENTS.md - 校园消费记账系统

## 项目概述
大学生生活费记账桌面应用。支持记录消费、分类统计（含饼图可视化）、月度分析、预算提醒、自定义分类、数据导出 CSV、亮/暗主题切换。

**当前版本**：v2.0 - 现代 Web 技术栈版本（推荐）
**历史版本**：v1.0 - PyQt5 版本（保留用于学习对比）

## 技术栈

### v2.0 现代 Web 版本（当前推荐）
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

### v2.0 现代 Web 版本

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

# 7. 构建便携版可执行文件（无需安装 Python/Node.js）
./build_portable.sh
# 或手动构建：
cd frontend && npm run build && cd ..
pyinstaller --clean portable.spec
# 产物在 dist/ 目录下，双击即可运行
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
├── campus_expense_web/              # v2.0 现代 Web 版本（推荐）
│   ├── app.py                       # pywebview 桌面启动器（开发模式）
│   ├── app_portable.py              # 便携版启动器（PyInstaller 打包用）
│   ├── portable.spec                # PyInstaller 打包配置
│   ├── build_portable.sh            # 一键构建便携版脚本
│   ├── requirements.txt             # Python 依赖
│   ├── README.md                    # 项目说明
│   ├── backend/
│   │   ├── main.py                  # FastAPI 后端（REST API）
│   │   ├── requirements.txt
│   │   ├── requirements-dev.txt     # 开发依赖（测试、代码质量）
│   │   ├── pyproject.toml           # 工具配置（black、isort、mypy等）
│   │   └── tests/
│   │       └── test_api.py          # 后端 API 测试（19个用例）
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── App.vue              # 主应用组件
│   │   │   ├── main.ts              # 入口文件
│   │   │   ├── components/
│   │   │   │   ├── ExpenseTab.vue   # 记账 Tab
│   │   │   │   ├── RecordsTab.vue   # 记录 Tab
│   │   │   │   ├── StatisticsTab.vue # 统计 Tab
│   │   │   │   ├── BudgetTab.vue    # 预算 Tab
│   │   │   │   └── SettingsTab.vue  # 设置 Tab
│   │   │   └── __tests__/           # 前端单元测试
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── vitest.config.ts
│   │   ├── eslint.config.js
│   │   └── tsconfig.json
│   └── dist/                        # 便携版可执行文件（构建产物）
│
├── campus_expense_tracker.py        # v1.0 PyQt5 版本（历史）
├── test_expense_tracker.py          # v1.0 单元测试
├── DESIGN.md                        # 设计文档
├── AGENTS.md                        # 本文件
├── iteration_log.md                 # 迭代记录
├── Makefile                         # 开发便捷命令
├── .github/workflows/ci.yml         # CI/CD 流水线
└── .gitignore
```

## 数据库结构
- **expenses**: id, amount, category, description, date, created_at
- **categories**: id, name, icon, is_default
- **budget**: id, monthly_budget
- **settings**: key, value（存储主题等配置）

## REST API 端点（v2.0）

### 消费记录
- `GET /api/expenses` - 获取消费记录列表（支持 year/month 筛选）
- `POST /api/expenses` - 创建消费记录
- `DELETE /api/expenses/{id}` - 删除消费记录

### 分类管理
- `GET /api/categories` - 获取所有分类
- `POST /api/categories` - 创建自定义分类
- `DELETE /api/categories/{id}` - 删除自定义分类

### 统计数据
- `GET /api/statistics/{year}/{month}` - 获取月度统计（总额、各分类占比）

### 预算管理
- `GET /api/budget` - 获取预算信息（含已花费、剩余、百分比）
- `PUT /api/budget` - 设置月度预算

### 数据导出
- `GET /api/export` - 导出全部记录为 CSV

## 不变量（严禁修改）
- 数据库表名和字段名
- 默认 8 种分类：餐饮、交通、学习、娱乐、社交、购物、医疗、其他
- CSV 导出列顺序：ID,日期,分类,描述,金额
- API 端点路径和响应格式
- 文件命名约定

## 测试说明

### v2.0 现代 Web 版本
- 后端 API 测试：`cd campus_expense_web/backend && pytest tests/ -v`（19个用例，97%覆盖率）
- 前端组件测试：`cd campus_expense_web/frontend && npm run test:run`
- 代码质量检查：`black --check backend/`、`mypy backend/`、`eslint frontend/src/`

### v1.0 PyQt5 版本
- 使用 pytest 运行 test_expense_tracker.py
- 测试覆盖：输入校验、数据库操作、统计计算、边界情况
- 测试使用临时数据库文件，不污染生产数据

## 安全注意事项
- 金额输入必须为正数（后端 Field(gt=0) 校验）
- 日期格式严格校验（YYYY-MM-DD）
- 删除操作需二次确认（前端弹窗）
- 分类名不可重复、不可为空
- CORS 配置限制（生产环境应限制 allow_origins）

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
- v2.0（已完成）：现代 Web 技术栈版本
- v3.0（计划中）：添加 Tauri 打包、移动端适配
