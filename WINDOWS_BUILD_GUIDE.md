# Windows 构建指南

## 概述

本指南说明如何在 Windows 系统上构建校园消费记账系统的便携版 exe。

**重要**：由于 PyInstaller 不支持跨平台编译，必须在 Windows 上构建 Windows exe。

有两种构建方式：

| 方式 | 适用场景 | 是否需要 Windows 电脑 |
|------|---------|---------------------|
| **GitHub Actions 自动构建**（推荐） | 已推送到 GitHub，推 tag 即自动出包 | 否 |
| **本地手动构建** | 无网络/无 GitHub，或需要反复调试 | 是 |

---

## 方式一：GitHub Actions 自动构建（推荐）

工作流文件：`.github/workflows/build-windows.yml`

```bash
# 1. 推送代码
git push origin master

# 2. 打标签触发构建（标签必须以 v 开头）
git tag v3.0.0
git push origin v3.0.0
```

构建约需 10-15 分钟，完成后可在两处下载：

- **Releases 页面**：`https://github.com/<用户名>/<仓库>/releases`（tag 触发时自动创建，含便携版与安装包）
- **Actions 页面**：`https://github.com/<用户名>/<仓库>/actions` → 选中运行 → 底部 Artifacts

也可以在 Actions 页面点击 "Build Windows Executable" → "Run workflow" 手动触发（不创建 Release，只产出 Artifact）。

> 注意：`resources/backend/`（PyInstaller 产物）未纳入版本管理，由 CI 在 Windows 上重新生成。

---

## 方式二：本地手动构建

## 环境要求

### 必需软件

1. **Python 3.10+**
   - 下载：https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **Node.js 18+ (LTS)**
   - 下载：https://nodejs.org/
   - 推荐使用 LTS 版本

3. **Git**（可选，用于克隆代码）
   - 下载：https://git-scm.com/

---

## 构建步骤

### 步骤 1：准备项目文件

将整个项目文件夹拷贝到 Windows 电脑，或通过 Git 克隆：

```bash
git clone <your-repo-url>
cd SofteareEnjineer
```

### 步骤 2：安装后端依赖

```bash
cd campus_expense_web
pip install -r requirements.txt
pip install pyinstaller
```

**验证安装**：
```bash
pip list | grep -E "(fastapi|uvicorn|pydantic|pyinstaller)"
```

应看到：
- fastapi
- uvicorn
- pydantic
- pyinstaller
- sqlite3（Python 内置）

### 步骤 3：打包后端为 exe

`backend.spec` 位于 `campus_expense_electron/`，且其中引用的源码路径写作
`../campus_expense_web/backend/main.py`——**因此必须在 `campus_expense_electron` 目录下执行**，
在 `campus_expense_web` 下执行会报 "spec 文件不存在" 或找不到源码。

```bash
# 回到项目根目录，进入 Electron 目录
cd ..
cd campus_expense_electron

# 使用 PyInstaller 打包
pyinstaller backend.spec --clean --noconfirm
```

**打包参数说明**：
- `--clean`：清理临时文件
- `--noconfirm`：覆盖已有输出

**打包完成后**，`campus_expense_electron/dist/backend/` 目录包含：
- `backend.exe` - 后端可执行文件
- `_internal/` - 依赖文件

### 步骤 4：复制后端到 Electron 资源目录

```bash
# 仍在 campus_expense_electron 目录执行
# Windows PowerShell
Remove-Item -Recurse -Force resources\backend -ErrorAction SilentlyContinue
Copy-Item -Recurse -Force dist\backend resources\backend

# Windows CMD
if exist resources\backend rmdir /s /q resources\backend
xcopy /E /I /Y dist\backend resources\backend\
```

**验证**：
```bash
dir resources\backend\backend.exe
```

应看到 `backend.exe` 文件。

### 步骤 5：安装前端依赖

```bash
# 仍在 campus_expense_electron 目录执行
npm install
```

**如果 npm install 失败**，尝试：
```bash
# 清除缓存
npm cache clean --force

# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 重新安装
npm install
```

### 步骤 6：构建 Windows 安装包

```bash
# 在 campus_expense_electron 目录执行
npm run build:win
```

**构建过程**：
1. electron-vite 编译前端代码
2. electron-builder 打包 Electron 应用
3. 生成 NSIS 安装包和 Portable 便携版

