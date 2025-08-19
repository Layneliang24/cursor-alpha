# 测试覆盖清单（模块 → 子功能）权威版

> 生成时间（UTC）：2025-08-19 10:12:36Z  |  来源：tests 目录扫描  |  说明：☑️ 已有测试覆盖；☐ 未覆盖

## 认证与用户（Auth/Users）
- ☑️ 用户注册 （文件 3；函数≈67）
  - `integration/test_api.py`
  - `regression/auth/test_user_authentication.py`
  - `unit/test_user_auth.py`
- ☑️ 用户登录 （文件 6；函数≈114）
  - `integration/test_api.py`
  - `regression/auth/test_user_authentication.py`
  - `unit/test_article_management.py`
  - `unit/test_news_dashboard.py`
  - `unit/test_user_auth.py`
  - ... 其余 1 个文件
- ☑️ Token 刷新 （文件 1；函数≈25）
  - `regression/auth/test_user_authentication.py`
- ☑️ 用户登出 （文件 3；函数≈67）
  - `integration/test_api.py`
  - `regression/auth/test_user_authentication.py`
  - `unit/test_user_auth.py`
- ☑️ 获取当前用户 （文件 1；函数≈24）
  - `unit/test_user_auth.py`
- ☑️ 用户列表（管理员） （文件 2；函数≈39）
  - `regression/auth/test_permissions.py`
  - `unit/test_user_auth.py`
- ☑️ 用户资料（Profiles） （文件 3；函数≈64）
  - `regression/auth/test_permissions.py`
  - `regression/auth/test_user_authentication.py`
  - `unit/test_user_auth.py`
- ☑️ 权限校验-模型权限 （文件 5；函数≈76）
  - `integration/test_api.py`
  - `regression/auth/test_permissions.py`
  - `unit/test_news_dashboard.py`
  - `unit/test_user_auth.py`
  - `utils/test_helpers.py`
- ☐ 权限校验-视图权限 
- ☐ 权限校验-路由权限 

## 文章与分类（Articles/Categories/Tags）
- ☑️ 文章列表 （文件 3；函数≈61）
  - `integration/test_api.py`
  - `regression/auth/test_permissions.py`
  - `unit/test_article_management.py`
- ☑️ 文章详情 （文件 5；函数≈111）
  - `integration/test_api.py`
  - `regression/auth/test_permissions.py`
  - `unit/test_article_management.py`
  - `unit/test_english_learning.py`
  - `unit/test_news_dashboard.py`
- ☑️ 创建文章 （文件 2；函数≈43）
  - `regression/auth/test_permissions.py`
  - `unit/test_article_management.py`
- ☐ 更新文章 
- ☑️ 删除文章 （文件 1；函数≈28）
  - `unit/test_article_management.py`
- ☐ 文章点赞 
- ☐ 文章收藏 
- ☑️ 分类列表 （文件 1；函数≈15）
  - `regression/auth/test_permissions.py`
- ☑️ 分类下文章 （文件 3；函数≈61）
  - `integration/test_api.py`
  - `regression/auth/test_permissions.py`
  - `unit/test_article_management.py`
- ☐ 标签列表 
- ☑️ 全文检索（如有） （文件 3；函数≈78）
  - `unit/test_article_management.py`
  - `unit/test_english_learning.py`
  - `unit/test_news_dashboard.py`

## 英语学习（Words/News/Typing/Stats）
- ☑️ 单词-列表 （文件 2；函数≈49）
  - `integration/test_api.py`
  - `unit/test_english_learning.py`
- ☑️ 单词-详情 （文件 2；函数≈49）
  - `integration/test_api.py`
  - `unit/test_english_learning.py`
- ☑️ 单词-进度更新 （文件 1；函数≈31）
  - `unit/test_english_learning.py`
- ☑️ 新闻-列表 （文件 5；函数≈75）
  - `integration/test_api.py`
  - `integration/test_news_api.py`
  - `unit/test_english_learning.py`
  - `unit/test_news_dashboard.py`
  - `unit/test_news_visibility_removal.py`
- ☑️ 新闻-详情 （文件 5；函数≈75）
  - `integration/test_api.py`
  - `integration/test_news_api.py`
  - `unit/test_english_learning.py`
  - `unit/test_news_dashboard.py`
  - `unit/test_news_visibility_removal.py`
