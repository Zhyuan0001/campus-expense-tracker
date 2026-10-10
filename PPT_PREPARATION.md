# 校园消费记账系统 v3.1.0 - PPT 演示材料

## 一、项目概述

### 1.1 项目背景
大学生生活费管理需求：
- 消费记录分散，难以统计
- 月度预算缺乏监控
- 需要可视化分析消费结构

### 1.2 产品定位
**便携式桌面应用** - "哪里解压哪里运行，数据随身携带"

### 1.3 核心功能
- ✅ 快速记账（消费记录增删查）
- ✅ **记录编辑**（行内编辑金额/分类/描述/日期）
- ✅ **搜索与筛选**（关键词、分类、日期区间、金额区间）
- ✅ 分类统计（饼图可视化）
- ✅ 月度分析（仪表盘总览）
- ✅ 预算提醒（进度条监控，三色状态）
- ✅ 数据导出（CSV 格式）
- ✅ **备份与恢复**（JSON 全量备份，恢复前二次确认）
- ✅ 主题切换（亮/暗模式）
- ✅ 自定义分类（个性化管理）
- ✅ **多比例响应式**（侧边栏 / 图标轨 / 底部栏三态自适应）

---

## 二、技术架构

### 2.1 技术栈选型

| 层级 | 技术 | 选型理由 |
|------|------|----------|
| **桌面包装** | Electron 33 | 内置 Chromium，跨平台一致体验 |
| **前端框架** | Vue 3 + TypeScript | 组合式 API，类型安全 |
| **UI 组件库** | Element Plus | 企业级组件，开箱即用 |
| **图表库** | ECharts 6 | 交互式数据可视化 |
| **后端框架** | FastAPI | 异步高性能，自动文档生成 |
| **数据库** | SQLite3 | 零配置，便携嵌入式 |
| **构建工具** | electron-vite + Vite | 极速热重载 |
| **打包工具** | electron-builder + PyInstaller | 双层打包，真正便携 |

### 2.2 架构图

```
┌─────────────────────────────────────────┐
│         Electron 主进程                  │
│  - 窗口管理                             │
│  - 后端生命周期控制                     │
│  - 数据库路径配置                       │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
┌───────▼─────┐  ┌────▼────────┐
│  渲染进程   │  │  后端进程   │
│  (Vue 3)    │  │  (FastAPI)  │
│             │  │             │
│ - 仪表盘    │  │ - REST API  │
│ - 记账表单  │◄─┤ - SQLite    │
│ - 统计图表  │  │ - 数据导出  │
│ - 预算管理  │  │             │
│ - 设置面板  │  │             │
└─────────────┘  └─────────────┘
     HTTP/JSON API (localhost:8000)
```

### 2.3 便携版实现原理

**双层打包方案**：

1. **PyInstaller** 将 FastAPI 后端打包为独立可执行文件
   - 包含 Python 运行时 + 所有依赖
   - 无需目标机器安装 Python

2. **electron-builder** 将 Electron + 后端 exe 打包
   - Windows: NSIS 安装包 / Portable 便携版
   - Linux: AppImage
   - 无需目标机器安装 Node.js

**数据库路径策略**：

```typescript
function getDbPath(): string {
  if (app.isPackaged) {
    // 生产模式：数据库与可执行文件同目录
    const portableDir = process.env['PORTABLE_EXECUTABLE_DIR']
    const base = portableDir ? portableDir : dirname(process.execPath)
    return join(base, 'campus_expenses.db')
  }
  // 开发模式：项目 resources 目录
  return join(__dirname, '../../resources/backend/campus_expenses.db')
}
```

---

## 三、功能演示

### 3.1 仪表盘（Dashboard）

**功能亮点**：
- 月度消费总额大字展示
- 分类占比饼图（ECharts 交互式）
- 最近 7 天消费趋势
- 预算使用进度条

**截图**：`/tmp/dashboard_dark.png`

### 3.2 快速记账（Expense Tab）

