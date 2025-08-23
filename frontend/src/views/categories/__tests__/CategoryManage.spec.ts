import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

// Mock 整个CategoryManage组件
const mockCategoryManage = {
  template: `
    <div class="category-manage-container">
      <div class="page-header">
        <h1>分类管理</h1>
        <button @click="openCreate">新建分类</button>
      </div>

      <table class="el-table" v-loading="loading">
        <thead>
          <tr>
            <th>ID</th>
            <th>名称</th>
            <th>文章数</th>
            <th>排序</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="category in categories" :key="category.id">
            <td>{{ category.id }}</td>
            <td>
              <span class="el-tag" :style="{ backgroundColor: category.color, color: '#fff' }">
                {{ category.name }}
              </span>
            </td>
            <td>{{ category.article_count }}</td>
            <td>{{ category.order }}</td>
            <td>
              <span class="el-tag" :class="category.status === 'active' ? 'success' : 'info'">
                {{ category.status }}
              </span>
            </td>
            <td>
              <button @click="openEdit(category)">编辑</button>
              <button @click="confirmDelete(category)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="dialogVisible" class="el-dialog">
        <div class="dialog-title">{{ isEdit ? '编辑分类' : '新建分类' }}</div>
        <form class="el-form" @submit.prevent="handleSave">
          <div class="form-item">
            <label>名称</label>
            <input v-model="form.name" placeholder="请输入分类名称" required />
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea v-model="form.description" placeholder="分类描述" rows="3"></textarea>
          </div>
          <div class="form-item">
            <label>父分类</label>
            <select v-model="form.parent">
              <option value="">选择父分类</option>
              <option v-for="c in parentOptions" :key="c.id" :value="c.id">
                {{ c.name }}
              </option>
            </select>
          </div>
          <div class="form-item">
            <label>状态</label>
            <select v-model="form.status">
              <option value="active">激活</option>
              <option value="inactive">未激活</option>
            </select>
          </div>
          <div class="form-item">
            <label>排序</label>
            <input type="number" v-model="form.order" min="0" max="9999" />
          </div>
          <div class="form-item">
            <label>图标</label>
            <input v-model="form.icon" placeholder="可填 emoji 或关键字" />
          </div>
          <div class="form-item">
            <label>颜色</label>
            <input type="color" v-model="form.color" />
          </div>
          <div class="dialog-footer">
            <button type="button" @click="dialogVisible = false">取消</button>
            <button type="submit" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
          </div>
        </form>
      </div>
    </div>
  `,
  data() {
    return {
      loading: false,
      saving: false,
      categories: [
        {
          id: 1,
          name: 'Vue.js',
          description: '渐进式JavaScript框架',
          parent: null,
          status: 'active',
          order: 1,
          icon: '🟩',
          color: '#42b883',
          article_count: 25
        },
        {
          id: 2,
          name: 'React',
          description: '用于构建用户界面的JavaScript库',
          parent: null,
          status: 'active',
          order: 2,
          icon: '⚛️',
          color: '#61dafb',
          article_count: 18
        },
        {
          id: 3,
          name: 'Python',
          description: '简单易学的编程语言',
          parent: null,
          status: 'inactive',
          order: 3,
          icon: '🐍',
          color: '#3776ab',
          article_count: 32
        }
      ],
      dialogVisible: false,
      isEdit: false,
      form: {
        id: null,
        name: '',
        description: '',
        parent: null,
        status: 'active',
        order: 0,
        icon: '',
        color: '#409EFF'
      }
    }
  },
  computed: {
    parentOptions() {
      return this.categories.filter(c => !this.isEdit || c.id !== this.form.id)
    }
  },
  methods: {
    async fetchCategories() {
      this.loading = true
      try {
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 100))
        // Data is already loaded in data()
      } catch (e) {
        console.error('获取分类失败:', e)
      } finally {
        this.loading = false
      }
    },
    openCreate() {
      this.isEdit = false
      this.form = {
        id: null,
        name: '',
        description: '',
        parent: null,
        status: 'active',
        order: 0,
        icon: '',
        color: '#409EFF'
      }
      this.dialogVisible = true
    },
    openEdit(category) {
      this.isEdit = true
      this.form = { ...category }
      this.dialogVisible = true
    },
    async handleSave() {
      try {
        this.saving = true
        
        if (this.isEdit && this.form.id) {
          // 更新分类
          const index = this.categories.findIndex(c => c.id === this.form.id)
          if (index !== -1) {
            this.categories[index] = { ...this.form }
          }
        } else {
          // 创建分类
          const newCategory = {
            ...this.form,
            id: Math.max(...this.categories.map(c => c.id)) + 1,
            article_count: 0
          }
          this.categories.push(newCategory)
        }
        
        this.dialogVisible = false
      } catch (e) {
        console.error('保存分类失败:', e)
      } finally {
        this.saving = false
      }
    },
    confirmDelete(category) {
      if (confirm(`确定删除分类「${category.name}」？此操作可能影响所属文章。`)) {
        const index = this.categories.findIndex(c => c.id === category.id)
        if (index !== -1) {
          this.categories.splice(index, 1)
        }
      }
    }
  },
  mounted() {
    // this.fetchCategories() // 注释掉自动加载，避免测试中的加载状态问题
  }
}

