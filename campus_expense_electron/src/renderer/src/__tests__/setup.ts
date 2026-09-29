import { config } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

// 与渲染层 main.ts 保持一致：注册组件并使用中文 locale，
// 否则分页/日期选择器等内置文案是英文，断言中文会失败
config.global.plugins = [[ElementPlus, { locale: zhCn }]]

// Element Plus 部分组件在 jsdom 下会访问 matchMedia
if (!window.matchMedia) {
  window.matchMedia = ((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false
  })) as typeof window.matchMedia
}
