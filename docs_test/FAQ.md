### docs_test 常见问题与解决方案（样板）

[返回总览](./README.md)

## [auth] 相关
问题：测试用例 API 路径不一致导致 404。
根因：测试仍用 `/api/english/`，实际为 `/api/v1/english/`。
解决：统一前缀 `/api/v1/`，并提供批量修复脚本。
验证：回归跑通 `tests/regression/english/*`。
相关：`../docs/FAQ.md#问题2：API路径不一致导致的测试失败`

## [news] 相关
问题A：图片无法显示（相对路径）。
根因：后端保存相对路径，前端未构建完整 URL。
解决：序列化器构建 `/media/` 完整 URL，并传递 request 上下文。
验证：管理页与仪表板图片均正常。
相关：`../docs/FAQ.md#问题5：新闻图片显示问题（图片URL构建错误）`

问题B：日期显示包含时分。
根因：前端格式化包含 hour/minute；序列化器类型不当。
解决：前端仅日期；后端 `DateTimeField(format='%Y-%m-%d')`。
相关：`../docs/FAQ.md#问题6：新闻日期显示分时信息（日期格式设置错误）`

问题C：修复后 500（字段类型不匹配）。
根因：将 `DateTimeField` 错设为 `DateField`。
解决：改为 `DateTimeField(format='%Y-%m-%d')`。
相关：`../docs/FAQ.md#问题7：修复图片显示问题后产生500错误（字段类型不匹配）`

## [english] 相关
问题：发音功能失效/叠加播放；暂停按钮无效。
根因：ref 丢失、缺少全局发音互斥；暂停状态未贯穿计时与输入。
解决：getCurrentInstance + 统一 ref 获取；全局互斥与防抖；在 store 增加暂停状态并改造计时与输入路径。
验证：对应 E2E 与单元测试通过。
相关：`../docs/FAQ.md#英语学习模块`


