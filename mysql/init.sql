-- Alpha项目数据库初始化脚本
-- 设置字符集和排序规则
ALTER DATABASE alpha_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户并授权（如果不存在）
CREATE USER IF NOT EXISTS 'alpha_user'@'%' IDENTIFIED BY 'alphapassword123';
GRANT ALL PRIVILEGES ON alpha_db.* TO 'alpha_user'@'%';
FLUSH PRIVILEGES;

-- 设置时区
SET time_zone = '+08:00';

