# 迭代记录 - 校园消费记账 GUI

## 项目信息
- **项目**：校园消费记账 GUI
- **技术栈**：Python 3.10 + PyQt5 + SQLite3 + matplotlib
- **开发者**：（姓名）
- **日期**：2026-09-29

---

## == 第1轮（初版）==

### 我给AI的提示词
```
【项目背景】
技术栈：Python 3.10 + PyQt5 + SQLite3 + matplotlib
项目概况：大学生生活费记账桌面 GUI，支持记录消费、分类统计（含饼图可视化）、
月度分析、预算提醒、自定义分类、数据导出 CSV、亮/暗主题切换。
编码约定：PEP8；类名 PascalCase；函数/变量 snake_case；中文界面。

【需求描述】
F1 记账：输入金额、选分类、填描述、选日期，提交保存
F2 查看记录：表格展示，支持按月筛选，删除选中记录
F3 分类统计：指定月份各分类金额与占比，饼图可视化
F4 月度统计：指定月份消费总额
F5 预算提醒：设置月预算，三色状态显示（绿/黄/红）
F6 自定义分类：用户可添加/删除自定义分类
F7 数据导出：导出全部记录为 CSV
F8 主题切换：亮色/暗色两套主题

【约束边界】
- 单文件主程序
- 数据库自动建表
- matplotlib 图表嵌入窗口内
- 金额必须 > 0，日期格式严格校验
- 默认分类不可删除

【验收标准】
- 5个Tab均可正常切换
- 记账后记录出现在列表中
- 饼图正确显示中文
- 预算三色状态正确
- 35个单元测试全部通过
```

### AI生成的初版要点
- 生成了 786 行代码，包含 8 个类（Database, PieChartWidget, ExpenseTab, RecordsTab, StatisticsTab, BudgetTab, SettingsTab, MainWindow）
- 实现了全部 8 个功能
- 使用 QSS 样式表实现亮/暗主题
- 发现两个问题：
  1. matplotlib 饼图中文字体缺失（CJK 字符显示为乱码）
  2. 分类排序不是按用户期望的顺序

---

## == 第2轮（第一次迭代修改）==

### 发现的问题
1. **matplotlib 中文字体缺失**：饼图中的"暂无数据"和分类名称显示为方框乱码
2. **分类排序问题**：分类按 is_default DESC 排序，导致顺序不自然

### 我给AI的修改要求
```
修复两个问题：
1. matplotlib 饼图中文字体缺失 - 需要配置中文字体，使用系统可用的 Noto Sans CJK 字体
2. 分类排序 - 改为按 id（插入顺序）排序，而不是按 is_default DESC
```

### AI修改了什么
1. 添加了 matplotlib 字体配置代码：
   - 使用 `fontManager.addfont()` 加载 `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`
   - 设置 `plt.rcParams["font.sans-serif"]` 优先使用 "Noto Sans CJK JP"
   - 设置 `plt.rcParams["axes.unicode_minus"] = False` 防止负号显示异常
2. 修改分类查询 SQL：`ORDER BY is_default DESC, name` → `ORDER BY id`
3. 新增测试用例 `test_categories_ordered_by_id` 验证分类顺序

### 验证结果
- 饼图中文渲染正常，无警告
- 分类顺序：餐饮、交通、学习、娱乐、社交、购物、医疗、其他（符合预期）
- 36 个测试全部通过

---

## == 第3轮（第二次迭代修改）==

### 发现的问题
预算 Tab 只有文字提示，缺少直观的可视化进度条

### 我给AI的修改要求
```
在预算 Tab 中添加进度条：
- 使用 QProgressBar 显示本月已使用百分比
- 进度条颜色随状态变化：绿色（<80%）、黄色（80%-100%）、红色（>100%超支）
- 超支时进度条显示 100%
```

### AI修改了什么
1. 导入 `QProgressBar` 组件
2. 在 BudgetTab 中添加进度条控件（高度 25px，显示百分比）
3. 更新 `_load()` 方法：
   - 计算已使用百分比并设置进度条值（最大 100）
   - 根据状态设置进度条颜色样式：
     - 绿色：`#00b894`（<80%）
     - 黄色：`#fdcb6e`（80%-100%）
     - 红色：`#d63031`（>100%）
