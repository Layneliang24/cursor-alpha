"""
简单的测试文件，用于验证覆盖率功能
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class SimpleTest(TestCase):
    """简单的测试类"""
    
    def test_basic_functionality(self):
        """测试基本功能"""
        self.assertTrue(True)
        self.assertEqual(1 + 1, 2)
    
    def test_user_creation(self):
        """测试用户创建"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_string_operations(self):
        """测试字符串操作"""
        text = "Hello, World!"
        self.assertEqual(len(text), 13)
        self.assertIn("Hello", text)
        self.assertTrue(text.startswith("Hello"))
        self.assertTrue(text.endswith("!"))
    
    def test_list_operations(self):
        """测试列表操作"""
        numbers = [1, 2, 3, 4, 5]
        self.assertEqual(len(numbers), 5)
        self.assertEqual(sum(numbers), 15)
        self.assertEqual(max(numbers), 5)
        self.assertEqual(min(numbers), 1)
        
        # 测试列表方法
        numbers.append(6)
        self.assertEqual(len(numbers), 6)
        self.assertEqual(numbers[-1], 6)
        
        numbers.reverse()
        self.assertEqual(numbers[0], 6)
        self.assertEqual(numbers[-1], 1)
    
    def test_dict_operations(self):
        """测试字典操作"""
        data = {
            'name': 'Test',
            'age': 25,
            'city': 'Beijing'
        }
        self.assertEqual(len(data), 3)
        self.assertEqual(data['name'], 'Test')
        self.assertEqual(data['age'], 25)
        self.assertIn('city', data)
        
        # 测试字典方法
        data['country'] = 'China'
        self.assertEqual(len(data), 4)
        self.assertEqual(data['country'], 'China')
        
        keys = list(data.keys())
        self.assertEqual(len(keys), 4)
        self.assertIn('name', keys)