**功能亮点**：
- 下拉选择分类（8 种默认 + 自定义）
- 金额输入自动校验（必须 > 0）
- 日期选择器（默认今天）
- 提交后表单自动清空
- 成功提示 Toast

**操作流程**：
1. 选择分类（如"餐饮"）
2. 输入金额（如 25.5）
3. 输入描述（如"午餐"）
4. 选择日期（默认今天）
5. 点击"添加消费"
6. 看到成功提示，表单清空

### 3.3 记录管理（Records Tab）

**功能亮点**：
- 表格展示所有记录
- 支持按年月筛选
- 删除前二次确认弹窗
- 分页显示（每页 10 条）

**截图**：`/tmp/delete_confirm.png`

### 3.4 统计分析（Statistics Tab）

**功能亮点**：
- 分类占比饼图（环形图）
- 月度对比柱状图
- 图例点击筛选
- 悬停显示详细数据

### 3.5 预算管理（Budget Tab）

**功能亮点**：
- 设置月度预算
- 实时显示已用/剩余
- 进度条可视化（绿色 < 80%，黄色 < 100%，红色超支）
- 超支警告提示

### 3.6 设置面板（Settings Tab）

**功能亮点**：
- 主题切换（亮/暗模式）
- 自定义分类管理（添加/删除）
- 数据导出 CSV
- 应用版本信息

**截图**：`/tmp/settings_tab.png`

### 3.7 暗色模式（Dark Mode）

**功能亮点**：
- 一键切换亮/暗主题
- 全局样式适配
- ECharts 图表颜色自适应
- 持久化存储用户偏好

**截图**：`/tmp/dark_mode.png`

---

## 四、迭代历程

### v1.0 - PyQt5 原型版（2026-09-28）

**技术栈**：Python + PyQt5 + SQLite + matplotlib

**完成功能**：
- 基础记账（增删改查）
- 分类统计（matplotlib 饼图）
- 月度分析
- 预算提醒
- 数据导出 CSV

**心得体会**：
- PyQt5 开发效率高，但 UI 美化困难
- matplotlib 图表交互性差
- 单文件部署简单，但跨平台需打包 Python

---

### v2.0 - 现代 Web 版（2026-09-29）

**技术栈**：Vue 3 + FastAPI + pywebview + Element Plus + ECharts

**改进点**：
- 前端：现代 Web 技术栈，UI 美观
- 后端：REST API，前后端分离
- 图表：ECharts 交互式可视化
- 主题：支持亮/暗模式切换

**遇到的问题**：
- pywebview 依赖系统 Webview，Linux 下样式不一致
- 部分 CSS 特性在系统 Webview 中不支持
- 跨平台体验不一致

**心得体会**：
- Web 技术栈 UI 开发效率高
- 前后端分离架构清晰
- 但 pywebview 不适合追求一致体验的桌面应用

---

### v3.0 - Electron 便携版（2026-09-29）

**技术栈**：Electron + Vue 3 + FastAPI + PyInstaller + electron-builder

**核心改进**：
- **桌面包装**：pywebview → Electron（内置 Chromium）
- **打包方案**：PyInstaller 打包后端，真正便携
- **UI 升级**：Indigo 主题色，10px 圆角，动画过渡
- **代码质量**：TypeScript 类型安全，统一 API 层

**四轮迭代**：