4. 未设置预算时清空进度条样式

### 验证结果
- 进度条正确显示已使用百分比
- 颜色随状态变化：25% 时绿色，105% 时红色
- 36 个测试全部通过

---

## == 我的检查与验证说明 ==

### 我怎么确认结果正确

1. **单元测试验证**：
   - 编写了 36 个单元测试，覆盖数据库操作、输入校验、统计计算、边界情况
   - 所有测试通过：`pytest test_expense_tracker.py -v` → 36 passed

2. **GUI 功能验证**（offscreen 模式）：
   - 5 个 Tab 正常切换显示
   - 记账功能：添加记录后列表刷新
   - 饼图渲染：中文字符正常显示，无字体警告
   - 预算进度条：数值和颜色正确
   - 分类排序：按插入顺序显示

3. **数据库操作验证**：
   - 临时数据库测试：增删查改、统计查询、自定义分类、预算设置
   - CSV 导出格式验证：表头正确，数据完整

4. **边界情况验证**：
   - 金额 ≤ 0：弹窗警告
   - 日期格式错误：弹窗警告
   - 空分类名：弹窗警告
   - 重复分类名：弹窗警告
   - 删除默认分类：不允许
   - 无记录月份：显示"暂无数据"

---

## == 心得 ==

### 本次协作最大惊喜
**AI 对 PyQt5 组件的熟悉程度超出预期**。我只需描述需求（如"添加进度条"），AI 就能准确使用 `QProgressBar` 并正确配置样式。QSS 样式表的生成也很准确，亮/暗主题的配色方案直接可用。

### 本次协作最大失望
**matplotlib 中文字体问题需要多轮调试**。AI 第一次尝试的 `plt.rcParams["font.sans-serif"]` 方案不生效，因为 matplotlib 无法自动发现系统的 .ttc 字体文件。最终需要用 `fontManager.addfont()` 手动加载字体文件。这类环境相关的坑，AI 无法提前预知，需要人工介入排查。

### 对 AI 辅助编程的反思
1. **意图澄清至关重要**：设计文档写得越详细（验收标准、约束边界），AI 生成的代码越符合预期
2. **AI 擅长生成代码，但不擅长验证**：必须通过单元测试和人工检查来确认正确性
3. **小步快跑有效**：每轮只改 1-2 个问题，便于定位和回滚
4. **环境问题是 AI 的盲区**：字体、路径、系统依赖等环境相关问题，AI 无法自动适配

---

## 验收自评

| 验收标准 | 是否达标 | 说明 |
|---------|---------|------|
| ① 功能跑通 | ✅ | 8 个功能全部实现，基本功能可演示 |
| ② ≥2轮迭代记录 | ✅ | 完成 3 轮迭代（初版 + 2 轮修改） |
| ③ ≥1次验证说明 | ✅ | 单元测试 36 个 + GUI 功能验证 + 边界测试 |
| ④ 1条心得 | ✅ | 已记录惊喜与失望，附反思总结 |

## v3.0 Electron 便携版 - 2026-09-29

### 核心改进
- **桌面框架**：从 pywebview 迁移到 Electron，内置 Chromium，更好的兼容性和性能
- **后端打包**：PyInstaller 将 FastAPI 后端打包为独立可执行文件，无需安装 Python
- **便携特性**：真正的双击即运行，哪里解压哪里运行，数据库随应用走
- **新增仪表盘**：Dashboard 首页，统计卡片 + 饼图 + 折线图 + 最近记录
- **统一 API 层**：消除 5 个组件中重复的 API_BASE 硬编码
- **Indigo 主题**：#6366F1 主色调，10px 圆角，现代化视觉
- **修复分页**：RecordsTab 从假分页改为客户端计算分页

### 技术架构
- 三层架构：Main（后端生命周期）+ Preload（安全桥接）+ Renderer（Vue3）
- 健康检查：TCP socket 轮询 `/api/health`，确保后端就绪再创建窗口
- 数据库路径：开发模式用项目目录，生产模式用用户数据目录
- 安全配置：contextIsolation=true, nodeIntegration=false, sandbox

