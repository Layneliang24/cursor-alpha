### docs_test API 契约（样板）

[返回总览](./README.md)

> 专注接口契约：路径、方法、参数、响应、错误码与示例。方案性描述放在 `GUIDE.md`。

#### 参考与来源
- 权威来源：`../docs/API.md`
- OpenAPI 规范：`../docs/spec/openapi.json`

---

## [auth] 接口
### POST /api/v1/auth/login/
- 描述：登录并返回 tokens 与用户信息（JWT）
- 请求示例：
```json
{
  "code": "xxx",
  "state": "yyy"
}
```
- 响应示例：
```json
{
  "accessToken": "...",
  "expiresIn": 3600
}
```
- 错误码：`400` 参数错误，`401` 未授权，`429` 频控

### GET /api/v1/users/me/
- 描述：获取当前用户信息

---

## [english-news] 接口
### GET /api/v1/english/news/
- 描述：新闻列表（分页/筛选/排序）
- 参考：查询参数规范见 `../docs/API.md#获取新闻列表`

---

## [article] 接口
### GET /api/v1/articles/
- 描述：文章列表（分页/筛选/排序）
### GET /api/v1/articles/{id}/
- 描述：文章详情
### POST /api/v1/articles/
- 描述：创建文章（需认证）

---

## 错误码约定（与 docs 对齐）
- `4xx` 客户端错误；`5xx` 服务端错误
- 统一错误响应：
```json
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "reason"
  }
}
```


