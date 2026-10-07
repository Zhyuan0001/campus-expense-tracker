# 桌面 Web 应用多比例响应式布局调研 —— 校园记账（Electron）适配方案

> 技术栈：Vue 3.5 + Element Plus 2.14 + ECharts 6.1 + Electron 33；Windows 便携版。

---

## 0. 现状速览（读代码得出）

| 位置 | 现状 | 问题 |
|---|---|---|
| `src/main/index.ts` | 窗口 `1200×800`，`minWidth: 900`，`minHeight: 650` | **硬伤**：minWidth 900 直接把「9:16 竖条窗」挡死，用户根本拉不窄；minHeight 650 让 16:9 笔记本（768 高）没有压缩余地 |
| `App.vue` | `<el-aside width="220px">` 固定宽度 + `<el-main padding:28px>` | 220px 侧栏在任何窗口都常驻，窄窗里吃掉一半屏；无任何断点 |
| `App.vue` 导航 | 6 项：首页 / 记账 / 记录 / 统计 / 预算 / 设置（`el-menu`，未用 `collapse`） | 无折叠、无抽屉、无底部栏 |
| `DashboardTab.vue` | `grid-template-columns: repeat(4,1fr)`；`@media(max-width:900px)`→2 列，`@media(max-width:600px)`→1 列；图表 2 列→1 列；`max-width:1200px` | 全项目**唯一**成体系的断点；但只按宽度，图表高度固定 260px |
| `StatisticsTab.vue` | `max-width:1200px`；饼图 `height:380px`，legend 竖排在**右侧** | 竖窗时右侧 legend 挤压饼图；无断点 |
| `RecordsTab.vue` | `el-table` 满宽，操作列 `fixed="right"`；`el-pagination` 用 `layout="total, sizes, prev, pager, next"` | 窄窗下表格横向溢出、分页条换行错乱 |
| `ExpenseTab.vue` | `max-width:800px`；表单栅格 `repeat(2,1fr)`；`label-width:80px` | 窄窗双列表单挤成一团 |
| `BudgetTab.vue` | `max-width:900px`；3 列卡片，`@media(max-width:700px)`→1 列 | 只在 700px 一次性塌到 1 列，中间无过渡 |
| `SettingsTab.vue` | `max-width:1000px` | 内容本就好排，风险小 |
| 图表 resize | Dashboard / Statistics 都监听 `window.resize` 调 `chart.resize()` | 只响应**窗口**尺寸；侧栏折叠时容器变了但窗口没变 → 图表不重算宽度 |

**结论**：目前只有「宽度断点」的雏形，且窗口最小尺寸限制了比例玩法；aspect-ratio / 容器查询 / 导航形态切换全部缺失。

---

## 1. 断点策略：按宽度 vs 按长宽比

### 1.1 两者是**正交**的，不是二选一
- **宽度断点（`@media (min-width/max-width)`）决定「骨架」**：侧栏是常驻还是抽屉、是侧栏还是底部 tab。导航方案取决于**可用横向空间**，与高度无关。
- **长宽比断点（`@media (aspect-ratio)` / `orientation`）决定「形状」**：同样是 1000px 宽，`1000×600`（横长）和 `1000×1600`（竖长）该完全不同的排法，而宽度断点**看不见**这个差别。这正是用户痛点「不同横纵比例怎么用」的根因。

> 一句话：**宽度管导航骨架，比例管堆叠密度，高度管纵向压缩。** 三者叠加使用。

### 1.2 `aspect-ratio` 媒体特性
范围特性（range feature），支持 `min-`/`max-`，值为 `宽/高`：
```css
@media (min-aspect-ratio: 16/9) { /* 比值 ≥1.78；21:9≈2.33 也命中 */ }
@media (max-aspect-ratio: 1/1)  { /* 比值 ≤1，竖长（高≥宽）*/ }
```
`min-aspect-ratio: 8/5` 命中 1.6 及以上；`max-aspect-ratio: 3/2` 命中 1.5 及以下（MDN 官方示例）。Baseline「广泛可用」，2015-07 起跨浏览器支持（MDN）。

