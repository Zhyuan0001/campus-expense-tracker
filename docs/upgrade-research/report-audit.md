# 校园记账桌面应用 — 代码审计报告

**范围**：`C:/Users/10473/AppData/Local/Temp/campus-expense-tracker/`（只读审计，未改动项目文件）。重点 v3.0 Electron + v2.0 Web/pywebview + 共用后端。

**结论速览**：Electron 版工程质量明显更高；共用的 FastAPI 后端**无 SQL 注入、金额/日期校验扎实，但缺"编辑记录"端点**；**Web 版前端有一批遗留缺陷**（UTC 日期错位、Vite 模板 CSS 破坏布局、图表监听泄漏、测试近乎为零）；**pywebview 生产路径因缺 `base:'./'` 必然白屏**。

## 1. 功能清单

**DB schema**（`campus_expense_web/backend/main.py`）：
- `expenses`(id, amount, category, description, date, created_at) L125-132
- `categories`(id, name UNIQUE, icon, is_default) L135-140，默认 8 分类 L154-163
- `budget`(id, monthly_budget) L143-146 — **单行全局预算，非按月**
- `settings`(key, value) L149-152 — **建表但未使用**（主题走 localStorage）
- DB 路径 `_get_db_path()` L272-280，模块导入即建连 L283。

**API 14 个路由**：`GET /`(L286)、`GET /api/health`(L291)、`GET/POST/DELETE /api/expenses`(L296/304/326)、`GET/POST/DELETE /api/categories`(L333/342/351)、`GET/PUT /api/budget`(L358/378)、`GET /api/statistics/{year}/{month}`(L384)、`GET /api/export`(L395)。**无编辑端点、无分页、无鉴权**（已全仓库确认）。前端组件：Web 版 5 Tab（ExpenseTab/RecordsTab/StatisticsTab/BudgetTab/SettingsTab）+ 遗留 `HelloWorld.vue`；Electron 版多 `DashboardTab`，并抽出 `api/index.ts`、`utils/constants.ts`、`composables/useTheme.ts`。**两版均无 vue-router（App.vue `component :is` 手工切换）、无 Pinia**。

## 2. 前端结构问题

- **P1 API 层重复**：`API_BASE` 硬编码 5 处（ExpenseTab:106、RecordsTab:73、StatisticsTab:62、BudgetTab:117、SettingsTab:114）；`getCategoryIcon` 重复 2 处（RecordsTab:132、StatisticsTab:112）；`loadCategories` 重复 4 处 → 每次切 Tab 重复请求分类。Electron 已用 `api/index.ts` 解决。
- **P1 UTC 日期错位**：Web `ExpenseTab.vue:124,175` 用 `new Date().toISOString().split('T')[0]`、`StatisticsTab.vue:75` 用 `.toISOString().slice(0,7)` → 东八区凌晨记错日期/月初看错月份。Electron 已用 `constants.ts:31-39` 的 `todayLocal()` 修复。
- **P1 图表/监听泄漏**：Web `StatisticsTab.vue:185-192` 注册 `window resize` 却**无 `onBeforeUnmount`、不 `dispose()`**，切 Tab 持续泄漏。Electron:148-151 已修。
- **P1 客户端分页**：`RecordsTab.vue:97-121` 拉全量再 slice，翻页/改页大小（L59-60）**重复拉全量**。Electron 改 `computed pagedExpenses`（仅止血，根因在后端无分页）。
- **P2**：ExpenseTab:120-125 金额初值 0 + `:min=0.01`，失焦钳到 0.01 可静默记 ¥0.01（Electron 已改 `undefined`，:112-119）；`ExpenseTab.vue:145-157` 顺序 await 未用 `Promise.all`；加载失败仅 `console.error`（ExpenseTab:141/RecordsTab:128/StatisticsTab:108/BudgetTab:159）；BudgetTab:86,137 阈值 `>80` 与 Electron `>=80` 不一致；SettingsTab:174 导出名硬编码忽略后端日期；HelloWorld.vue 及 `assets/{hero.png,vite.svg,vue.svg}`、`public/icons.svg` 为模板死代码。

## 3. 后端逐端点

- **SQL 注入：无**。全部参数化绑定；`get_expenses` L196 的 f-string 仅拼常量片段，值仍绑定。安全。
- **校验**：amount `gt=0, allow_inf_nan=False` L70 ✅；date 正则+真实日期 L26,306-311 ✅；description max 200 L72 ✅；分类名 strip+1-20 L86-94 ✅。缺口：**记录 category 仅 min_length=1，无 max_length、不去空白、不校验存在于分类表** L71；**icon 无 max_length** L87；**year 完全不校验** L297,384。
- **错误处理**：端点无 try/except，DB 异常退化为无信息 500（L304-404）；`delete_category` 对"不存在"和"默认分类"统一 400（L351-355），且**删分类不清理由它引用的记录**（L237-245）→ 记录/统计残留该分类名。
- **设计**：`budget` 是全局单行（L143-146,247-256），`GET /api/budget` 取当月支出（L361-362），"月度预算"语义与实现不符。
- **安全 P1**：CORS `allow_origins=["*"]` + 无鉴权 + 绑 127.0.0.1（L37-43）→ 浏览器任意网页可跨域读写个人记账数据（AGENTS.md:284 承认是已知取舍）。

## 4. 测试覆盖

- **后端 pytest 约 30 用例**（`tests/test_api.py`）：覆盖良好，含 `TestDefectRegressions`(L322-447) 针对 Infinity/NaN、非补零日期、空白分类、CSV 字节、year 过滤。漏测：`PUT /api/budget` 的 0/负/极大值（仅正常值 L260-266）、delete_category 不存在 vs 默认的状态码区分、category/icon 超长、导出文件名头。
- **Web vitest 严重不足**：仅 3 文件 × 2 条"能挂载"断言（如 `ExpenseTab.test.ts:5-15`），**无行为断言**；StatisticsTab/SettingsTab 无测试。
- **Electron vitest 质量高**：6 页 + useTheme 共 40+ 行为用例。
- **CI**：`ci.yml:155` `npm run lint || true` 吞掉 ESLint 失败；Electron 无 lint/prettier。