### 构建流程
1. PyInstaller 打包后端 → `resources/backend/backend`
2. electron-vite 构建前端
3. electron-builder 打包为 AppImage（Linux）或 NSIS（Windows）

### 文件变更
- 新增：`campus_expense_electron/` 完整 Electron 项目
- 修改：`campus_expense_web/backend/main.py`（健康检查、lifespan、可配置 DB 路径）
- 修改：`campus_expense_web/backend/tests/test_api.py`（修复测试隔离）
- 更新：`AGENTS.md`（v3.0 文档）
- 新增：`campus_expense_electron/README.md`

### 测试验证
- 后端 API 测试：19/19 通过，95% 覆盖率
- Electron 开发模式：启动成功，所有 API 端点正常响应
- PyInstaller 打包：后端可执行文件独立运行成功

---

## v3.0 质量迭代（Round 1-4）- 2026-09-29

### Round 1: 关键视觉和交互修复
- **DashboardTab**：添加 v-loading 加载状态；stat card 添加 `min-width:0` + `text-overflow` 防溢出；错误处理从静默改为 ElMessage.error
- **StatisticsTab/BudgetTab/RecordsTab**：标题添加 `white-space: nowrap` 防截断；BudgetTab 添加 loading 状态和错误提示
- **SettingsTab**：CSV 导出文件名添加日期后缀 `campus_expenses_2026-09-29.csv`；导出按钮添加 loading 状态
- **App.vue**：componentMap 类型从 `Record<string, any>` 改为 `Record<string, Component>`；fallback 到 DashboardTab

### Round 2: 代码质量和性能优化
- **共享常量**：提取 `CATEGORY_COLORS`、`CATEGORY_ICON_MAP`、`getCategoryIcon()`、`isDarkMode()`、`getChartTextColor()`、`getChartBorderColor()` 到 `utils/constants.ts`，消除 6 个组件中的重复代码
- **Dashboard 趋势数据**：6 次串行 API 调用改为 `Promise.all` 并行加载，加载速度提升约 5 倍
- **ECharts 暗色模式**：所有图表（饼图、折线图）的边框色、文字色根据主题动态切换
- **API 层清理**：移除未使用的 `healthCheck()` 方法

### Round 3: 后端 API 增强
- **created_at 一致性**：`add_expense` 改为由 Python 生成时间戳并写入 DB，API 响应与 DB 存储一致
- **description 校验**：添加 `max_length=200` 限制
- **预算原子操作**：`set_budget` 从 DELETE+INSERT 改为 `INSERT OR REPLACE`，避免竞态条件
- **月份校验**：`get_expenses` 添加月份范围校验（1-12）
- **CORS 修复**：`allow_credentials` 改为 `False`（与 `allow_origins=["*"]` 不冲突）
- **CSV 导出**：临时文件名添加日期避免冲突

### Round 4: UI 打磨和细节完善
- **全局样式增强**：`style.css` 添加暗色模式文字色变量、`*` 选择器主题过渡动画、自定义滚动条样式
- **响应式布局**：Dashboard 统计卡片 4→2→1 列自适应；图表行 2→1 列；Budget 统计卡 3→1 列
- **侧边栏交互**：菜单项添加 hover 效果、transition 动画
- **ExpenseTab**：`loadMonthlyStats` 改为 Promise.all 并行加载

### 验证结果
- `electron-vite build` 编译成功，2259 模块无错误
- Electron dev 模式启动正常，后端自动 spawn
- 所有 API 端点返回 200 OK
- 趋势数据并行加载验证：6 个月统计同时请求完成

---

## v3.0 全面质量审计与修复（Round 5-7）- 2026-09-30

### 我给AI的提示词
```
注意，请再次在本机上确认所有功能实现无误，按照ppt流程规范安全可追溯的进行工程，
对整个软件的所有功能和细节进行全面测试，擅长使用子agent团队进行研究、测试、判断、提升；
得到完美的exe便携软件
```

