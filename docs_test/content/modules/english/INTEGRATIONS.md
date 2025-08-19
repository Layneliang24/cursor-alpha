# 英语学习模块整合附录

本附录收纳与英语学习模块相关的方案/重构/集成计划，来源于历史零散文档，便于集中查阅与维护。

## A. 智能打字练习功能集成设计（原 ENGLISH_TYPING_INTEGRATION_DESIGN.md）
- 项目标的、功能需求、数据模型（Word/TypingSession/UserTypingStats/TypingPracticeRecord/DailyPracticeStats/KeyErrorStats）
- 数据分析页面结构、可视化组件、聚合服务接口
- API 端点（exercise_heatmap/word_heatmap/wpm_trend/accuracy_trend/key_error_stats）
- 前端页面与组件骨架（DataAnalysis.vue + 各图表组件）
- 性能优化、指标定义与分阶段实施计划

## B. 智能打字练习重构文档（原 TYPING_PRACTICE_REFACTOR.md）
- 界面与交互（按任意键开始、自动发音、实时拼写检查、快捷键）
- 有道发音 API、键盘声音 Hook、状态管理要点
- 文件结构与使用说明、已实现与待优化清单、性能与总结

## C. Qwerty Learn 集成计划（原 QWERTY_LEARN_INTEGRATION_PLAN.md）
- 价值分析与整体架构（智能词汇学习、SM-2 算法、学习分析、个性化推荐）
- 功能模块与数据模型、SM-2 复习算法核心、学习分析与推荐引擎骨架
- 分阶段实施计划、成本效益与风险评估、成功指标与参考资料

维护说明：
- 以上三份文档的详细内容保留在对应模块主文档与本附录中要点索引；如需细节，请参考模块主文档或提交变更同步至此附录。
