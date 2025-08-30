"""
AI助教核心服务

提供场景生成、用法纠错、学习建议、个性化推荐等核心AI助教功能
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.cache import cache

from .manager import AIServiceManager
from .cost_monitor import CostMonitor
from .rate_limiter import RateLimiter
from .quality_assessor import ResponseQualityAssessor
from ..adapters.base import AIMessage, MessageRole, AIResponse

logger = logging.getLogger(__name__)


class TutorFunctionType(Enum):
    """AI助教功能类型"""
    SCENARIO_GENERATION = "scenario_generation"        # 场景生成
    USAGE_CORRECTION = "usage_correction"              # 用法纠错
    LEARNING_SUGGESTION = "learning_suggestion"        # 学习建议
    PERSONALIZED_RECOMMENDATION = "personalized_recommendation"  # 个性化推荐
    EXPRESSION_EXPLANATION = "expression_explanation"   # 表达解释
    PRACTICE_GUIDANCE = "practice_guidance"            # 练习指导


@dataclass
class TutorRequest:
    """AI助教请求数据"""
    user: User
    function_type: TutorFunctionType
    content: str
    context: Optional[Dict[str, Any]] = None
    user_level: Optional[str] = None  # beginner, intermediate, advanced
    target_language: str = "en"
    source_language: str = "zh"
    
    
@dataclass
class TutorResponse:
    """AI助教响应数据"""
    function_type: TutorFunctionType
    content: str
    suggestions: List[str]
    metadata: Dict[str, Any]
    quality_score: Optional[float] = None
    response_time: Optional[float] = None
    cost: Optional[float] = None
    

class AITutorService:
    """
    AI助教核心服务类
    
    提供场景生成、用法纠错、学习建议、个性化推荐等功能
    """
    
    def __init__(self):
        """初始化AI助教服务"""
        self.ai_manager = AIServiceManager()
        self.cost_monitor = CostMonitor()
        self.rate_limiter = RateLimiter()
        self.quality_assessor = ResponseQualityAssessor()
        
        # 功能映射
        self.function_handlers = {
            TutorFunctionType.SCENARIO_GENERATION: self._generate_scenario,
            TutorFunctionType.USAGE_CORRECTION: self._correct_usage,
            TutorFunctionType.LEARNING_SUGGESTION: self._suggest_learning,
            TutorFunctionType.PERSONALIZED_RECOMMENDATION: self._recommend_personalized,
            TutorFunctionType.EXPRESSION_EXPLANATION: self._explain_expression,
            TutorFunctionType.PRACTICE_GUIDANCE: self._guide_practice,
        }
        
        # 性能缓存配置
        self.cache_timeout = getattr(settings, 'AI_TUTOR_CACHE_TIMEOUT', 3600)
        
        logger.info("AI助教服务已初始化")
    
    async def process_request(self, request: TutorRequest) -> TutorResponse:
        """
        处理AI助教请求
        
        Args:
            request: 助教请求数据
            
        Returns:
            助教响应数据
        """
        start_time = time.time()
        
        try:
            # 速率限制检查
            if not await self._check_rate_limit(request.user, request.function_type):
                raise ValueError("请求频率超限，请稍后再试")
            
            # 检查缓存
            cache_key = self._generate_cache_key(request)
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.info(f"命中缓存: {request.function_type.value}")
                return cached_response
            
            # 获取处理函数
            handler = self.function_handlers.get(request.function_type)
            if not handler:
                raise ValueError(f"不支持的功能类型: {request.function_type}")
            
            # 执行AI请求
            response_content, ai_response = await handler(request)
            
            # 计算成本
            cost = await self.cost_monitor.calculate_cost(ai_response)
            
            # 质量评估
            quality_score = await self.quality_assessor.assess_response(
                request.content, response_content, request.context
            )
            
            # 构建响应
            response = TutorResponse(
                function_type=request.function_type,
                content=response_content,
                suggestions=self._extract_suggestions(response_content, request.function_type),
                metadata={
                    'model': ai_response.model,
                    'provider': ai_response.provider,
                    'usage': ai_response.usage,
                    'user_level': request.user_level,
                    'target_language': request.target_language,
                    'source_language': request.source_language,
                },
                quality_score=quality_score,
                response_time=time.time() - start_time,
                cost=cost
            )
            
            # 记录成本
            await self.cost_monitor.record_usage(
                user=request.user,
                function_type=request.function_type.value,
                cost=cost,
                tokens=ai_response.usage.get('total_tokens', 0) if ai_response.usage else 0,
                response=ai_response
            )
            
            # 缓存响应
            cache.set(cache_key, response, self.cache_timeout)
            
            logger.info(f"AI助教请求完成: {request.function_type.value}, 耗时: {response.response_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"AI助教请求失败: {request.function_type.value}, 错误: {e}")
            # 返回错误响应
            return TutorResponse(
                function_type=request.function_type,
                content=f"处理失败: {str(e)}",
                suggestions=[],
                metadata={'error': str(e)},
                response_time=time.time() - start_time
            )
    
    async def _generate_scenario(self, request: TutorRequest) -> Tuple[str, AIResponse]:
        """生成使用场景"""
        prompt = self._build_scenario_prompt(request)
        return await self._call_ai(prompt, request)
    
    async def _correct_usage(self, request: TutorRequest) -> Tuple[str, AIResponse]:
        """纠正用法错误"""
        prompt = self._build_correction_prompt(request)
        return await self._call_ai(prompt, request)
    
    async def _suggest_learning(self, request: TutorRequest) -> Tuple[str, AIResponse]:
        """提供学习建议"""
        prompt = self._build_suggestion_prompt(request)
        return await self._call_ai(prompt, request)
    
    async def _recommend_personalized(self, request: TutorRequest) -> Tuple[str, AIResponse]:
        """个性化推荐"""
        prompt = self._build_recommendation_prompt(request)
        return await self._call_ai(prompt, request)
    
    async def _explain_expression(self, request: TutorRequest) -> Tuple[str, AIResponse]:
        """解释表达含义"""
        prompt = self._build_explanation_prompt(request)
        return await self._call_ai(prompt, request)
    
    async def _guide_practice(self, request: TutorRequest) -> Tuple[str, AIResponse]:
        """指导练习"""
        prompt = self._build_practice_prompt(request)
        return await self._call_ai(prompt, request)
    
    async def _call_ai(self, prompt: str, request: TutorRequest) -> Tuple[str, AIResponse]:
        """调用AI服务"""
        messages = [
            AIMessage(role=MessageRole.SYSTEM, content=self._get_system_prompt(request)),
            AIMessage(role=MessageRole.USER, content=prompt)
        ]
        
        response = await self.ai_manager.generate_response(messages)
        return response.content, response
    
    def _build_scenario_prompt(self, request: TutorRequest) -> str:
        """构建场景生成提示词"""
        expression = request.content
        level = request.user_level or "intermediate"
        
        return f"""请为表达"{expression}"生成3个实用的使用场景。

