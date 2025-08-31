/**
 * SecureInput组件测试
 * 测试安全输入组件的验证和清理功能
 */
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElInput } from 'element-plus'
import SecureInput from '@/components/common/SecureInput.vue'

describe('SecureInput Component', () => {
  it('应该渲染基本输入框', () => {
    const wrapper = mount(SecureInput, {
      props: {
        modelValue: 'test value',
        placeholder: '请输入内容'
      },
      global: {
        components: {
          ElInput
        }
      }
    })
    
    expect(wrapper.find('.secure-input').exists()).toBe(true)
    expect(wrapper.findComponent(ElInput).exists()).toBe(true)
  })
  
  it('应该检测和清理XSS攻击', async () => {
    const wrapper = mount(SecureInput, {
      props: {
        modelValue: '',
        securityRule: {
          enableXSSDetection: true
        }
      },
      global: {
        components: {
          ElInput
        }
      }
    })
    
    // 模拟用户输入XSS载荷
    const xssPayload = '<script>alert("xss")</script>'
    const input = wrapper.findComponent(ElInput)
    
    await input.vm.$emit('input', xssPayload)
    
    // 应该发出XSS检测事件
    expect(wrapper.emitted('xss-detected')).toBeTruthy()
    expect(wrapper.emitted('xss-detected')?.[0]).toEqual([xssPayload, expect.any(String)])
    
    // 应该显示XSS警告
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.xss-warning').exists()).toBe(true)
  })
  
  it('应该限制输入长度', async () => {
    const maxLength = 10
    const wrapper = mount(SecureInput, {
      props: {
        modelValue: '',
        securityRule: {
          maxLength
        }
      },
      global: {
        components: {
          ElInput
        }
      }
    })
    
    // 输入超长文本
    const longText = 'A'.repeat(20)
    const input = wrapper.findComponent(ElInput)
    
    await input.vm.$emit('input', longText)
    
    // 应该发出长度超限事件
    expect(wrapper.emitted('length-exceeded')).toBeTruthy()
    
    // 应该显示长度警告（当接近限制时）
    const nearLimitText = 'A'.repeat(9)  // 90%的长度
    await input.vm.$emit('input', nearLimitText)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.find('.length-warning').exists()).toBe(true)
  })
  
  it('应该执行自定义验证', async () => {
    const customValidator = vi.fn().mockReturnValue('自定义错误')
    
    const wrapper = mount(SecureInput, {
      props: {
        modelValue: '',
        securityRule: {
          validator: customValidator
        }
      },
      global: {
        components: {
          ElInput
        }
      }
    })
    
    const input = wrapper.findComponent(ElInput)
    await input.vm.$emit('input', 'test')
    
    // 应该调用自定义验证器
    expect(customValidator).toHaveBeenCalledWith('test')
    
    // 应该发出验证错误事件
    expect(wrapper.emitted('validation-error')).toBeTruthy()
    
    // 应该显示错误消息
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.error-message').exists()).toBe(true)
  })
  
  it('应该支持不同的输入类型', () => {
    const types = ['text', 'textarea', 'password', 'email', 'url']
    
    types.forEach(type => {
      const wrapper = mount(SecureInput, {
        props: {
          modelValue: '',
          type: type as any
        },
        global: {
          components: {
            ElInput
          }
        }
      })
      
      expect(wrapper.findComponent(ElInput).exists()).toBe(true)
    })
  })
  
  it('应该正确处理v-model', async () => {
    const wrapper = mount(SecureInput, {
      props: {
        modelValue: 'initial value'
      },
      global: {
        components: {
          ElInput
        }
      }
    })
    
    // 检查初始值
    expect(wrapper.findComponent(ElInput).props('modelValue')).toBe('initial value')
    
    // 模拟输入变化
    const input = wrapper.findComponent(ElInput)
    await input.vm.$emit('input', 'new value')
    
    // 应该发出update:modelValue事件
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['new value'])
  })
  
  it('应该在失焦时进行最终验证', async () => {
    const wrapper = mount(SecureInput, {
      props: {
        modelValue: 'initial',
        securityRule: {
          enableXSSDetection: true
        }
      },
      global: {
        components: {
          ElInput
        }
      }
    })
    
    // 模拟失焦事件
    const input = wrapper.findComponent(ElInput)
    await input.vm.$emit('blur', new FocusEvent('blur'))
    
    // 应该发出blur事件
    expect(wrapper.emitted('blur')).toBeTruthy()
  })
  
  it('应该显示自定义错误消息', async () => {
    const customError = '自定义错误消息'
    
    const wrapper = mount(SecureInput, {
      props: {
        modelValue: '',
        customError
      },
      global: {
        components: {
          ElInput
        }
      }
    })
    
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.error-message').text()).toContain(customError)
  })
  
  it('应该根据输入类型设置默认长度限制', () => {
    const testCases = [
      { type: 'email', expectedMax: 254 },
      { type: 'url', expectedMax: 2048 },
      { type: 'textarea', expectedMax: 5000 },
      { type: 'text', expectedMax: 100 }
    ]
    
    testCases.forEach(({ type, expectedMax }) => {
      const wrapper = mount(SecureInput, {
        props: {
          modelValue: '',
          type: type as any
        },
        global: {
          components: {
            ElInput
          }
        }
      })
      
      expect(wrapper.findComponent(ElInput).props('maxlength')).toBe(expectedMax)
    })
  })
  
  it('应该支持禁用XSS检测', async () => {
    const wrapper = mount(SecureInput, {
      props: {
        modelValue: '',
        securityRule: {
          enableXSSDetection: false
        }
      },
      global: {
        components: {
          ElInput
        }
      }
    })
    
    // 输入XSS载荷
    const input = wrapper.findComponent(ElInput)
    await input.vm.$emit('input', '<script>alert("xss")</script>')
    
    // 不应该发出XSS检测事件
    expect(wrapper.emitted('xss-detected')).toBeFalsy()
    
    // 不应该显示XSS警告
    expect(wrapper.find('.xss-warning').exists()).toBe(false)
  })
  
  it('应该支持允许HTML模式', async () => {
    const htmlContent = '<b>加粗文本</b>'
    
    const wrapper = mount(SecureInput, {
      props: {
        modelValue: '',
        securityRule: {
          allowHTML: true
        }
      },
      global: {
        components: {
          ElInput
        }
      }
    })
    
    const input = wrapper.findComponent(ElInput)
    await input.vm.$emit('input', htmlContent)
    
    // 在允许HTML模式下，应该保留HTML标签
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([htmlContent])
  })
  
  it('应该正确计算长度使用百分比', () => {
    const wrapper = mount(SecureInput, {
      props: {
        modelValue: 'AAAAA',  // 5个字符
        securityRule: {
          maxLength: 10
        }
      },
      global: {
        components: {
          ElInput
        }
      }
    })
    
    // 5/10 = 50%
    expect(wrapper.vm.lengthUsagePercent).toBe(50)
  })
  
  it('应该支持所有Element Plus输入框属性', () => {
    const wrapper = mount(SecureInput, {
      props: {
        modelValue: 'test',
        placeholder: '测试占位符',
        disabled: true,
        readonly: true,
        clearable: true,
        size: 'large',
        showPassword: true,
        showWordLimit: true
      },
      global: {
        components: {
          ElInput
        }
      }
    })
    
    const input = wrapper.findComponent(ElInput)
    expect(input.props('placeholder')).toBe('测试占位符')
    expect(input.props('disabled')).toBe(true)
    expect(input.props('readonly')).toBe(true)
    expect(input.props('clearable')).toBe(true)
    expect(input.props('size')).toBe('large')
    expect(input.props('showPassword')).toBe(true)
    expect(input.props('showWordLimit')).toBe(true)
  })
})
