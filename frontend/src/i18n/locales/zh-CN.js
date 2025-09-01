export default {
  // 通用
  common: {
    confirm: '确认',
    cancel: '取消',
    save: '保存',
    delete: '删除',
    edit: '编辑',
    add: '添加',
    search: '搜索',
    loading: '加载中...',
    noData: '暂无数据',
    back: '返回',
    next: '下一步',
    previous: '上一步',
    submit: '提交',
    reset: '重置',
    close: '关闭',
    open: '打开',
    refresh: '刷新',
    export: '导出',
    import: '导入',
    download: '下载',
    upload: '上传',
    copy: '复制',
    paste: '粘贴',
    select: '选择',
    all: '全部',
    none: '无',
    yes: '是',
    no: '否',
    success: '成功',
    error: '错误',
    warning: '警告',
    info: '信息',
    required: '必填',
    optional: '可选'
  },

  // 导航
  nav: {
    dashboard: '仪表板',
    aiConfig: 'AI配置',
    monitoring: '监控',
    statistics: '统计',
    settings: '设置',
    configManagement: '配置管理',
    logout: '退出登录',
    profile: '个人资料',
    articles: '文章',
    englishLearning: '英语学习',
    newsDashboard: '新闻仪表板',
    wordLearning: '单词学习',
    expressions: '地道表达',
    newsList: '新闻列表',
    login: '登录',
    register: '注册',
    createArticle: '发布文章',
    myArticles: '我的文章'
  },

  // 登录页面
  login: {
    title: 'AI服务配置系统',
    subtitle: '技术博客网站 - 测试CI/CD',
    welcomeBack: '欢迎回来',
    loginYourAccount: '登录您的账户',
    username: '用户名',
    password: '密码',
    captcha: '验证码',
    usernamePlaceholder: '请输入用户名或邮箱',
    passwordPlaceholder: '请输入密码',
    captchaPlaceholder: '请输入验证码',
    login: '登录',
    rememberMe: '记住我',
    forgotPassword: '忘记密码？',
    loginError: '登录失败，请检查用户名和密码',
    loginSuccess: '登录成功',
    features: {
      richArticles: '丰富的技术文章',
      professionalCommunity: '专业的技术社区',
      qualityExperience: '优质的学习体验'
    }
  },

  // AI配置页面
  aiConfig: {
    title: 'AI服务配置',
    providers: '服务提供商',
    models: 'AI模型',
    apiKeys: 'API密钥',
    promptTemplates: '提示模板',
    modelConfigs: '模型配置',
    usageQuotas: '使用配额',
    failoverStrategies: '故障转移策略',
    auditLogs: '审计日志',
    healthStatus: '健康状态',
    statistics: '统计分析',
    configManagement: '配置管理',
    systemSettings: '系统设置',
    
    // 服务提供商
    provider: {
      name: '提供商名称',
      type: '提供商类型',
      baseUrl: '基础URL',
      apiVersion: 'API版本',
      status: '状态',
      active: '激活',
      inactive: '未激活',
      addProvider: '添加提供商',
      editProvider: '编辑提供商',
      deleteProvider: '删除提供商',
      providerTypes: {
        openai: 'OpenAI',
        anthropic: 'Anthropic',
        azure: 'Azure OpenAI',
        custom: '自定义'
      }
    },

    // AI模型
    model: {
      name: '模型名称',
      provider: '提供商',
      modelId: '模型ID',
      maxTokens: '最大令牌数',
      temperature: '温度',
      topP: 'Top P',
      frequencyPenalty: '频率惩罚',
      presencePenalty: '存在惩罚',
      addModel: '添加模型',
      editModel: '编辑模型',
      deleteModel: '删除模型'
    },

    // API密钥
    apiKey: {
      name: '密钥名称',
      provider: '提供商',
      keyValue: '密钥值',
      isActive: '是否激活',
      lastUsed: '最后使用时间',
      addKey: '添加密钥',
      editKey: '编辑密钥',
      deleteKey: '删除密钥',
      maskKey: '隐藏密钥',
      showKey: '显示密钥'
    },

    // 提示模板
    promptTemplate: {
      name: '模板名称',
      description: '描述',
      content: '内容',
      variables: '变量',
      addTemplate: '添加模板',
      editTemplate: '编辑模板',
      deleteTemplate: '删除模板'
    },

    // 模型配置
    modelConfig: {
      name: '配置名称',
      model: '模型',
      parameters: '参数',
      addConfig: '添加配置',
      editConfig: '编辑配置',
      deleteConfig: '删除配置'
    },

    // 使用配额
    usageQuota: {
      name: '配额名称',
      provider: '提供商',
      model: '模型',
      dailyLimit: '每日限制',
      monthlyLimit: '每月限制',
      used: '已使用',
      remaining: '剩余',
      addQuota: '添加配额',
      editQuota: '编辑配额',
      deleteQuota: '删除配额'
    },

    // 故障转移策略
    failoverStrategy: {
      name: '策略名称',
      priority: '优先级',
      providers: '提供商列表',
      conditions: '条件',
      addStrategy: '添加策略',
      editStrategy: '编辑策略',
      deleteStrategy: '删除策略'
    }
  },

  // 监控页面
  monitoring: {
    title: '监控仪表板',
    realTimeStatus: '实时状态',
    performanceMetrics: '性能指标',
    errorRates: '错误率',
    responseTimes: '响应时间',
    throughput: '吞吐量',
    activeConnections: '活跃连接',
    systemHealth: '系统健康度',
    alerts: '告警',
    logs: '日志'
  },

  // 统计分析页面
  statistics: {
    title: '统计分析',
    usageStatistics: '使用统计',
    costAnalysis: '成本分析',
    performanceAnalysis: '性能分析',
    userBehavior: '用户行为',
    timeRange: '时间范围',
    today: '今天',
    yesterday: '昨天',
    last7Days: '最近7天',
    last30Days: '最近30天',
    last90Days: '最近90天',
    custom: '自定义',
    exportData: '导出数据',
    generateReport: '生成报告'
  },

  // 设置页面
  settings: {
    title: '系统设置',
    userProfile: '个人信息',
    preferencesLabel: '偏好设置',
    securityLabel: '安全设置',
    notifications: '通知设置',
    system: '系统设置',
    loginHistory: '登录历史',
    deviceManagement: '设备管理',
    
    // 个人信息
    profile: {
      username: '用户名',
      email: '邮箱',
      displayName: '显示名称',
      avatar: '头像',
      bio: '个人简介',
      changePassword: '修改密码',
      oldPassword: '旧密码',
      newPassword: '新密码',
      confirmPassword: '确认密码'
    },

    // 偏好设置
    preferences: {
      theme: '主题',
      language: '语言',
      timezone: '时区',
      autoSave: '自动保存',
      debugMode: '调试模式',
      analyticsEnabled: '启用分析',
      lightTheme: '浅色主题',
      darkTheme: '深色主题',
      autoTheme: '自动主题'
    },

    // 安全设置
    security: {
      twoFactorAuth: '双因素认证',
      sessionTimeout: '会话超时',
      loginNotifications: '登录通知',
      enable2FA: '启用双因素认证',
      disable2FA: '禁用双因素认证',
      timeoutMinutes: '超时时间（分钟）'
    },

    // 通知设置
    notifications: {
      emailNotifications: '邮件通知',
      pushNotifications: '推送通知',
      notificationFrequency: '通知频率',
      immediate: '立即',
      daily: '每日',
      weekly: '每周'
    },

    // 系统设置
    system: {
      autoSave: '自动保存',
      debugMode: '调试模式',
      analyticsEnabled: '启用分析',
      systemConfig: '系统配置',
      globalSettings: '全局设置'
    },

    // 登录历史
    loginHistory: {
      loginTime: '登录时间',
      ipAddress: 'IP地址',
      location: '位置',
      deviceType: '设备类型',
      browser: '浏览器',
      os: '操作系统',
      status: '状态',
      successful: '成功',
      failed: '失败'
    },

    // 设备管理
    deviceManagement: {
      deviceName: '设备名称',
      deviceType: '设备类型',
      ipAddress: 'IP地址',
      browser: '浏览器',
      os: '操作系统',
      lastActivity: '最后活动',
      status: '状态',
      terminateSession: '终止会话',
      terminateAllSessions: '终止所有会话',
      active: '活跃',
      inactive: '非活跃'
    }
  },

  // 配置管理
  configManagement: {
    title: '配置管理',
    importExport: '导入导出',
    templates: '模板管理',
    versionControl: '版本控制',
    
    // 导入导出
    importExport: {
      exportConfig: '导出配置',
      importConfig: '导入配置',
      selectFile: '选择文件',
      dragDrop: '拖拽文件到此处',
      supportedFormats: '支持格式：JSON, YAML',
      exportSuccess: '导出成功',
      importSuccess: '导入成功',
      importError: '导入失败',
      validateConfig: '验证配置'
    },

    // 模板管理
    templates: {
      createTemplate: '创建模板',
      applyTemplate: '应用模板',
      templateName: '模板名称',
      templateDescription: '模板描述',
      saveAsTemplate: '保存为模板',
      deleteTemplate: '删除模板'
    },

    // 版本控制
    versionControl: {
      versionHistory: '版本历史',
      createVersion: '创建版本',
      rollbackVersion: '回滚版本',
      versionNumber: '版本号',
      versionDescription: '版本描述',
      createTime: '创建时间',
      rollback: '回滚',
      compare: '比较'
    }
  },

  // 错误信息
  errors: {
    networkError: '网络错误',
    serverError: '服务器错误',
    validationError: '验证错误',
    permissionDenied: '权限不足',
    notFound: '未找到',
    timeout: '请求超时',
    unknownError: '未知错误',
    invalidInput: '输入无效',
    requiredField: '此字段为必填项',
    invalidFormat: '格式无效',
    fileTooLarge: '文件过大',
    unsupportedFileType: '不支持的文件类型',
    logoutFailed: '退出登录失败'
  },

  // 成功信息
  success: {
    saveSuccess: '保存成功',
    deleteSuccess: '删除成功',
    updateSuccess: '更新成功',
    createSuccess: '创建成功',
    importSuccess: '导入成功',
    exportSuccess: '导出成功',
    operationSuccess: '操作成功'
  },

  // 确认对话框
  confirm: {
    deleteConfirm: '确定要删除吗？',
    logoutConfirm: '确定要退出登录吗？',
    unsavedChanges: '有未保存的更改，确定要离开吗？',
    terminateSession: '确定要终止此会话吗？',
    terminateAllSessions: '确定要终止所有会话吗？',
    rollbackVersion: '确定要回滚到此版本吗？'
  }
}
