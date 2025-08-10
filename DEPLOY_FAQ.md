## Alpha 部署 FAQ 与常用命令速查

以下整理了从“代码已在 GitHub 与云服务器”到“Docker 运行 + CI/CD”过程中最常见的问题、原因与解决办法，并附常用命令速查。

### 0. 环境与文件清单
- 服务器安装 Docker + Compose（v2 命令为 `docker compose`）
- 项目关键文件：
  - `docker-compose.prod.yml`
  - `backend/Dockerfile.prod`
  - `frontend/Dockerfile.prod`、`frontend/nginx.prod.conf`、`frontend/nginx.conf`
  - `production.env`（仅存服务器，不入库；可由 `production.env.example` 复制生成）

---

### 1. Docker 安装/CentOS 7 EOL 警告
问题：安装脚本提示 CentOS 7 已停止支持或安装失败。
- 原因：CentOS 7 EOL，官方脚本/仓库支持不完整。
- 处理：
  - 优先升级系统到 Ubuntu 20.04+/Rocky 8+/AlmaLinux 8+。
  - 临时方案：用国内源安装 Docker，或换镜像站点；但长期建议升级 OS。

### 2. `docker pull`/`compose pull` 超时（registry-1.docker.io）
问题：超时或握手失败。
- 原因：访问 Docker Hub 网络慢/DNS 解析问题。
- 处理：配置 `/etc/docker/daemon.json`：
```
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://hub-mirror.c.163.com",
    "https://docker.mirrors.ustc.edu.cn"
  ],
  "dns": ["223.5.5.5","119.29.29.29"],
  "ipv6": false
}
```
重启 Docker：`systemctl daemon-reload && systemctl restart docker`

### 3. DNS 报错 `no such host`（镜像域名解析失败）
- 处理：同上设置 `dns`；换可用代理仓库前缀拉取后重打标签：
```
docker pull docker.m.daocloud.io/library/mysql:8.0
docker tag docker.m.daocloud.io/library/mysql:8.0 mysql:8.0
```

### 4. `compose pull` 与 `compose up` 的关系
- `pull`：只拉镜像到本机。
- `up`：若本地无镜像，会拉取；若需构建本地镜像，也会触发构建。
- 网络不畅时，先 `pull` 能更清晰地看下载是否卡住。

### 5. 后端构建很慢（apt/pip 依赖）
- 原因：基础镜像/apt/pip 从国外下载。
- 处理：在 `backend/Dockerfile.prod` 使用国内 apt 与 pip 源，并保持分层：
  - apt 层（兼容 deb822）：检测 `sources.list` 或 `debian.sources`，替换为阿里源；只安装必须依赖；清理缓存。
  - pip 层：使用阿里 pypi 源（`-i https://mirrors.aliyun.com/pypi/simple`）。
- 注意：首次修改源后可 `--no-cache` 构建建立缓存；后续正常 `build` 即可命中缓存，速度显著提升。

### 6. 是否每次都 `--no-cache`？
- 否。只有以下改动才需要：
  - 修改了 `backend/Dockerfile(.prod)` 中 apt/pip 层或基础镜像版本。
  - 修改了 `requirements.txt`。
- 日常只改代码时：`docker compose build backend` 即可（复用缓存）。

### 7. MySQL 重启/初始化失败（`MYSQL_USER=root`）
问题：`[Entrypoint] MYSQL_USER="root" ...`。
- 原因：官方镜像不允许用 `MYSQL_USER=root`。
- 正确配置（示例，写入 `production.env`）：
```
MYSQL_ROOT_PASSWORD=your_strong_root_pwd
MYSQL_DATABASE=alpha_db
MYSQL_USER=alpha_user
MYSQL_PASSWORD=your_strong_db_pwd

DB_NAME=alpha_db
DB_USER=alpha_user
DB_PASSWORD=your_strong_db_pwd
DB_HOST=mysql
DB_PORT=3306
```
- 若初始化阶段失败且可丢数据：删除卷后重来（危险）：
```
docker compose -f docker-compose.prod.yml down
docker volume ls | grep mysql_data
docker volume rm <卷名>
docker compose -f docker-compose.prod.yml up -d mysql
```

### 8. 后端写日志报 `PermissionError: /app/logs/django.log`
- 原因：挂载了宿主机目录 `./logs:/app/logs`，容器内非 root 用户无权写。
- 处理：
```
mkdir -p logs backend/media backend/static
chmod -R 777 logs backend/media backend/static
```
- 最佳实践：生产可仅输出到 stdout（Docker 收集日志），避免文件权限问题。

