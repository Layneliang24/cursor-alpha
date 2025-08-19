# CI/CD 配置指南

## 📋 概述

本文档说明如何配置Alpha项目的CI/CD流程，解决GitHub Actions中的环境变量问题。

## 🚨 当前问题

CI/CD报错：缺少必需的环境变量
```
The job is failing because required environment variables (HOST, USERNAME, SSH_KEY, PORT, PROJECT_DIR) are missing.
```

## 🔧 解决方案

### 1. 设置GitHub Secrets

在GitHub仓库中设置以下Secrets：

#### 必需的环境变量
| Secret名称 | 说明 | 示例值 |
|-----------|------|--------|
| `HOST` | 服务器IP地址或域名 | `192.168.1.100` 或 `your-server.com` |
| `USERNAME` | SSH用户名 | `root` 或 `deploy` |
| `SSH_KEY` | SSH私钥内容 | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `PORT` | SSH端口 | `22` |
| `PROJECT_DIR` | 项目部署目录 | `/var/www/alpha` |

#### 可选的环境变量
| Secret名称 | 说明 | 示例值 |
|-----------|------|--------|
| `PASS_PHRASE` | SSH私钥密码（如果有） | `your-passphrase` |

### 2. 设置步骤

#### 步骤1：生成SSH密钥对
```bash
# 生成SSH密钥对
ssh-keygen -t rsa -b 4096 -C "deploy@alpha.com"

# 查看公钥（添加到服务器）
cat ~/.ssh/id_rsa.pub

# 查看私钥（添加到GitHub Secrets）
cat ~/.ssh/id_rsa
```

#### 步骤2：配置服务器
```bash
# 在服务器上创建部署用户
sudo adduser deploy
sudo usermod -aG docker deploy

# 添加SSH公钥到服务器
mkdir -p /home/deploy/.ssh
echo "your-public-key" >> /home/deploy/.ssh/authorized_keys
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys

# 创建项目目录
sudo mkdir -p /var/www/alpha
sudo chown deploy:deploy /var/www/alpha
```

#### 步骤3：设置GitHub Secrets

1. 进入GitHub仓库
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 添加以下Secrets：

```
HOST=your-server-ip
USERNAME=deploy
SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
... (完整的私钥内容)
-----END OPENSSH PRIVATE KEY-----
PORT=22
PROJECT_DIR=/var/www/alpha
```

### 3. 测试配置

#### 手动测试SSH连接
```bash
# 测试SSH连接
ssh -i ~/.ssh/id_rsa deploy@your-server-ip

# 测试项目目录访问
ssh -i ~/.ssh/id_rsa deploy@your-server-ip "ls -la /var/www/alpha"
```

#### 测试GitHub Actions
1. 推送代码到main分支
2. 检查Actions页面
3. 查看部署日志

## 🔄 自动化部署流程

### 当前部署流程
1. 代码推送到main分支
2. GitHub Actions触发部署
3. SSH连接到服务器
4. 拉取最新代码
5. 构建Docker镜像
6. 启动服务

### 部署命令
```bash
# 在服务器上执行的命令
cd /var/www/alpha
git fetch --all
git reset --hard origin/main
docker compose -f docker-compose.prod.yml --env-file production.env build backend frontend
docker compose -f docker-compose.prod.yml --env-file production.env up -d mysql
docker compose -f docker-compose.prod.yml --env-file production.env run --rm backend python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml --env-file production.env up -d backend frontend
docker image prune -f
```

## 🛠️ 故障排除

### 常见问题

#### 1. SSH连接失败
```bash
# 检查SSH密钥权限
chmod 600 ~/.ssh/id_rsa

# 测试SSH连接
ssh -v -i ~/.ssh/id_rsa deploy@your-server-ip
```

#### 2. 权限问题
```bash
# 确保部署用户有Docker权限
sudo usermod -aG docker deploy

# 确保项目目录权限正确
sudo chown -R deploy:deploy /var/www/alpha
```

#### 3. Docker权限问题
```bash
# 重启Docker服务
sudo systemctl restart docker

# 检查Docker组权限
groups deploy
```

### 调试命令
```bash
# 查看GitHub Actions日志
# 在Actions页面点击具体的workflow查看详细日志

# 在服务器上手动执行部署命令
cd /var/www/alpha
docker compose -f docker-compose.prod.yml --env-file production.env ps
```

## 📝 环境变量检查清单

- [ ] `HOST` - 服务器地址已设置
- [ ] `USERNAME` - SSH用户名已设置
- [ ] `SSH_KEY` - SSH私钥已设置
- [ ] `PORT` - SSH端口已设置
- [ ] `PROJECT_DIR` - 项目目录已设置
- [ ] `PASS_PHRASE` - SSH密码（如果需要）
- [ ] SSH公钥已添加到服务器
- [ ] 服务器用户权限已配置
- [ ] 项目目录已创建并设置权限
- [ ] Docker权限已配置

## 🔒 安全建议

1. **使用专用部署用户**：不要使用root用户进行部署
2. **限制SSH访问**：只允许密钥认证，禁用密码认证
3. **定期轮换密钥**：定期更新SSH密钥
4. **监控部署日志**：定期检查部署日志
5. **备份配置**：备份重要的配置文件

---

*最后更新：2024年12月*