#### Round 1：视觉与交互修复
- 统一主题色为 Indigo (#6366F1)
- 修复暗色模式下图表文字不可见
- 优化表单提交后清空逻辑
- 添加删除确认弹窗

#### Round 2：代码质量与性能
- 提取共享常量（分类颜色、图标）
- 统一 API 层（axios 封装）
- 优化 ECharts 配置（响应式尺寸）
- 添加 TypeScript 类型注解

#### Round 3：后端 API 增强
- 添加健康检查端点 `/health`
- 优化数据库连接管理（lifespan）
- 添加 CORS 中间件
- 改进错误处理

#### Round 4：UI 打磨与细节
- 仪表盘布局优化
- 统计图表交互增强
- 设置面板分类管理
- 响应式适配

**心得体会**：
- Electron 虽然体积大，但体验一致性好
- 双层打包方案复杂，但便携性强
- Web 技术栈开发效率高，UI 美化容易

### v3.1.0 - 调研驱动的功能升级（2026-10-07）

**做法**：先调研再动手，不做"拍脑袋加功能"。两份调研报告见 `docs/upgrade-research/`。

**调研结论（对标约 20 款记账应用 + 桌面应用缩放方案）**：
- 本项目**缺「编辑记录」**——竞品里属必备功能，只能删了重记是"合格硬伤"
- 竞品教训反复提到"数据丢失/停止维护是致命伤" → **备份/恢复**优先级提至 P0
- 缺**搜索与筛选**，记录一多就找不到
- 现状 `minWidth: 900` 把竖窗形态挡死，侧栏 220px 常驻无折叠

**本版实现**：

| 方向 | 改动 |
|------|------|
| 记录编辑 | 新增 `PUT /api/expenses/{id}`；记录页每行加编辑按钮，弹窗改金额/分类/描述/日期 |
| 搜索筛选 | 记录页加关键词搜索（描述/分类）、分类下拉、筛选/重置、匹配条数提示；后端 `GET /api/expenses` 支持 keyword / category / date_from / date_to / min_amount / max_amount |
| 备份恢复 | 新增 `GET /api/backup`（JSON 全量）与 `POST /api/restore`（整库替换）；设置页加"数据备份与恢复"卡片，恢复前二次确认 |
| 多比例响应式 | 新增 `composables/useLayout.ts`，按窗口尺寸与长宽比输出 `navMode`（侧边栏 / 图标轨 / 底部栏）、`cols` 等；断点沿用 Windows 官方分级并叠加"竖窗""超宽"两个形状判断 |

**验证**：后端测试 30 → **47 个**（覆盖率 95%）；渲染层测试 30 → **32 个**；
端到端实测编辑落库、关键词筛选、备份破坏恢复往返、竖窗底部栏形态。

---

## 五、测试报告

### 5.1 功能测试

> 端到端实测：以生产构建产物 + 真实后端，在浏览器中逐功能点击验证（2026-10-10）。

| 测试项 | 预期结果 | 状态 |
|--------|----------|------|
| 添加消费记录 | 成功创建、表单清空、日期保留今天、本月概览联动 | ✅ |
| **记录编辑** | 行内编辑按钮 → 弹窗回填正确 → 保存后列表与数据库同步更新 | ✅ |
| **搜索与筛选** | 关键词"地铁"把 3 行筛成 1 行；分类筛选与重置可用 | ✅ |
| 删除消费记录 | 二次确认弹窗；取消不删、确认才删 | ✅ |
| 分类统计饼图 | 正确显示占比（实测占比合计 100.0%） | ✅ |
| 月度预算设置 | 保存成功，进度条与三色状态正确（80% 边界为黄色） | ✅ |
| **备份与恢复** | 备份 3 条 ¥136.5 → 删 2 条并改预算 → 恢复后数据与预算完整还原 | ✅ |
| 主题切换 | 全局样式切换，重启后保持所选主题 | ✅ |
| 数据导出 CSV | 表头 `ID,日期,分类,描述,金额`、utf-8-sig 带 BOM，Excel 中文不乱码 | ✅ |
| 自定义分类 | 添加成功并同步到记账下拉框；默认分类不可删除 | ✅ |
| **多比例响应式** | 竖窗（717×744，比例 0.96）时导航呈底部栏 | ✅ |

### 5.2 输入校验与破坏性测试

**自动化测试**（每次 push 由 CI 并行执行，四路 job）：

| 范围 | 数量 | 覆盖率 | 说明 |
|------|------|--------|------|
| 后端 API（pytest） | **47 个** | 95% | 含 11 个回归用例，锁死下表加粗的场景 |
| 渲染层组件（vitest） | **32 个** | — | 6 个页面组件 + 主题/布局 composable |
| 类型检查 | tsc + vue-tsc | — | node 与 web 两套 tsconfig |
| 代码规范 | black / isort / flake8 / prettier | — | 版本固定在 requirements-dev.txt |

**逐项校验**（下表为真实 HTTP 实测；加粗行为 v3.0.1 补的回归用例）：

| 测试场景 | 输入 | 预期 | 实际 | 状态 |
|----------|------|------|------|------|
| 负数金额 | amount=-10 | 422 错误 | ✓ | ✅ |
| 零金额 | amount=0 | 422 错误 | ✓ | ✅ |
| 超大金额 | amount=999999999 | 成功 | ✓ | ✅ |
| 空分类 | category="" | 422 错误 | ✓ | ✅ |
| 超长分类名 | 21 字符 | 422 错误 | ✓ | ✅ |
| 超长描述 | 201 字符 | 422 错误 | ✓ | ✅ |
| 错误日期格式 | date="2026/09/29" | 400 错误 | ✓ | ✅ |
| 空日期 | date="" | 400 错误 | ✓ | ✅ |
| 不存在的分类 | category="不存在的" | 成功（宽松校验，无外键约束） | ✓ | ✅ |
| SQL 注入 | category="'; DROP TABLE" | 存储为普通文本（全参数化绑定） | ✓ | ✅ |
| XSS 攻击 | description="<script>alert(1)</script>" | 存储为普通文本，渲染时转义 | ✓ | ✅ |
| 删除不存在的记录 | DELETE /api/expenses/99999 | 404 错误 | ✓ | ✅ |
| 重复分类名 | POST 已存在的分类 | 400 错误 | ✓ | ✅ |
| 删除默认分类 | DELETE 默认分类 | 400 错误 | ✓ | ✅ |
| **非有限数金额** | amount=Infinity / NaN | **422 且绝不落库** | ✓ | ✅ |
| **非补零日期** | date="2026-9-5" | **400** | ✓ | ✅ |
| **不存在的日期** | date="2026-02-30" | 400 | ✓ | ✅ |
| **空白分类名** | name="   " | **422** | ✓ | ✅ |
| **预算非有限数** | PUT amount=Infinity | **422** | ✓ | ✅ |
| **CSV 字节内容** | 描述含逗号/引号/换行 | RFC4180 转义 + BOM + 表头逐字符一致 | ✓ | ✅ |

> **说明**：v3.0 时期曾用一份 28 项手工黑盒清单验收（当时记录 27/28），
> 但它在 19 个单测全绿的情况下漏掉了上表加粗的 5 类真实缺陷——原因是那些测试走
> TestClient 的内存调用，且从不发送 Infinity、非补零日期与空白分类名。
> 其中"Infinity 落库"会让之后所有读接口永久 500、"非补零日期"会让统计与记录列表对不上账。
> v3.0.1 起改为「真实 HTTP 黑盒 + 回归用例」双轨，这些场景已固化为自动化测试。

**前端层测试**：
- 金额输入框输入字母 → HTML5 `type="number"` 自动过滤
- 特殊字符输入 → 正常存储，前端转义显示
- 快速连续提交 → 表单提交后清空，防止重复

### 5.3 便携性测试

**已在 Linux 开发机验证**：
1. 开发模式启动，后端自动拉起、健康探活通过 ✓
2. 数据库路径解析正确（`DB_PATH` 环境变量优先，回退到可写目录探测）✓
3. 数据持久化，重启应用后数据保留 ✓
4. PyInstaller 打包的后端可独立运行 ✓
5. CI 日志确认真实打包产物中含 `resources\backend\backend.exe` ✓

**Windows 实机验证**：

- [x] 在真实 Windows 机器上运行便携版 exe：启动正常（无黑色控制台窗口、无白屏）
- [x] 增删改查、编辑、搜索筛选、图表、预算、主题、备份恢复等功能正常
- [x] `campus_expenses.db` 在 exe 同目录生成，数据可持久化
- [ ] 拷贝 exe + db 到 U 盘，在另一台 Windows 电脑运行，数据保留（建议演示前顺手验一次）

> 演示建议：**用 NSIS 安装版**。portable 版每次启动会把 95MB 解压到临时目录且期间无界面，
> 存在"用户以为没点上、再点一次导致解压目录被清理"的残余风险；安装版没有这个环节。

---

## 六、核心代码展示

### 6.1 Electron 主进程（后端生命周期管理）

```typescript
function startBackend(): void {
  const { cmd, args, cwd } = getBackendCommand()
  
  const env = {
    ...process.env,
    DB_PATH: getDbPath(),  // 便携版数据库路径
    PORT: String(BACKEND_PORT)
  }

  backendProcess = spawn(cmd, args, {
    cwd,
    env,
    stdio: ['ignore', 'pipe', 'pipe'],
    // 后端是控制台子系统程序，不隐藏的话 Windows 会额外弹一个黑色控制台窗口
    windowsHide: true
  })

  backendProcess.stdout?.on('data', (data: Buffer) => {
    console.log(`[Backend] ${data.toString().trim()}`)
  })

  backendProcess.on('error', (err: Error) => {
    // 常见于杀毒软件隔离了 backend.exe，必须给出可见提示而不是静默退出
    dialog.showErrorBox('后端无法启动', `未能启动内置的后端服务：${err.message}`)
  })

  backendProcess.on('exit', (code: number | null) => {
    console.log(`后端进程退出，退出码: ${code}`)
    backendExitCode = code
    backendProcess = null
  })
}

// 必须校验业务健康检查接口，而不是只探测端口：
// 端口被其它服务占用时 TCP 也能连通，窗口会照常打开，但所有请求都打到错误的服务上
function waitForBackend(maxRetries = 120, interval = 500): Promise<void> {
  return new Promise((resolve, reject) => {
    let retries = 0
    const check = async (): Promise<void> => {
      try {
        const res = await fetch(`http://${BACKEND_HOST}:${BACKEND_PORT}/api/health`)
        if (res.ok) {
          resolve()
          return
        }
        throw new Error(`健康检查返回 ${res.status}`)
      } catch {
        retries++
        if (retries >= maxRetries) {
          reject(new Error('后端在 60 秒内未就绪'))
        } else {
          setTimeout(check, interval)
        }
      }
    }
    check()
  })
}
```

### 6.2 统一 API 层

> 把原先散落在 5 个组件里的 `API_BASE` 硬编码与重复请求逻辑收敛到一处（`api/index.ts`）。

```typescript
const API_BASE = 'http://127.0.0.1:8000/api'