### 审计方法（三路并行）
1. **子agent A：Windows 运行时静态审查**——读 electron-builder 的 portable.nsi 模板与
   PyInstaller 源码，逐项核对打包后在 Windows 上的真实行为
2. **子agent B：后端黑盒测试**——起真实 uvicorn 进程，对 12 个路由做 31 组验收项实测，
   含并发、CSV 字节内容、统计口径一致性
3. **浏览器端到端**——生产构建产物 + 真实后端，逐功能点击验证 6 个页面

### 发现并修复的缺陷

| 编号 | 严重度 | 缺陷 | 修复 |
|---|---|---|---|
| W1 | 致命 | portable 双击两次会互删解压目录（portable.nsi 启动/退出各 RMDir 一次且无 splash 静默解压）；主进程无单实例锁 | 加 requestSingleInstanceLock + second-instance 聚焦已有窗口 |
| W2 | 致命 | 后端启动失败/超时时只打日志就退出，用户看到"闪一下什么都没有" | dialog.showErrorBox 给出可见错误 |
| W3 | 致命 | 装到 Program Files 或写保护 U 盘时数据库目录不可写，后端 import 期即崩 | getDbPath 逐级探测可写性，回退到用户数据目录 |
| W4 | 高 | 后端是控制台子系统程序且 spawn 未隐藏，Windows 必弹黑色空控制台窗 | spawn 加 windowsHide: true |
| W5 | 高 | 启动探活只连 TCP 端口，端口被别的服务占用时误判为就绪→白屏 | 改为请求 /api/health，超时放宽到 60s |
| W6 | 高 | before-quit 里异步 spawn taskkill 来不及执行，残留 backend.exe 占端口 | 改 spawnSync 同步杀进程 |
| W7 | 中 | 中文 traceback 经管道输出时 Windows 代码页可能 UnicodeEncodeError 二次崩溃 | 注入 PYTHONUTF8/PYTHONIOENCODING |
| W8 | 中 | preload 暴露 getAppVersion/getUserDataPath 但主进程一个 ipcMain.handle 都没注册 | 补齐 handler，设置页版本号改为真实读取 |
| B1 | 严重 | amount=Infinity 通过 gt=0 校验落库，此后所有读接口永久 500（数据投毒） | Field 加 allow_inf_nan=False |
| B2 | 高 | amount=NaN 时错误详情无法 JSON 序列化，422 变 500 | 自定义 RequestValidationError 处理器净化非有限浮点 |
| B3 | 高 | 非补零日期 '2026-9-5' 能入库但被 SQLite strftime 静默丢弃，记录列表与统计对不上账 | 严格补零正则 + 真实日期双重校验，返回 400 |
| B4 | 中 | 空白分类名 '   ' 绕过 min_length=1；'餐饮 ' 与 '餐饮' 裂成两个分类 | field_validator 先去空白再校验 |
| B5 | 中 | CSV 导出写固定可预测的 /tmp 路径，符号链接可劫持覆写任意文件 | 改内存生成直接返回，不落盘 |
| B6 | 低 | 只传 year 或只传 month 时筛选被静默忽略返回全量 | 分别支持 year-only / month-only |
| U1 | 中 | Element Plus 未配置 locale，分页/二次确认/日期选择器全是英文，违反"所有文本使用中文" | app.use(ElementPlus, { locale: zhCn }) |
| U2 | 中 | 日期默认值用 toISOString()（UTC），东八区凌晨 0-8 点默认成昨天 | 新增 todayLocal()/thisMonthLocal() 统一替换 |
| U3 | 中 | 金额初始 0 被 el-input-number 钳到 min=0.01，不填金额直接保存会静默记一笔 ¥0.01 | 初始值改 undefined，提交前保留两位小数 |
| U4 | 低 | 记录表缺 ID 列、统计总额非红色、预算 80% 边界用 >80、首页未设预算显示 ¥0.00 橙色 | 按设计逐条修正 |
| U5 | 低 | RecordsTab/StatisticsTab 加载了分类却从未使用，每次进页面白发一次请求 | 删除死代码 |
| C1 | 高 | npm run typecheck 从未通过：主进程打包分支返回对象缺 args 字段 | 补 args: []，typecheck 接入验证流程 |