**构建完成后**，`dist/` 目录包含：
- `校园消费记账 Setup 3.0.0.exe` - NSIS 安装包
- `校园消费记账 3.0.0.exe` - Portable 便携版（单文件）
- `win-unpacked/` - 未打包版本（可直接运行）

---

## 测试便携版

### 测试 1：基本功能

1. 双击 `校园消费记账 3.0.0.exe`
2. 等待应用启动（首次启动可能需要 5-10 秒）
3. 验证功能：
   - 添加消费记录
   - 查看记录列表
   - 查看统计图表
   - 设置预算
   - 切换主题

### 测试 2：数据持久化

1. 添加一条消费记录（如：餐饮 25.5 元）
2. 关闭应用
3. 检查 exe 同目录是否生成 `campus_expenses.db`
4. 重新启动应用
5. 验证之前的记录是否保留

### 测试 3：便携性

1. 将 exe 和 `campus_expenses.db` 拷贝到 U 盘
2. 在另一台 Windows 电脑运行
3. 验证数据是否保留
4. 添加新记录
5. 拷贝回原电脑，验证新记录是否保留

---

## 常见问题

### Q1: npm install 失败，提示 node-gyp 错误

**解决方案**：
```bash
# 安装 Windows 构建工具（需要管理员权限）
npm install --global windows-build-tools

# 或手动安装 Visual Studio Build Tools
# 下载：https://visualstudio.microsoft.com/visual-cpp-build-tools/
# 安装时勾选 "C++ build tools"
```

### Q2: PyInstaller 打包失败

**解决方案**：
```bash
# 升级 PyInstaller
pip install --upgrade pyinstaller

# 确认执行目录正确：backend.spec 在 campus_expense_electron 下
cd campus_expense_electron
dir backend.spec
```

**不要**用 `pyi-makespec` 重新生成 spec：Electron 主进程按
`resources/backend/backend.exe` + `_internal/` 的**目录模式**（onedir）查找后端，
而 makespec 默认生成的 onefile 结构与之不匹配，会导致打包后白屏。
现有 `backend.spec` 已配置好隐藏导入（uvicorn/fastapi/pydantic 等），请直接使用。

### Q3: electron-builder 打包失败，提示 Wine 相关错误

**解决方案**：
- 确保在 Windows 上构建（不需要 Wine）
- 如果仍有问题，尝试使用 `--win portable` 只构建便携版：
```bash
npx electron-builder --win portable
```

### Q4: 应用启动后白屏

**可能原因**：
1. 后端 exe 未正确复制到 resources/backend/
2. 端口 8000 被占用

**解决方案**：
```bash
# 检查端口
netstat -ano | findstr :8000

# 如果端口被占用，杀掉占用进程
taskkill /PID <进程ID> /F

# 检查 backend.exe 是否存在
dir resources\backend\backend.exe
```

### Q5: 数据库文件没有生成在 exe 同目录

**可能原因**：
- 使用了旧版本代码

**解决方案**：
- 确保 `src/main/index.ts` 中的 `getDbPath()` 函数正确：
```typescript
function getDbPath(): string {
  if (app.isPackaged) {
    const portableDir = process.env['PORTABLE_EXECUTABLE_DIR']
    const base = portableDir ? portableDir : dirname(process.execPath)
    return join(base, 'campus_expenses.db')
  }
  return join(__dirname, '../../resources/backend/campus_expenses.db')
}
```

### Q6: 杀毒软件报毒

**原因**：
- PyInstaller 打包的 exe 可能被误报

**解决方案**：
1. 添加信任/白名单
2. 使用代码签名证书（需要购买）
3. 向杀毒软件厂商提交误报

---

## 构建脚本（一键构建）

创建 `build-windows.bat` 文件：