export const api = {
  // year/month 与筛选条件可组合；后端已做参数校验
  getExpenses(year?: number, month?: number, filters?: {
    keyword?: string; category?: string
    date_from?: string; date_to?: string
    min_amount?: number; max_amount?: number
  }) {
    return axios.get<Expense[]>(`${API_BASE}/expenses`, { params: { year, month, ...filters } })
  },

  createExpense(data: { amount: number; category: string; description: string; date: string }) {
    return axios.post<Expense>(`${API_BASE}/expenses`, data)
  },

  updateExpense(id: number, data: { amount: number; category: string; description: string; date: string }) {
    return axios.put<Expense>(`${API_BASE}/expenses/${id}`, data)   // v3.1.0 新增
  },

  deleteExpense(id: number) {
    return axios.delete(`${API_BASE}/expenses/${id}`)
  },

  getBackup() {
    return axios.get<BackupData>(`${API_BASE}/backup`)              // v3.1.0 新增
  },

  restoreBackup(payload: unknown) {
    return axios.post<{ message: string }>(`${API_BASE}/restore`, payload)  // v3.1.0 新增
  }
  // 其余：分类增删查、月度统计、预算读写、CSV 导出
}
```

### 6.3 后端数据库路径策略

```python
def _get_db_path() -> str:
    """获取数据库路径，支持便携版"""
    env_path = os.environ.get("DB_PATH")
    if env_path:
        return env_path
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，数据库与 exe 同目录
        return os.path.join(os.path.dirname(sys.executable), "campus_expenses.db")
    # 开发模式
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "campus_expenses.db")
```

---

## 七、心得体会

### 7.1 技术选型经验

**Electron vs pywebview vs Tauri**：

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **Electron** | 体验一致，生态成熟 | 体积大（~150MB） | 追求一致体验 |
| **pywebview** | 体积小，启动快 | 依赖系统 Webview | 内部工具 |
| **Tauri** | 体积最小，性能好 | Rust 学习曲线 | 性能敏感应用 |

**结论**：对于课程作业和演示，Electron 是最佳选择——开发效率高，体验一致，部署简单。

### 7.2 便携版实现难点

**难点 1：双层打包**
- PyInstaller 打包后端为 exe
- electron-builder 打包 Electron + 后端 exe
- 需要配置 `extraResources` 将后端 exe 复制到 resources

**难点 2：数据库路径**
- 开发模式：`resources/backend/campus_expenses.db`
- 生产模式（NSIS）：`dirname(process.execPath)/campus_expenses.db`
- 生产模式（Portable）：`PORTABLE_EXECUTABLE_DIR/campus_expenses.db`

**难点 3：后端生命周期**
- Electron 主进程启动时 spawn 后端
- 等待后端就绪（TCP 端口探测）
- 窗口关闭时 kill 后端进程
- 异常退出时清理后端进程

### 7.3 代码质量提升

**TypeScript 类型安全**：
```typescript
interface ExpenseCreate {
  amount: number
  category: string
  description?: string
  date: string
}
```

**统一 API 层**：
- 集中管理所有 API 调用
- 统一错误处理
- 方便 Mock 数据测试

**共享常量**：
```typescript
export const CATEGORY_COLORS: Record<string, string> = {
  '餐饮': '#FF6B6B',
  '交通': '#4ECDC4',
  '学习': '#45B7D1',
  // ...
}
```

### 7.4 测试经验

**黑盒测试重要性**：
- 发现边界情况（负数金额、超长字符串）
- 验证安全性（SQL 注入、XSS）
- 提升代码健壮性

**测试策略**：
- API 层：curl / Postman 测试接口
- 前端层：浏览器手动测试交互
- 集成测试：端到端测试完整流程

### 7.5 课程收获

1. **全栈开发能力**：前端 Vue + 后端 FastAPI + 桌面 Electron
2. **工程化思维**：TypeScript、代码质量工具、Git 工作流
3. **产品意识**：用户体验、UI 设计、迭代优化
4. **问题解决**：便携版打包、数据库路径、进程管理

---

## 八、未来展望

### 8.1 功能扩展
- [ ] 多账本支持（个人/家庭/项目）
- [ ] 周期性账单（自动记录固定消费）
- [ ] 数据统计增强（同比/环比分析）
- [ ] 云同步（可选，多设备同步）
- [ ] 移动端适配（React Native / Flutter）

### 8.2 技术优化
- [ ] 数据库加密（SQLCipher）
- [ ] 自动更新（electron-updater）
- [ ] 性能优化（虚拟滚动、懒加载）
- [ ] 单元测试覆盖（Vitest + pytest）

### 8.3 商业化探索
- [ ] 免费增值模式（基础功能免费，高级功能付费）
- [ ] 主题市场（用户自定义主题）
- [ ] 插件系统（第三方扩展）

---

## 九、演示流程建议

### 9.1 开场（1 分钟）
- 介绍项目背景和需求
- 展示产品定位："便携式桌面记账应用"

### 9.2 功能演示（5 分钟）
1. **启动应用**（10 秒）
   - 双击 exe，展示快速启动（演示建议用安装版）

2. **添加消费**（30 秒）
   - 选择分类、输入金额、描述、日期
   - 提交，展示成功提示与首页概览联动

3. **查看与编辑记录**（45 秒）
   - 切换到记录页，展示列表（ID/日期/分类/描述/金额）
   - **用关键词搜索**（如输入"地铁"）演示筛选，再点"重置"
   - **点击行内编辑按钮**改金额，保存后展示列表同步更新
   - 删除记录，展示二次确认弹窗

4. **统计分析**（1 分钟）
   - 切换到统计页
   - 展示饼图与分类占比表
   - 切换月份看历史数据

5. **预算管理**（30 秒）
   - 设置月度预算
   - 展示进度条与三色状态（把预算调到刚好 80% 展示黄色提醒档）

6. **备份与恢复**（45 秒）
   - 设置页点"备份数据"，展示导出的 JSON
   - 故意删掉两条记录
   - 点"从备份恢复"，展示二次确认与恢复后数据还原

7. **主题切换与多比例响应式**（45 秒）
   - 设置页切换暗色主题，展示全局样式与图表同步适配
   - **拖动窗口拉成竖条**，展示导航从侧边栏自动变为底部栏、指标卡列数变化

8. **数据导出**（30 秒）
   - 导出 CSV 文件
   - 用 Excel 打开展示中文与金额格式正常

### 9.3 技术讲解（3 分钟）
- 展示架构图
- 讲解便携版实现原理（数据库为何能跟着 exe 走）
- 展示核心代码片段

### 9.4 迭代历程（1 分钟）
- v1.0（PyQt5）→ v2.0（Web 栈）→ v3.0（Electron 便携版）→ **v3.1.0（编辑/搜索/备份恢复/响应式）**
- 重点讲 v3.0.1 那一轮"全面质量审计查出 21 项缺陷"——包括 Infinity 数据投毒、
  portable 双击互删等，说明为什么要"先验证再交付"
- 再讲 v3.1.0 "先调研 20 款竞品再定优先级"，解释为什么做的是编辑记录而不是花哨功能

### 9.5 心得体会（1 分钟）
- 技术选型经验
- 遇到的挑战和解决方案
- 课程收获

### 9.6 Q&A（1 分钟）

**总时长**：约 12 分钟

---

## 十、附录

### 10.1 项目文件结构

```
SofteareEnjineer/
├── campus_expense_electron/          # v3.1.0 Electron 便携版（当前）
│   ├── src/
│   │   ├── main/index.ts             # Electron 主进程（后端生命周期/单实例锁/错误提示）
│   │   ├── preload/index.ts          # 预加载脚本（contextBridge 安全桥接）
│   │   └── renderer/src/
│   │       ├── App.vue               # 主应用组件（按 navMode 切换导航形态）
│   │       ├── api/index.ts          # 统一 API 层
│   │       ├── components/           # 6 个功能组件（含 Dashboard）
│   │       ├── composables/          # useTheme（主题）/ useLayout（多比例响应式）
│   │       ├── utils/constants.ts    # 分类配色、图标、todayLocal() 等共享工具
│   │       └── __tests__/            # 渲染层 vitest 组件测试（32 个用例）
│   ├── vitest.config.ts              # 渲染层测试配置
│   ├── resources/backend/            # PyInstaller 打包产物（gitignore，CI 生成）
│   ├── backend.spec                  # PyInstaller 打包配置
│   └── package.json                  # 项目配置（electron-builder 配置在 build 字段）
│
├── campus_expense_web/              # v2.0 现代 Web 版（历史）
│   ├── backend/
│   │   ├── main.py                  # FastAPI 后端（v3.x 共用）
│   │   └── tests/test_api.py        # 后端 pytest（47 个用例，覆盖率 95%）
│   └── frontend/                    # Vue 3 前端
│
├── docs/upgrade-research/           # v3.1.0 升级调研报告（功能矩阵/响应式/代码审计/开发环境）
├── .github/workflows/               # CI（4 路 job）+ Windows 构建发布工作流
├── campus_expense_tracker.py        # v1.0 PyQt5 版（历史）
├── AGENTS.md                        # 项目说明（给 AI 智能体的项目说明书）
├── DESIGN.md                        # 设计文档（含 v3.0 实现偏差说明）
├── PPT_PREPARATION.md               # 本文件
├── ITERATION_AND_INSIGHTS.md        # 迭代记录与心得（提交版）
├── iteration_log.md                 # 迭代记录（完整版，含全部轮次）
└── WINDOWS_BUILD_GUIDE.md           # Windows 构建指南
```

### 10.2 API 端点列表

> 下表与 `campus_expense_web/backend/main.py` 的实际路由逐条核对（2026-10-10）。

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/` | 服务标识 |
| GET | `/api/health` | 健康检查（Electron 主进程用它做启动探活） |
| GET | `/api/expenses` | 获取消费记录；支持 year / month / keyword / category / date_from / date_to / min_amount / max_amount 筛选 |
| POST | `/api/expenses` | 创建消费记录 |
| **PUT** | `/api/expenses/{id}` | **编辑消费记录**（v3.1.0 新增） |
| DELETE | `/api/expenses/{id}` | 删除消费记录 |
| GET | `/api/categories` | 获取分类列表 |
| POST | `/api/categories` | 创建自定义分类（名称去空白后不可为空、不可重复） |
| DELETE | `/api/categories/{id}` | 删除自定义分类（默认分类拒绝删除） |
| GET | `/api/budget` | 获取预算与本月使用情况（未设置时 monthly_budget 为 null） |
| **PUT** | `/api/budget` | 设置月度预算（注意是 PUT） |
| GET | `/api/statistics/{year}/{month}` | 月度统计：总额 + 按分类聚合（饼图数据） |
| GET | `/api/export` | 导出全部记录为 CSV（内存生成，utf-8-sig 带 BOM） |
| **GET** | `/api/backup` | **导出全量 JSON 备份**（记录 + 分类 + 预算，v3.1.0 新增） |
| **POST** | `/api/restore` | **从备份恢复**（整库替换，v3.1.0 新增） |

