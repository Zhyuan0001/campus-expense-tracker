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