### 1.3 `orientation` 关键字（竖/横粗判定）
```css
@media (orientation: portrait)  { /* 高 ≥ 宽 */ }
@media (orientation: landscape) { /* 宽 > 高 */ }
```
`orientation` 就是 `aspect-ratio` 相对 1:1 的特例，语义清晰，适合做「竖窗 → 换导航」的总开关。测的是**视口**非物理设备；软键盘会让视口变宽而误判（MDN 警告），桌面应用不受影响。

### 1.4 还需要一条**高度断点**
16:9 笔记本（`1366×768`）宽度够大（走「大屏」分支），但**高度只有 768**，纵向很紧：
```css
@media (max-height: 700px) { /* 压缩 padding、图表高度、卡片内边距 */ }
```
这正是 16:9 场景的关键，纯宽度断点永远触发不了它。

### 1.5 `@media` vs `@container`（容器查询）
| 维度 | `@media` | `@container` |
|---|---|---|
| 参照对象 | 视口 / 整个窗口 | 元素自身的父容器 |
| 擅长 | 页面级骨架（导航形态） | **组件级**自适应（卡片、图表、表单） |
| 复用性 | 全局断点会膨胀 | 组件走到哪适配到哪 |
| 支持度 | 全绿 | 全球 >90%，Chrome/Firefox/Safari/Edge 均支持，可上生产无需 polyfill |

**用法建议**：二者**配合**，不互替。
- 窗口级决策（导航换形态、主栅格列数）→ `@media`。
- 卡片级决策（「本月支出」卡片在自己的列里变上下堆叠）→ `@container`。这样同一张 `stat-card` 在 4 列/2 列/1 列里各自独立重排。
```css
.stat-cards { container-type: inline-size; }
@container (max-width: 260px) {
  .stat-card-inner { flex-direction: column; align-items: flex-start; }
}
```
> Electron 33 = Chromium 130，`@container`、`aspect-ratio` 媒体特性、`:has()` 均原生支持。（Chromium 版本对应未逐条查证。）

### 1.6 断点选值：优先参考 Windows 官方分级
微软 Windows 应用官方断点：

| 尺寸分级 | 断点 | 典型窗口 | 典型设备 |
|---|---|---|---|
| Small | **≤640px** | 480×854、540×960 | 手机/电视 |
| Medium | **641–1007px** | 960×540 | 平板 |
| Large | **≥1008px** | 1024×640、1366×768、1920×1080 | PC / 笔记本 |

桌面应用照抄这套即可，比自拍脑袋（768/992/1200）更贴 Windows 生态。

---

## 2. 桌面应用多比例布局模式

### 2.1 侧边栏在窄窗的四种归宿
| 形态 | 触发条件 | 优点 | 缺点 |
|---|---|---|---|
| **常驻全栏**（现 220px） | 宽窗 | 导航一眼可见 | 窄窗太占地 |
| **图标轨 rail**（64px，仅图标+tooltip） | 中窄窗 | 保留切换入口、省地 | 需记图标含义 |
| **抽屉 drawer**（隐藏，汉堡唤出，覆盖式） | 窄/竖窗 | 不占内容区 | 多一次点击 |
| **底部 tab bar**（图标+文字，5–6 项） | 竖窗/极窄 | 移动端直觉、拇指可达 | 占纵向空间 |

判据：**横向够 → 左侧栏（全栏/rail）；竖向为主或缺横向 → 底部栏。** 对应 `orientation` 横/竖两分支。

### 2.2 内容栅格重排（宽度驱动）
- **指标卡**：`4→3→2→1` 列（用 `repeat(auto-fit, minmax(...))` 可自动完成）。
- **图表**：`2 列→1 列`；竖窗/矮窗时降高度。
- **表格**：窄窗三选一 —— ① 隐藏次要列 + 横向滚动；② 转「卡片列表」；③ 保留表格 + `overflow-x:auto`。
- **表单**：`2 列→1 列`，`label-width` 固定 80px 改为 `label-position="top"`。