- ☑️ 新闻-图片URL构建 （文件 7；函数≈28）
  - `integration/test_bbc_fix_verification.py`
  - `integration/test_fixes_verification.py`
  - `integration/test_news_api.py`
  - `unit/test_bbc_news_save.py`
  - `unit/test_bbc_simple.py`
  - ... 其余 2 个文件
- ☑️ 新闻-日期格式化 （文件 9；函数≈127）
  - `integration/test_bbc_fix_verification.py`
  - `integration/test_news_api.py`
  - `regression/english/test_data_analysis.py`
  - `unit/test_bbc_news_save.py`
  - `unit/test_data_analysis.py`
  - ... 其余 4 个文件
- ☑️ 爬虫-触发（crawl-news） （文件 4；函数≈24）
  - `integration/test_fixes_verification.py`
  - `unit/test_bbc_news_save.py`
  - `unit/test_bbc_simple.py`
  - `unit/test_techcrunch_and_image_cleanup.py`
- ☐ 爬虫-状态 
- ☐ 打字-创建会话 
- ☐ 打字-提交记录 
- ☑️ 打字-暂停/继续 （文件 3；函数≈25）
  - `regression/english/test_pause_resume.py`
  - `test_quick_validation.py`
  - `test_simple_validation.py`
- ☑️ 打字-发音（防抖/互斥） （文件 3；函数≈20）
  - `regression/english/test_pronunciation.py`
  - `test_quick_validation.py`
  - `test_simple_validation.py`
- ☑️ 打字-错误统计 （文件 5；函数≈106）
  - `regression/english/test_data_analysis.py`
  - `regression/english/test_pause_resume.py`
  - `unit/test_data_analysis.py`
  - `unit/test_english_learning.py`
  - `unit/test_typing_practice.py`
- ☑️ 统计-热力图 （文件 3；函数≈43）
  - `regression/english/test_data_analysis.py`
  - `test_simple_validation.py`
  - `unit/test_data_analysis.py`
- ☑️ 统计-趋势 （文件 2；函数≈39）
  - `regression/english/test_data_analysis.py`
  - `unit/test_data_analysis.py`
- ☑️ 统计-概览 （文件 2；函数≈39）
  - `regression/english/test_data_analysis.py`
  - `unit/test_data_analysis.py`

## 新闻爬虫与图片链路（Crawler/Images）
- ☑️ Fundus 爬虫-发布者映射 （文件 2；函数≈7）
  - `unit/test_cnn_crawler.py`
  - `unit/test_fundus_crawler.py`
- ☑️ Fundus 爬虫-数据入库 （文件 5；函数≈43）
  - `integration/test_fixes_verification.py`
  - `unit/test_bbc_news_save.py`
  - `unit/test_bbc_simple.py`
  - `unit/test_news_dashboard.py`
  - `unit/test_techcrunch_and_image_cleanup.py`
- ☑️ 传统爬虫-BBC （文件 6；函数≈31）
  - `integration/test_bbc_fix_verification.py`
  - `integration/test_news_api.py`
  - `unit/test_bbc_news_save.py`
  - `unit/test_bbc_simple.py`
  - `unit/test_fundus_crawler.py`
  - ... 其余 1 个文件
- ☑️ 传统爬虫-CNN （文件 2；函数≈25）
  - `unit/test_cnn_crawler.py`
  - `unit/test_news_dashboard.py`
- ☑️ 图片下载与保存 （文件 7；函数≈28）
  - `integration/test_bbc_fix_verification.py`
  - `integration/test_fixes_verification.py`
  - `integration/test_news_api.py`
  - `unit/test_bbc_news_save.py`
  - `unit/test_bbc_simple.py`
  - ... 其余 2 个文件
- ☐ 媒体访问路径 
- ☐ 管理页-获取管理列表 

## 数据与基础设施（DB/Jobs/Infra）
- ☑️ MySQL 连接校验 （文件 2；函数≈6）
  - `test_settings_mysql.py`
  - `unit/test_mysql_connection.py`
- ☑️ 作业/任务（Celery/Jobs） （文件 1；函数≈1）
  - `unit/test_jobs.py`
- ☑️ 测试脚手架/配置 （文件 12；函数≈36）
  - `integration/test_bbc_fix_verification.py`
  - `integration/test_fixes_verification.py`
  - `test_quick_validation.py`
  - `test_settings.py`
  - `test_settings_mysql.py`
  - ... 其余 7 个文件
