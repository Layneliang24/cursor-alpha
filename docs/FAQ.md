# 常见问题解答 (FAQ)

## 目录
- [按业务模块分类](#按业务模块分类)
  - [🎓 英语学习模块](#-英语学习模块)
  - [📰 新闻系统模块](#-新闻系统模块)
  - [🧪 测试与CI/CD](#-测试与cicd)
- [🔧 技术问题分类](#-技术问题分类)
- [📝 问题记录模板](#-问题记录模板)
- [🚀 最佳实践](#-最佳实践)
- [📚 参考资料](#-参考资料)

## 📋 文档说明

本文档记录项目开发过程中遇到的技术问题和解决方案，按功能模块分类整理，便于后续开发和问题排查。

## 🎯 更新规范

每次解决一个问题后，需要按以下格式记录：

1. **问题描述**：清晰描述问题的现象和影响
2. **问题分析**：分析问题的根本原因
3. **解决方案**：详细记录解决步骤和代码修改
4. **经验总结**：总结经验和最佳实践
5. **相关文件**：列出涉及的文件和代码位置

---

## 业务模块

### 📚 英语学习模块

#### 🎯 智能练习页面

##### 问题1：自动发音功能失效

**问题描述**
- 智能练习页面切换单词时，自动发音功能不工作
- 控制台显示 `组件不可用，延迟重试...` 和 `重试失败`
- 手动点击发音按钮也无法播放音频

**问题分析**
1. **组件引用失效**：`wordPronunciationRef.value` 为 `null`
2. **组件重新创建**：每次单词切换时，`wordComponentKey` 更新导致组件重新渲染
3. **ref 丢失**：组件重新创建后，原来的 ref 引用失效
4. **Vue 3 ref 绑定问题**：动态组件和 key 属性变化导致 ref 引用不稳定

**解决方案**

1. **引入 getCurrentInstance**
```javascript
import { getCurrentInstance } from 'vue'

// 获取组件实例
const instance = getCurrentInstance()
```

2. **使用多重 ref 获取方式**
```javascript
// 尝试多种方式获取组件引用
let componentRef = wordPronunciationRef.value
if (!componentRef && instance) {
  componentRef = instance.refs?.wordPronunciationRef
}
```

3. **延迟获取组件引用**
```javascript
// 等待组件完全渲染后再尝试发音
setTimeout(() => {
  // 获取组件引用并调用方法
}, 100) // 给组件100ms时间完成渲染
```

4. **统一 ref 获取逻辑**
```javascript
// 在所有发音方法中使用相同的组件引用获取方式
const getComponentRef = () => {
  let componentRef = wordPronunciationRef.value
  if (!componentRef && instance) {
    componentRef = instance.refs?.wordPronunciationRef
  }
  return componentRef
}
```

**经验总结**
1. **Vue 3 ref 绑定**：当组件频繁重新创建时，ref 引用可能失效
2. **getCurrentInstance 备选方案**：使用 `instance.refs` 作为 ref 失效时的备选方案
3. **延迟获取策略**：给组件足够时间完成渲染后再获取引用
4. **多重备选方案**：确保组件引用获取的可靠性

**相关文件**
- `frontend/src/views/english/TypingPractice.vue`：主要修改文件
- `frontend/src/components/typing/WordPronunciationIcon.vue`：发音组件
- `frontend/src/stores/typing.js`：状态管理

**解决时间**：2025-01-17

---

### 🧪 测试与CI/CD

> 参见 `docs/TESTING_STANDARDS.md` 获取完整规范与流程；本节聚合与测试/CI 相关的问题记录。

#### 问题1：测试系统基础设施搭建

**问题描述**
- 项目缺乏完整的测试体系，新功能容易破坏现有功能
- 没有标准化的测试目录结构和测试用例
- 缺乏一键测试执行机制
- 测试覆盖情况不明确

**问题分析**
1. **测试体系缺失**：项目只有零散的测试文件，缺乏系统性
2. **测试环境不统一**：不同开发者使用不同的测试配置
3. **测试执行复杂**：需要手动运行多个测试文件
4. **测试覆盖未知**：不清楚哪些功能有测试，哪些没有

**解决方案**

1. **建立标准化测试目录结构**
```
tests/
├── regression/          # 回归测试
│   ├── english/        # 英语学习模块测试
│   ├── auth/           # 认证模块测试
│   └── ...
├── new_features/       # 新功能测试
├── unit/              # 单元测试
├── integration/       # 集成测试
├── resources/         # 测试资源
├── reports/           # 测试报告
└── run_tests.py       # 一键测试脚本
```

2. **配置MySQL测试数据库**
```python
# tests/test_settings_mysql.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test_alpha_db',
        'USER': 'root',
        'PASSWORD': 'meimei520',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

3. **实现一键测试脚本**
```python
# tests/run_tests.py
class TestRunner:
    def run_module_tests(self, module_name):
        """运行指定模块的测试"""
        command = f"python -m pytest tests/regression/{module_name}/ -v"
        return self.run_command(command)
```

4. **创建测试覆盖分析文档**
- 详细分析89个功能的测试覆盖情况
- 按模块、页面、功能三级结构组织
- 标记测试状态和优先级

**经验总结**
1. **测试体系重要性**：完整的测试体系是项目稳定性的基础
2. **标准化目录结构**：便于维护和扩展测试用例
3. **生产环境测试数据库**：使用MySQL确保测试环境与生产环境一致
4. **自动化测试执行**：一键测试脚本提高开发效率
5. **测试覆盖分析**：明确测试覆盖情况，指导测试补充

**相关文件**
- `tests/`：整个测试目录结构
- `tests/run_tests.py`：一键测试脚本
- `tests/test_settings_mysql.py`：MySQL测试配置
- `tests/FUNCTION_COVERAGE_ANALYSIS.md`：功能覆盖分析文档

**解决时间**：2025-01-17

---

#### 问题2：API路径不一致导致的测试失败

**问题描述**
- 测试用例中使用的API路径与实际项目API路径不匹配
- 测试期望 `/api/english/` 但实际项目使用 `/api/v1/english/`
- 导致大量API测试失败，返回404错误

**问题分析**
1. **API版本化**：项目使用了版本化的API路径 `/api/v1/`
2. **测试用例过时**：测试用例基于旧的API路径编写
3. **路径配置分散**：API路径配置在多个地方，容易不一致

**解决方案**

1. **批量修复API路径**
```python
# tests/fix_api_paths.py
import os
import re

def fix_api_paths():
    """批量修复测试文件中的API路径"""
    test_dir = "tests/regression"
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换API路径
                new_content = re.sub(
                    r'/api/english/', 
                    '/api/v1/english/', 
                    content
                )
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
```

2. **统一API路径规范**
- 所有API路径使用 `/api/v1/` 前缀
- 在测试文档中明确API路径规范
- 建立API路径检查机制

**经验总结**
1. **API版本化管理**：明确API版本化策略，避免路径混乱
2. **测试用例同步**：API变更时及时更新测试用例
3. **自动化修复**：使用脚本批量修复路径问题
4. **规范文档化**：将API路径规范写入文档

**相关文件**
- `tests/fix_api_paths.py`：API路径修复脚本
- `tests/regression/english/`：英语模块测试文件
- `backend/apps/english/urls.py`：API路由配置

**解决时间**：2025-01-17

---

##### 问题3：Django权限创建冲突

**问题描述**
- 权限测试中创建Django权限时出现 `IntegrityError`
- 错误信息：`Duplicate entry '9-add_article' for key 'auth_permission.auth_permission_content_type_id_codename_01ab375a_uniq'`
- Django已经为模型自动创建了权限，测试中又手动创建相同权限

**问题分析**
1. **Django自动权限**：Django为每个模型自动创建增删改查权限
2. **测试重复创建**：测试代码手动创建已存在的权限
3. **权限唯一性约束**：权限的content_type和codename组合必须唯一

**解决方案**

1. **使用get方法获取已存在权限**
```python
# 修改前：创建权限
self.add_article_permission = Permission.objects.create(
    codename='add_article',
    name='Can add article',
    content_type=content_type
)

# 修改后：获取已存在权限
self.add_article_permission = Permission.objects.get(
    codename='add_article',
    content_type=content_type
)
```

2. **权限存在性检查**
```python
def get_or_create_permission(codename, content_type):
    """获取或创建权限"""
    try:
        return Permission.objects.get(
            codename=codename,
            content_type=content_type
        )
    except Permission.DoesNotExist:
        return Permission.objects.create(
            codename=codename,
            name=f'Can {codename}',
            content_type=content_type
        )
```

**经验总结**
1. **Django权限机制**：了解Django自动权限创建机制
2. **避免重复创建**：使用get方法获取已存在权限
3. **权限管理策略**：在测试中合理管理权限对象
4. **错误处理**：添加适当的异常处理机制

**相关文件**
- `tests/regression/auth/test_permissions.py`：权限测试文件
- `backend/apps/articles/models.py`：文章模型

**解决时间**：2025-01-17

---

### 📰 新闻系统模块

##### 问题5：新闻图片显示问题（图片URL构建错误）

**问题描述**
- 英语新闻页面图片无法显示，显示为破损图片图标
- 图片URL显示为相对路径格式：`news_images/xxx.jpg`
- 前端无法正确加载本地存储的新闻图片
- 这是一个反复出现的老问题，用户反馈"发生过百八十次"

**问题分析**
1. **图片URL格式问题**：后端存储的图片URL是相对路径（如 `news_images/xxx.jpg`）
2. **前端URL构建缺失**：前端直接使用相对路径，无法构建完整的图片访问URL
3. **序列化器缺少处理**：后端序列化器没有将相对路径转换为完整URL
4. **媒体文件访问路径**：本地图片需要 `/media/` 前缀才能正确访问

**解决方案**

1. **修改序列化器，添加图片URL处理方法**
```python
# backend/apps/english/serializers.py
class NewsSerializer(serializers.ModelSerializer):
    # 构建完整的图片URL
    image_url = serializers.SerializerMethodField()
    
    def get_image_url(self, obj):
        """构建完整的图片URL"""
        if not obj.image_url:
            return None
        
        # 如果是相对路径（本地图片），构建完整URL
        if obj.image_url.startswith('news_images/'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/media/{obj.image_url}')
            else:
                # 如果没有request上下文，使用默认域名
                from django.conf import settings
                return f"{settings.BASE_URL}/media/{obj.image_url}" if hasattr(settings, 'BASE_URL') else f"/media/{obj.image_url}"
        
        # 如果是完整URL，直接返回
        return obj.image_url
```

2. **修改视图，传递request上下文**
```python
# backend/apps/english/views.py
def list(self, request, *args, **kwargs):
    page = self.paginate_queryset(self.get_queryset())
    serializer = self.get_serializer(page, many=True, context={'request': request})
    return self.get_paginated_response(serializer.data)
```

**经验总结**
1. **图片URL处理**：本地图片需要构建完整的媒体文件访问URL
2. **序列化器设计**：使用 `SerializerMethodField` 处理复杂的字段转换逻辑
3. **request上下文**：确保序列化器能获取到request对象来构建完整URL
4. **相对路径转换**：统一处理相对路径到绝对URL的转换逻辑

**相关文件**
- `backend/apps/english/serializers.py`：修改序列化器，添加图片URL处理方法
- `backend/apps/english/views.py`：修改视图，传递request上下文

**解决时间**：2025-01-17

**问题严重性**：⭐⭐⭐⭐ 影响用户体验，图片无法显示

**教训总结**
- 图片URL处理是常见问题，需要在序列化器层面统一处理
- 本地媒体文件的URL构建需要考虑域名和路径前缀
- 这类问题容易反复出现，需要建立标准化的处理流程

---

##### 问题6：新闻日期显示分时信息（日期格式设置错误）

**问题描述**
- 英语新闻页面日期显示包含时分信息，如 "2025-01-17 14:30"
- 新闻列表应该只显示日期，不需要显示具体时间
- 前端和后端的日期格式设置不一致，导致用户体验不佳

**问题分析**
1. **前端日期格式化问题**：`formatDate` 函数包含了 `hour: '2-digit', minute: '2-digit'` 选项
2. **后端时间字段格式**：`created_at` 和 `updated_at` 字段没有设置日期格式，可能包含时间信息
3. **日期显示不一致**：不同位置的日期显示格式不统一

**解决方案**

1. **修复前端日期格式化函数**
```javascript
// frontend/src/views/english/NewsDashboard.vue
const formatDate = (dateString) => {
  if (!dateString) return '暂无日期'
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return '日期无效'
    }
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
      // 移除 hour 和 minute 选项
    })
  } catch (error) {
    console.error('日期格式化错误:', error, dateString)
    return '日期错误'
  }
}
```

2. **修复后端时间字段格式**
```python
# backend/apps/english/serializers.py
class NewsSerializer(serializers.ModelSerializer):
    # 格式化发布日期，只显示日期不显示时间
    publish_date = serializers.DateField(format='%Y-%m-%d', read_only=True)
    
    # 格式化时间字段，只显示日期不显示时间
    created_at = serializers.DateField(format='%Y-%m-%d', read_only=True)
    updated_at = serializers.DateField(format='%Y-%m-%d', read_only=True)
```

**经验总结**
1. **日期格式统一**：前端和后端的日期格式应该保持一致
2. **用户体验**：新闻列表通常只需要显示日期，不需要显示具体时间
3. **代码审查**：日期格式化函数应该仔细检查，避免不必要的时分显示
4. **序列化器设计**：时间字段应该根据业务需求设置合适的格式

**相关文件**
- `frontend/src/views/english/NewsDashboard.vue`：修复前端日期格式化函数
- `backend/apps/english/serializers.py`：修复后端时间字段格式

**解决时间**：2025-01-17

**问题严重性**：⭐⭐⭐ 影响用户体验，显示信息冗余

**教训总结**
- 日期格式设置需要前后端协调一致
- 新闻类应用通常只需要显示日期，不需要显示具体时间
- 格式化函数应该根据实际业务需求设计

---

##### 问题7：修复图片显示问题后产生500错误（字段类型不匹配）

**问题描述**
- 修复新闻图片显示问题后，新闻API返回500内部服务器错误
- 前端无法获取新闻数据，页面完全无法显示
- 错误信息：`Request failed with status code 500`
- 这是一个典型的"修复一个问题又产生新问题"的案例

**问题分析**
1. **字段类型不匹配**：在序列化器中错误地将 `DateTimeField` 设置为 `DateField`
2. **模型继承关系**：`News` 模型继承自 `TimeStampedModel`，其中 `created_at` 和 `updated_at` 是 `DateTimeField`
3. **序列化器错误设置**：
   ```python
   # 错误的设置
   created_at = serializers.DateField(format='%Y-%m-%d', read_only=True)
   updated_at = serializers.DateField(format='%Y-%m-%d', read_only=True)
   ```
4. **类型转换失败**：Django无法将 `DateTimeField` 的值转换为 `DateField`，导致序列化失败

**解决方案**

1. **修正字段类型定义**
```python
# backend/apps/english/serializers.py
class NewsSerializer(serializers.ModelSerializer):
    # 格式化发布日期，只显示日期不显示时间
    publish_date = serializers.DateField(format='%Y-%m-%d', read_only=True)
    
    # 修正：DateTimeField需要DateTimeField，但可以设置格式只显示日期
    created_at = serializers.DateTimeField(format='%Y-%m-%d', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%d', read_only=True)
    
    # 构建完整的图片URL
    image_url = serializers.SerializerMethodField()
```

2. **验证修复效果**
```bash
# 运行测试脚本验证API是否正常工作
python test_news_fix.py
# 输出：状态码: 200 ✓ 成功！API正常工作
```

**经验总结**
1. **字段类型一致性**：序列化器中的字段类型必须与模型字段类型匹配
2. **继承关系理解**：必须深入了解模型的继承关系和字段定义
3. **修复验证**：每次修复后都要验证功能是否正常，避免产生新问题
4. **类型安全**：Django的字段类型系统是严格的，不能随意混用

**相关文件**
- `backend/apps/english/serializers.py`：修正字段类型定义
- `backend/apps/english/models.py`：`TimeStampedModel` 基类定义

**解决时间**：2025-01-17

**问题严重性**：⭐⭐⭐⭐ 核心功能完全中断

**教训总结**
- **修复验证**：修复一个问题后，必须立即验证相关功能是否正常
- **字段类型匹配**：序列化器字段类型必须与模型字段类型完全一致
- **继承关系**：使用继承模型时，必须了解基类的字段定义
- **测试驱动**：每次修改后都应该有相应的测试验证

**用户反馈**
> "你修复一个问题，又产生新的问题"

这个反馈提醒我们：
1. 修复问题时要更加谨慎
2. 每次修复后都要全面测试
3. 要理解代码的依赖关系和类型系统

---

##### 问题8：新闻管理页面缺少fetchManagementNews方法（方法未实现）

**问题描述**
- 新闻管理页面加载列表失败，控制台报错：`newsStore.fetchManagementNews is not a function`
- 新闻管理对话框无法显示新闻列表
- 这是一个功能缺失问题，不是bug修复

**问题分析**
1. **方法缺失**：`useNewsStore` 中缺少 `fetchManagementNews` 方法
2. **状态缺失**：store中缺少 `managementNews` 和 `managementNewsLoading` 状态
3. **数据流不完整**：新闻管理界面无法获取和显示新闻数据
4. **删除后刷新问题**：删除新闻后没有刷新管理界面的新闻列表

**解决方案**

1. **添加缺失的状态和方法**
```javascript
// frontend/src/stores/news.js
export const useNewsStore = defineStore('news', {
  state: () => ({
    // ... 其他状态
    
    // 管理界面新闻列表
    managementNews: [],
    managementNewsLoading: false,
  }),

  actions: {
    // 获取管理界面新闻列表
    async fetchManagementNews(params = {}) {
      this.managementNewsLoading = true
      try {
        const query = {
          page: 1,
          page_size: 100, // 管理界面显示更多新闻
          ...params
        }
        const resp = await englishAPI.getNewsList(query)
        const data = resp?.data || resp?.results || resp?.items || []
        this.managementNews = data
        return data
      } finally {
        this.managementNewsLoading = false
      }
    },
  }
})
```

2. **修复删除后的刷新逻辑**
```javascript
// frontend/src/views/english/NewsDashboard.vue
const deleteNews = async (news) => {
  // ... 删除逻辑
  
  // 删除后立即刷新管理界面的新闻列表
  await newsStore.fetchManagementNews()
}

const batchDelete = async () => {
  // ... 批量删除逻辑
  
  // 批量删除后刷新管理界面的新闻列表
  await newsStore.fetchManagementNews()
}
```

**经验总结**
1. **功能完整性**：开发新功能时要确保所有相关的方法和状态都已实现
2. **数据流设计**：要设计完整的数据获取、显示、更新流程
3. **状态管理**：Pinia store应该包含所有必要的状态和actions
4. **用户体验**：操作后要及时刷新相关数据，保持界面同步

**相关文件**
- `frontend/src/stores/news.js`：添加缺失的状态和方法
- `frontend/src/views/english/NewsDashboard.vue`：修复删除后的刷新逻辑

**解决时间**：2025-01-17

**问题严重性**：⭐⭐⭐ 功能无法使用，影响管理功能

**教训总结**
- **功能开发**：新功能开发时要确保所有依赖都已实现
- **测试覆盖**：每个功能点都要有相应的测试验证
- **代码审查**：代码审查时要检查功能的完整性
- **用户体验**：要考虑用户操作的完整流程

---




### 🎓 英语学习模块

##### 问题2：发音重叠和重复播放

**问题描述**
- 多次输入错误会触发多次发音，形成重叠播放
- 新的发音没有停止之前的发音，导致多个音频同时播放
- 用户体验差，音频混乱，资源浪费

**问题分析**
1. **缺少发音互斥机制**：没有全局的发音状态管理
2. **错误重发音逻辑**：每次错误都重新播放，没有防抖机制
3. **音频实例管理**：多个音频实例同时存在，没有统一管理
4. **发音时机控制**：缺少发音频率限制和互斥控制

**解决方案**

1. **全局发音管理**
```javascript
// 全局发音实例管理
const pronunciationInstances = ref(new Set())

// 停止所有发音
const stopAllPronunciations = () => {
  pronunciationInstances.value.forEach(instance => {
    if (instance && typeof instance.stop === 'function') {
      instance.stop()
    }
  })
  pronunciationInstances.value.clear()
}
```

2. **发音防抖机制**
```javascript
// 防抖发音方法
const debouncedPlayPronunciation = (componentRef) => {
  if (pronunciationDebounceTimer.value) {
    clearTimeout(pronunciationDebounceTimer.value)
  }
  
  pronunciationDebounceTimer.value = setTimeout(() => {
    if (componentRef && componentRef.playSound) {
      componentRef.playSound()
    }
    pronunciationDebounceTimer.value = null
  }, 300) // 300ms内只执行一次
}
```

3. **全局发音控制**
```javascript
// 在WordPronunciationIcon组件中
const playSound = () => {
  // 全局发音管理：停止其他所有发音
  if (window.stopAllPronunciations) {
    window.stopAllPronunciations()
  }
  
  // 播放当前发音
  // ... 播放逻辑
}
```

4. **资源清理**
```javascript
onUnmounted(() => {
  // 清理全局发音管理函数
  delete window.stopAllPronunciations
  delete window.addPronunciationInstance
  
  // 清理防抖定时器
  if (pronunciationDebounceTimer.value) {
    clearTimeout(pronunciationDebounceTimer.value)
  }
  
  // 停止所有发音
  stopAllPronunciations()
})
```

**经验总结**
1. **全局状态管理**：发音功能需要全局状态管理，避免多个实例冲突
2. **防抖机制**：对于频繁触发的事件，使用防抖机制控制执行频率
3. **资源管理**：及时清理音频实例和定时器，避免内存泄漏
4. **互斥控制**：确保同时只有一个发音在播放，提升用户体验

**相关文件**
- `frontend/src/views/english/TypingPractice.vue`：主要修改文件，添加发音管理
- `frontend/src/components/typing/WordPronunciationIcon.vue`：发音组件，添加全局控制
- `docs/FAQ.md`：问题记录文档

**解决时间**：2025-01-17

---

##### 问题3：练习界面暂停按钮不起作用

**问题描述**
- 练习界面暂停按钮点击无反应
- 计时器继续运行，不受暂停状态影响
- 键盘输入在暂停状态下仍然有效
- 暂停状态没有实际控制练习流程

**问题分析**
1. **暂停逻辑不完整**：`togglePause` 函数只是改变了状态变量，没有实际控制功能
2. **计时器未受暂停状态影响**：store 中的计时器没有检查暂停状态
3. **键盘输入未受暂停状态控制**：暂停状态下仍然可以输入字母
4. **暂停状态管理缺失**：缺少暂停时间记录和状态同步
5. **响应式更新问题**：组件中的 `sessionTime` 重复定义导致响应式更新失效

**解决方案**

1. **完善暂停功能实现**
```javascript
const togglePause = () => {
  isPaused.value = !isPaused.value
  // 同步store中的暂停状态
  typingStore.isPaused = isPaused.value
  
  if (isPaused.value) {
    console.log('练习暂停')
    // 记录当前已用时间
    const currentElapsed = typingStore.sessionTime
    typingStore.pauseElapsedTime = currentElapsed
    console.log('记录暂停时已用时间:', currentElapsed, '秒')
    
    // 暂停计时器 - 直接调用store的方法
    typingStore.stopSessionTimer()
    console.log('暂停后计时器状态:', typingStore.isTimerRunning())
  } else {
    console.log('练习继续')
    // 继续计时器，从暂停的时间开始
    if (typingStore.pauseElapsedTime !== null) {
      // 设置新的开始时间，从暂停的时间开始计算
      const newStartTime = Date.now() - (typingStore.pauseElapsedTime * 1000)
      console.log('继续练习，从时间开始:', typingStore.pauseElapsedTime, '秒，新开始时间:', newStartTime)
      
      // 使用store的方法设置时间，确保状态同步
      typingStore.setSessionStartTime(newStartTime)
      typingStore.pauseElapsedTime = null
      
      // 使用setTimeout确保时间设置完成后再启动计时器
      setTimeout(() => {
        console.log('setTimeout后启动计时器，sessionStartTime:', typingStore.sessionStartTime)
        typingStore.startSessionTimer()
        console.log('继续后计时器状态:', typingStore.isTimerRunning())
      }, 50) // 给50ms确保时间设置完成
    } else {
      // 如果没有暂停时间记录，直接启动计时器
      typingStore.startSessionTimer()
      console.log('继续后计时器状态:', typingStore.isTimerRunning())
    }
  }
}
```

2. **添加暂停状态管理**
```javascript
// 在typing store中添加
const isPaused = ref(false)
const pauseStartTime = ref(null)
const pauseElapsedTime = ref(null) // 暂停时已用时间

// 导出状态
return {
  isPaused,
  pauseStartTime,
  pauseElapsedTime,
  // ... 其他状态
}
```

3. **修改计时器逻辑支持暂停**
```javascript
sessionTimer.value = setInterval(() => {
  // 检查是否处于暂停状态
  if (isPaused.value) {
    console.log('计时器暂停中，跳过更新')
    return // 暂停时不更新计时
  }
  
  // 正常计时逻辑
  if (sessionStartTime.value) {
    const elapsed = Math.floor((Date.now() - sessionStartTime.value) / 1000)
    sessionTime.value = elapsed
  }
}, 1000)
```

4. **暂停状态下禁用键盘输入**
```javascript
// 检查是否处于暂停状态
if (isPaused.value) {
  console.log('练习已暂停，不处理输入')
  return
}
```

5. **重置时清除暂停状态**
```javascript
const resetPractice = () => {
  // 重置暂停状态
  isPaused.value = false
  typingStore.isPaused = false
  typingStore.pauseStartTime = null
  typingStore.pauseElapsedTime = null
  
  // 确保计时器停止
  typingStore.stopSessionTimer()
  
  // 重置练习状态
  typingStore.resetPractice()
}
```

6. **修复响应式更新问题**
```javascript
// 在setup函数中使用computed确保响应式更新
sessionTime: computed(() => {
  const time = typingStore.sessionTime
  console.log('sessionTime computed更新:', time)
  return time
}),
```

**经验总结**
1. **状态管理完整性**：暂停功能需要完整的状态管理，包括计时器、输入控制等
2. **功能逻辑完整性**：UI状态变化需要对应实际的功能控制
3. **状态同步**：组件状态和store状态需要保持同步
4. **用户体验**：暂停功能应该完全停止练习流程，包括计时和输入
5. **响应式更新**：避免重复定义状态，使用computed确保响应式更新

**相关文件**
- `frontend/src/views/english/TypingPractice.vue`：主要修改文件，完善暂停功能
- `frontend/src/stores/typing.js`：状态管理，添加暂停状态控制
- `docs/FAQ.md`：问题记录文档

**解决时间**：2025-01-17

---

## 🔧 技术问题分类

### Vue.js 相关问题

#### ref 引用失效
- **常见原因**：组件重新创建、动态组件、key 属性变化
- **解决方案**：使用 getCurrentInstance、延迟获取、多重备选方案

#### 组件生命周期
- **常见问题**：组件挂载时机、异步渲染、ref 绑定时机
- **解决方案**：使用 nextTick、setTimeout、事件监听

### 音频播放问题

#### 发音功能
- **技术栈**：@vueuse/sound、HTMLAudioElement、有道词典API
- **常见问题**：CORS、音频加载、播放时机
- **解决方案**：API代理、延迟加载、错误重试

---

## 📝 问题记录模板

### 问题记录格式

```markdown
##### 问题X：[问题标题]

**问题描述**
- 现象1
- 现象2
- 影响范围

**问题分析**
1. 原因1
2. 原因2
3. 根本原因

**解决方案**
1. 步骤1
2. 步骤2
3. 代码示例

**经验总结**
1. 经验1
2. 经验2
3. 最佳实践

**相关文件**
- 文件1：说明
- 文件2：说明

**解决时间**：YYYY-MM-DD
```

---

## 🚀 最佳实践

### 问题解决流程
1. **问题复现**：确保能稳定复现问题
2. **日志分析**：查看控制台日志和错误信息
3. **代码审查**：检查相关代码逻辑
4. **方案设计**：设计解决方案
5. **实施修复**：按步骤实施修复
6. **测试验证**：验证问题是否解决
7. **文档记录**：按规范记录到FAQ

### 代码质量要求
1. **错误处理**：添加适当的错误处理和日志
2. **性能优化**：避免不必要的重复操作
3. **代码复用**：提取公共逻辑到工具函数
4. **测试覆盖**：为修复的功能添加测试用例

---

## 📚 参考资料

- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Vue 3 ref 和 reactive](https://vuejs.org/guide/essentials/reactivity-fundamentals.html)
- [@vueuse/sound 文档](https://vueuse.org/integrations/useSound/)
- [有道词典API](https://ai.youdao.com/doc.s#guide)

---

*最后更新：2025-01-17*
*维护者：开发团队*

---

## 问题11：数据库状态与代码不匹配

**问题描述：** 恢复代码后，数据库状态与代码不匹配，导致API错误

**解决方案：**
1. 创建数据库备份脚本 `backup_database.py`
2. 备份包含字典和单词数据的完整状态
3. 将备份文件提交到git仓库，确保数据与代码同步
4. 提供恢复脚本，可以从备份文件恢复数据库状态

**恢复步骤：**
```bash
# 备份数据库
python backend/backup_database.py

# 恢复数据库
python backend/backup_database.py restore database_backup_YYYYMMDD_HHMMSS.json
```

**所属业务或模块：** 数据库管理

## 问题12：API兼容性问题导致500错误

**问题描述：** 恢复代码后，API返回500错误，提示 `'WSGIRequest' object has no attribute 'query_params'`

**问题分析：**
1. **请求类型不匹配**：Django的普通视图中使用 `request.GET`，而DRF ViewSet中使用 `request.query_params`
2. **代码恢复问题**：从远程仓库恢复代码后，之前的兼容性修复丢失
3. **测试环境差异**：直接测试ViewSet方法时使用不同的请求对象类型

**解决方案：**
1. **添加兼容性代码**：在API方法中添加请求类型检查
```python
# 兼容不同的请求类型
if hasattr(request, 'query_params'):
    category = request.query_params.get('category', 'CET4_T')
    difficulty = request.query_params.get('difficulty', 'intermediate')
    chapter = request.query_params.get('chapter')
    limit = int(request.query_params.get('limit', 50))
else:
    category = request.GET.get('category', 'CET4_T')
    difficulty = request.GET.get('difficulty', 'intermediate')
    chapter = request.GET.get('chapter')
    limit = int(request.GET.get('limit', 50))
```

2. **修复字典查询逻辑**：使用 `category` 而不是 `name` 字段查询字典
```python
dictionary = Dictionary.objects.get(category=category)
```

**经验总结：**
1. **代码恢复风险**：从远程仓库恢复代码可能丢失本地修复
2. **兼容性处理**：API代码需要考虑不同的请求类型
3. **数据库查询**：使用正确的字段进行数据库查询
4. **测试验证**：每次修复后都要验证API功能

**所属业务或模块：** API接口

## 问题13：练习完成后出现404错误

**问题描述：**
- 练习完成后浏览器控制台出现两个404错误：
  - `favicon.ico:1 Failed to load resource: the server responded with a status of 404 (Not Found)`
  - `/api/v1/english/typing-practice/daily-progress/?days=7:1 Failed to load resource: the server responded with a status of 404 (Not Found)`
- 前端显示"获取每日进度失败"的错误信息

**问题分析：**
1. **favicon.ico 404错误**：前端项目缺少favicon.ico文件，浏览器自动请求但找不到文件
2. **daily-progress API 404错误**：前端调用`/daily-progress/`路径，但后端方法名为`daily_progress`，生成的路由是`/daily_progress/`
3. **URL路径不匹配**：前端使用连字符，后端生成下划线路径

**解决方案：**

1. **修复API路由问题**
```python
# backend/apps/english/views.py
@method_decorator(cache_page(60 * 10))
@action(detail=False, methods=['get'], url_path='daily-progress')  # 添加url_path参数
def daily_progress(self, request):
    """获取每日学习进度 - 优化版本"""
    # ... 原有代码保持不变
```

2. **添加favicon.ico链接**
```html
<!-- frontend/index.html -->
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Alpha 技术共享平台</title>
    <link rel="icon" href="data:;base64,=" />  <!-- 添加空favicon避免404 -->
</head>
```

**验证结果：**
- API测试：`GET /api/v1/english/typing-practice/daily-progress/` 返回200状态码
- 无认证时正确返回401错误
- 前端构建成功，无语法错误

**经验总结：**
1. **API路径规范**：RESTful API中URL通常使用连字符分隔，需要在`@action`装饰器中明确指定`url_path`
2. **favicon处理**：可以使用空的data URI避免404请求，或添加实际的favicon文件
3. **前后端路径一致性**：确保前端API调用路径与后端路由完全匹配

**所属业务或模块：** 英语学习 - 智能练习