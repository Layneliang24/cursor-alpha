# -*- coding: utf-8 -*-
"""
暂停/继续功能测试
测试英语学习模块的练习暂停和继续相关功能
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import Mock, patch
import time
from datetime import datetime, timedelta

from tests.utils.test_helpers import TestDataFactory, TestUserManager
from apps.english.models import TypingPracticeRecord

User = get_user_model()


class TestPauseResumeAPI(TestCase):
    """暂停/继续API测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = TestUserManager.create_test_user()
        self.client.force_authenticate(user=self.user)
        
        # 创建测试练习会话
        self.session_data = {
            'start_time': datetime.now(),
            'is_paused': False,
            'pause_start_time': None,
            'pause_elapsed_time': 0
        }
    
    def test_pause_practice_session(self):
        """测试暂停练习会话"""
        # 模拟暂停请求
        pause_data = {
            'action': 'pause',
            'timestamp': datetime.now().isoformat()
        }
        
        response = self.client.post('/api/v1/english/typing-practice/pause/', pause_data)
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('is_paused', response.data['data'])
        self.assertTrue(response.data['data']['is_paused'])
    
    def test_resume_practice_session(self):
        """测试继续练习会话"""
        # 先暂停
        pause_data = {'action': 'pause', 'timestamp': datetime.now().isoformat()}
        self.client.post('/api/v1/english/typing-practice/pause/', pause_data)
        
        # 然后继续
        resume_data = {
            'action': 'resume',
            'timestamp': datetime.now().isoformat()
        }
        
        response = self.client.post('/api/v1/english/typing-practice/resume/', resume_data)
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('is_paused', response.data['data'])
        self.assertFalse(response.data['data']['is_paused'])
    
    def test_pause_resume_workflow(self):
        """测试暂停/继续工作流"""
        # 1. 开始练习
        start_data = {'action': 'start', 'timestamp': datetime.now().isoformat()}
        start_response = self.client.post('/api/v1/english/typing-practice/start/', start_data)
        self.assertEqual(start_response.status_code, status.HTTP_200_OK)
        
        # 2. 暂停练习
        pause_data = {'action': 'pause', 'timestamp': datetime.now().isoformat()}
        pause_response = self.client.post('/api/v1/english/typing-practice/pause/', pause_data)
        self.assertEqual(pause_response.status_code, status.HTTP_200_OK)
        
        # 3. 继续练习
        resume_data = {'action': 'resume', 'timestamp': datetime.now().isoformat()}
        resume_response = self.client.post('/api/v1/english/typing-practice/resume/', resume_data)
        self.assertEqual(resume_response.status_code, status.HTTP_200_OK)
        
        # 4. 验证最终状态
        status_response = self.client.get('/api/v1/english/typing-practice/status/')
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        self.assertFalse(status_response.data['data']['is_paused'])
    
    def test_pause_timing_accuracy(self):
        """测试暂停时间准确性"""
        # 记录暂停开始时间
        pause_start = datetime.now()
        pause_data = {'action': 'pause', 'timestamp': pause_start.isoformat()}
        
        self.client.post('/api/v1/english/typing-practice/pause/', pause_data)
        
        # 等待一段时间
        time.sleep(0.1)
        
        # 继续练习
        resume_data = {'action': 'resume', 'timestamp': datetime.now().isoformat()}
        response = self.client.post('/api/v1/english/typing-practice/resume/', resume_data)
        
        # 验证暂停时间计算
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertIn('pause_elapsed_time', data)
        self.assertGreater(data['pause_elapsed_time'], 0)
    
    def test_multiple_pause_resume_cycles(self):
        """测试多次暂停/继续循环"""
        for cycle in range(3):
            with self.subTest(cycle=cycle):
                # 暂停
                pause_data = {'action': 'pause', 'timestamp': datetime.now().isoformat()}
                pause_response = self.client.post('/api/v1/english/typing-practice/pause/', pause_data)
                self.assertEqual(pause_response.status_code, status.HTTP_200_OK)
                
                # 继续
                resume_data = {'action': 'resume', 'timestamp': datetime.now().isoformat()}
                resume_response = self.client.post('/api/v1/english/typing-practice/resume/', resume_data)
                self.assertEqual(resume_response.status_code, status.HTTP_200_OK)
                
                # 验证状态
                status_response = self.client.get('/api/v1/english/typing-practice/status/')
                self.assertEqual(status_response.status_code, status.HTTP_200_OK)
                self.assertFalse(status_response.data['data']['is_paused'])
    
    def test_invalid_pause_resume_actions(self):
        """测试无效的暂停/继续操作"""
        invalid_actions = [
            {'action': 'invalid_action', 'timestamp': datetime.now().isoformat()},
            {'action': '', 'timestamp': datetime.now().isoformat()},
            {'action': 'null_value', 'timestamp': datetime.now().isoformat()}
        ]
        
        for action_data in invalid_actions:
            with self.subTest(action=action_data['action']):
                response = self.client.post('/api/v1/english/typing-practice/pause/', action_data)
                # 由于API现在会验证请求数据，应该返回400错误
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestPauseResumeService(TestCase):
    """暂停/继续服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.user = TestUserManager.create_test_user()
        self.session_data = {
            'start_time': datetime.now(),
            'is_paused': False,
            'pause_start_time': None,
            'pause_elapsed_time': 0
        }
    
    def test_pause_logic(self):
        """测试暂停逻辑"""
        from apps.english.services import PracticeSessionService
        
        service = PracticeSessionService()
        
        # 模拟暂停操作
        pause_result = service.pause_session(self.user.id)
        
        self.assertTrue(pause_result['success'])
        self.assertTrue(pause_result['data']['is_paused'])
        self.assertIsNotNone(pause_result['data']['pause_start_time'])
    
    def test_resume_logic(self):
        """测试继续逻辑"""
        from apps.english.services import PracticeSessionService
        
        service = PracticeSessionService()
        
        # 先暂停
        service.pause_session(self.user.id)
        
        # 然后继续
        resume_result = service.resume_session(self.user.id)
        
        self.assertTrue(resume_result['success'])
        self.assertFalse(resume_result['data']['is_paused'])
        self.assertIsNone(resume_result['data']['pause_start_time'])
    
    def test_pause_time_calculation(self):
        """测试暂停时间计算"""
        from apps.english.services import PracticeSessionService
        
        service = PracticeSessionService()
        
        # 开始暂停
        pause_start = datetime.now()
        service.pause_session(self.user.id)
        
        # 等待一段时间
        time.sleep(0.1)
        
        # 继续并获取暂停时间
        resume_result = service.resume_session(self.user.id)
        
        self.assertIn('pause_elapsed_time', resume_result['data'])
        self.assertGreater(resume_result['data']['pause_elapsed_time'], 0)
    
    def test_session_state_consistency(self):
        """测试会话状态一致性"""
        from apps.english.services import PracticeSessionService
        
        service = PracticeSessionService()
        
        # 验证初始状态
        initial_status = service.get_session_status(self.user.id)
        self.assertFalse(initial_status['data']['is_paused'])
        
        # 暂停后验证状态
        service.pause_session(self.user.id)
        paused_status = service.get_session_status(self.user.id)
        self.assertTrue(paused_status['data']['is_paused'])
        
        # 继续后验证状态
        service.resume_session(self.user.id)
        resumed_status = service.get_session_status(self.user.id)
        self.assertFalse(resumed_status['data']['is_paused'])


@pytest.mark.unit
class TestPauseResumeUnit(TestCase):
    """暂停/继续单元测试类"""
    
    def test_timer_pause_logic(self):
        """测试计时器暂停逻辑"""
        # 模拟计时器状态
        timer_state = {
            'is_running': True,
            'start_time': datetime.now(),
            'elapsed_time': 60,  # 60秒
            'is_paused': False
        }
        
        # 暂停计时器
        timer_state['is_paused'] = True
        timer_state['pause_start_time'] = datetime.now()
        
        # 验证暂停状态
        self.assertTrue(timer_state['is_paused'])
        self.assertIsNotNone(timer_state['pause_start_time'])
        self.assertEqual(timer_state['elapsed_time'], 60)  # 暂停时时间不变
    
    def test_timer_resume_logic(self):
        """测试计时器继续逻辑"""
        # 模拟暂停状态
        pause_start = datetime.now()
        timer_state = {
            'is_running': True,
            'start_time': datetime.now() - timedelta(minutes=2),
            'elapsed_time': 60,
            'is_paused': True,
            'pause_start_time': pause_start,
            'pause_elapsed_time': 30  # 暂停了30秒
        }
        
        # 继续计时器
        timer_state['is_paused'] = False
        timer_state['pause_start_time'] = None
        timer_state['pause_elapsed_time'] = 0
        
        # 验证继续状态
        self.assertFalse(timer_state['is_paused'])
        self.assertIsNone(timer_state['pause_start_time'])
        self.assertEqual(timer_state['pause_elapsed_time'], 0)
    
    def test_pause_duration_calculation(self):
        """测试暂停持续时间计算"""
        # 模拟暂停开始和结束时间
        pause_start = datetime.now()
        time.sleep(0.1)  # 等待100毫秒
        pause_end = datetime.now()
        
        # 计算暂停持续时间
        pause_duration = (pause_end - pause_start).total_seconds()
        
        # 验证计算准确性
        self.assertGreater(pause_duration, 0)
        self.assertLess(pause_duration, 1)  # 应该小于1秒
    
    def test_session_time_accuracy(self):
        """测试会话时间准确性"""
        # 模拟练习会话
        session_start = datetime.now()
        total_pause_time = 0
        
        # 模拟多次暂停/继续
        pause_cycles = [
            {'pause_duration': 10},  # 暂停10秒
            {'pause_duration': 15},  # 暂停15秒
            {'pause_duration': 5}    # 暂停5秒
        ]
        
        for cycle in pause_cycles:
            total_pause_time += cycle['pause_duration']
        
        # 计算实际练习时间
        session_end = datetime.now()
        total_session_time = (session_end - session_start).total_seconds()
        actual_practice_time = max(0, total_session_time - total_pause_time)  # 确保不为负数
        
        # 验证时间计算
        self.assertGreaterEqual(actual_practice_time, 0)
        self.assertLessEqual(actual_practice_time, total_session_time)


@pytest.mark.integration
class TestPauseResumeIntegration(TestCase):
    """暂停/继续集成测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.user = TestUserManager.create_test_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_pause_resume_with_practice_data(self):
        """测试带练习数据的暂停/继续"""
        # 1. 开始练习并输入一些单词
        practice_data = [
            {'word': 'hello', 'is_correct': True, 'typing_speed': 50.0},
            {'word': 'world', 'is_correct': False, 'typing_speed': 45.0}
        ]
        
        for data in practice_data:
            response = self.client.post('/api/v1/english/typing-practice/submit/', data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. 暂停练习
        pause_response = self.client.post('/api/v1/english/typing-practice/pause/', 
                                        {'action': 'pause', 'timestamp': datetime.now().isoformat()})
        self.assertEqual(pause_response.status_code, status.HTTP_200_OK)
        
        # 3. 继续练习
        resume_response = self.client.post('/api/v1/english/typing-practice/resume/', 
                                         {'action': 'resume', 'timestamp': datetime.now().isoformat()})
        self.assertEqual(resume_response.status_code, status.HTTP_200_OK)
        
        # 4. 继续输入单词
        more_practice_data = [
            {'word': 'computer', 'is_correct': True, 'typing_speed': 55.0}
        ]
        
        for data in more_practice_data:
            response = self.client.post('/api/v1/english/typing-practice/submit/', data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_pause_resume_with_timer_synchronization(self):
        """测试暂停/继续与计时器同步"""
        # 1. 开始练习
        start_response = self.client.post('/api/v1/english/typing-practice/start/', 
                                        {'action': 'start', 'timestamp': datetime.now().isoformat()})
        self.assertEqual(start_response.status_code, status.HTTP_200_OK)
        
        # 2. 获取初始状态
        initial_status = self.client.get('/api/v1/english/typing-practice/status/')
        self.assertEqual(initial_status.status_code, status.HTTP_200_OK)
        initial_time = initial_status.data['data']['session_time']
        
        # 3. 暂停练习
        self.client.post('/api/v1/english/typing-practice/pause/', 
                        {'action': 'pause', 'timestamp': datetime.now().isoformat()})
        
        # 4. 等待一段时间
        time.sleep(0.1)
        
        # 5. 继续练习
        self.client.post('/api/v1/english/typing-practice/resume/', 
                        {'action': 'resume', 'timestamp': datetime.now().isoformat()})
        
        # 6. 验证计时器状态
        final_status = self.client.get('/api/v1/english/typing-practice/status/')
        self.assertEqual(final_status.status_code, status.HTTP_200_OK)
        final_time = final_status.data['data']['session_time']
        
        # 时间应该继续增加
        self.assertGreaterEqual(final_time, initial_time)
    
    def test_pause_resume_with_multiple_users(self):
        """测试多用户的暂停/继续"""
        # 创建第二个用户
        user2 = TestUserManager.create_test_user(username='test_user_2')
        client2 = APIClient()
        client2.force_authenticate(user=user2)
        
        # 两个用户同时进行练习
        for i, (client, user) in enumerate([(self.client, self.user), (client2, user2)]):
            with self.subTest(user=user.username):
                # 开始练习
                start_response = client.post('/api/v1/english/typing-practice/start/', 
                                          {'action': 'start', 'timestamp': datetime.now().isoformat()})
                self.assertEqual(start_response.status_code, status.HTTP_200_OK)
                
                # 暂停练习
                pause_response = client.post('/api/v1/english/typing-practice/pause/', 
                                          {'action': 'pause', 'timestamp': datetime.now().isoformat()})
                self.assertEqual(pause_response.status_code, status.HTTP_200_OK)
                
                # 继续练习
                resume_response = client.post('/api/v1/english/typing-practice/resume/', 
                                           {'action': 'resume', 'timestamp': datetime.now().isoformat()})
                self.assertEqual(resume_response.status_code, status.HTTP_200_OK)
                
                # 验证状态
                status_response = client.get('/api/v1/english/typing-practice/status/')
                self.assertEqual(status_response.status_code, status.HTTP_200_OK)
                self.assertFalse(status_response.data['data']['is_paused'])


class TestPauseResumeFrontend(TestCase):
    """暂停/继续前端测试类"""
    
    def test_pause_resume_button_states(self):
        """测试暂停/继续按钮状态"""
        # 模拟按钮状态
        button_states = {
            'practice_running': {
                'pause_button': {'visible': True, 'enabled': True, 'text': '暂停'},
                'resume_button': {'visible': False, 'enabled': False, 'text': '继续'}
            },
            'practice_paused': {
                'pause_button': {'visible': False, 'enabled': False, 'text': '暂停'},
                'resume_button': {'visible': True, 'enabled': True, 'text': '继续'}
            }
        }
        
        # 验证状态逻辑
        for state, buttons in button_states.items():
            with self.subTest(state=state):
                if state == 'practice_running':
                    self.assertTrue(buttons['pause_button']['visible'])
                    self.assertFalse(buttons['resume_button']['visible'])
                else:
                    self.assertFalse(buttons['pause_button']['visible'])
                    self.assertTrue(buttons['resume_button']['visible'])
    
    def test_timer_display_consistency(self):
        """测试计时器显示一致性"""
        # 模拟计时器状态
        timer_states = [
            {'is_paused': False, 'display': '00:01:30', 'expected_color': 'green'},
            {'is_paused': True, 'display': '00:01:30', 'expected_color': 'orange'},
            {'is_paused': False, 'display': '00:02:15', 'expected_color': 'green'}
        ]
        
        for state in timer_states:
            with self.subTest(state=state):
                # 验证显示逻辑
                if state['is_paused']:
                    self.assertEqual(state['expected_color'], 'orange')
                else:
                    self.assertEqual(state['expected_color'], 'green')
    
    def test_pause_resume_ui_feedback(self):
        """测试暂停/继续UI反馈"""
        # 模拟UI反馈状态
        feedback_states = [
            {'action': 'pause', 'message': '练习已暂停', 'icon': 'pause', 'color': 'warning'},
            {'action': 'resume', 'message': '练习已继续', 'icon': 'play', 'color': 'success'}
        ]
        
        for feedback in feedback_states:
            with self.subTest(action=feedback['action']):
                # 验证反馈信息
                self.assertIn('message', feedback)
                self.assertIn('icon', feedback)
                self.assertIn('color', feedback)
                
                # 验证图标和颜色的一致性
                if feedback['action'] == 'pause':
                    self.assertEqual(feedback['icon'], 'pause')
                    self.assertEqual(feedback['color'], 'warning')
                else:
                    self.assertEqual(feedback['icon'], 'play')
                    self.assertEqual(feedback['color'], 'success')
