import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getUserDataPath: () => ipcRenderer.invoke('get-user-data-path'),
  saveCsv: (content: string, defaultName: string): Promise<string | null> =>
    ipcRenderer.invoke('save-csv', content, defaultName),
  saveJson: (content: string, defaultName: string): Promise<string | null> =>
    ipcRenderer.invoke('save-json', content, defaultName)
})
