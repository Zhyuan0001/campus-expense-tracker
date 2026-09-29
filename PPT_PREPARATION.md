# 校园消费记账系统 v3.0 - PPT 演示材料

## 一、项目概述

### 1.1 项目背景
大学生生活费管理需求：
- 消费记录分散，难以统计
- 月度预算缺乏监控
- 需要可视化分析消费结构

### 1.2 产品定位
**便携式桌面应用** - "哪里解压哪里运行，数据随身携带"

### 1.3 核心功能
- ✅ 快速记账（消费记录增删改查）
- ✅ 分类统计（饼图可视化）
- ✅ 月度分析（仪表盘总览）
- ✅ 预算提醒（进度条监控）
- ✅ 数据导出（CSV 格式）
- ✅ 主题切换（亮/暗模式）
- ✅ 自定义分类（个性化管理）

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

---

## 五、测试报告

### 5.1 功能测试

| 测试项 | 预期结果 | 实际结果 | 状态 |
|--------|----------|----------|------|
| 添加消费记录 | 成功创建，表单清空 | ✓ | ✅ |
| 删除消费记录 | 弹窗确认，成功删除 | ✓ | ✅ |
| 分类统计饼图 | 正确显示占比 | ✓ | ✅ |
| 月度预算设置 | 保存成功，进度条更新 | ✓ | ✅ |
| 主题切换 | 全局样式切换 | ✓ | ✅ |
| 数据导出 CSV | 文件下载成功 | ✓ | ✅ |
| 自定义分类 | 添加/删除成功 | ✓ | ✅ |

### 5.2 黑盒破坏性测试

**API 层测试（27/28 通过）**：

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
| 不存在的分类 | category="不存在的" | 成功（宽松校验） | ✓ | ✅ |
| SQL 注入 | category="'; DROP TABLE" | 存储为普通文本 | ✓ | ✅ |
| XSS 攻击 | description="<script>alert(1)</script>" | 存储为普通文本 | ✓ | ✅ |
| 删除不存在的记录 | DELETE /api/expenses/99999 | 404 错误 | ✓ | ✅ |
| 重复分类名 | POST 已存在的分类 | 400 错误 | ✓ | ✅ |
| 删除默认分类 | DELETE 默认分类 | 400 错误 | ✓ | ✅ |

**前端层测试**：
- 金额输入框输入字母 → HTML5 `type="number"` 自动过滤
- 特殊字符输入 → 正常存储，前端转义显示
- 快速连续提交 → 表单提交后清空，防止重复

### 5.3 便携性测试

**测试场景**：
1. 在 Linux 开发机运行开发模式 ✓
2. 验证数据库路径正确 ✓
3. 数据持久化测试 ✓
4. 重启应用后数据保留 ✓

**预期 Windows 测试**：
- 双击 exe 启动
- 数据库在 exe 同目录创建
- 数据持久化
- 拷贝到 U 盘，在其他 Windows 电脑运行，数据保留

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
    stdio: ['ignore', 'pipe', 'pipe']
  })

  backendProcess.stdout?.on('data', (data: Buffer) => {
    console.log(`[Backend] ${data.toString().trim()}`)
  })

  backendProcess.on('exit', (code: number | null) => {
    console.log(`后端进程退出，退出码: ${code}`)
    backendProcess = null
  })
}

function waitForBackend(maxRetries = 40, interval = 500): Promise<void> {
  return new Promise((resolve, reject) => {
    let retries = 0
    const check = (): void => {
      const socket = net.createConnection(BACKEND_PORT, BACKEND_HOST, () => {
        socket.destroy()
        resolve()
      })
      socket.on('error', () => {
        socket.destroy()
        retries++
        if (retries >= maxRetries) {
          reject(new Error('后端启动超时'))
        } else {
          setTimeout(check, interval)
        }
      })
    }
    check()
  })
}
```

### 6.2 统一 API 层

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  timeout: 5000
})

export const expenseApi = {
  getList: (year?: number, month?: number) => 
    api.get('/expenses', { params: { year, month } }),
  create: (data: ExpenseCreate) => 
    api.post('/expenses', data),
  delete: (id: number) => 
    api.delete(`/expenses/${id}`)
}

export const categoryApi = {
  getList: () => api.get('/categories'),
  create: (data: CategoryCreate) => 
    api.post('/categories', data),
  delete: (id: number) => 
    api.delete(`/categories/${id}`)
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
   - 双击 exe，展示快速启动
   
2. **添加消费**（30 秒）
   - 选择分类、输入金额、描述、日期
   - 提交，展示成功提示
   
3. **查看记录**（30 秒）
   - 切换到记录 Tab
   - 展示刚添加的记录
   - 删除记录，展示确认弹窗
   
4. **统计分析**（1 分钟）
   - 切换到统计 Tab
   - 展示饼图，悬停显示详情
   - 点击图例筛选分类
   
5. **预算管理**（30 秒）
   - 设置月度预算
   - 展示进度条变化
   
6. **主题切换**（30 秒）
   - 切换到暗色模式
   - 展示全局样式适配
   
7. **数据导出**（30 秒）
   - 导出 CSV 文件
   - 用 Excel 打开展示

### 9.3 技术讲解（3 分钟）
- 展示架构图
- 讲解便携版实现原理
- 展示核心代码片段

### 9.4 迭代历程（1 分钟）
- v1.0 → v2.0 → v3.0 演进
- 每轮迭代改进点

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
├── campus_expense_electron/          # v3.0 Electron 便携版
│   ├── src/
│   │   ├── main/index.ts             # Electron 主进程
│   │   ├── preload/index.ts          # 预加载脚本
│   │   └── renderer/src/
│   │       ├── App.vue               # 主应用组件
│   │       ├── api/index.ts          # 统一 API 层
│   │       └── components/           # 6 个功能组件
│   ├── resources/backend/            # PyInstaller 打包的后端
│   └── package.json                  # 项目配置
│
├── campus_expense_web/              # v2.0 现代 Web 版（历史）
│   ├── backend/main.py               # FastAPI 后端
│   └── frontend/                     # Vue 3 前端
│
├── campus_expense_tracker.py        # v1.0 PyQt5 版（历史）
├── AGENTS.md                         # 项目说明
├── DESIGN.md                         # 设计文档
└── iteration_log.md                  # 迭代记录
```

### 10.2 API 端点列表

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/expenses` | 获取消费记录列表 |
| POST | `/api/expenses` | 创建消费记录 |
| DELETE | `/api/expenses/{id}` | 删除消费记录 |
| GET | `/api/categories` | 获取分类列表 |
| POST | `/api/categories` | 创建自定义分类 |
| DELETE | `/api/categories/{id}` | 删除自定义分类 |
| GET | `/api/statistics/monthly` | 获取月度统计 |
| GET | `/api/statistics/category` | 获取分类统计 |
| GET | `/api/budget` | 获取当前预算 |
| POST | `/api/budget` | 设置月度预算 |
| GET | `/api/budget/status` | 获取预算使用状态 |
| GET | `/api/export/csv` | 导出 CSV |
| GET | `/api/settings/theme` | 获取当前主题 |
| POST | `/api/settings/theme` | 设置主题 |

### 10.3 数据库表结构

```sql
-- 消费记录表
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL CHECK(amount > 0),
    category TEXT NOT NULL,
    description TEXT DEFAULT '',
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

-- 预算表
CREATE TABLE budget (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

**文档版本**：v3.0  
**最后更新**：2026-09-29  
**作者**：校园消费记账团队
