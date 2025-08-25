#!/usr/bin/env python
"""
测试月历热力图布局修复
验证是否从6行7列改为5行7列
"""

import pytest
from datetime import datetime
from django.contrib.auth import get_user_model
from apps.english.services import DataAnalysisService

User = get_user_model()

def test_calendar_layout():
    """测试月历热力图布局"""
    print("=== 测试月历热力图布局修复 ===")
    
    # 获取当前月份
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    print(f"测试月份: {year}年{month}月")
    
    # 获取服务实例
    service = DataAnalysisService()
    
    # 获取第一个用户
    user = User.objects.first()
    if not user:
        print("❌ 没有找到用户，无法测试")
        return
    
    try:
        # 获取月历数据
        calendar_data = service.get_monthly_calendar_data(user.id, year, month)
        
        # 检查weeks_data结构
        weeks_data = calendar_data.get('weeks_data', [])
        print(f"总周数: {len(weeks_data)}")
        
        # 验证周数
        if len(weeks_data) == 5:
            print("✅ 修复成功：现在是5行7列布局")
        elif len(weeks_data) == 6:
            print("❌ 修复失败：仍然是6行7列布局")
        else:
            print(f"⚠️  异常：周数为{len(weeks_data)}")
        
        # 显示每周的天数
        for i, week in enumerate(weeks_data):
            print(f"第{i+1}周: {len(week)}天")
        
        # 计算总天数
        total_days = sum(len(week) for week in weeks_data)
        print(f"总天数: {total_days}")
        
        # 验证天数合理性
        if total_days == 35:  # 5周 × 7天
            print("✅ 总天数正确 (35天)")
        elif total_days == 42:  # 6周 × 7天
            print("❌ 总天数过多 (42天)")
        else:
            print(f"⚠️  异常总天数: {total_days}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_calendar_layout()