要求：
1. 场景要符合{level}水平学习者的理解能力
2. 提供具体的对话或描述情境
3. 包含该表达的自然使用方式
4. 解释在该场景中使用的原因

请以JSON格式返回：
{{
    "scenarios": [
        {{
            "title": "场景标题",
            "context": "场景描述",
            "dialogue": "对话示例",
            "explanation": "使用说明"
        }}
    ]
}}"""

    def _build_correction_prompt(self, request: TutorRequest) -> str:
        """构建用法纠错提示词"""
        user_text = request.content
        level = request.user_level or "intermediate"
        
        return f"""请分析以下文本中的用法错误并提供纠正建议：

用户文本："{user_text}"
用户水平：{level}

请检查：
1. 语法错误
2. 地道表达使用错误
3. 词汇搭配问题
4. 语序问题

请以JSON格式返回：
{{
    "corrections": [
        {{
            "error": "错误内容",
            "correction": "正确表达",
            "explanation": "错误原因和改正说明",
            "type": "错误类型"
        }}
    ],
    "overall_score": "整体评分(1-10)",
    "improvement_tips": ["改进建议"]
}}"""

    def _build_suggestion_prompt(self, request: TutorRequest) -> str:
        """构建学习建议提示词"""
        context = request.context or {}
        level = request.user_level or "intermediate"
        
        learning_history = context.get('learning_history', '')
        weak_areas = context.get('weak_areas', [])
        
        return f"""基于用户的学习情况，提供个性化学习建议：

用户水平：{level}
学习历史：{learning_history}
薄弱环节：{', '.join(weak_areas)}
当前关注：{request.content}

请提供：
1. 具体的学习计划建议
2. 推荐的学习资源
3. 练习重点
4. 学习策略建议

