# MySQL测试数据库配置指南

## 🎯 为什么使用MySQL进行测试？

### ✅ 优势
1. **生产环境一致性**：与生产环境使用相同的数据库类型
2. **SQL语法兼容性**：避免SQLite和MySQL的语法差异
3. **性能测试**：更真实的性能测试环境
4. **特性测试**：可以测试MySQL特有的功能
5. **数据完整性**：MySQL的约束和索引行为更接近生产环境

### ❌ 劣势
1. **配置复杂性**：需要额外的MySQL配置
2. **资源消耗**：比SQLite占用更多系统资源
3. **依赖外部服务**：需要MySQL服务运行

## 🔧 配置步骤

### 1. 创建测试数据库

```sql
-- 连接到MySQL
mysql -u root -p

-- 创建测试数据库
CREATE DATABASE test_alpha_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 验证数据库创建
SHOW DATABASES;
```

### 2. 配置测试设置

使用 `tests/test_settings_mysql.py` 配置文件：

```bash
# 设置环境变量
export DJANGO_SETTINGS_MODULE=tests.test_settings_mysql

# 或者修改 pytest.ini
DJANGO_SETTINGS_MODULE = tests.test_settings_mysql
```

### 3. 安装MySQL依赖

```bash
pip install mysqlclient
# 或者
pip install PyMySQL
```

### 4. 运行测试

```bash
# 使用MySQL配置运行测试
python -m pytest tests/regression/english/test_data_analysis.py -v

# 或者使用一键测试脚本
python tests/run_tests.py --module=english
```

## 📝 配置文件说明

### `tests/test_settings_mysql.py`

- **数据库引擎**：`django.db.backends.mysql`
- **测试数据库**：`test_alpha_db`
- **字符集**：`utf8mb4`
- **排序规则**：`utf8mb4_unicode_ci`

### 环境变量配置

```bash
# Windows PowerShell
$env:DJANGO_SETTINGS_MODULE = "tests.test_settings_mysql"

# Windows CMD
set DJANGO_SETTINGS_MODULE=tests.test_settings_mysql

# Linux/Mac
export DJANGO_SETTINGS_MODULE=tests.test_settings_mysql
```

## 🚀 快速切换配置

### 方法1：环境变量切换

```bash
# 使用SQLite（快速测试）
export DJANGO_SETTINGS_MODULE=tests.test_settings

# 使用MySQL（生产环境测试）
export DJANGO_SETTINGS_MODULE=tests.test_settings_mysql
```

### 方法2：修改pytest.ini

```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = tests.test_settings_mysql  # 改为MySQL配置
```

### 方法3：命令行参数

```bash
# 使用特定配置运行测试
python -m pytest tests/ --ds=tests.test_settings_mysql
```

## 🔍 验证配置

### 检查数据库连接

```python
# 在测试中验证数据库类型
from django.db import connection
print(f"Database engine: {connection.vendor}")
print(f"Database name: {connection.settings_dict['NAME']}")
```

### 检查表结构

```sql
-- 连接到测试数据库
USE test_alpha_db;

-- 查看表结构
SHOW TABLES;
DESCRIBE english_typing_word;
```

## ⚠️ 注意事项

1. **数据库权限**：确保MySQL用户有创建/删除数据库的权限
2. **端口冲突**：确保MySQL服务在指定端口运行
3. **字符集**：使用utf8mb4以支持完整的Unicode字符
4. **测试隔离**：每次测试后清理测试数据
5. **性能影响**：MySQL测试比SQLite慢，但更真实

## 🎉 最佳实践

1. **开发阶段**：使用SQLite快速迭代
2. **集成测试**：使用MySQL验证生产环境兼容性
3. **CI/CD**：在CI环境中使用MySQL进行完整测试
4. **性能测试**：使用MySQL进行真实的性能基准测试
5. **数据迁移测试**：使用MySQL测试数据库迁移脚本

## 🔄 切换回SQLite

如果需要快速切换回SQLite配置：

```bash
# 修改pytest.ini
DJANGO_SETTINGS_MODULE = tests.test_settings

# 或者设置环境变量
export DJANGO_SETTINGS_MODULE=tests.test_settings
```

