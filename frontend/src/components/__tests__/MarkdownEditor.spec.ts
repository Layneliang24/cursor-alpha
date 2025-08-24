import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import MarkdownEditor from '../MarkdownEditor.vue'

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  }
}))

describe('MarkdownEditor.vue Component', () => {
  let wrapper: any

  const defaultProps = {
    modelValue: '# 测试标题\n这是测试内容'
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('正确渲染Markdown编辑器组件容器', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.find('.markdown-editor').exists()).toBe(true)
      expect(wrapper.find('.editor-container').exists()).toBe(true)
    })

    it('使用默认属性正确渲染', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.find('.markdown-editor').exists()).toBe(true)
      expect(wrapper.find('.editor-container').exists()).toBe(true)
    })

    it('正确应用传入的属性', () => {
      wrapper = mount(MarkdownEditor, {
        props: defaultProps,
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.props().modelValue).toBe(defaultProps.modelValue)
    })
  })

  describe('属性验证', () => {
    it('modelValue属性有正确的默认值', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.props().modelValue).toBe('')
    })

    it('placeholder文本正确显示', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      const textarea = wrapper.find('.markdown-input')
      const placeholder = textarea.attributes('placeholder')
      expect(placeholder).toContain('请输入Markdown内容')
    })

    it('组件正确挂载', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.markdown-editor').exists()).toBe(true)
    })
  })

  describe('组件生命周期', () => {
    it('组件正确挂载和卸载', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.markdown-editor').exists()).toBe(true)
      
      wrapper.unmount()
      expect(wrapper.vm).toBeDefined()
    })

    it('重复挂载组件不会出错', () => {
      for (let i = 0; i < 3; i++) {
        wrapper = mount(MarkdownEditor, {
          global: {
            stubs: {
              'el-button': {
                template: '<button class="el-button"><slot /></button>',
                props: ['size', 'title', 'type'],
                emits: ['click']
              }
            }
          }
        })
        expect(wrapper.exists()).toBe(true)
        wrapper.unmount()
      }
    })
  })

  describe('编辑器功能', () => {
    it('渲染编辑器标题', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.text()).toContain('编辑器')
    })

    it('渲染预览标题', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.text()).toContain('预览')
    })

    it('渲染文本输入框', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      const textarea = wrapper.find('.markdown-input')
      expect(textarea.exists()).toBe(true)
    })

    it('渲染预览区域', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      const preview = wrapper.find('.markdown-preview')
      expect(preview.exists()).toBe(true)
    })

    it('渲染工具栏', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      const tools = wrapper.find('.editor-tools')
      expect(tools.exists()).toBe(true)
    })

    it('显示主要工具按钮', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      const buttons = wrapper.findAll('.editor-tools .el-button')
      expect(buttons.length).toBeGreaterThan(0)
    })
  })

  describe('输入功能', () => {
    it('支持v-model双向绑定', async () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      const textarea = wrapper.find('.markdown-input')
      const testContent = '# 测试标题\n这是测试内容'
      
      await textarea.setValue(testContent)
      await nextTick()
      
      expect(wrapper.vm.content).toBe(testContent)
    })

    it('输入框有正确的占位符文本', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      const textarea = wrapper.find('.markdown-input')
      const placeholder = textarea.attributes('placeholder')
      
      expect(placeholder).toContain('请输入Markdown内容')
    })

    it('处理输入事件', async () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      const textarea = wrapper.find('.markdown-input')
      const testContent = 'New content'
      
      await textarea.setValue(testContent)
      await nextTick()
      
      expect(wrapper.vm.content).toBe(testContent)
    })

    it('正确接收modelValue prop', () => {
      const testValue = '# Initial content'
      wrapper = mount(MarkdownEditor, {
        props: {
          modelValue: testValue
        },
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.vm.content).toBe(testValue)
    })
  })

  describe('边界情况', () => {
    it('空内容时正确处理', () => {
      wrapper = mount(MarkdownEditor, {
        props: { modelValue: '' },
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.props().modelValue).toBe('')
      expect(wrapper.vm.content).toBe('')
    })

    it('null内容时正确处理', () => {
      wrapper = mount(MarkdownEditor, {
        props: { modelValue: null },
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.props().modelValue).toBe(null)
    })

    it('undefined内容时正确处理', () => {
      wrapper = mount(MarkdownEditor, {
        props: { modelValue: undefined },
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      // Vue会将undefined处理为空字符串，这是正常行为
      expect(wrapper.vm.content).toBe('')
    })

    it('长内容时正确处理', () => {
      const longContent = '# 长标题\n'.repeat(1000)
      wrapper = mount(MarkdownEditor, {
        props: { modelValue: longContent },
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.props().modelValue).toBe(longContent)
      expect(wrapper.vm.content).toBe(longContent)
    })
  })

  describe('CSS样式', () => {
    it('组件有正确的CSS类', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.classes()).toContain('markdown-editor')
      expect(wrapper.find('.editor-container').classes()).toContain('editor-container')
    })

    it('编辑器容器有正确的样式属性', () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      const editorContainer = wrapper.find('.editor-container')
      expect(editorContainer.exists()).toBe(true)
    })
  })

  describe('组件稳定性', () => {
    it('频繁内容变化时组件保持稳定', async () => {
      wrapper = mount(MarkdownEditor, {
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      // 快速连续变化内容
      for (let i = 0; i < 10; i++) {
        const testContent = `Content ${i}`
        await wrapper.setProps({ modelValue: testContent })
        await nextTick()
        
        expect(wrapper.exists()).toBe(true)
        expect(wrapper.vm.content).toBe(testContent)
      }
    })

    it('极端内容值时组件保持稳定', () => {
      const extremeContent = '!@#$%^&*()_+-=[]{}|;:,.<>?'
      wrapper = mount(MarkdownEditor, {
        props: { modelValue: extremeContent },
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.props().modelValue).toBe(extremeContent)
    })
  })

  describe('响应式属性变化', () => {
    it('modelValue变化时正确更新', async () => {
      wrapper = mount(MarkdownEditor, {
        props: { modelValue: '原始内容' },
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.props().modelValue).toBe('原始内容')
      
      await wrapper.setProps({ modelValue: '新内容' })
      await nextTick()
      
      expect(wrapper.props().modelValue).toBe('新内容')
      expect(wrapper.vm.content).toBe('新内容')
    })

    it('内容变化时正确更新', async () => {
      wrapper = mount(MarkdownEditor, {
        props: { modelValue: '原始内容' },
        global: {
          stubs: {
            'el-button': {
              template: '<button class="el-button"><slot /></button>',
              props: ['size', 'title', 'type'],
              emits: ['click']
            }
          }
        }
      })
      
      expect(wrapper.props().modelValue).toBe('原始内容')
      
      await wrapper.setProps({ modelValue: '新内容' })
      await nextTick()
      
      expect(wrapper.props().modelValue).toBe('新内容')
      expect(wrapper.vm.content).toBe('新内容')
    })
  })
}) 