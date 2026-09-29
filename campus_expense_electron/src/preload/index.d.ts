interface ElectronAPI {
  getAppVersion: () => Promise<string>
  getUserDataPath: () => Promise<string>
  saveCsv: (content: string, defaultName: string) => Promise<string | null>
}

interface Window {
  // 仅 Electron 环境由 preload 注入；浏览器/单元测试环境下为 undefined
  electronAPI?: ElectronAPI
}
