import { app, BrowserWindow, Menu, dialog, ipcMain } from 'electron'
import { join, dirname } from 'path'
import { spawn, spawnSync, ChildProcess } from 'child_process'
import { accessSync, constants } from 'fs'
import { writeFile } from 'fs/promises'

let mainWindow: BrowserWindow | null = null
let backendProcess: ChildProcess | null = null
let backendExitCode: number | null = null

const BACKEND_PORT = 8000
const BACKEND_HOST = '127.0.0.1'

// portable 目标每次启动都会解压到同一个 $TEMP 目录，双击两次会互删文件；
// 装到 Program Files 时数据目录不可写。单实例锁只能解决前者的一半，
// 因此 getDbPath 还需要可写探测，失败时也要给出可见的错误提示。
if (!app.requestSingleInstanceLock()) {
  app.quit()
  process.exit(0)
}

function getBackendCommand(): { cmd: string; args: string[]; cwd?: string } {
  if (app.isPackaged) {
    const exeName = process.platform === 'win32' ? 'backend.exe' : 'backend'
    return {
      cmd: join(process.resourcesPath, 'backend', exeName),
      args: []
    }
  } else {
    return {
      cmd: 'python3',
      args: ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', String(BACKEND_PORT)],
      cwd: join(__dirname, '../../../campus_expense_web/backend')
    }
  }
}

function isWritable(dir: string): boolean {
  try {
    accessSync(dir, constants.W_OK)
    return true
  } catch {
    return false
  }
}

function getDbPath(): string {
  if (!app.isPackaged) {
    return join(__dirname, '../../resources/backend/campus_expenses.db')
  }

  // 便携版必须优先落在 exe 同目录，这是"数据库随应用走"的前提；
  // 装到 Program Files 或写保护 U 盘时该目录不可写，逐级回退到用户数据目录，
  // 否则后端会在 import 阶段就因无法建库而崩溃
  const candidates = [process.env['PORTABLE_EXECUTABLE_DIR'], dirname(process.execPath)]
  for (const dir of candidates) {
    if (dir && isWritable(dir)) {
      return join(dir, 'campus_expenses.db')
    }
  }
  return join(app.getPath('userData'), 'campus_expenses.db')
}

function startBackend(): void {
  const { cmd, args, cwd } = getBackendCommand()
  const dbPath = getDbPath()

  const env = {
    ...process.env,
    DB_PATH: dbPath,
    PORT: String(BACKEND_PORT),
    // 后端的错误信息含中文，Windows 下 stdout 被重定向为管道时 Python 会用本地
    // 代码页编码，遇到中文可能抛 UnicodeEncodeError 导致二次崩溃
    PYTHONUTF8: '1',
    PYTHONIOENCODING: 'utf-8'
  }

  console.log(`数据库路径: ${dbPath}`)

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

  backendProcess.stderr?.on('data', (data: Buffer) => {
    console.error(`[Backend] ${data.toString().trim()}`)
  })

  backendProcess.on('error', (err: Error) => {
    console.error('后端启动失败:', err.message)
    dialog.showErrorBox(
      '后端无法启动',
      `未能启动内置的后端服务：${err.message}\n\n` +
        '这通常是杀毒软件隔离了 resources\\backend\\backend.exe 导致的，请将其加入白名单后重试。'
    )
  })

  backendProcess.on('exit', (code: number | null) => {
    console.log(`后端进程退出，退出码: ${code}`)
    backendExitCode = code
    backendProcess = null
  })
}

