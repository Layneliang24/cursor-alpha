

```python
import requests
import pytest

# 基础API端点URL（根据实际环境调整）
BASE_API_URL = "http://localhost:8000/api/"

@pytest.fixture(scope="session")
def auth_token():
    """获取认证令牌的fixture"""
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_API_URL}auth/login/", data=login_data)
    assert response.status_code == 200, "登录失败"
    return response.json().get("token")

def test_article_list_endpoint(auth_token):
    """测试文章列表接口"""
    headers = {"Authorization": f"Token {auth_token}"}
    response = requests.get(f"{BASE_API_URL}articles/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list), "响应数据应为列表类型"

def test_word_detail_endpoint(auth_token):
    """测试单词详情接口（假设存在ID为1的单词）"""
    headers = {"Authorization": f"Token {auth_token}"}
    response = requests.get(f"{BASE_API_URL}words/1/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "word" in data, "响应缺少'word'字段"
    assert "pronunciation" in data, "响应缺少'pronunciation'字段"

def test_typing_practice_endpoint(auth_token):
    """测试打字练习接口响应格式"""
    headers = {"Authorization": f"Token {auth_token}"}
    response = requests.get(f"{BASE_API_URL}typing/practice/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "sentence" in data, "响应缺少'sentence'字段"
    assert isinstance(data.get("difficulty", ""), str), "'difficulty'字段应为字符串类型"

def test_unauthorized_access():
    """测试未认证的接口访问"""
    response = requests.get(f"{BASE_API_URL}articles/")
    assert response.status_code == 401, "未认证访问应返回401状态码"

if __name__ == "__main__":
    # 运行所有测试
    import sys
    pytest.main([__file__, '-v'])
```

这个测试脚本包含以下特点：
1. 使用pytest框架组织测试用例
2. 包含认证fixture管理
3. 测试了不同类型的API端点：
   - 带认证的文章列表接口
   - 单个单词详情接口
   - 打字练习接口
   - 未认证访问测试
4. 检查HTTP状态码和响应数据格式
5. 可直接运行执行测试

注意：需要根据实际的API端点URL、认证方式和数据格式调整：
- 修改BASE_API_URL为实际后端地址
- 更新auth_token中使用的登录凭证
- 根据实际接口规范调整断言条件
- 添加必要的环境变量管理（如需要）