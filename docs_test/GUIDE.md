### docs_test 实施指南（样板）

[返回总览](./README.md)

> 本文件承载“怎么做”的细节与证据；若需一句话级目标，请查看 `README.md`。

## [auth] JWT 认证与权限策略（与 docs 对齐）
背景与目标：统一登录态与授权控制，接口全部走 `/api/v1/` 版本前缀。

实施要点：
1. 登录/登出/刷新：`/api/v1/auth/login|logout|token/refresh/`
2. 用户信息：`/api/v1/users/me/`
3. 前端拦截器：401 统一跳转登录；本地存储 access token
4. 权限：按模块与功能划分，测试用例补充（见 `../docs/TODO.md`）

相关：
- API：`../docs/API.md#🔐-认证`
- TODO：`../docs/TODO.md#第三阶段：API路由修复-已完成`

## [news] Fundus 集成与常见问题修复
背景与目标：集成 Fundus 爬虫（150+ 新闻源）、打通图片与日期展示链路。

实施要点：
1. Fundus 集成与管理命令：`crawl_news --crawler fundus`（dry-run/verbose）
2. 图片访问：序列化器构建 `/media/` 完整 URL，视图传递 `request`
3. 日期显示：前端仅日期；后端 `DateTimeField(format='%Y-%m-%d')`
4. 管理页：补全 `fetchManagementNews` 与状态，删除后刷新

相关：
- 模块文档：`../docs/modules/NEWS_SYSTEM.md`
- FAQ：`../docs/FAQ.md#新闻系统模块`

## [article] 文章系统（已上线）与全文检索改造
背景与目标：支持高亮、多字段筛选与排序；可水平扩展。

实施步骤（概述）：
1. 索引结构设计（标题、摘要、标签、作者、时间）
2. 同步策略：写入/更新/删除的索引一致性
3. 查询语法与排序策略
4. 观测：查询耗时与失败率

相关：
- TODO：`./TODO.md#待办`
- 参考：`../docs/technical/DATABASE.md`

## [english] 智能练习数据分析与学习统计
背景与目标：统一模型口径、事件埋点、指标统计；确保验收一致性。

实施步骤（概述）：
1. 模型梳理与字段口径统一（参考 `../docs/spec/db/english_models.json`）
2. Store 与前端路由一致性校验（参考 `../docs/spec/stores/english.json`、`../docs/spec/frontend_routes.json`）
3. 验收用例与数据集（参考 `../docs/spec/acceptance/english_words.md`、`../docs/spec/acceptance/english_news.md`）

相关：
- TODO：`../docs/TODO.md#英语学习模块`
- FAQ：`../docs/FAQ.md#英语学习模块`
- 参考：`../docs/spec/db/english_models.json`、`../docs/spec/acceptance/english_words.md`


