# 备份与恢复

## 📋 概述

本文档汇总Alpha项目的备份策略与恢复流程，来源于整体部署文档的备份章节，便于独立维护与执行。

## 💾 数据备份策略

### 数据库备份
```bash
# 创建备份脚本
sudo tee /usr/local/bin/backup_alpha_db.sh > /dev/null <<EOF
#!/bin/bash
BACKUP_DIR="/var/backups/alpha"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="alpha_production"
DB_USER="alpha_user"
DB_PASS="your_password_here"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME > $BACKUP_DIR/${DB_NAME}_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/${DB_NAME}_$DATE.sql

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Database backup completed: ${DB_NAME}_$DATE.sql.gz"
EOF

# 设置执行权限
sudo chmod +x /usr/local/bin/backup_alpha_db.sh

# 添加到定时任务（每天2:00执行）
sudo crontab -e
0 2 * * * /usr/local/bin/backup_alpha_db.sh
```

### 文件备份
```bash
# 创建文件备份脚本
sudo tee /usr/local/bin/backup_alpha_files.sh > /dev/null <<EOF
#!/bin/bash
BACKUP_DIR="/var/backups/alpha"
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE_DIR="/var/www/alpha"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份媒体文件
tar -czf $BACKUP_DIR/media_${DATE}.tar.gz -C $SOURCE_DIR media/

# 备份代码文件
tar -czf $BACKUP_DIR/code_${DATE}.tar.gz -C $SOURCE_DIR --exclude=venv --exclude=node_modules .

# 删除30天前的备份
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Files backup completed"
EOF

# 设置执行权限
sudo chmod +x /usr/local/bin/backup_alpha_files.sh

# 添加到定时任务（每周日3:00执行）
sudo crontab -e
0 3 * * 0 /usr/local/bin/backup_alpha_files.sh
```

## ♻️ 数据恢复流程

### 数据库恢复
```bash
# 恢复数据库
mysql -u alpha_user -p alpha_production < backup_file.sql

# 或使用gunzip解压后恢复
gunzip -c backup_file.sql.gz | mysql -u alpha_user -p alpha_production
```

### 文件恢复
```bash
# 恢复媒体文件
tar -xzf media_backup.tar.gz -C /var/www/alpha/

# 恢复代码文件
tar -xzf code_backup.tar.gz -C /var/www/alpha/
```

## ✅ 备份验证

### 定期验证
```bash
# 验证数据库备份
mysql -u alpha_user -p -e "USE alpha_production; SHOW TABLES;"

# 验证文件备份
ls -la /var/backups/alpha/
du -sh /var/backups/alpha/*
```

---

最后更新：2025-01-17
来源：docs/DEPLOYMENT.md 备份章节

---

## 容器化环境快速方案（合并自 06-部署运维/备份策略）

### 核心命令
```bash
# MySQL（容器内导出到宿主机目录）
TS=$(date +%F)
mkdir -p /opt/alpha/backups
docker ps -qf name=mysql | ForEach-Object { docker exec -i $_ mysqldump -ualpha -palpha_pass alpha } | gzip > /opt/alpha/backups/alpha_${TS}.sql.gz

# 媒体文件（示例路径）
rsync -a --delete /opt/alpha/data/media/ /opt/alpha/backups/media/
```

### 恢复（示例）
```bash
gunzip -c /opt/alpha/backups/alpha_YYYY-MM-DD.sql.gz | docker exec -i $(docker ps -qf name=mysql) mysql -ualpha -palpha_pass alpha
rsync -a /opt/alpha/backups/media/ /opt/alpha/data/media/
```
