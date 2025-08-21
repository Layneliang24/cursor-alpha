#!/usr/bin/env python
"""
热重载功能测试文件
修改此文件后，Django 服务器应该自动重载
"""

def test_function():
    """测试函数 - 修改这个函数的返回值来测试热重载"""
    return "🔥 热重载测试 - 服务器应该已经自动重载了！"

def another_test_function():
    """另一个测试函数"""
    return "这是另一个测试函数 - 热重载工作正常！"

def new_function():
    """新增的函数 - 测试热重载是否检测到新文件"""
    return "这是一个新添加的函数 - 热重载检测成功！"

def hot_reload_status():
    """热重载状态检查"""
    return "✅ 热重载功能已启用并正常工作"

if __name__ == "__main__":
    print("🔥 热重载测试文件")
    print("📝 修改此文件后，Django 服务器应该自动重载")
    print("✅ 当前返回值:", test_function())
    print("🆕 新函数:", new_function())
    print("📊 状态:", hot_reload_status())