### 2.3 超宽屏（21:9 / 32:9）
1. **居中限宽**：`.container{max-width:1400px;margin:0 auto}`。
2. **多面板**：`grid-template-columns:250px 1fr 300px`。
3. **`clamp()` 流式**：`width:clamp(320px,80vw,1600px)`。

检测超宽用 `@media (min-aspect-ratio: 21/9)`。
**对本项目**：推荐「居中限宽 + 适度多列」：上限 ~1400px 居中；`min-aspect-ratio:21/9` 时图表 2 列提到 3 列。

---

## 3. 竖屏 / 窄窗形态（9:16，像手机）

- **导航一律沉到底部 tab bar**，5–6 个图标+短标签。
- **高频动作做成 FAB（悬浮「＋记一笔」）**：右下角圆形按钮。
- **内容单列卡片流**：指标卡 2×2 或单列；图表整宽单列；表格→卡片列表。
- **图表 legend 移到底部**：`StatisticsTab` 现为 `orient:'vertical', right:'5%'`，竖窗改 `orient:'horizontal', bottom:0`。
- **首屏信息密度**：「顶部月度总额大数字 + 下方滚动明细」。

> 竖窗关键不是「宽度小」，而是「**宽 < 高**」。即使宽度 700px，只要 `orientation:portrait`，也应改底部导航+单列。

---

## 4. 技术实现

### 4.1 CSS：Grid / Flex / clamp
- **骨架**：Grid（两列 `[nav][content]` ↔ 一行 `[content]` + 底部 `[nav]`）。
- **卡片流**：`grid-template-columns: repeat(auto-fit, minmax(min(240px,100%), 1fr))`。
- **流式间距**：`padding: clamp(12px, 2vw, 28px)`；图表 `height: clamp(180px, 32vh, 380px)`。
- **过渡**：侧栏宽度加 `transition: width .2s`。

### 4.2 Element Plus 响应式能力
- **栅格**：`el-row`/`el-col`，24 栏制，`el-col` 支持 `xs/sm/md/lg/xl`（约 xs<768 / sm≥768 / md≥992 / lg≥1200 / xl≥1920）：
  ```html
  <el-col :xs="24" :sm="12" :md="8" :lg="6">…</el-col>
  ```
  当前项目大量手写 Grid，可继续手写（更可控）。
- **菜单折叠**：`<el-menu :collapse="collapsed" collapse-transition>` → 宽度 64px，折叠态自动只显图标+tooltip。
- **抽屉**：`<el-drawer direction="ltr">` 承载窄窗侧栏；`el-aside` 宽度改动态 `:width="asideWidth"`。
- **表格/分页**：`el-table` 配 `:fit` 与列 `v-if="!narrow"`；`el-pagination` 的 `layout` 窄窗降级为 `"prev, pager, next"`。

### 4.3 Vue 层：响应式 hook
**(a) 全局窗口尺寸响应**（驱动骨架）：
```ts
// composables/useLayout.ts
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
export function useLayout() {
  const w = ref(window.innerWidth), h = ref(window.innerHeight)
  const onResize = () => { w.value = window.innerWidth; h.value = window.innerHeight }
  onMounted(() => window.addEventListener('resize', onResize))
  onBeforeUnmount(() => window.removeEventListener('resize', onResize))
  const ratio = computed(() => w.value / h.value)
  const isUltrawide = computed(() => ratio.value >= 21 / 9)
  const isPortrait  = computed(() => ratio.value <= 1)
  const isNarrow    = computed(() => w.value <= 640)
  const navMode = computed<'full' | 'rail' | 'bottom'>(() =>
    isPortrait.value || isNarrow.value ? 'bottom'
    : w.value <= 1007 ? 'rail' : 'full')
  const cols = computed(() => isUltrawide.value ? 3 : w.value >= 1008 ? 4 : w.value > 640 ? 2 : 1)
  return { w, h, ratio, isUltrawide, isPortrait, isNarrow, navMode, cols }
}
```

