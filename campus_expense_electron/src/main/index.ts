import { app, BrowserWindow, Menu } from 'electron'
import { join, dirname } from 'path'
import { spawn, ChildProcess } from 'child_process'
import net from 'net'

let mainWindow: BrowserWindow | null = null
let backendProcess: ChildProcess | null = null

const BACKEND_PORT = 8000
const BACKEND_HOST = '127.0.0.1'

function getBackendCommand(): { cmd: string; args: string[]; cwd?: string } {
  if (app.isPackaged) {
    const exeName = process.platform === 'win32' ? 'backend.exe' : 'backend'
    return {
      cmd: join(process.resourcesPath, 'backend', exeName)
    }
  } else {
    return {
      cmd: 'python3',
      args: ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', String(BACKEND_PORT)],
      cwd: join(__dirname, '../../../campus_expense_web/backend')
    }
  }
}

function getDbPath(): string {
  if (app.isPackaged) {
    const portableDir = process.env['PORTABLE_EXECUTABLE_DIR']
    const base = portableDir ? portableDir : dirname(process.execPath)
    return join(base, 'campus_expenses.db')
  }
  return join(__dirname, '../../resources/backend/campus_expenses.db')
}

function startBackend(): void {
  const { cmd, args, cwd } = getBackendCommand()

  const env = {
    ...process.env,
    DB_PATH: getDbPath(),
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

  backendProcess.stderr?.on('data', (data: Buffer) => {
    console.error(`[Backend] ${data.toString().trim()}`)
  })

  backendProcess.on('error', (err: Error) => {
    console.error('后端启动失败:', err.message)
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

function stopBackend(): void {
  if (backendProcess) {
    console.log('正在停止后端...')
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', String(backendProcess.pid), '/f', '/t'])
    } else {
      backendProcess.kill('SIGTERM')
    }
    backendProcess = null
  }
}

function createWindow(): void {
  Menu.setApplicationMenu(null)

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 650,
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

app.whenReady().then(async () => {
  startBackend()

  try {
    await waitForBackend()
    console.log('后端已就绪，创建窗口...')
  } catch (err) {
    console.error('后端启动失败:', err)
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
