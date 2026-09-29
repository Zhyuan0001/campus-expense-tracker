interface ElectronAPI {
  getAppVersion: () => Promise<string>
  getUserDataPath: () => Promise<string>
}

interface Window {
  electronAPI: ElectronAPI
}