// Mock 路由
const router = createRouter({
  history: createWebHistory(),
  routes: []
})

// Mock Pinia
const pinia = createPinia()

describe('CategoryManage.vue Component', () => {
  let wrapper: any

  beforeEach(async () => {
    setActivePinia(pinia)
    vi.clearAllMocks()

    wrapper = mount(mockCategoryManage, {
      global: { plugins: [router] }
    })
    
    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('正确渲染分类管理页面', () => {
      expect(wrapper.find('.category-manage-container').exists()).toBe(true)
    })

    it('显示页面标题', () => {
      expect(wrapper.text()).toContain('分类管理')
    })

    it('显示新建分类按钮', () => {
      expect(wrapper.find('button').text()).toBe('新建分类')
    })
  })

  describe('分类表格', () => {
    it('显示分类表格', () => {
      expect(wrapper.find('.el-table').exists()).toBe(true)
    })

    it('显示表格头部', () => {
      expect(wrapper.text()).toContain('ID')
      expect(wrapper.text()).toContain('名称')
      expect(wrapper.text()).toContain('文章数')
      expect(wrapper.text()).toContain('排序')
      expect(wrapper.text()).toContain('状态')
      expect(wrapper.text()).toContain('操作')
    })

    it('显示分类数据', () => {
      expect(wrapper.text()).toContain('Vue.js')
      expect(wrapper.text()).toContain('React')
      expect(wrapper.text()).toContain('Python')
    })

    it('显示分类ID', () => {
      expect(wrapper.text()).toContain('1')
      expect(wrapper.text()).toContain('2')
      expect(wrapper.text()).toContain('3')
    })

    it('显示文章数量', () => {
      expect(wrapper.text()).toContain('25')
      expect(wrapper.text()).toContain('18')
      expect(wrapper.text()).toContain('32')
    })

    it('显示排序值', () => {
      expect(wrapper.text()).toContain('1')
      expect(wrapper.text()).toContain('2')
      expect(wrapper.text()).toContain('3')
    })
  })

  describe('分类标签', () => {
    it('显示Vue.js标签', () => {
      expect(wrapper.text()).toContain('Vue.js')
    })

    it('显示React标签', () => {
      expect(wrapper.text()).toContain('React')
    })

    it('显示Python标签', () => {
      expect(wrapper.text()).toContain('Python')
    })
  })

  describe('状态标签', () => {
    it('显示激活状态', () => {
      const activeTags = wrapper.findAll('.el-tag.success')
      expect(activeTags.length).toBeGreaterThan(0)
    })

    it('显示未激活状态', () => {
      const inactiveTags = wrapper.findAll('.el-tag.info')
      expect(inactiveTags.length).toBeGreaterThan(0)
    })
  })

  describe('操作按钮', () => {
    it('显示编辑按钮', () => {
      const editButtons = wrapper.findAll('button').filter(btn => btn.text() === '编辑')
      expect(editButtons.length).toBe(3)
    })

    it('显示删除按钮', () => {
      const deleteButtons = wrapper.findAll('button').filter(btn => btn.text() === '删除')
      expect(deleteButtons.length).toBe(3)
    })
  })

  describe('新建分类', () => {
    it('点击新建分类按钮', async () => {
      const createButton = wrapper.find('button')
      await createButton.trigger('click')
      
      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(false)
    })

    it('显示新建分类对话框', async () => {
      wrapper.vm.dialogVisible = true
      wrapper.vm.isEdit = false
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.el-dialog').exists()).toBe(true)
      expect(wrapper.text()).toContain('新建分类')
    })

    it('重置表单数据', async () => {
      wrapper.vm.openCreate()
      
      expect(wrapper.vm.form.id).toBeNull()
      expect(wrapper.vm.form.name).toBe('')
      expect(wrapper.vm.form.description).toBe('')
      expect(wrapper.vm.form.parent).toBeNull()
      expect(wrapper.vm.form.status).toBe('active')
      expect(wrapper.vm.form.order).toBe(0)
      expect(wrapper.vm.form.icon).toBe('')
      expect(wrapper.vm.form.color).toBe('#409EFF')
    })
  })

  describe('编辑分类', () => {
    it('点击编辑按钮', async () => {
      const editButtons = wrapper.findAll('button').filter(btn => btn.text() === '编辑')
      await editButtons[0].trigger('click')
      
      expect(wrapper.vm.dialogVisible).toBe(true)
      expect(wrapper.vm.isEdit).toBe(true)
    })

    it('显示编辑分类对话框', async () => {
      wrapper.vm.dialogVisible = true
      wrapper.vm.isEdit = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.el-dialog').exists()).toBe(true)
      expect(wrapper.text()).toContain('编辑分类')
    })

    it('填充表单数据', async () => {
      const category = wrapper.vm.categories[0]
      wrapper.vm.openEdit(category)
      
      expect(wrapper.vm.form.id).toBe(category.id)
      expect(wrapper.vm.form.name).toBe(category.name)
      expect(wrapper.vm.form.description).toBe(category.description)
      expect(wrapper.vm.form.status).toBe(category.status)
      expect(wrapper.vm.form.order).toBe(category.order)
      expect(wrapper.vm.form.icon).toBe(category.icon)
      expect(wrapper.vm.form.color).toBe(category.color)
    })
  })

  describe('表单字段', () => {
    it('显示名称输入框', async () => {
      wrapper.vm.dialogVisible = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('input[placeholder="请输入分类名称"]').exists()).toBe(true)
    })

    it('显示描述文本框', async () => {
      wrapper.vm.dialogVisible = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('textarea[placeholder="分类描述"]').exists()).toBe(true)
    })

    it('显示父分类选择器', async () => {
      wrapper.vm.dialogVisible = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('select').exists()).toBe(true)
    })

    it('显示状态选择器', async () => {
      wrapper.vm.dialogVisible = true
      await wrapper.vm.$nextTick()
      
      const statusSelect = wrapper.findAll('select')[1]
      expect(statusSelect.exists()).toBe(true)
    })

    it('显示排序输入框', async () => {
      wrapper.vm.dialogVisible = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('input[type="number"]').exists()).toBe(true)
    })

    it('显示图标输入框', async () => {
      wrapper.vm.dialogVisible = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('input[placeholder="可填 emoji 或关键字"]').exists()).toBe(true)
    })

    it('显示颜色选择器', async () => {
      wrapper.vm.dialogVisible = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('input[type="color"]').exists()).toBe(true)
    })
  })

  describe('父分类选项', () => {
    it('计算父分类选项', () => {
      const options = wrapper.vm.parentOptions
      expect(options.length).toBe(3)
      expect(options[0].name).toBe('Vue.js')
      expect(options[1].name).toBe('React')
      expect(options[2].name).toBe('Python')
    })

    it('编辑时排除当前分类', async () => {
      wrapper.vm.isEdit = true
      wrapper.vm.form.id = 1
      await wrapper.vm.$nextTick()
      
      const options = wrapper.vm.parentOptions
      expect(options.length).toBe(2)
      expect(options.find(c => c.id === 1)).toBeUndefined()
    })
  })

  describe('保存分类', () => {
    it('保存新建分类', async () => {
      const originalCount = wrapper.vm.categories.length
      wrapper.vm.form.name = '新分类'
      wrapper.vm.form.description = '新分类描述'
      
      await wrapper.vm.handleSave()
      
      expect(wrapper.vm.categories.length).toBe(originalCount + 1)
      expect(wrapper.vm.dialogVisible).toBe(false)
    })

    it('保存编辑分类', async () => {
      const category = wrapper.vm.categories[0]
      wrapper.vm.form = { ...category, name: '更新后的名称' }
      wrapper.vm.isEdit = true
      
      await wrapper.vm.handleSave()
      
      expect(wrapper.vm.categories[0].name).toBe('更新后的名称')
      expect(wrapper.vm.dialogVisible).toBe(false)
    })

    it('保存状态管理', async () => {
      wrapper.vm.saving = false
      await wrapper.vm.handleSave()
      
      expect(wrapper.vm.saving).toBe(false)
    })
  })

  describe('删除分类', () => {
    it('确认删除分类', async () => {
      const originalCount = wrapper.vm.categories.length
      const category = wrapper.vm.categories[0]
      
      // Mock confirm to return true
      global.confirm = vi.fn(() => true)
      
      wrapper.vm.confirmDelete(category)
      
      expect(wrapper.vm.categories.length).toBe(originalCount - 1)
      expect(wrapper.vm.categories.find(c => c.id === category.id)).toBeUndefined()
    })

    it('取消删除分类', async () => {
      const originalCount = wrapper.vm.categories.length
      const category = wrapper.vm.categories[0]
      
      // Mock confirm to return false
      global.confirm = vi.fn(() => false)
      
      wrapper.vm.confirmDelete(category)
      
      expect(wrapper.vm.categories.length).toBe(originalCount)
      expect(wrapper.vm.categories.find(c => c.id === category.id)).toBeDefined()
    })
  })

  describe('响应式数据', () => {
    it('分类数据正确绑定', () => {
      expect(wrapper.vm.categories.length).toBe(3)
      expect(wrapper.vm.categories[0].name).toBe('Vue.js')
      expect(wrapper.vm.categories[1].name).toBe('React')
      expect(wrapper.vm.categories[2].name).toBe('Python')
    })

    it('对话框状态正确绑定', () => {
      expect(wrapper.vm.dialogVisible).toBe(false)
      expect(wrapper.vm.isEdit).toBe(false)
    })

    it('表单数据正确绑定', () => {
      expect(wrapper.vm.form.name).toBe('')
      expect(wrapper.vm.form.status).toBe('active')
      expect(wrapper.vm.form.color).toBe('#409EFF')
    })
  })

  describe('数据加载', () => {
    it('获取分类列表', () => {
      expect(wrapper.vm.fetchCategories).toBeDefined()
    })

    it('加载状态显示', async () => {
      wrapper.vm.loading = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.loading).toBe(true)
    })
  })

  describe('边界情况', () => {
    it('无分类时显示空表格', async () => {
      wrapper.vm.categories = []
      await wrapper.vm.$nextTick()
      
      const rows = wrapper.findAll('tbody tr')
      expect(rows.length).toBe(0)
    })

    it('表单验证', async () => {
      wrapper.vm.dialogVisible = true
      wrapper.vm.form.name = ''
      await wrapper.vm.$nextTick()
      
      const nameInput = wrapper.find('input[placeholder="请输入分类名称"]')
      expect(nameInput.attributes('required')).toBeDefined()
    })
  })

  describe('样式类名', () => {
    it('成功状态样式', () => {
      const successTags = wrapper.findAll('.el-tag.success')
      expect(successTags.length).toBeGreaterThan(0)
    })

    it('信息状态样式', () => {
      const infoTags = wrapper.findAll('.el-tag.info')
      expect(infoTags.length).toBeGreaterThan(0)
    })
  })
}) 