## 🎯 为什么使用MySQL进行测试？

### ✅ 优势
1. **生产环境一致性**：与生产环境使用相同的数据库类型
2. **SQL语法兼容性**：避免SQLite和MySQL的语法差异
3. **性能测试**：更真实的性能测试环境
4. **特性测试**：可以测试MySQL特有的功能
5. **数据完整性**：MySQL的约束和索引行为更接近生产环境

### ❌ 劣势
1. **配置复杂性**：需要额外的MySQL配置
2. **资源消耗**：比SQLite占用更多系统资源
3. **依赖外部服务**：需要MySQL服务运行

## 🔧 配置步骤

### 1. 创建测试数据库

```sql
-- 连接到MySQL
mysql -u root -p

-- 创建测试数据库
CREATE DATABASE test_alpha_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 验证数据库创建
SHOW DATABASES;
```

### 2. 配置测试设置

使用 `tests/test_settings_mysql.py` 配置文件：

```bash
# 设置环境变量
export DJANGO_SETTINGS_MODULE=tests.test_settings_mysql

# 或者修改 pytest.ini
DJANGO_SETTINGS_MODULE = tests.test_settings_mysql
```

### 3. 安装MySQL依赖

```bash
pip install mysqlclient
# 或者
pip install PyMySQL
```

### 4. 运行测试

```bash
# 使用MySQL配置运行测试
python -m pytest tests/regression/english/test_data_analysis.py -v

# 或者使用一键测试脚本
python tests/run_tests.py --module=english
```

## 📝 配置文件说明

### `tests/test_settings_mysql.py`

- **数据库引擎**：`django.db.backends.mysql`
- **测试数据库**：`test_alpha_db`
- **字符集**：`utf8mb4`
- **排序规则**：`utf8mb4_unicode_ci`

### 环境变量配置

```bash
# Windows PowerShell
$env:DJANGO_SETTINGS_MODULE = "tests.test_settings_mysql"

# Windows CMD
set DJANGO_SETTINGS_MODULE=tests.test_settings_mysql

# Linux/Mac
export DJANGO_SETTINGS_MODULE=tests.test_settings_mysql
```

## 🚀 快速切换配置

### 方法1：环境变量切换

```bash
# 使用SQLite（快速测试）
export DJANGO_SETTINGS_MODULE=tests.test_settings

# 使用MySQL（生产环境测试）
export DJANGO_SETTINGS_MODULE=tests.test_settings_mysql
```

### 方法2：修改pytest.ini

```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = tests.test_settings_mysql  # 改为MySQL配置
```

### 方法3：命令行参数

```bash
# 使用特定配置运行测试
python -m pytest tests/ --ds=tests.test_settings_mysql
```

## 🔍 验证配置

### 检查数据库连接

```python
# 在测试中验证数据库类型
from django.db import connection
print(f"Database engine: {connection.vendor}")
print(f"Database name: {connection.settings_dict['NAME']}")
```

### 检查表结构

```sql
-- 连接到测试数据库
USE test_alpha_db;

-- 查看表结构
SHOW TABLES;
DESCRIBE english_typing_word;
```

## ⚠️ 注意事项

1. **数据库权限**：确保MySQL用户有创建/删除数据库的权限
2. **端口冲突**：确保MySQL服务在指定端口运行
3. **字符集**：使用utf8mb4以支持完整的Unicode字符
4. **测试隔离**：每次测试后清理测试数据
5. **性能影响**：MySQL测试比SQLite慢，但更真实

## 🎉 最佳实践

1. **开发阶段**：使用SQLite快速迭代
2. **集成测试**：使用MySQL验证生产环境兼容性
3. **CI/CD**：在CI环境中使用MySQL进行完整测试
4. **性能测试**：使用MySQL进行真实的性能基准测试
5. **数据迁移测试**：使用MySQL测试数据库迁移脚本

## 🔄 切换回SQLite

如果需要快速切换回SQLite配置：

```bash
# 修改pytest.ini
DJANGO_SETTINGS_MODULE = tests.test_settings

# 或者设置环境变量
export DJANGO_SETTINGS_MODULE=tests.test_settings
```
