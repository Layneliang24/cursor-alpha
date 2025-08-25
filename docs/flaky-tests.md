# Flaky测试复跑与隔离机制

## 概述

Flaky测试是指在相同代码和环境下，有时通过有时失败的不稳定测试。这种测试会降低CI/CD的可靠性，影响开发效率。本项目实现了完整的flaky测试检测、重试和隔离机制。

## 功能特性

### 🔄 自动重试机制
- 失败的测试自动重试（默认最多3次）
- 智能重试策略，避免无限重试
- 记录重试次数和结果

### 📊 稳定性统计
- 跟踪每个测试的历史执行结果
- 计算测试成功率和平均执行时间
- 识别不稳定的测试用例

### 🚫 测试隔离
- 自动跳过已知的flaky测试
- 防止不稳定测试影响CI流程
- 支持手动标记flaky测试

### 📈 详细报告
- 生成HTML和JSON格式的报告
- 可视化测试稳定性趋势
- 提供改进建议

## 使用方法

### 基本命令

```bash
# 运行flaky测试检测
make flaky-test

# 分析flaky测试报告
make flaky-analyze

# 运行稳定性检查（多次运行测试）
make flaky-stability

# 跳过已知flaky测试运行
make flaky-isolate
```

### 高级用法

```bash
# 使用Python脚本直接管理
python scripts/flaky_test_manager.py --action test
python scripts/flaky_test_manager.py --action analyze
python scripts/flaky_test_manager.py --action stability --iterations 10

# 后端pytest配置
cd backend
pytest --flaky-max-retries=5 --flaky-threshold=0.7
pytest --flaky-isolate  # 跳过flaky测试

# 前端vitest配置
cd frontend
npm run test -- --config vitest.flaky.config.js
```

## 配置选项

### 后端配置 (pytest.ini)

```ini
[tool:pytest]
addopts = 
    -p tests.plugins.pytest_flaky
    --flaky-max-retries=3
    --flaky-threshold=0.8
    --flaky-report-dir=tests/reports/flaky
markers =
    flaky: mark test as potentially flaky
    slow: mark test as slow running
```

### 前端配置 (vitest.flaky.config.js)

```javascript
export default defineConfig({
  test: {
    retry: 3,  // 重试次数
    reporters: ['default', new FlakyReporter()],
    testTimeout: 10000,
  },
})
```

## 标记Flaky测试

### 后端 (Python)

```python
import pytest

@pytest.mark.flaky
def test_unstable_feature():
    # 可能不稳定的测试
    pass

@pytest.mark.flaky
@pytest.mark.slow
def test_slow_and_unstable():
    # 既慢又不稳定的测试
    pass
```

### 前端 (JavaScript)

```javascript
// 在测试描述中标记
it('should handle flaky behavior', () => {
  // 可能不稳定的测试
})

// 或者使用注释标记
// @flaky
it('should work sometimes', () => {
  // 不稳定的测试
})
```

## 报告解读

### 成功率阈值
- **绿色 (>80%)**: 稳定测试
- **黄色 (50-80%)**: 轻微不稳定
- **红色 (<50%)**: 严重不稳定

### 报告文件位置
- 综合报告: `tests/reports/flaky/comprehensive_flaky_report.html`
- 后端报告: `backend/tests/reports/flaky/flaky_report.html`
- 前端报告: `frontend/tests/reports/flaky/flaky_report.html`
- 历史数据: `*/flaky_history.json`

## CI/CD集成

### GitHub Actions

项目已配置GitHub Actions自动检测flaky测试：

```yaml
# 定时运行flaky检测
- cron: '0 2 * * *'  # 每天凌晨2点

# 手动触发
# 在commit message中包含 [flaky-check]
```

### 稳定性门禁

```bash
# CI中的稳定性检查
if [ "$STABILITY" < "0.8" ]; then
  echo "⚠️ 测试稳定性低于80%，需要关注flaky测试"
  exit 1
fi
```

## 最佳实践

### 1. 预防Flaky测试