## 5. 响应式

- **关键**：Web `src/style.css` 里约 10 处 `@media(max-width:1024px)` 全是 **Vite 模板 hero/#next-steps 示例规则**（L28/68/78/179/193/204/213/251/271），与业务无关；业务组件**零 `@media`**。
- **P1 布局破坏**：`style.css:159-169` `#app{width:1126px;margin:auto;text-align:center;border-inline}`，`main.ts:6-7` 中 CSS 后加载生效 → 应用被锁 1126px 居中、全局文字居中，与 `App.vue:105-110` 打架；`:root{font:18px}` 抬高字号。应整体换成 Electron 版 style.css。
- 固定 `el-aside width="220px"`（App.vue:4）不折叠；固定列数网格 `ExpenseTab.vue:233` repeat(2)/`BudgetTab.vue:214` repeat(3)；图表写死高度（StatisticsTab:245-248=400px、Dashboard:321=260px）。Electron 窗口最小 900×650（`main/index.ts:170-171`）、pywebview 800×600（`app.py:79`），窄窗/系统缩放下预算三列卡片会挤压溢出。无 aspect-ratio/容器查询。Electron 略好：DashboardTab:342-355、BudgetTab:249-253 有断点。

## 6. 健壮性/安全

- 超大金额：后端仅 `gt=0` **无上限**（L70），前端无 `:max` → 可写 1e308 级。**P2**
- XSS：分类名/描述/图标均 `{{ }}` 文本插值，**无 `v-html`，风险低**；CSV 顿号/引号转义有回归测试（L407-421）。
- 日期格式后端严格；但 Web 前端传入的却是 UTC 日期（§2）。
- 异常提示不一致：保存类透出 `detail`（ExpenseTab:182/SettingsTab:152），删除类笼统"删除失败"（RecordsTab:143/SettingsTab:165），加载类静默。

## 7. 便携版差异

**Electron（健壮）**：单实例锁 L17-20；`getDbPath()` 可写探测 + 逐级回退 `userData` L38-62；探活查 `/api/health` 而非端口 L112-145；同步 `taskkill /f /t` L154-161；`windowsHide` L85 + `PYTHONUTF8` L74 防 Windows 弹窗/中文崩溃；CSV 走原生 IPC L201-216；preload 仅暴露 3 方法。**遗留**：dev 命令硬编码 `python3`（L31，Windows 常见只有 `python`）**P2**；`sandbox:false`（L178）**P2**。

**pywebview（问题多）**：
- **P0 生产白屏**：`app.py:71-72` 用 `file://dist/index.html`，但 `vite.config.ts:5-7` **无 `base:'./'`** → 产物引用绝对 `/assets/...` → `file:///assets/...` 404 → 空白窗。
- **P1**：`start_backend` L26-34 不保存 Popen 句柄 → 关窗不杀 uvicorn，**残留占 8000**；`wait_for_port` L14-23 只探 TCP 不探 `/api/health` → 端口被占仍白屏；`sys.executable -m uvicorn` L30 在 PyInstaller 冻结后失效。
- DB 路径各版不同（pywebview 写 `campus_expense_web/campus_expenses.db`），数据不互通。

## 8. 改进点汇总

**P0**
1. pywebview 生产白屏 — `vite.config.ts:5-7` 加 `base:'./'`，或改本地 HTTP 加载。

**P1**
2. 缺编辑端点 — 后端加 `PUT/PATCH /api/expenses/{id}`（复用 `ExpenseCreate`+`DATE_PATTERN`），前端记录行加编辑按钮；补测试。
3. Web UTC 日期 — 移植 `todayLocal()/thisMonthLocal()` 到 `ExpenseTab.vue:124,175`、`StatisticsTab.vue:75`。
4. Web 模板 CSS 污染 — 换 `style.css`，删 HelloWorld 及模板资源。
5. 图表泄漏 — 照抄 Electron `StatisticsTab.vue:148-151`。
6. 全量拉取+客户端分页 — 后端加 `limit/offset`+`total`，前端服务端分页。
7. CORS `*`+无鉴权 — `main.py:37-43` 收敛来源或加本地 token。
8. pywebview 进程不受托管/探活弱 — `app.py:26-34,14-23`。
9. Web 未设 Element Plus 中文 locale — `main.ts:16` 加 `zhCn`（Electron `main.ts:2,14` 已做）。
10. Web 测试形同虚设 — 以 Electron 测试为模板补行为断言。
11. 记录 category 不受控 + 金额无上限 — `main.py:71` 加 max_length 并校验存在，`:70` 加 `le`。

**P2**：`PUT /api/budget` 边界测试、year 校验、delete_category 状态码语义与不解引用清理、预算非按月、icon 无长度限制、端点无 try/except、前端加载失败静默、阈值口径不一致、Web 导出文件名/index.html 模板值、Electron `python3` 与 `sandbox:false`、CI `lint||true`、窄窗响应式（侧栏折叠、网格降级、图表高度）。

**健康度对比**：Web 版在 API 抽离、时区、主题、图表清理、i18n、模板残留、测试、打包健壮性上全面落后；Electron 版除后端共性问题和少量 dev/sandbox 项外，是可靠的当前版本。建议修复顺序：P0 → P1-3(日期) → P1-4(CSS) → P1-2(编辑) → P1-6(分页) → P1-7(安全) → 其余。
