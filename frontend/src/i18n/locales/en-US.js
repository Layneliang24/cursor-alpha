export default {
  // Common
  common: {
    confirm: 'Confirm',
    cancel: 'Cancel',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    add: 'Add',
    search: 'Search',
    loading: 'Loading...',
    noData: 'No Data',
    back: 'Back',
    next: 'Next',
    previous: 'Previous',
    submit: 'Submit',
    reset: 'Reset',
    close: 'Close',
    open: 'Open',
    refresh: 'Refresh',
    export: 'Export',
    import: 'Import',
    download: 'Download',
    upload: 'Upload',
    copy: 'Copy',
    paste: 'Paste',
    select: 'Select',
    all: 'All',
    none: 'None',
    yes: 'Yes',
    no: 'No',
    success: 'Success',
    error: 'Error',
    warning: 'Warning',
    info: 'Info',
    required: 'Required',
    optional: 'Optional'
  },

  // Navigation
  nav: {
    dashboard: 'Dashboard',
    aiConfig: 'AI Config',
    monitoring: 'Monitoring',
    statistics: 'Statistics',
    settings: 'Settings',
    configManagement: 'Config Management',
    logout: 'Logout',
    profile: 'Profile',
    articles: 'Articles',
    englishLearning: 'English Learning',
    newsDashboard: 'News Dashboard',
    wordLearning: 'Word Learning',
    expressions: 'Expressions',
    newsList: 'News List',
    login: 'Login',
    register: 'Register',
    createArticle: 'Create Article',
    myArticles: 'My Articles'
  },

  // Login page
  login: {
    title: 'AI Service Configuration System',
    subtitle: 'Tech Blog Website - CI/CD Testing',
    welcomeBack: 'Welcome Back',
    loginYourAccount: 'Login to your account',
    username: 'Username',
    password: 'Password',
    captcha: 'Captcha',
    usernamePlaceholder: 'Enter username or email',
    passwordPlaceholder: 'Enter password',
    captchaPlaceholder: 'Enter captcha',
    login: 'Login',
    rememberMe: 'Remember me',
    forgotPassword: 'Forgot password?',
    loginError: 'Login failed, please check username and password',
    loginSuccess: 'Login successful',
    features: {
      richArticles: 'Rich Technical Articles',
      professionalCommunity: 'Professional Tech Community',
      qualityExperience: 'Quality Learning Experience'
    }
  },

  // AI Config page
  aiConfig: {
    title: 'AI Service Configuration',
    providers: 'Service Providers',
    models: 'AI Models',
    apiKeys: 'API Keys',
    promptTemplates: 'Prompt Templates',
    modelConfigs: 'Model Configurations',
    usageQuotas: 'Usage Quotas',
    failoverStrategies: 'Failover Strategies',
    auditLogs: 'Audit Logs',
    healthStatus: 'Health Status',
    statistics: 'Statistics Analysis',
    configManagement: 'Configuration Management',
    systemSettings: 'System Settings',
    
    // Service Providers
    provider: {
      name: 'Provider Name',
      type: 'Provider Type',
      baseUrl: 'Base URL',
      apiVersion: 'API Version',
      status: 'Status',
      active: 'Active',
      inactive: 'Inactive',
      addProvider: 'Add Provider',
      editProvider: 'Edit Provider',
      deleteProvider: 'Delete Provider',
      providerTypes: {
        openai: 'OpenAI',
        anthropic: 'Anthropic',
        azure: 'Azure OpenAI',
        custom: 'Custom'
      }
    },

    // AI Models
    model: {
      name: 'Model Name',
      provider: 'Provider',
      modelId: 'Model ID',
      maxTokens: 'Max Tokens',
      temperature: 'Temperature',
      topP: 'Top P',
      frequencyPenalty: 'Frequency Penalty',
      presencePenalty: 'Presence Penalty',
      addModel: 'Add Model',
      editModel: 'Edit Model',
      deleteModel: 'Delete Model'
    },

    // API Keys
    apiKey: {
      name: 'Key Name',
      provider: 'Provider',
      keyValue: 'Key Value',
      isActive: 'Is Active',
      lastUsed: 'Last Used',
      addKey: 'Add Key',
      editKey: 'Edit Key',
      deleteKey: 'Delete Key',
      maskKey: 'Mask Key',
      showKey: 'Show Key'
    },

    // Prompt Templates
    promptTemplate: {
      name: 'Template Name',
      description: 'Description',
      content: 'Content',
      variables: 'Variables',
      addTemplate: 'Add Template',
      editTemplate: 'Edit Template',
      deleteTemplate: 'Delete Template'
    },

    // Model Configurations
    modelConfig: {
      name: 'Config Name',
      model: 'Model',
      parameters: 'Parameters',
      addConfig: 'Add Config',
      editConfig: 'Edit Config',
      deleteConfig: 'Delete Config'
    },

    // Usage Quotas
    usageQuota: {
      name: 'Quota Name',
      provider: 'Provider',
      model: 'Model',
      dailyLimit: 'Daily Limit',
      monthlyLimit: 'Monthly Limit',
      used: 'Used',
      remaining: 'Remaining',
      addQuota: 'Add Quota',
      editQuota: 'Edit Quota',
      deleteQuota: 'Delete Quota'
    },

    // Failover Strategies
    failoverStrategy: {
      name: 'Strategy Name',
      priority: 'Priority',
      providers: 'Provider List',
      conditions: 'Conditions',
      addStrategy: 'Add Strategy',
      editStrategy: 'Edit Strategy',
      deleteStrategy: 'Delete Strategy'
    }
  },

  // Monitoring page
  monitoring: {
    title: 'Monitoring Dashboard',
    realTimeStatus: 'Real-time Status',
    performanceMetrics: 'Performance Metrics',
    errorRates: 'Error Rates',
    responseTimes: 'Response Times',
    throughput: 'Throughput',
    activeConnections: 'Active Connections',
    systemHealth: 'System Health',
    alerts: 'Alerts',
    logs: 'Logs'
  },

  // Statistics page
  statistics: {
    title: 'Statistics Analysis',
    usageStatistics: 'Usage Statistics',
    costAnalysis: 'Cost Analysis',
    performanceAnalysis: 'Performance Analysis',
    userBehavior: 'User Behavior',
    timeRange: 'Time Range',
    today: 'Today',
    yesterday: 'Yesterday',
    last7Days: 'Last 7 Days',
    last30Days: 'Last 30 Days',
    last90Days: 'Last 90 Days',
    custom: 'Custom',
    exportData: 'Export Data',
    generateReport: 'Generate Report'
  },

  // Settings page
  settings: {
    title: 'System Settings',
    userProfile: 'User Profile',
    preferencesLabel: 'Preferences',
    securityLabel: 'Security',
    notifications: 'Notifications',
    system: 'System',
    loginHistory: 'Login History',
    deviceManagement: 'Device Management',
    
    // User Profile
    profile: {
      username: 'Username',
      email: 'Email',
      displayName: 'Display Name',
      avatar: 'Avatar',
      bio: 'Bio',
      changePassword: 'Change Password',
      oldPassword: 'Old Password',
      newPassword: 'New Password',
      confirmPassword: 'Confirm Password'
    },

    // Preferences
    preferences: {
      theme: 'Theme',
      language: 'Language',
      timezone: 'Timezone',
      autoSave: 'Auto Save',
      debugMode: 'Debug Mode',
      analyticsEnabled: 'Analytics Enabled',
      lightTheme: 'Light Theme',
      darkTheme: 'Dark Theme',
      autoTheme: 'Auto Theme'
    },

    // Security
    security: {
      twoFactorAuth: 'Two-Factor Authentication',
      sessionTimeout: 'Session Timeout',
      loginNotifications: 'Login Notifications',
      enable2FA: 'Enable 2FA',
      disable2FA: 'Disable 2FA',
      timeoutMinutes: 'Timeout (minutes)'
    },

    // Notifications
    notifications: {
      emailNotifications: 'Email Notifications',
      pushNotifications: 'Push Notifications',
      notificationFrequency: 'Notification Frequency',
      immediate: 'Immediate',
      daily: 'Daily',
      weekly: 'Weekly'
    },

    // System
    system: {
      autoSave: 'Auto Save',
      debugMode: 'Debug Mode',
      analyticsEnabled: 'Analytics Enabled',
      systemConfig: 'System Configuration',
      globalSettings: 'Global Settings'
    },

    // Login History
    loginHistory: {
      loginTime: 'Login Time',
      ipAddress: 'IP Address',
      location: 'Location',
      deviceType: 'Device Type',
      browser: 'Browser',
      os: 'Operating System',
      status: 'Status',
      successful: 'Successful',
      failed: 'Failed'
    },

    // Device Management
    deviceManagement: {
      deviceName: 'Device Name',
      deviceType: 'Device Type',
      ipAddress: 'IP Address',
      browser: 'Browser',
      os: 'Operating System',
      lastActivity: 'Last Activity',
      status: 'Status',
      terminateSession: 'Terminate Session',
      terminateAllSessions: 'Terminate All Sessions',
      active: 'Active',
      inactive: 'Inactive'
    }
  },

  // Configuration Management
  configManagement: {
    title: 'Configuration Management',
    importExport: 'Import/Export',
    templates: 'Template Management',
    versionControl: 'Version Control',
    
    // Import/Export
    importExport: {
      exportConfig: 'Export Configuration',
      importConfig: 'Import Configuration',
      selectFile: 'Select File',
      dragDrop: 'Drag and drop files here',
      supportedFormats: 'Supported formats: JSON, YAML',
      exportSuccess: 'Export successful',
      importSuccess: 'Import successful',
      importError: 'Import failed',
      validateConfig: 'Validate Configuration'
    },

    // Template Management
    templates: {
      createTemplate: 'Create Template',
      applyTemplate: 'Apply Template',
      templateName: 'Template Name',
      templateDescription: 'Template Description',
      saveAsTemplate: 'Save as Template',
      deleteTemplate: 'Delete Template'
    },

    // Version Control
    versionControl: {
      versionHistory: 'Version History',
      createVersion: 'Create Version',
      rollbackVersion: 'Rollback Version',
      versionNumber: 'Version Number',
      versionDescription: 'Version Description',
      createTime: 'Create Time',
      rollback: 'Rollback',
      compare: 'Compare'
    }
  },

  // Error messages
  errors: {
    networkError: 'Network Error',
    serverError: 'Server Error',
    validationError: 'Validation Error',
    permissionDenied: 'Permission Denied',
    notFound: 'Not Found',
    timeout: 'Request Timeout',
    unknownError: 'Unknown Error',
    invalidInput: 'Invalid Input',
    requiredField: 'This field is required',
    invalidFormat: 'Invalid Format',
    fileTooLarge: 'File too large',
    unsupportedFileType: 'Unsupported file type',
    logoutFailed: 'Logout failed'
  },

  // Success messages
  success: {
    saveSuccess: 'Save successful',
    deleteSuccess: 'Delete successful',
    updateSuccess: 'Update successful',
    createSuccess: 'Create successful',
    importSuccess: 'Import successful',
    exportSuccess: 'Export successful',
    operationSuccess: 'Operation successful'
  },

  // Confirmation dialogs
  confirm: {
    deleteConfirm: 'Are you sure you want to delete?',
    logoutConfirm: 'Are you sure you want to logout?',
    unsavedChanges: 'You have unsaved changes, are you sure you want to leave?',
    terminateSession: 'Are you sure you want to terminate this session?',
    terminateAllSessions: 'Are you sure you want to terminate all sessions?',
    rollbackVersion: 'Are you sure you want to rollback to this version?'
  }
}