**(b) 容器尺寸响应**（驱动卡片/图表）—— 用 `ResizeObserver` 监听**内容区容器**而非 `window`：
```ts
const ro = new ResizeObserver(([e]) => {
  const cw = e.contentRect.width
  cardCols.value = cw > 1000 ? 4 : cw > 700 ? 2 : 1
  chart?.resize()
})
onMounted(() => ro.observe(contentRef.value!))
onBeforeUnmount(() => ro.disconnect())
```
（测试环境已 mock `ResizeObserver`，见 `__tests__/testHelpers.ts`。）

### 4.4 ECharts 自适应
- 建议换成 `ResizeObserver + resize()`，并加**防抖/throttle**。
- 初始化前必须确保容器已有宽高。

### 4.5 Electron 层
- **必须放宽最小尺寸**：`minWidth:900/minHeight:650` → 例如 `minWidth:360, minHeight:420`。**这是前置条件**，不改窗口约束，后面所有 CSS 都白搭。
- 可选支持记忆上次窗口 bounds。

---

## 5. 参考案例：桌面/Web 应用怎么处理窗口缩放

| 应用 | 做法 | 启示 |
|---|---|---|
| **VS Code** | 最左「活动栏」图标轨（64px）+ 可折叠侧栏面板 | 侧栏→图标轨 rail 是桌面软件标配 |
| **Notion / Obsidian** | 侧栏可手动/自动折叠成图标 + 折叠按钮 | 用户可手动干预 |
| **Slack / Discord** | 窄窗时频道/成员列表变覆盖式抽屉 | 宽度断点触发 drawer 的成熟范式 |
| **Windows 应用（XAML）** | 官方断点 Small≤640 / Medium 641–1007 / Large≥1008；五种技法：重定位、缩放、重排、显隐、重架构 | **直接采用这套断点值** |
| **Material Design** | 导航抽屉三态：标准/模态/底部栏 | 抽屉三态 = §2.1 |
| **超宽屏仪表盘** | 居中限宽 / 多面板 / `clamp()` | 本项目用「居中限宽 1400 + 适度三列」 |
| **移动端记账 app** | 底部 tab + 悬浮 FAB + 单列卡片 + 大数字总额 | 竖窗形态直接抄 |

---

## 6. 本项目具体方案

### 6.1 断点总表

**A. 宽度断点（定导航骨架 + 栅格列数）**

| 名称 | 宽度 | 侧栏形态 | 主内容 | 指标卡 | 图表 |
|---|---|---|---|---|---|
| 超宽 | ≥1600px | 全栏 240px | 限宽 1400 居中 | 4 列 | 3 列 |
| 大/常规 | 1008–1599px | 全栏 220px | 限宽 1200 | 4 列 | 2 列 |
| 中 | 768–1007px | **图标轨 64px**（`el-menu collapse`） | 自适应 | 3→2 列 | 2→1 列 |
| 窄 | 480–767px | **底部 tab bar**（可加汉堡抽屉） | 满宽 | 2 列 | 1 列 |
| 极窄 | <480px | 底部 tab bar | 满宽 | 1 列 | 1 列 |

**B. 长宽比断点（定形状，与宽度正交叠加）**

| 条件 | 追加动作 |
|---|---|
| `(min-aspect-ratio: 21/9)` 超宽 | 图表/卡片 3 列；内容限宽 1400 |
| `(orientation: portrait)` 竖窗 | **强制底部导航**；卡片单列；饼图 legend 移底部；表格转卡片列表；显示 FAB |
| `(max-height: 700px)` 矮窗（16:9 笔记本） | `el-main` padding 28→16；图表高 260→200；卡片内边距收紧 |

