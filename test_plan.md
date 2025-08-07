# Alpha 技术共享平台 - 测试计划

## 🎯 测试目标

确保Alpha技术共享平台的每个功能模块都能正确工作，包括：
- Django后端配置正确
- 数据库模型正常工作
- API接口功能完整
- 用户认证系统可靠
- 前端页面正常显示

## 📋 测试阶段

### 第一阶段：基础环境测试 (1-2小时)
- [ ] Python环境检查
- [ ] Django项目配置验证
- [ ] 数据库连接测试
- [ ] 依赖包安装验证

### 第二阶段：数据库模型测试 (1小时)
- [ ] 模型迁移测试
- [ ] 数据表创建验证
- [ ] 模型关系测试
- [ ] 自定义方法测试

### 第三阶段：API接口测试 (2-3小时)
- [ ] 用户认证API测试
- [ ] 文章管理API测试
- [ ] 分类管理API测试
- [ ] 权限控制测试

### 第四阶段：前端功能测试 (2-3小时)
- [ ] Vue项目构建测试
- [ ] 页面路由测试
- [ ] 组件功能测试
- [ ] API集成测试

### 第五阶段：集成测试 (1-2小时)
- [ ] 前后端联调测试
- [ ] 用户流程测试
- [ ] 性能压力测试
- [ ] 安全漏洞测试

## 🧪 测试用例

### 1. 环境配置测试

#### 1.1 Python环境检查
```bash
# 检查Python版本
python --version

# 检查pip版本
pip --version

# 检查虚拟环境
python -c "import sys; print(sys.executable)"
```

#### 1.2 Django项目检查
```bash
# 检查Django版本
python -c "import django; print(django.get_version())"

# 检查项目配置
python manage.py check

# 检查数据库连接
python manage.py dbshell
```

#### 1.3 依赖包检查
```bash
# 安装依赖
pip install -r requirements.txt

# 检查关键包
python -c "import rest_framework; print('DRF OK')"
python -c "import corsheaders; print('CORS OK')"
python -c "import jwt; print('JWT OK')"
```

### 2. 数据库模型测试

#### 2.1 模型迁移测试
```bash
# 创建迁移文件
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 检查迁移状态
python manage.py showmigrations
```

#### 2.2 模型功能测试
```python
# 测试用户模型
from apps.users.models import User
user = User.objects.create_user(username='test', email='test@example.com', password='test123')
print(f"用户创建成功: {user.username}")

# 测试分类模型
from apps.categories.models import Category
category = Category.objects.create(name='技术', slug='tech', description='技术相关')
print(f"分类创建成功: {category.name}")

# 测试文章模型
from apps.articles.models import Article
article = Article.objects.create(
    title='测试文章',
    content='这是测试内容',
    author=user,
    category=category
)
print(f"文章创建成功: {article.title}")
```

### 3. API接口测试

#### 3.1 认证API测试
```bash
# 测试用户注册
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"test123"}'

# 测试用户登录
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

#### 3.2 文章API测试
```bash
# 获取文章列表
curl http://127.0.0.1:8000/api/articles/

# 创建文章
curl -X POST http://127.0.0.1:8000/api/articles/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"测试文章","content":"内容","category":1}'
```

### 4. 前端功能测试

#### 4.1 Vue项目测试
```bash
# 检查Node.js环境
node --version
npm --version

# 安装依赖
cd frontend
npm install

# 启动开发服务器
npm run dev
```

#### 4.2 页面功能测试
- [ ] 首页加载正常
- [ ] 用户登录页面
- [ ] 文章列表页面
- [ ] 文章详情页面
- [ ] 用户注册页面

## 🚨 常见问题排查

### 1. Django配置问题
```bash
# 检查settings.py配置
python manage.py check --deploy

# 检查静态文件配置
python manage.py collectstatic --dry-run

# 检查数据库配置
python manage.py dbshell
```

### 2. 数据库问题
```bash
# 重置数据库
python manage.py flush

# 重新创建迁移
python manage.py makemigrations --empty apps.users
python manage.py makemigrations --empty apps.articles
python manage.py makemigrations --empty apps.categories
```

### 3. API问题
```bash
# 检查API路由
python manage.py show_urls

# 测试API端点
python manage.py shell
```

## 📊 测试报告模板

### 测试结果记录
```
测试日期: _________
测试人员: _________
测试环境: _________

✅ 通过测试:
- [ ] 环境配置
- [ ] 数据库模型
- [ ] API接口
- [ ] 前端功能
- [ ] 集成测试

❌ 失败测试:
- [ ] 问题描述
- [ ] 错误信息
- [ ] 解决方案

📝 备注:
```

## 🎯 下一步行动计划

1. **立即执行**: 基础环境测试
2. **修复问题**: 根据测试结果修复配置问题
3. **逐步推进**: 按阶段执行测试计划
4. **记录结果**: 详细记录每个测试结果
5. **持续改进**: 根据测试反馈优化代码

---

*测试计划版本: v1.0*
*最后更新: 2024年1月* 