### 验证结果
- 后端：19 → **30 个测试通过**，覆盖率 95% → **97%**；black/isort/flake8 全过
- 渲染层：typecheck（node+web）全过，electron-vite build 成功（2260 模块）
- 浏览器端到端：F1 记账（成功提示/清空/日期保留/概览联动）、F2 记录（ID 列/二次确认/取消不删）、
  F3 统计（红色总额/饼图/占比 100.0%）、F5 预算（空状态/80% 边界黄色/超支红色）、
  F6 分类（新增自定义/默认不可删/同步到记账下拉框）、F8 主题（即时生效/刷新后保持）全部实测通过
- Windows 构建：GitHub Actions 4 分 38 秒成功，产出便携版 94.7MB + NSIS 安装包 94.9MB，
  便携版 exe 已下载并校验（PE32 GUI、MZ 头、字节数与 Release 完全一致）

### 已知未修复项（有意保留，附理由）
- CORS allow_origins=["*"]：桌面单机应用，收紧可能破坏 file:// 来源的打包态，风险收益比不合算
- CSV 金额导出为原始浮点而非两位小数：导出是数据而非展示，展示层已统一 toFixed(2)
- SQLite 单连接 + async handler 的串行化特性：当前架构下无并发问题，改每请求连接属重构，留待 v4.0
- portable 目标二次双击的残余风险：单实例锁只能阻止第二个 Electron 实例，NSIS 解压壳的 RMDir
  发生在应用启动前；彻底解决需要 splash 图或改用 NSIS 安装版，答辩建议用安装版演示

---

## v3.1.0 功能升级（第 4-5 轮）- 2026-10-07

> 本轮在另一台 Windows 机器上完成，代码与调研文档已合并回 master（调研文档在 `docs/upgrade-research/`）。

### 我给AI的提示词
```
【项目背景】
校园消费记账桌面应用 v3.0（Electron + Vue3 + Element Plus + ECharts + FastAPI + SQLite），
已发布为 Windows 便携版 exe。现在想把它从"能跑通的课程作业"提升到"合格/优秀的软件"，
但我不确定该补哪些功能，也不确定桌面应用在不同窗口比例下该怎么布局。

【需求描述】
1. 先做调研，不要直接写代码：
   a) 对标市面上的记账应用（钱迹/随手记/鲨鱼/一木/薄荷/YNAB/Actual/Firefly III/MMEX/
      ezBookkeeping），拉一张功能矩阵，标出必备/推荐/加分，并在"本项目"一列标出已有与缺失
   b) 调研桌面 Web 应用（VS Code / Notion / Slack / Windows XAML）怎么处理窗口缩放，
      给出适合本项目的断点方案（宽度断点 + 长宽比断点）
2. 按调研结论只做 P0（合格线）里性价比最高的几项，不要一次全做
3. 响应式要覆盖"竖窗/窄窗"形态，现在窗口最小 900x650 根本拉不窄

【约束边界】
- 不改数据库表名和字段名，不改已有 API 的路径与响应格式
- 保持便携版语义：数据库仍落在 exe 同目录
- 新功能要有测试
- 已有的输入校验（金额必须是有限数、日期严格补零）不能回退

【验收标准】
- 编辑已有记录：行内按钮能改金额/分类/描述/日期，保存后列表与数据库都更新
- 搜索与筛选：能按关键词（描述/分类）和分类筛选，能一键重置
- 备份与恢复：能导出 JSON 备份、能从备份恢复；恢复前二次确认，且能覆盖回原数据
- 响应式：窗口拉成竖条时导航变底部栏，拉宽时回到侧边栏；指标卡列数随宽度变化
```

### 发现的问题 / 需求来源
本轮的需求不是"我觉得该加什么"，而是两份调研报告（`docs/upgrade-research/`）推导出来的：
- **`report-features.md`**（对标约 20 款记账应用）给出 P0 合格线清单。对照发现本项目
  **没有编辑记录功能**（矩阵 A3，必备级）——只能删了重记，属于"合格硬伤"；
  **没有备份/恢复**（B2），而调研里"数据丢失/停止维护是致命伤"被反复提及；
  **没有搜索筛选**（D1/C6）。这三项即本轮范围。