**C. 实现优先级（改动顺序）**
1. `main/index.ts`：放宽 `minWidth/minHeight` ——**先做**。
2. 新增 `useLayout.ts`，暴露 `navMode / cols / isPortrait / isUltrawide`。
3. `App.vue`：`el-aside` 宽度动态化 + `el-menu :collapse` + 底部 tab 分支。
4. 各 Tab：栅格改 `auto-fit` 或按 `cols` 动态；图表接 `ResizeObserver`；`el-pagination` layout 降级；表格窄窗隐藏次要列。
5. `style.css`：加 `aspect-ratio` / 高度断点媒体查询与 `clamp()` 间距。

### 6.2 各比例布局草图

**① 16:9 横长屏（1366×768，比例 1.78）** —— 宽度走「大屏」，高度紧 → `max-height:700px` 压缩
```
┌────────┬────────────────────────────────────────────┐
│ 校园记账│ [本月支出][剩余预算][本月笔数][日均消费]      │ ← 4 卡（padding 收紧）
│ ●首页  │ ┌───────────────┬───────────────┐          │
│  记账  │ │   分类占比     │   近6月趋势    │          │ ← 2 图（高 200）
│  记录  │ └───────────────┴───────────────┘          │
│  统计  │ ┌─────────────────────────────────────────┐ │
│  预算  │ │           最近记录 (表格)                │ │
│  设置  │ └─────────────────────────────────────────┘ │
└────────┴────────────────────────────────────────────┘
   220px                     内容限宽 1200 居中
```

**② 9:16 竖长屏（450×800，比例 0.56）** —— `orientation:portrait`，**强制底部导航**
```
┌──────────────────────┐
│ ☰  校园记账        ⋯ │  顶栏（汉堡/更多）
├──────────────────────┤
│  本月支出  ¥1234.56   │  大数字总额
│ ┌────────┐┌────────┐ │
│ │剩余预算││本月笔数│ │  指标卡 2×2
│ └────────┘└────────┘ │
│ ┌────────┐┌────────┐ │
│ │ 日均   ││ 预算%  │ │
│ └────────┘└────────┘ │
│ ┌──────────────────┐ │
│ │   分类占比(饼)    │ │  图表单列、legend 移底部
│ └──────────────────┘ │
│ ┌──────────────────┐ │
│ │   近6月趋势       │ │
│ └──────────────────┘ │
│ ┌──────────────────┐ │
│ │ 最近记录(卡片列表)│ │  表格→卡片
│ └──────────────────┘ │
│                   (＋)│  ← FAB 记一笔
├──────────────────────┤
│ 首页 记账 记录 统计 预算│  底部 tab bar
└──────────────────────┘
```

**③ 21:9 超宽屏（2560×1080，比例 2.37）** —— 限宽 1400 居中 + 三列
```
┌────────┬──────────────────────────────────────────────────────┐
│        │   [本月支出][剩余预算][本月笔数][日均消费]            │
│ 校园记账│  ┌───────────┬───────────┬───────────┐              │
│  ●首页 │  │  分类占比  │  近6月趋势 │ 预算进度   │  ← 3 列       │
│   记账 │  └───────────┴───────────┴───────────┘              │
│   记录 │        ┌───────────────────────────┐                │
│   统计 │        │       最近记录             │  ← 限宽 1400    │
│   预算 │        └───────────────────────────┘                │
│   设置 │                                    （两侧自然留白）   │
└────────┴──────────────────────────────────────────────────────┘
```

**④ 小窗口（640×480，比例 1.33）** —— 宽度 ≤640
```
┌──────────────────────┐
│ ☰  校园记账           │
├──────────────────────┤
│ ┌────────┐┌────────┐ │
│ │本月支出││剩余预算│ │  指标卡 2 列
│ └────────┘└────────┘ │
│ ┌────────┐┌────────┐ │
│ │本月笔数││ 日均   │ │
│ └────────┘└────────┘ │
│ ┌──────────────────┐ │
│ │   分类占比        │ │  图表单列
│ └──────────────────┘ │
│ ┌──────────────────┐ │
│ │   近6月趋势       │ │
│ └──────────────────┘ │
├──────────────────────┤
│ 首页 记账 记录 统计   │  底部 tab
└──────────────────────┘
```