```batch
@echo off
echo ========================================
echo 校园消费记账系统 - Windows 构建脚本
echo ========================================
echo.

echo [1/5] 安装后端依赖...
cd campus_expense_web
call pip install -r requirements.txt
call pip install pyinstaller
if errorlevel 1 (
    echo 错误：后端依赖安装失败
    pause
    exit /b 1
)

echo.
echo [2/5] 打包后端为 exe...
rem backend.spec 在 campus_expense_electron 下，且其内部路径相对于该目录
cd ..\campus_expense_electron
call pyinstaller backend.spec --clean --noconfirm
if errorlevel 1 (
    echo 错误：后端打包失败
    pause
    exit /b 1
)

echo.
echo [3/5] 复制后端到 Electron 资源目录...
if exist resources\backend rmdir /s /q resources\backend
xcopy /E /I /Y dist\backend resources\backend\
if errorlevel 1 (
    echo 错误：复制后端文件失败
    pause
    exit /b 1
)

echo.
echo [4/5] 安装前端依赖...
call npm install
if errorlevel 1 (
    echo 错误：前端依赖安装失败
    pause
    exit /b 1
)

echo.
echo [5/5] 构建 Windows 安装包...
call npm run build:win
if errorlevel 1 (
    echo 错误：构建失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 构建完成！
echo 安装包位置：dist\校园消费记账 Setup 3.0.0.exe
echo 便携版位置：dist\校园消费记账 3.0.0.exe
echo ========================================
pause
```

**使用方法**：
```bash
# 在项目根目录双击运行
build-windows.bat
```

---

## 构建输出说明

### NSIS 安装包（推荐分发）

**文件**：`校园消费记账 Setup 3.0.0.exe`

**特点**：
- 标准 Windows 安装向导
- 用户可选择安装目录
- 创建桌面快捷方式
- 创建开始菜单项
- 支持卸载

**适用场景**：
- 正式分发
- 长期使用

### Portable 便携版（推荐测试）

**文件**：`校园消费记账 3.0.0.exe`

**特点**：
- 单文件，无需安装
- 双击即可运行
- 数据库在 exe 同目录创建
- 可放入 U 盘随身携带

**适用场景**：
- 演示测试
- 便携使用
- 不想安装软件的用户

### win-unpacked 未打包版

**目录**：`win-unpacked/`

**特点**：
- 已解压的应用文件
- 直接运行 `win-unpacked/校园消费记账.exe`
- 体积较大（包含所有文件）

**适用场景**：
- 开发调试
- 快速测试（无需重新打包）

---

## 性能优化建议

### 减小打包体积

1. **排除不必要的文件**

编辑 `package.json` 的 `build.files` 字段：
```json
"build": {
  "files": [
    "**/*",
    "!node_modules/**/*.{md,ts,tsx,js.map}",
    "!node_modules/.cache/**/*"
  ]
}
```

2. **使用 UPX 压缩 exe**

安装 UPX：https://upx.github.io/

在 `package.json` 中添加：
```json
"build": {
  "win": {
    "target": ["portable"],
    "executableName": "campus-expense"
  },
  "nsis": {
    "oneClick": false
  }
}
```

PyInstaller 的 `backend.spec` 中启用 UPX：
```python
a = Analysis(...
    upx=True,
    upx_exclude=[],
)
```

### 加快构建速度

1. **使用缓存**
```bash
# electron-builder 缓存
set ELECTRON_BUILDER_CACHE=%USERPROFILE%\.cache\electron-builder

# npm 缓存
npm config set cache %USERPROFILE%\.npm-cache
```

2. **增量构建**
```bash
# 只重新打包，不重新编译前端
npx electron-builder --win portable --prepackaged win-unpacked
```

---

## 发布建议

### 内部测试

1. 使用 Portable 便携版
2. 通过网盘/邮件分发
3. 收集反馈

### 正式发布

1. 使用 NSIS 安装包
2. 添加代码签名（可选，避免杀毒软件报毒）
3. 上传到 GitHub Releases / 官网
4. 提供安装说明文档

---

## 检查清单

构建前确认：

- [ ] Python 3.10+ 已安装
- [ ] Node.js 18+ 已安装
- [ ] 后端依赖已安装（`pip install -r requirements.txt`）
- [ ] 前端依赖已安装（`npm install`）
- [ ] `backend.spec` 文件存在
- [ ] 磁盘空间充足（至少 2GB）

构建后验证：

- [ ] `dist/` 目录生成了 exe 文件
- [ ] 便携版可以双击运行
- [ ] 应用启动正常，无白屏
- [ ] 数据库文件在 exe 同目录创建
- [ ] 所有功能正常工作
- [ ] 数据持久化正常

---

## 技术支持

如遇到问题：

1. 查看本文档"常见问题"部分
2. 检查 `iteration_log.md` 中的已知问题
3. 联系开发团队

---

**文档版本**：v1.0  
**最后更新**：2026-09-29  
**适用版本**：校园消费记账系统 v3.0