请以JSON格式返回：
{{
    "learning_plan": {{
        "short_term": ["短期目标"],
        "long_term": ["长期目标"]
    }},
    "resources": ["推荐资源"],
    "practice_focus": ["练习重点"],
    "strategies": ["学习策略"]
}}"""

    def _build_recommendation_prompt(self, request: TutorRequest) -> str:
        """构建个性化推荐提示词"""
        context = request.context or {}
        level = request.user_level or "intermediate"
        
        interests = context.get('interests', [])
        learned_expressions = context.get('learned_expressions', [])
        
        return f"""基于用户兴趣和已学内容，推荐相关的地道表达：

用户水平：{level}
兴趣领域：{', '.join(interests)}
已学表达：{', '.join(learned_expressions[:10])}  # 最近10个
当前表达：{request.content}

请推荐：
1. 相关的地道表达
2. 同类场景的其他表达
3. 进阶表达
4. 实用短语

请以JSON格式返回：
{{
    "related_expressions": [
        {{
            "expression": "表达内容",
            "meaning": "含义解释",
            "usage": "使用场合",
            "difficulty": "难度等级",
            "reason": "推荐理由"
        }}
    ]
}}"""

    def _build_explanation_prompt(self, request: TutorRequest) -> str:
        """构建表达解释提示词"""
        expression = request.content
        level = request.user_level or "intermediate"
        
        return f"""请详细解释地道表达"{expression}"：

用户水平：{level}

请包含：
1. 字面含义和实际含义
2. 使用场合和语境
3. 语法结构分析
4. 相似表达对比
5. 使用注意事项

请以JSON格式返回：
{{
    "literal_meaning": "字面含义",
    "actual_meaning": "实际含义",
    "usage_context": "使用语境",
    "grammar_analysis": "语法分析",
    "similar_expressions": ["相似表达"],
    "usage_notes": ["使用注意事项"],
    "examples": ["使用示例"]
}}"""

    def _build_practice_prompt(self, request: TutorRequest) -> str:
        """构建练习指导提示词"""
        expression = request.content
        level = request.user_level or "intermediate"
        
        return f"""为表达"{expression}"设计练习活动：

用户水平：{level}

请设计：
1. 填空练习
2. 造句练习
3. 情境对话练习
4. 识别练习

请以JSON格式返回：
{{
    "exercises": [
        {{
            "type": "练习类型",
            "title": "练习标题",
            "content": "练习内容",
            "answer": "参考答案",
            "tips": "练习提示"
        }}
    ]
}}"""

    def _get_system_prompt(self, request: TutorRequest) -> str:
        """获取系统提示词"""
        return f"""你是一位专业的{request.target_language}语言AI助教，专门帮助{request.source_language}母语者学习地道表达。

你的特点：
- 耐心、友善、专业
- 能够根据学习者水平调整教学方式
- 擅长解释语言细节和文化背景
- 提供实用的学习建议

请用{request.source_language}回答，确保解释清晰易懂。"""

    def _extract_suggestions(self, content: str, function_type: TutorFunctionType) -> List[str]:
        """从响应中提取建议"""
        # 这里可以实现更复杂的建议提取逻辑
        suggestions = []
        
        if function_type == TutorFunctionType.SCENARIO_GENERATION:
            suggestions.append("尝试在日常对话中使用这些场景")
            suggestions.append("注意语调和语境的匹配")
        elif function_type == TutorFunctionType.USAGE_CORRECTION:
            suggestions.append("重点关注语法结构")
            suggestions.append("多做相关练习")
        elif function_type == TutorFunctionType.LEARNING_SUGGESTION:
            suggestions.append("制定学习计划")
            suggestions.append("定期复习和练习")
        
        return suggestions
    
    async def _check_rate_limit(self, user: User, function_type: TutorFunctionType) -> bool:
        """检查速率限制"""
        return await self.rate_limiter.check_limit(
            user_id=user.id,
            action=f"tutor_{function_type.value}",
            window_seconds=3600,  # 1小时窗口
            max_requests=50  # 每小时最多50次请求
        )
    
    def _generate_cache_key(self, request: TutorRequest) -> str:
        """生成缓存键"""
        content_hash = hash(request.content)
        context_hash = hash(str(request.context)) if request.context else 0
        
        return f"ai_tutor:{request.function_type.value}:{content_hash}:{context_hash}:{request.user_level}"
    
    async def get_usage_statistics(self, user: User, days: int = 30) -> Dict[str, Any]:
        """获取用户使用统计"""
        return await self.cost_monitor.get_user_statistics(user, days)
    
    async def get_quality_report(self, user: User = None, days: int = 30) -> Dict[str, Any]:
        """获取质量报告"""
        return await self.quality_assessor.get_quality_report(user, days)
