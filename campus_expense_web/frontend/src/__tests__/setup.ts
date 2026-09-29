import { config } from '@vue/test-utils'
import { beforeAll } from 'vitest'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

beforeAll(() => {
  config.global.plugins = [ElementPlus]
})
