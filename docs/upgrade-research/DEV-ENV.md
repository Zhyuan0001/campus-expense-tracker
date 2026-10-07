# 开发环境与规范（子 agent 任务书附件）

> 给后续做开发/测试/评价的子 agent。**先读这份，再动手。**

## 项目
- Windows 便携版记账应用：**Vue3 + Element Plus + ECharts + FastAPI + SQLite**，Electron 打包成单 exe。
- 本地代码：`C:/Users/10473/AppData/Local/Temp/campus-expense-tracker/`（clone 而来，**Temp 会被系统清，重要产物别只留这**）
- GitHub：`Zhyuan0001/campus-expense-tracker`（public）

## 怎么跑起来
| | 命令 | 地址 |
|:--|:--|:--|
| 前端 | `cd campus_expense_web/frontend && npm run dev` | http://localhost:5173 |
| 后端 | `cd campus_expense_web/backend && <venv>/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000` | http://127.0.0.1:8000 |
| 项目 venv | `C:/Users/10473/AppData/Local/Temp/campus-expense-tracker/.venv` | — |
| 数据库 | `campus_expense_web/campus_expenses.db`（SQLite，表：expenses/categories/budget/settings） | — |

## 浏览器操作（Playwright MCP，已配好可用）
- 工具名：`mcp__playwright__browser_*`（navigate / click / type / snapshot / screenshot / console_messages / network_requests …）
- 驱动**系统 Edge**，**默认有头**（屏幕上能看到窗口在动），用的是**临时 profile**（无登录态、关掉即清）
- 输出文件落：`C:\Users\10473\AppData\Local\Temp\playwright-mcp\`
- ⚠️ **Element Plus 的 `el-select`**：要**点外层 wrapper**（snapshot 里带 `[cursor=pointer]` 的 generic），点里面的 `combobox` input 会报 "intercepts pointer events"
- ⚠️ 截图是**给模型看**的，不等于给用户看；操作应基于 `browser_snapshot` 的无障碍树，**不要靠截图坐标点**
- ⚠️ 首次调用会拉起 Edge，稍慢；用 `browser_wait_for` 等页面就绪

## 环境铁律（踩过的坑）
- 跑 `.py` 用**全路径**解释器（项目 venv 或大杂烩 `E:\jetbrain\pycharmproject\pythonproject666\.venv\Scripts\python.exe`），别用裸 `python`
- **沙箱**：Bash 工具写不了 E 盘的 npm/pip 缓存 → npm 加 `--cache <TEMP>/npm-cache`，pip 加 `--no-cache-dir`
- **`npm ... | tail` 会吞退出码**（拿到 tail 的 0）→ 判断成败别用管道，用后台任务退出码或先落盘
- **heredoc 里别写字面 `\\`**（经 JSON 折叠成一个 `\`，语法错）→ 用 `pathlib.Path(...).as_posix()` 之类绕开
- 长任务（npm/pip/构建）**放后台**跑

## 报告规范
- 落盘目录：`D:/二春/嵌入式/campus-upgrade/`
- 正文写文件，**最终回复 ≤200 字摘要**（子 agent 系统提示倾向只回文本，**任务书须点名要求写文件**）
- 结论优先：**问题 + 位置(文件:行号) + 严重度 + 建议修法**
