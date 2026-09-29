import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import RecordsTab from '../components/RecordsTab.vue'

describe('RecordsTab', () => {
  it('renders component correctly', () => {
    const wrapper = mount(RecordsTab)
    expect(wrapper.exists()).toBe(true)
  })

  it('is a Vue component', () => {
    const wrapper = mount(RecordsTab)
    expect(wrapper.vm).toBeDefined()
  })
})