```python
# ❌ 不好的做法
def test_timing_sensitive():
    start = time.time()
    do_something()
    assert time.time() - start < 1.0  # 时间依赖

# ✅ 好的做法
def test_timing_with_tolerance():
    with timeout(5):  # 使用超时而不是精确时间
        result = do_something()
        assert result.is_complete()
```

```javascript
// ❌ 不好的做法
it('should update immediately', async () => {
  await button.click()
  expect(status.text()).toBe('updated')  // 可能还未更新
})

// ✅ 好的做法
it('should update eventually', async () => {
  await button.click()
  await waitFor(() => {
    expect(status.text()).toBe('updated')
  })
})
```

### 2. 处理外部依赖

```python
# ✅ 使用mock避免外部依赖
@patch('requests.get')
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {'status': 'ok'}
    result = call_external_api()
    assert result['status'] == 'ok'
```

### 3. 避免竞态条件

```python
# ✅ 使用适当的同步机制
def test_concurrent_access():
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(worker_function) for _ in range(2)]
        results = [f.result() for f in futures]
        assert all(r.success for r in results)
```

### 4. 环境隔离

```python
# ✅ 每个测试使用独立的环境
def test_with_clean_state():
    with temporary_database():
        # 测试逻辑
        pass
```

## 故障排除

### 常见Flaky测试原因

1. **时间依赖**: 测试依赖特定的执行时间
2. **竞态条件**: 多线程或异步操作的时序问题
3. **外部依赖**: 网络、数据库、文件系统等外部资源
4. **环境变量**: 测试环境的配置差异
5. **内存/资源**: 系统资源不足导致的随机失败
6. **测试顺序**: 测试之间的相互影响

### 调试技巧

```bash
# 1. 多次运行单个测试
pytest tests/test_flaky.py::test_unstable -v --tb=short

# 2. 启用详细日志
pytest --log-cli-level=DEBUG

# 3. 使用稳定性检查
python scripts/flaky_test_manager.py --action stability --iterations 20

# 4. 查看历史数据
cat tests/reports/flaky/flaky_history.json | jq '.test_results["test_name"]'
```

### 修复策略

1. **增加等待时间**: 使用`time.sleep()`或`await`
2. **使用重试装饰器**: `@retry(times=3, delay=1)`
3. **改进断言**: 使用范围断言而不是精确值
4. **Mock外部依赖**: 使用`unittest.mock`或`vi.mock()`
5. **环境清理**: 确保测试后清理状态

## 监控和维护

### 定期检查

```bash
# 每周运行稳定性检查
crontab -e
0 2 * * 1 cd /path/to/project && make flaky-stability
```

### 报告审查

1. 每周审查flaky测试报告
2. 优先修复成功率<50%的测试
3. 考虑删除无法修复的测试
4. 更新测试策略和最佳实践

### 团队协作

1. 在代码审查中关注测试稳定性
2. 分享flaky测试修复经验
3. 建立测试质量指标
4. 定期培训团队成员

## 扩展功能

### 自定义Reporter

```python
# 自定义pytest reporter
class CustomFlakyReporter:
    def pytest_runtest_logreport(self, report):
        if report.when == 'call':
            # 自定义报告逻辑
            pass
```

### 集成通知

```python
# 发送Slack通知
def send_flaky_alert(flaky_tests):
    if len(flaky_tests) > 5:
        slack_webhook.send({
            'text': f'⚠️ 发现{len(flaky_tests)}个flaky测试'
        })
```

### 数据分析

```python
# 分析flaky测试趋势
import pandas as pd
import matplotlib.pyplot as plt

def analyze_flaky_trends(history_data):
    df = pd.DataFrame(history_data)
    df['success_rate'] = df['passed'] / df['total']
    df.plot(x='date', y='success_rate')
    plt.savefig('flaky_trends.png')
```

## 参考资源

- [Google Testing Blog - Flaky Tests](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Martin Fowler - Eradicating Non-Determinism in Tests](https://martinfowler.com/articles/nonDeterminism.html)