---

## 明细（按测试文件 → 函数）
### `integration/test_api.py`
- test_api_endpoint_integration()
- test_article_creation()
- test_article_detail()
- test_article_list()
- test_authorized_access()
- test_bulk_operations()
- test_expression_detail()
- test_expression_list()
- test_full_user_workflow()
- test_health_check_endpoint()
- test_news_detail()
- test_news_list()
- test_unauthorized_access()
- test_user_login()
- test_user_logout()
- test_user_registration()
- test_word_detail()
- test_word_list()

### `integration/test_bbc_fix_verification.py`
- （未检测到函数）

### `integration/test_fixes_verification.py`
- test_image_cleanup_fixes()
- test_techcrunch_fixes()

### `integration/test_news_api.py`
- test_backend_server()
- test_news_crawling()
- test_news_list()

### `regression/auth/test_permissions.py`
- test_admin_article_permissions()
- test_admin_user_permissions()
- test_article_author_permissions()
- test_article_non_author_permissions()
- test_article_read_permissions()
- test_category_read_permissions()
- test_category_write_permissions()
- test_group_permission_assignment()
- test_group_permission_inheritance()
- test_multi_level_permission_workflow()
- test_permission_checking()
- test_permission_escalation_prevention()
- test_regular_user_permissions()
- test_unauthorized_access()
- test_user_profile_permissions()

### `regression/auth/test_user_authentication.py`
- test_authentication_state_management()
- test_full_authentication_workflow()
- test_get_user_profile()
- test_get_user_profile_unauthorized()
- test_login_form_validation()
- test_multiple_user_authentication()
- test_password_reset_confirm_invalid_token()
- test_password_reset_confirm_password_mismatch()
- test_password_reset_confirm_success()
- test_password_reset_request_invalid_email()
- test_password_reset_request_success()
- test_protected_endpoint_with_token()
- test_register_form_validation()
- test_token_obtain_pair()
- test_token_refresh()
- test_update_user_profile()
- test_user_login_invalid_credentials()
- test_user_login_missing_fields()
- test_user_login_success()
- test_user_logout_success()
- test_user_logout_unauthorized()
- test_user_registration_duplicate_email()
- test_user_registration_duplicate_username()
- test_user_registration_password_mismatch()
- test_user_registration_success()

### `regression/english/test_data_analysis.py`
- test_accuracy_trend_api()
- test_accuracy_trend_data_generation()
- test_data_overview_api()
- test_data_overview_generation()
- test_date_range_filtering()
- test_date_range_validation()
- test_exercise_heatmap_api()
- test_exercise_heatmap_data_generation()
- test_full_data_analysis_workflow()
- test_heatmap_level_calculation()
- test_key_error_stats_api()
- test_key_error_stats_data_generation()
- test_unauthorized_access()
- test_word_heatmap_api()
- test_word_heatmap_data_generation()
- test_wpm_trend_api()
- test_wpm_trend_data_generation()

### `regression/english/test_pause_resume.py`
- test_invalid_pause_resume_actions()
- test_multiple_pause_resume_cycles()
- test_pause_duration_calculation()
- test_pause_logic()
- test_pause_practice_session()
- test_pause_resume_button_states()
- test_pause_resume_ui_feedback()
- test_pause_resume_with_multiple_users()
- test_pause_resume_with_practice_data()
- test_pause_resume_with_timer_synchronization()
- test_pause_resume_workflow()
- test_pause_time_calculation()
- test_pause_timing_accuracy()
- test_resume_logic()
- test_resume_practice_session()
- test_session_state_consistency()
- test_session_time_accuracy()
- test_timer_display_consistency()
- test_timer_pause_logic()
- test_timer_resume_logic()

### `regression/english/test_pronunciation.py`
- test_api_error_handling()
- test_pronunciation_audio_url_generation()
- test_pronunciation_auto_play_logic()
- test_pronunciation_batch_processing()
- test_pronunciation_cache_mechanism()
- test_pronunciation_component_rendering()
- test_pronunciation_error_recovery()
- test_pronunciation_fallback_mechanism()
- test_pronunciation_format_validation()
- test_pronunciation_overlap_prevention()
- test_pronunciation_quality_validation()
- test_pronunciation_rate_limiting()
- test_pronunciation_url_validation()
- test_pronunciation_workflow_integration()
- test_youdao_api_integration()