**⑤ 自由缩放（过渡要平滑）**
- 侧栏宽度、主内容 padding 全部 `transition`。
- 卡片栅格用 `auto-fit + minmax(min(240px,100%),1fr)`，连续变化而非跳档。
- 卡片内部用 `@container` 决定「横排→竖排」。
- ECharts 用 `ResizeObserver` + 防抖跟手重绘。

### 6.3 关键代码落点（最小改动清单）
```ts
// src/main/index.ts
new BrowserWindow({ width:1200, height:800, minWidth:360, minHeight:420, ... })
```
```html
<!-- App.vue —— 三态导航 -->
<el-container :class="['app-container', `nav-${navMode}`]">
  <el-aside v-if="navMode !== 'bottom'" :width="navMode==='rail' ? '64px' : '220px'">
    <el-menu :collapse="navMode==='rail'" collapse-transition>…</el-menu>
  </el-aside>
  <el-main>…</el-main>
  <nav v-if="navMode === 'bottom'" class="bottom-tab">…</nav>
</el-container>
```
```css
/* style.css */
@media (orientation: portrait) { .app-container { flex-direction: column; } }
@media (min-aspect-ratio: 21/9) { .main-content > * { max-width: 1400px; margin-inline: auto; } }
@media (max-height: 700px)     { .main-content { padding: 16px; } .chart { height: 200px; } }
```

---

## 7. 未查证 / 需现场确认的点
- Element Plus `el-col` 的 `xs/sm/md/lg/xl` **精确像素值**（约 768/992/1200/1920）来自社区博客，未从 EP 官方文档逐字核对。
- Electron 33 ↔ Chromium 130 对应关系未逐条查证。
- `@container` 全球支持「>90%」来自 freetoolkit 博客，未用 caniuse 数值逐一核对。
- 本项目**未实际运行**窗口验证重排，草图为设计推演，落地后需在不同比例下实测。

---

## 参考来源
- MDN — `aspect-ratio` 媒体特性：https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/aspect-ratio
- MDN — `orientation` 媒体特性：https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/orientation
- Microsoft Learn — Screen sizes and breakpoints：https://learn.microsoft.com/en-us/windows/apps/design/layout/screen-sizes-and-breakpoints-for-responsive-design
- Microsoft Learn — Layout overview for Windows apps：https://learn.microsoft.com/en-us/windows/apps/design/layout/
- freeCodeCamp — Media Queries vs Container Queries：https://www.freecodecamp.org/news/media-queries-vs-container-queries/
- dev-toolbox — Ultrawide viewport layout strategies：https://www.dev-toolbox.tech/tools/viewport-size-reference/examples/ultrawide-viewport-layout
- dev.to — Container Queries vs Media Queries：https://dev.to/nickbenksim/container-queries-vs-media-queries-when-and-what-to-use-fij
- freetoolkit — CSS Container Queries explained：https://www.freetoolkit.io/blog/css-container-queries-explained
- Element Plus 栅格响应式：https://blog.csdn.net/gitblog_00506/article/details/165002621
- ECharts Handbook — Chart Container：https://echarts.apache.org/handbook/en/concepts/chart-size/
- ECharts 容器自适应/ResizeObserver：https://github.com/apache/echarts/issues/17428
- uxdworld — Bottom Tab Bar Navigation Design Best Practices：https://uxdworld.com/bottom-tab-bar-navigation-design-best-practices/
- Material Design — Responsive layout grid：https://m2.material.io/design/layout/responsive-layout-grid.html
- Electron — Window Customization：https://www.electronjs.org/docs/latest/tutorial/window-customization