### 9. 前端 Nginx 容器 `addgroup: group 'nginx' in use`
- 原因：`nginx:alpine` 已有 `nginx` 用户/组；重复创建报错。
- 处理：删除 `addgroup/adduser`，或做幂等检查；确保仍创建日志目录并授权即可。

### 10. ImportError（如 `ExternalLinkViewSet`/`password_reset_request`）
- 原因：镜像里是旧代码；更新代码后未重建镜像。
- 处理：
```
git fetch --all && git reset --hard origin/main
docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml --env-file production.env up -d backend
```
- 仍不生效：进容器检查 `/app/apps/api/views.py` 是否有新代码；必要时 `build --no-cache`。

### 11. `DJANGO_SECRET_KEY` 是什么/如何设置
- 用于签名会话/CSRF 等；必须保密，生产使用长随机字符串。
- 位置：`backend/alpha/settings.py` 读取环境变量。
- 生成：`python -c "import secrets; print(secrets.token_urlsafe(64))"`
- 设置：`production.env` 中写入 `DJANGO_SECRET_KEY=...`，不要提交到 Git。

### 12. `DJANGO_ALLOWED_HOSTS` 填什么
- 用逗号分隔域名/IP（不要空格），与请求 Host 一致（不含端口）。
- 示例：`your-domain.com,www.your-domain.com,你的服务器IP`

### 13. 首次 `up` 很慢的原因
- 拉基础镜像 + 构建后端/前端（pip/npm）+ 数据库初始化。首轮慢属正常；有缓存后会快很多。

### 14. Nginx 配置未挂载导致前端起不来
- 确保存在并挂载：
```
mkdir -p nginx/conf.d ssl logs/nginx
cp frontend/nginx.conf nginx/nginx.conf
cp frontend/nginx.prod.conf nginx/conf.d/default.conf
```

### 15. CI/CD（GitHub Actions → SSH 部署）
- 在仓库 Secrets 添加：`HOST`、`USERNAME`、`SSH_KEY`、`PORT`（可加 `PROJECT_DIR`）。
- 工作流做：SSH 到服务器 → `git reset --hard origin/main` → `docker compose up --build -d`。
- 注意：`production.env` 只在服务器，不入库。

### 16. 拉取代码会不会覆盖我改过的 Dockerfile？
- `git reset --hard origin/main` 会覆盖为远端版本。
- 建议把你确认的加速修改提交进仓库，保证环境一致；或临时用 `git update-index --skip-worktree backend/Dockerfile.prod` 避免被写回（不推荐长期使用）。

---

## 常用命令速查

### Git
```
git status
git add -A && git commit -m "chore: ..." && git push
git fetch --all && git reset --hard origin/main
```

### Docker 服务与网络
```
systemctl status docker
systemctl daemon-reload && systemctl restart docker
docker info | grep -A3 "Registry Mirrors"
```

### Compose 常用
```
# 查看
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=200
docker compose -f docker-compose.prod.yml logs --tail=200 backend

# 启动/更新（生产）
docker compose -f docker-compose.prod.yml --env-file production.env up -d
docker compose -f docker-compose.prod.yml --env-file production.env up -d backend

# 构建
docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml build frontend
docker compose -f docker-compose.prod.yml build backend --no-cache   # 仅在依赖层变动时

# 停止/移除
docker compose -f docker-compose.prod.yml down
```

### 容器与镜像
```
docker ps
docker exec -it alpha_backend_prod bash
docker image ls
docker system prune -f
```

### 网络与连通性
```
curl -I http://localhost
curl -I http://localhost/api/v1/
nslookup registry-1.docker.io
nslookup docker.m.daocloud.io
```

### MySQL 初始化/重置（危险）
```
docker compose -f docker-compose.prod.yml logs --tail=200 mysql
docker volume ls | grep mysql_data
docker volume rm <卷名>   # 会清空数据
```

### 镜像代理拉取 + 重打标签
```
docker pull docker.m.daocloud.io/library/mysql:8.0
docker tag docker.m.daocloud.io/library/mysql:8.0 mysql:8.0
```

---

如需把日志改为仅输出到 stdout、引入 wait-for-db、更细的健康检查或将构建转移到 CI/CD（服务器仅拉镜像运行），可再告知，我可以进一步精简与优化。 


