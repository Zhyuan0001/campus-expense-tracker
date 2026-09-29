# 校园消费记账系统 - 现代Web版

基于 Vue3 + TypeScript + Element Plus + FastAPI 的现代化桌面记账应用。

## ✨ 特性

- 🎨 **现代化UI**：Element Plus组件库，美观的Material风格
- 📱 **高DPI支持**：完美适配4K/Retina屏幕
- 🌓 **亮/暗主题**：一键切换，自动保存偏好
- 📊 **数据可视化**：ECharts饼图展示分类统计
- 🔒 **本地存储**：SQLite数据库，数据安全
- 📦 **跨平台**：Windows/Linux/macOS

## 🚀 快速开始

### 便携版（推荐 - 双击即用）

直接运行构建好的可执行文件，无需安装 Python 或 Node.js：

```bash
# 构建便携版（首次需要）
./build_portable.sh

# 运行
./dist/校园消费记账系统
```

构建产物在 `dist/` 目录下，约 165MB 的单文件，可复制到任意位置运行。
数据库文件会自动创建在可执行文件同级目录。

### 开发模式

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install

# 设置开发环境变量
export DEV_MODE=1

# 启动应用
python3 app.py
```

### 生产模式

```bash
# 构建前端
cd frontend
npm run build

# 启动应用
python3 app.py
```

## 🛠️ 技术栈

**前端**：
- Vue 3 + TypeScript
- Element Plus (UI组件库)
- ECharts (图表)
- Axios (HTTP客户端)
- Vite (构建工具)

**后端**：
- FastAPI (Web框架)
- SQLite3 (数据库)
- Pydantic (数据验证)

**桌面包装**：
- pywebview (原生窗口)
- PyInstaller (便携版打包)

## 📁 项目结构

```
campus_expense_web/
├── app.py                 # 桌面应用启动器（开发模式）
├── app_portable.py        # 便携版启动器（PyInstaller打包用）
├── portable.spec          # PyInstaller 打包配置
├── build_portable.sh      # 一键构建便携版脚本
├── requirements.txt       # Python依赖
├── backend/
│   ├── main.py           # FastAPI后端
│   ├── requirements.txt
│   └── tests/            # API测试
├── frontend/
│   ├── src/
│   │   ├── components/   # Vue组件
│   │   ├── App.vue       # 主应用
│   │   └── main.ts       # 入口
│   └── package.json
└── dist/                  # 便携版可执行文件（构建产物）
```

## 📝 功能

- ✅ 记账：添加消费记录（金额、分类、描述、日期）
- ✅ 查看记录：表格展示，按月筛选，删除记录
- ✅ 分类统计：饼图可视化，月度分析
- ✅ 预算提醒：设置月预算，进度条显示，三色状态
- ✅ 自定义分类：添加/删除自定义分类
- ✅ 数据导出：导出CSV文件
- ✅ 主题切换：亮色/暗色主题

## 🎯 开发计划

- [ ] 数据备份与恢复
- [ ] 多账户支持
- [ ] 云端同步
- [ ] 移动端适配

## 📄 License

MIT
