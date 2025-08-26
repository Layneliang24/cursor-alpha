# 本地AI设置指南（无需API密钥）

## 🎯 **为什么选择本地AI？**

### **优势：**
- ✅ **无需API密钥** - 完全免费使用
- ✅ **隐私保护** - 数据不离开本地
- ✅ **无限制使用** - 不受API调用限制
- ✅ **离线工作** - 不依赖网络连接
- ✅ **自定义模型** - 可训练专用模型

### **适用场景：**
- 个人开发项目
- 企业内部开发
- 对隐私要求高的项目
- 网络环境受限的场景

## 🚀 **方案一：使用Ollama（推荐）**

### **1. 安装Ollama**

#### **Windows安装：**
```bash
# 1. 下载安装包
https://ollama.ai/download

# 2. 运行安装程序
# 3. 启动Ollama服务
ollama serve
```

#### **macOS安装：**
```bash
# 使用Homebrew
brew install ollama

# 启动服务
ollama serve
```

#### **Linux安装：**
```bash
# 使用官方脚本
curl -fsSL https://ollama.ai/install.sh | sh

# 启动服务
ollama serve
```

### **2. 下载AI模型**

```bash
# 下载代码生成专用模型
ollama pull codellama:7b

# 或下载通用模型
ollama pull llama2:7b
ollama pull mistral:7b

# 查看已安装模型
ollama list
```

### **3. 测试Ollama**

```bash
# 测试模型是否正常工作
ollama run codellama:7b "写一个Python函数"

# 或使用API测试
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "codellama:7b",
    "prompt": "写一个Python函数"
  }'
```

### **4. 运行本地AI流水线**

```bash
# 使用本地AI流水线
python scripts/local_ai_pipeline.py \
  --input docs/spec/requirements/idiomatic_expressions_enhancement.md \
  --ai-model codellama:7b \
  --project-root .

# 预览模式
python scripts/local_ai_pipeline.py \
  --input docs/spec/requirements/idiomatic_expressions_enhancement.md \
  --dry-run
```

## 🔧 **方案二：使用备用规则引擎**

如果不想安装Ollama，可以使用内置的规则引擎：

```bash
# 直接运行（会自动使用备用方案）
python scripts/local_ai_pipeline.py \
  --input docs/spec/requirements/idiomatic_expressions_enhancement.md
```

### **备用方案功能：**
- ✅ 智能需求解析（基于正则表达式）
- ✅ 代码分析（AST解析）
- ✅ 模板代码生成
- ✅ 重复文件检测
- ✅ 文件哈希管理

## 📊 **方案对比**

| 功能 | Ollama + 本地模型 | 备用规则引擎 | 云端AI |
|------|-------------------|--------------|--------|
| **费用** | 免费 | 免费 | 付费 |
| **隐私** | 完全本地 | 完全本地 | 云端处理 |
| **网络** | 无需网络 | 无需网络 | 需要网络 |
| **性能** | 中等 | 快速 | 快速 |
| **质量** | 高 | 中等 | 高 |
| **安装** | 需要安装 | 无需安装 | 无需安装 |

## 🛠️ **安装步骤详解**

### **步骤1：安装Ollama**

#### **Windows详细步骤：**
1. 访问 https://ollama.ai/download
2. 下载Windows安装包
3. 运行安装程序
4. 打开命令提示符或PowerShell
5. 运行：`ollama serve`
6. 保持窗口打开

#### **验证安装：**
```bash
# 检查Ollama版本
ollama --version

# 检查服务状态
curl http://localhost:11434/api/tags
```

### **步骤2：下载模型**

```bash
# 下载推荐的代码生成模型
ollama pull codellama:7b

# 等待下载完成（约3-5GB）
# 下载完成后会显示模型信息
```

### **步骤3：测试模型**

```bash
# 简单测试
ollama run codellama:7b "写一个Python的Hello World"

# 代码生成测试
ollama run codellama:7b "写一个Django模型类"
```

### **步骤4：运行流水线**

```bash
# 进入项目目录
cd /path/to/your/project

# 运行本地AI流水线
python scripts/local_ai_pipeline.py \
  --input docs/spec/requirements/idiomatic_expressions_enhancement.md \
  --ai-model codellama:7b
```

## 🔍 **故障排除**

### **问题1：Ollama服务无法启动**

**解决方案：**
```bash
# 检查端口占用
netstat -an | findstr 11434

# 如果端口被占用，关闭占用进程
# 或修改Ollama端口
set OLLAMA_HOST=0.0.0.0:11435
ollama serve
```

### **问题2：模型下载失败**

**解决方案：**
```bash
# 检查网络连接
ping ollama.ai

# 使用代理（如果需要）
set HTTPS_PROXY=http://proxy:port
ollama pull codellama:7b

# 或使用镜像源
ollama pull codellama:7b --registry-url https://mirror.ghproxy.com/
```

### **问题3：内存不足**

**解决方案：**
```bash
# 使用更小的模型
ollama pull codellama:3b

# 或使用量化模型
ollama pull codellama:7b-q4_0

# 修改运行参数
python scripts/local_ai_pipeline.py \
  --ai-model codellama:3b
```

### **问题4：流水线运行失败**

**解决方案：**
```bash
# 检查Python依赖
pip install requests

# 检查文件权限
chmod +x scripts/local_ai_pipeline.py

# 使用备用方案
python scripts/local_ai_pipeline.py \
  --input docs/spec/requirements/idiomatic_expressions_enhancement.md \
  --dry-run
```

## 📈 **性能优化**

### **1. 模型选择**

```bash
# 快速响应（较小模型）
ollama pull codellama:3b

# 高质量输出（较大模型）
ollama pull codellama:13b

# 平衡选择（推荐）
ollama pull codellama:7b
```

### **2. 硬件要求**

| 模型大小 | 最小内存 | 推荐内存 | 推荐GPU |
|----------|----------|----------|---------|
| 3B | 4GB | 8GB | 可选 |
| 7B | 8GB | 16GB | 推荐 |
| 13B | 16GB | 32GB | 必需 |

### **3. 配置优化**

```bash
# 设置环境变量
set OLLAMA_NUM_PARALLEL=4
set OLLAMA_HOST=0.0.0.0:11434

# 启动Ollama
ollama serve
```

## 🎯 **使用建议**

### **1. 首次使用**
```bash
# 1. 安装Ollama
# 2. 下载codellama:7b模型
# 3. 测试基本功能
# 4. 运行流水线
```

### **2. 日常使用**
```bash
# 启动Ollama服务（后台运行）
ollama serve &

# 运行流水线
python scripts/local_ai_pipeline.py --input your_requirement.md
```

### **3. 团队使用**
```bash
# 共享模型文件
# 统一模型版本
# 配置团队环境变量
```

## 📋 **总结**

**本地AI流水线的优势：**

1. **🔒 隐私安全** - 数据完全本地处理
2. **💰 成本低廉** - 无需支付API费用
3. **⚡ 响应快速** - 无网络延迟
4. **🛠️ 功能完整** - 包含所有智能功能
5. **🔄 重复防护** - 避免重复生成文件

**推荐配置：**
- **模型**：codellama:7b
- **内存**：16GB+
- **存储**：10GB+ 可用空间
- **网络**：首次下载需要网络

**立即开始：**
```bash
# 安装Ollama
# 下载模型
ollama pull codellama:7b

# 运行流水线
python scripts/local_ai_pipeline.py \
  --input docs/spec/requirements/idiomatic_expressions_enhancement.md
```

这样您就可以享受完整的AI增强流水线功能，而无需任何API密钥！ 