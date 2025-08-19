# 验收清单 - 英语学习模块：单词功能

## 接口契约
- [ ] 符合 `docs/spec/openapi.json` 中 `/english/words/`、`/english/words/{id}/`、`/english/progress/` 的请求与响应结构
- [ ] 统一响应包：`{ success, message, data, pagination? }`
- [ ] 鉴权：Bearer JWT；无权限返回 401/403
- [ ] 分页参数：`page`、`page_size` 生效

## 数据模型
- [ ] 按 `docs/spec/db/english_models.json` 创建 `english_words`、`user_word_progress` 表
- [ ] 索引与唯一约束生效（`word` 唯一、`(user_id, word_id)` 唯一）
- [ ] `difficulty_level`、`status` 枚举与 `docs/spec/enums.yaml` 一致

## 业务规则
- [ ] 新建单词：`word` 去重（忽略大小写/首尾空白）
- [ ] 更新进度：`mastery_level` 范围 [0,1]；`status` 变更时更新 `next_review_date`
- [ ] 列表筛选：支持 `difficulty_level`、`category`（可选）

## 缓存与限流
- [ ] 热门列表缓存（Redis）TTL≥300s，Key规范：`english:words:list:{query_hash}`
- [ ] 词典外部API访问遵循 `docs/spec/rate_limit.yaml`

## 前端页面
- [ ] 路由符合 `docs/spec/frontend_routes.json`，权限守卫启用
- [ ] `WordLearning.vue`：加载/空态/错误态处理；播放发音按钮可用（软失败不阻塞）
- [ ] 进度更新后，页面与后端数据一致

## 测试
- [ ] 后端单测：模型/序列化/视图/权限（覆盖率≥80%）
- [ ] 接口契约测试：根据 OpenAPI 生成用例或手写校验字段
- [ ] 前端组件单测：渲染、交互、权限指令
- [ ] E2E：登录→访问 /english/words → 查看列表→更新进度→刷新后保持

## 性能/安全
- [ ] P95 响应时间 < 500ms（本地或测试环境）
- [ ] XSS/SQL注入防护；日志不记录敏感信息

## 交付物
- [ ] 迁移脚本与回滚说明
- [ ] 初始种子数据导入（见 `tests/fixtures/english_seed.json`）
- [ ] README 片段（如何启用模块/环境变量）
