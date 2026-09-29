// 测试环境 DOM 补丁：jsdom 未实现 ResizeObserver，
// Element Plus 的 el-table / el-select 等组件挂载时需要它
export function installDomStubs(): void {
  if (typeof globalThis.ResizeObserver === 'undefined') {
    globalThis.ResizeObserver = class {
      observe(): void {}
      unobserve(): void {}
      disconnect(): void {}
    } as unknown as typeof ResizeObserver
  }
}

// ElMessage 会把提示节点真实挂到 document.body，
// 每个用例结束后清空 body，避免跨用例的文案断言互相污染
export function cleanupBody(): void {
  document.body.innerHTML = ''
}