- **`report-audit.md`**（代码审计）确认了上述缺口，并额外记录 v2.0 Web 版的遗留问题
  （UTC 日期错位、图表监听泄漏、pywebview 生产路径缺 `base:'./'` 必然白屏）。
- **`report-responsive.md`**：现状是"只有宽度断点的雏形，且 `minWidth: 900` 直接把竖窗挡死"，
  侧栏 220px 常驻且无折叠、无底部栏；报告给出了断点总表与最小改动清单。

### AI 实际改了什么

**后端**（`campus_expense_web/backend/main.py`，+161 行）
- 新增 `PUT /api/expenses/{id}` 编辑记录，沿用同一套校验（金额有限数 + 日期补零正则与真实日期）
- 新增 `GET /api/backup`（导出全部记录/分类/预算为 JSON）与 `POST /api/restore`（整库替换）
- `get_expenses` 扩展筛选参数：keyword / category / date_from / date_to / min_amount / max_amount
- 新增 17 个后端测试，测试总数 30 → 47

**前端**（`campus_expense_electron`）
- `RecordsTab.vue`：新增关键词搜索框（描述/分类，回车即搜、清空自动重查）、分类下拉、
  "筛选/重置"按钮与"匹配 N 条"提示；每行新增编辑按钮，弹出编辑弹窗（金额/分类/描述/日期），
  保存后刷新列表
- `SettingsTab.vue`：新增"数据备份与恢复"卡片，备份导出 JSON（文件名复用 `todayLocal()`），
  恢复前用 `ElMessageBox.confirm` 二次确认
- 新增 `composables/useLayout.ts`：把窗口尺寸/比例抽成响应式状态，导出 `navMode`
  （full / rail / bottom）、`cols`、`isPortrait`、`isUltrawide`、`isCompactHeight`。
  断点沿用 Windows 官方分级（Small ≤640 / Medium 641–1007 / Large ≥1008），
  并叠加"竖窗"与"超宽"两个形状判断——纯宽度断点看不见这两个维度
- `App.vue`：导航按 `navMode` 切换形态（宽窗侧边栏 / 中宽图标轨 / 竖窗底部 tab bar）
- 新增 2 个渲染层测试，测试总数 30 → 32

### 验证结果
- 后端 **47 个 pytest 通过**，覆盖率 95%；black/isort/flake8 全过
- 渲染层 **32 个 vitest 通过**；typecheck（node + web）全过
- 端到端实测（生产构建产物 + 真实后端，浏览器驱动）：
  - 编辑：把 id=3 的金额从 ¥88.00 改成 ¥99.00 → 列表刷新，数据库确认为 99.0
  - 搜索：关键词"地铁"把 3 行筛成 1 行
  - 备份恢复：备份 3 条共 ¥136.5 → 删 2 条并把预算改成 5000 → 恢复后 3 条、¥136.5、预算回到未设置
  - 响应式：视口 717×744（比例 0.96，竖窗）时导航呈底部 tab bar，与 `useLayout` 的 portrait 分支一致
- Windows 构建：GitHub Actions 成功，产出 v3.1.0 便携版 99.3MB + 安装包 99.6MB，Release 已发布

---

## == 我的检查与验证说明（v3.x）==

### 我怎么确认结果正确

1. **自动化测试**：后端 47 个 pytest（覆盖率 95%）覆盖新端点的正常路径与边界——编辑记录沿用
   金额/日期校验、备份恢复的整库替换、筛选参数组合；渲染层 32 个 vitest 覆盖组件行为，
   其中版本号断言特意改成"格式匹配"而非硬编码，避免发版就要改测试。
2. **端到端人工验证**（不完全信测试）：把生产构建产物用静态服务器托管、接真实后端，
   在浏览器里逐功能点击。理由是本项目的单元测试走 ASGI 内存调用，
   测不出真实的 HTTP 行为与界面交互——这一点在 v3.0.1 的缺陷（Infinity 投毒）上已经吃过亏。