### `test_quick_validation.py`
- test_basic_functionality()

### `test_settings.py`
- （未检测到函数）

### `test_settings_mysql.py`
- （未检测到函数）

### `test_simple_validation.py`
- test_data_analysis_logic()
- test_frontend_logic()
- test_pause_resume_logic()
- test_pronunciation_logic()

### `unit/test_article_management.py`
- test_articles_ordering()
- test_articles_pagination()
- test_create_article_missing_required_fields()
- test_create_article_success()
- test_create_article_with_draft_status()
- test_create_article_with_invalid_category()
- test_create_article_without_authentication()
- test_delete_article_by_non_author()
- test_delete_article_success()
- test_delete_article_without_authentication()
- test_delete_nonexistent_article()
- test_edit_article_by_non_author()
- test_edit_article_change_category()
- test_edit_article_change_status()
- test_edit_article_success()
- test_edit_article_without_authentication()
- test_edit_nonexistent_article()
- test_filter_articles_by_author()
- test_filter_articles_by_category()
- test_filter_articles_by_status()
- test_get_article_detail()
- test_get_draft_article_by_author()
- test_get_draft_article_by_non_author()
- test_get_nonexistent_article()
- test_search_articles_by_content()
- test_search_articles_by_summary()
- test_search_articles_by_title()
- test_search_articles_no_results()

### `unit/test_articles.py`
- （未检测到函数）

### `unit/test_basic.py`
- test_admin_url()
- test_api_root_url()
- test_create_superuser_if_not_exists_command()
- test_database_connection()
- test_database_operations()
- test_database_setting()
- test_debug_setting()
- test_external_api_calls()
- test_installed_apps()
- test_quick_math()
- test_string_operations()
- test_superuser_creation()
- test_user_creation()
- test_wait_for_db_command()

### `unit/test_bbc_news_save.py`
- test_bbc_crawler_content_extraction()
- test_content_length_validation()
- test_crawler_initialization()
- test_duplicate_url_detection()
- test_full_crawl_process()
- test_news_model_fields()
- test_news_save_with_insufficient_content()
- test_news_save_with_sufficient_content()

### `unit/test_bbc_simple.py`
- （未检测到函数）

### `unit/test_categories.py`
- （未检测到函数）

### `unit/test_cnn_crawler.py`
- test_alternative_cnn()
- test_available_publishers_file()
- test_cnn_publisher()
- test_fundus_crawler_service()
- test_fundus_import()
- test_publisher_collection()

### `unit/test_data_analysis.py`
- test_accuracy_trend_api()
- test_aggregate_daily_stats()
- test_api_requires_authentication()
- test_api_with_invalid_date_format()
- test_api_without_date_parameters()
- test_date_range_validation()
- test_empty_data_analysis()
- test_exercise_heatmap_api()
- test_get_accuracy_trend()
- test_get_data_overview()
- test_get_exercise_heatmap()
- test_get_heatmap_level()
- test_get_key_error_stats()
- test_get_word_heatmap()
- test_get_wpm_trend()
- test_invalid_user_id()
- test_key_error_stats_api()
- test_large_data_performance()
- test_large_date_range()
- test_overview_api()
- test_word_heatmap_api()
- test_wpm_trend_api()

### `unit/test_english_learning.py`
- test_expression_learning_progress()
- test_filter_expressions_by_category()
- test_filter_expressions_by_difficulty()
- test_filter_news_by_difficulty()
- test_filter_news_by_source()
- test_filter_words_by_category()
- test_filter_words_by_difficulty()
- test_get_expression_detail()
- test_get_expression_list()
- test_get_news_detail()
- test_get_news_list()
- test_get_typing_history()
- test_get_typing_statistics()
- test_get_typing_words()
- test_get_typing_words_by_chapter()
- test_get_typing_words_by_difficulty()
- test_get_word_detail()
- test_get_word_list()
- test_news_reading_progress()
- test_search_expressions()
- test_search_news()
- test_search_words()
- test_submit_typing_result()
- test_typing_practice_progress()
- test_typing_practice_review()
- test_typing_practice_session()
- test_typing_word_detail()
- test_update_news_progress()
- test_update_word_progress()
- test_word_learning_progress()
- test_word_statistics()

### `unit/test_fundus_crawler.py`
- test_fundus_crawling()

### `unit/test_jobs.py`
- test_jobs_list()

