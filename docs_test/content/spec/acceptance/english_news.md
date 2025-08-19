# 验收清单 - 英语学习模块：新闻功能

## 接口契约
- [ ] 符合 `docs/spec/openapi.json` `/english/news/`、`/english/news/{id}/`、`/english/news/crawl/`
- [ ] 支持查询参数：`category`、`difficulty_level`、`date_from`、`date_to`、`q`
- [ ] 统一响应包格式；鉴权与错误码一致

## 数据模型
- [ ] `english_news` 按 `docs/spec/db/english_models.json` 创建
- [ ] 索引：`publish_date`、`category`、`difficulty_level`、`source`
- [ ] 记录来源合规：`source_url`、`license`、`quality_score`

## 业务规则
- [ ] 爬虫遵循 `docs/spec/rate_limit.yaml`（robots、频率、重试、指纹去重）
- [ ] 内容清洗：移除脚本/广告；摘要生成（可选）
- [ ] 搜索策略：无 ES 时提供 MySQL 简易全文/LIKE 回退

## 前端页面
- [ ] 列表筛选条件生效；分页正确
- [ ] 详情展示：标题/时间/来源/正文；空态/加载/错误态

## 测试
- [ ] 后端单测：模型/视图/爬虫策略（mock）
- [ ] 合同测试：查询参数与响应字段校验
- [ ] E2E：筛选→阅读→返回列表保持筛选状态

## 性能/安全
- [ ] 列表 P95 < 600ms；详情 P95 < 500ms
- [ ] 版权合规校验；日志不存储受版权限制正文片段（如有要求）

## 交付物
- [ ] 爬虫配置样例与运行说明
- [ ] 种子数据包含 2 篇示例新闻（见 `tests/fixtures/english_seed.json`）