3. **交叉验证**：备份/恢复不是"点了没报错就算过"，而是构造"备份 → 主动破坏数据 → 恢复 →
   逐项比对金额合计与预算值"的往返用例，确认恢复真的把数据还原了而不是只弹了成功提示。
4. **审查边界**：编辑弹窗确认回填值正确（金额 88.00 / 分类 / 日期 / 描述计数 2/200）后才提交；
   搜索用中文关键词验证（顺带发现裸 curl 传中文查询串会被 uvicorn 判为非法请求，属于测试方法问题而非程序缺陷）。
5. **回归检查**：升级后重跑 v3.0.1 修过的中文 locale 与 `todayLocal()` 是否仍在生效——
   分页仍显示"共 3 条 / 20条/页"，新代码里的备份文件名也复用了 `todayLocal()`，说明修复被沿用了。

---

## == 心得（v3.x）==

### 本次协作最大惊喜
**"先调研再动手"比"直接加功能"高效得多。** 我原本的想法是"多加点功能显得厉害"，
但让 AI 先对标约 20 款真实记账应用、拉出功能矩阵并按必备/推荐/加分排序之后，
结论完全变了：本项目真正缺的是**编辑记录**这种"不补就算不上合格"的基础能力，
而不是多账本、云同步这类听起来厉害的东西。同一份调研还指出"数据丢失/停止维护是致命伤"，
于是备份/恢复被提到 P0——这是我自己拍脑袋排不出来的优先级。

### 本次协作最大失望
**AI 在"环境相关的坑"上仍然会重复踩。** 另一台 Windows 机器上，子 agent 在环境说明里
专门记录了"`npm ... | tail` 会吞掉退出码导致误判成功"这类教训——而我在本机验证时
**原封不动地又踩了一次**（用 `npm ci | tail` 的退出码判断成功，实际是 TLS 失败）。
同一个坑在同一个项目里被两次记录，说明这类问题没法靠"记住"解决，只能靠把判断方式固化下来
（比如改成先落盘再看文件、或用后台任务退出码）。这也印证了设计文档写得越具体、
后续越不容易走回头路。

---

## 验收自评（v3.1.0 提交版）

| 验收标准 | 是否达标 | 证据 |
|---------|---------|------|
| ① 功能跑通：选定需求的基本功能可演示正确结果 | ✅ | 核心功能 8 项（记账 / 记录列表+搜索筛选 / **编辑记录** / 删除二次确认 / 分类统计饼图 / 预算三色提醒 / 自定义分类 / CSV 导出）+ 三项增强（**备份恢复** / 亮暗主题 / **多比例响应式**）均可在 Windows 便携版上演示，端到端已逐项点击验证 |
| ② ≥2轮迭代记录：每轮记录"我给AI的修改要求"+"AI实际改了什么" | ✅ | 共 5 轮：v1.0 三轮（初版 + 中文字体修复 + 预算进度条）、v3.0 质量迭代 Round 1-4、v3.0 全面质量审计 Round 5-7（21 项缺陷）、v3.1.0 功能升级（本轮）。每轮均含"我给AI的提示词"与"AI实际改了什么" |
| ③ ≥1次验证说明：写清楚"我怎么确认AI生成结果是正确的" | ✅ | 两节《我的检查与验证说明》：v1.0 用 36 个单测 + offscreen GUI 验证；v3.x 用后端 47 个 pytest + 渲染层 32 个 vitest + 端到端浏览器点击 + 备份恢复往返比对 + 回归检查 |
| ④ 1条心得：本次协作中最大的意外是什么，AI 在哪里让你惊喜或失望 | ✅ | 两节《心得》：v1.0 记录 matplotlib 中文字体需人工介入；v3.x 记录"先调研再动手"带来的优先级修正（惊喜）与环境类坑被重复踩中（失望） |

**提交物**：本文件即《迭代记录与心得》的完整版，可直接发布到个人博客；
仓库内另有一份面向提交的精简排版版本 `ITERATION_AND_INSIGHTS.md`。