### `unit/test_models.py`
- test_article_creation()
- test_article_str_representation()
- test_article_timestamps()
- test_bulk_operations()
- test_category_creation()
- test_category_str_representation()
- test_expression_creation()
- test_expression_str_representation()
- test_model_imports()
- test_news_creation()
- test_news_published_date()
- test_news_str_representation()
- test_profile_creation()
- test_profile_str_representation()
- test_progress_creation()
- test_progress_mastery_level_validation()
- test_progress_str_representation()
- test_user_creation()
- test_user_profile_creation()
- test_user_str_representation()
- test_word_creation()
- test_word_difficulty_choices()
- test_word_str_representation()

### `unit/test_mysql_connection.py`
- test_connection_pool()
- test_connection_string()
- test_database_configuration()
- test_database_connection()
- test_database_operations()
- test_transaction_rollback()

### `unit/test_news_dashboard.py`
- test_crawl_settings_persistence()
- test_date_formatting()
- test_news_api_requires_auth()
- test_news_categorization()
- test_news_crawl_api()
- test_news_dashboard_page_loads()
- test_news_dashboard_requires_auth()
- test_news_deletion()
- test_news_detail_api()
- test_news_filtering_by_source()
- test_news_filtering_logic()
- test_news_list_api_returns_data()
- test_news_ordering()
- test_news_pagination()
- test_news_search_functionality()
- test_news_stats_calculation()
- test_news_store_initialization()
- test_news_visibility_toggle()
- test_text_truncation()

### `unit/test_news_visibility_removal.py`
- test_api_without_visibility()
- test_is_visible_field_removed()
- test_news_creation_without_visibility()
- test_news_deletion_refresh()

### `unit/test_simple.py`
- test_basic_math()
- test_directory_structure()
- test_django_import()
- test_environment_variables()
- test_file_operations()
- test_list_operations()
- test_pytest_import()
- test_python_environment()
- test_rest_framework_import()
- test_string_operations()

### `unit/test_techcrunch_and_image_cleanup.py`
- test_article_content_extraction()
- test_content_quality_validation()
- test_crawler_error_handling()
- test_crawler_initialization()
- test_full_crawl_process()
- test_image_cleanup_with_invalid_path()
- test_image_cleanup_with_nonexistent_file()
- test_news_deletion_with_external_image()
- test_news_deletion_with_local_image()
- test_news_deletion_without_image()
- test_news_update_with_image_change()
- test_parse_rss_item_with_invalid_data()
- test_parse_rss_item_with_valid_data()
- test_rss_content_retrieval()

### `unit/test_todos.py`
- test_todos_list()

### `unit/test_typing_practice.py`
- test_complete_typing_practice_flow()
- test_get_daily_progress()
- test_get_typing_statistics()
- test_get_typing_words()
- test_get_typing_words_invalid_dictionary()
- test_get_typing_words_invalid_difficulty()
- test_submit_typing_practice()
- test_submit_typing_practice_invalid_word_id()
- test_submit_typing_practice_missing_is_correct()
- test_submit_typing_practice_missing_word_id()
- test_typing_practice_performance()
- test_typing_session_creation()
- test_typing_session_serializer()
- test_typing_word_serializer()
- test_user_typing_stats_serializer()
- test_user_typing_stats_update()

### `unit/test_user_auth.py`
- test_admin_user_access_admin_endpoint()
- test_authenticated_user_access_protected_endpoint()
- test_password_reset_confirm_success()
- test_password_reset_request_nonexistent_email()
- test_password_reset_request_success()
- test_regular_user_access_admin_endpoint()
- test_unauthenticated_user_access_protected_endpoint()
- test_user_login_missing_credentials()
- test_user_login_nonexistent_user()
- test_user_login_success()
- test_user_login_with_email()
- test_user_login_wrong_password()
- test_user_logout_success()
- test_user_logout_without_authentication()
- test_user_profile_self_access()
- test_user_registration_duplicate_email()
- test_user_registration_duplicate_username()
- test_user_registration_missing_required_fields()
- test_user_registration_password_mismatch()
- test_user_registration_success()
- test_verify_user_identity_missing_credentials()
- test_verify_user_identity_success()
- test_verify_user_identity_with_email()
- test_verify_user_identity_wrong_password()

### `unit/test_users.py`
- （未检测到函数）

### `utils/test_helpers.py`
- （未检测到函数）
