import { resolve } from 'path'
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve('src/renderer/src')
    }
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['src/renderer/src/__tests__/setup.ts'],
    include: ['src/renderer/src/**/*.test.ts'],
    server: {
      deps: {
        // element-plus 必须内联走 Vite 管线（与真实渲染层打包行为一致）：
        // 若被 externalize 而经 Node 原生 ESM→CJS 互操作加载，
        // 其内部 `import AsyncValidator from 'async-validator'` 拿到的是
        // { default: Schema } 包装对象（async-validator CJS 构建无 __esModule 标记），
        // `new AsyncValidator(...)` 抛 TypeError 且被 element-plus 静默吞掉，
        // 导致 el-form.validate() 恒为 true、必填校验在测试环境中完全失效
        inline: ['element-plus']
      }
    }
  }
})