> 主题（亮/暗）**没有后端接口**，由渲染层 localStorage 持久化；
> 数据库中的 `settings` 表按设计保留但当前未使用。
> 早期文档曾列出 `/api/statistics/monthly`、`/api/statistics/category`、
> `/api/budget/status`、`/api/export/csv`、`/api/settings/theme`，这些端点从未实现，已更正。

### 10.3 数据库表结构

```sql
-- 消费记录表
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 分类表
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    icon TEXT DEFAULT '📌',
    is_default INTEGER DEFAULT 0
);

-- 预算表（单行全局预算）
CREATE TABLE budget (
    id INTEGER PRIMARY KEY,
    monthly_budget REAL
);

-- 设置表
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

### 10.4 默认分类

| 分类 | 图标 | 颜色 |
|------|------|------|
| 餐饮 | 🍜 | #FF6B6B |
| 交通 | 🚌 | #4ECDC4 |
| 学习 | 📚 | #45B7D1 |
| 娱乐 | 🎮 | #F9CA24 |
| 社交 | 🎉 | #FF9FF3 |
| 购物 | 🛒 | #54A0FF |
| 医疗 | 💊 | #5F27CD |
| 其他 | 📌 | #2EC4B6 |

---

**文档版本**：v3.1.0  
**最后更新**：2026-10-10  
**作者**：校园消费记账团队

> 相关文档：迭代记录与心得见 `iteration_log.md`（完整版）与 `ITERATION_AND_INSIGHTS.md`（提交版）；
> 升级调研报告见 `docs/upgrade-research/`；构建指南见 `WINDOWS_BUILD_GUIDE.md`。
