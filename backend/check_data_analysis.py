#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.english.models import TypingPracticeRecord, TypingPracticeSession
from apps.english.services import DataAnalysisService
from apps.users.models import User

def main():
    # 获取testuser
    try:
        user = User.objects.get(username='testuser')
        print(f"用户: {user.username} (ID: {user.id})")
    except User.DoesNotExist:
        print("用户testuser不存在")
        return
    
    # 检查TypingPracticeRecord数据
    records = TypingPracticeRecord.objects.filter(user=user).order_by('-created_at')[:10]
    print(f"\n最近10条TypingPracticeRecord记录:")
    for record in records:
        print(f"  {record.created_at} - 单词: {record.word}, 正确: {record.is_correct}, WPM: {record.typing_speed}")
    
    # 检查TypingPracticeSession数据
    sessions = TypingPracticeSession.objects.filter(user=user).order_by('-start_time')[:10]
    print(f"\n最近10条TypingPracticeSession记录:")
    for session in sessions:
        print(f"  {session.start_time} - 日期: {session.session_date}, 单词数: {session.total_words}, 正确率: {session.accuracy_rate}%")
    
    # 测试数据分析服务
    service = DataAnalysisService()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    overview = service.get_data_overview(user.id, start_date, end_date)
    print(f"\n数据概览 (最近30天):")
    print(f"  总练习次数: {overview['total_exercises']}")
    print(f"  总单词数: {overview['total_words']}")
    print(f"  平均WPM: {overview['avg_wpm']}")
    print(f"  平均正确率: {overview['avg_accuracy']}%")
    
    # 检查数据是否真的是静态的
    print(f"\n检查数据时间戳:")
    latest_record = TypingPracticeRecord.objects.filter(user=user).order_by('-created_at').first()
    latest_session = TypingPracticeSession.objects.filter(user=user).order_by('-start_time').first()
    
    if latest_record:
        print(f"  最新记录时间: {latest_record.created_at}")
    if latest_session:
        print(f"  最新会话时间: {latest_session.start_time}")
    
    # 检查是否有重复数据
    total_records = TypingPracticeRecord.objects.filter(user=user).count()
    total_sessions = TypingPracticeSession.objects.filter(user=user).count()
    unique_words = TypingPracticeRecord.objects.filter(user=user).values('word').distinct().count()
    
    print(f"\n数据统计:")
    print(f"  总记录数: {total_records}")
    print(f"  总会话数: {total_sessions}")
    print(f"  不同单词数: {unique_words}")
    
if __name__ == '__main__':
    main()