function waitForBackend(maxRetries = 120, interval = 500): Promise<void> {
  return new Promise((resolve, reject) => {
    let retries = 0

    // 必须校验业务健康检查接口而不是只探测端口：端口被其它服务占用时
    // TCP 能连通，窗口会照常打开，但所有请求都打到错误的服务上，表现为白屏
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
          const exitHint =
            backendExitCode !== null ? `\n\n后端进程已退出，退出码 ${backendExitCode}。` : ''
          reject(
            new Error(
              `后端在 ${Math.round((maxRetries * interval) / 1000)} 秒内未就绪。${exitHint}` +
                `\n\n请检查 ${BACKEND_PORT} 端口是否被其它程序占用。`
            )
          )
        } else {
          setTimeout(check, interval)
        }
      }
    }

    check()
  })
}

function stopBackend(): void {
  if (!backendProcess) return

  console.log('正在停止后端...')
  const proc = backendProcess
  backendProcess = null

  if (process.platform === 'win32') {
    if (proc.pid === undefined) return
    // 必须同步执行：before-quit 里异步 spawn 的 taskkill 往往来不及运行主进程就退出了，
    // 残留的 backend.exe 会一直占着 8000 端口，导致下次启动健康检查打到旧进程上
    spawnSync('taskkill', ['/pid', String(proc.pid), '/f', '/t'], { windowsHide: true })
  } else {
    proc.kill('SIGTERM')
  }
}

function createWindow(): void {
  Menu.setApplicationMenu(null)

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    // 放宽最小尺寸：原先 900x650 直接把窄窗/竖窗挡死，响应式布局无从谈起
    minWidth: 400,
    minHeight: 480,
    title: '校园消费记账系统 v3.0',
    show: false,
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false
    }
  })

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show()
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  if (process.env.ELECTRON_RENDERER_URL) {
    mainWindow.loadURL(process.env.ELECTRON_RENDERER_URL)
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

function registerIpcHandlers(): void {
  ipcMain.handle('get-app-version', () => app.getVersion())
  ipcMain.handle('get-user-data-path', () => app.getPath('userData'))

  ipcMain.handle(
    'save-csv',
    async (_event, content: string, defaultName: string): Promise<string | null> => {
      const { canceled, filePath } = await dialog.showSaveDialog({
        title: '导出消费记录',
        defaultPath: defaultName,
        filters: [{ name: 'CSV 文件', extensions: ['csv'] }]
      })
      if (canceled || !filePath) return null

      // Blob.text() 按规范会剥掉 UTF-8 BOM，而 Excel 需要 BOM 才能正确识别中文，
      // 因此这里统一去掉再补回，避免出现双 BOM
      await writeFile(filePath, `\uFEFF${content.replace(/^\uFEFF/, '')}`, 'utf-8')
      return filePath
    }
  )

  ipcMain.handle(
    'save-json',
    async (_event, content: string, defaultName: string): Promise<string | null> => {
      const { canceled, filePath } = await dialog.showSaveDialog({
        title: '\u5BFC\u51FA\u5907\u4EFD',
        defaultPath: defaultName,
        filters: [{ name: 'JSON \u5907\u4EFD', extensions: ['json'] }]
      })
      if (canceled || !filePath) return null

      // JSON \u5907\u4EFD\u4E0D\u80FD\u52A0 BOM\uFF0C\u5426\u5219 JSON.parse \u4F1A\u5931\u8D25
      await writeFile(filePath, content, 'utf-8')
      return filePath
    }
  )
}

app.on('second-instance', () => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore()
    mainWindow.focus()
  }
})

app.whenReady().then(async () => {
  registerIpcHandlers()
  startBackend()

  try {
    await waitForBackend()
    console.log('后端已就绪，创建窗口...')
  } catch (err) {
    console.error('后端启动失败:', err)
    dialog.showErrorBox('后端启动失败', (err as Error).message)
    stopBackend()
    app.quit()
    return
  }

  createWindow()
})

app.on('window-all-closed', () => {
  stopBackend()
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  stopBackend()
})

process.on('exit', () => {
  stopBackend()
})

process.on('SIGINT', () => {
  stopBackend()
  app.quit()
})

process.on('SIGTERM', () => {
  stopBackend()
  app.quit()
})
