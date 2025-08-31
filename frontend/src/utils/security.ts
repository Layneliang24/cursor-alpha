/**
 * 安全工具类 - XSS防护和数据转义
 * 基于2024年最新安全实践
 */
import DOMPurify from 'dompurify'

/**
 * HTML内容安全过滤配置
 */
const DEFAULT_PURIFY_CONFIG = {
  ALLOWED_TAGS: [
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'a', 'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'code', 'pre'
  ],
  ALLOWED_ATTR: ['href', 'target', 'rel'],
  ALLOW_DATA_ATTR: false,
  ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|cid|xmpp):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i
}

/**
 * 严格模式配置 - 仅允许基本文本格式
 */
const STRICT_PURIFY_CONFIG = {
  ALLOWED_TAGS: ['strong', 'b', 'em', 'i'],
  ALLOWED_ATTR: [],
  ALLOW_DATA_ATTR: false
}

/**
 * 安全清理HTML内容，防止XSS攻击
 * @param dirty 待清理的HTML字符串
 * @param strict 是否使用严格模式（默认false）
 * @returns 清理后的安全HTML字符串
 */
export const sanitizeHTML = (dirty: string, strict: boolean = false): string => {
  if (!dirty || typeof dirty !== 'string') {
    return ''
  }

  const config = strict ? STRICT_PURIFY_CONFIG : DEFAULT_PURIFY_CONFIG
  return DOMPurify.sanitize(dirty, config)
}

/**
 * 验证并清理URL，防止javascript:协议攻击
 * @param url 待验证的URL
 * @returns 安全的URL或空字符串
 */
export const sanitizeURL = (url: string): string => {
  if (!url || typeof url !== 'string') {
    return ''
  }

  // 移除前后空白字符
  const trimmedUrl = url.trim()
  
  // 检查是否为安全协议
  const safeProtocolRegex = /^(https?:\/\/|mailto:|tel:)/i
  const relativeUrlRegex = /^[./]/
  
  if (safeProtocolRegex.test(trimmedUrl) || relativeUrlRegex.test(trimmedUrl)) {
    return trimmedUrl
  }
  
  // 如果不是安全协议，返回空字符串
  return ''
}

/**
 * 转义特殊字符，防止XSS攻击
 * @param text 待转义的文本
 * @returns 转义后的安全文本
 */
export const escapeHTML = (text: string): string => {
  if (!text || typeof text !== 'string') {
    return ''
  }

  const escapeMap: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  }

  return text.replace(/[&<>"'\/]/g, (char) => escapeMap[char])
}

/**
 * 验证输入内容是否包含潜在的XSS攻击向量
 * @param input 用户输入内容
 * @returns 是否包含危险内容
 */
export const containsXSSVectors = (input: string): boolean => {
  if (!input || typeof input !== 'string') {
    return false
  }

  const xssPatterns = [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi,
    /<iframe\b/gi,
    /<object\b/gi,
    /<embed\b/gi,
    /<form\b/gi,
    /data:text\/html/gi,
    /vbscript:/gi,
    /expression\s*\(/gi
  ]

  return xssPatterns.some(pattern => pattern.test(input))
}

/**
 * 清理用户输入的文本内容
 * @param input 用户输入
 * @param maxLength 最大长度限制
 * @returns 清理后的安全文本
 */
export const sanitizeUserInput = (input: string, maxLength: number = 1000): string => {
  if (!input || typeof input !== 'string') {
    return ''
  }

  // 移除前后空白字符
  let cleaned = input.trim()
  
  // 长度限制
  if (cleaned.length > maxLength) {
    cleaned = cleaned.substring(0, maxLength)
  }
  
  // 移除潜在危险字符
  cleaned = cleaned.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '')
  
  // 转义HTML特殊字符
  return escapeHTML(cleaned)
}

/**
 * 验证文件名是否安全
 * @param filename 文件名
 * @returns 是否为安全的文件名
 */
export const isSecureFilename = (filename: string): boolean => {
  if (!filename || typeof filename !== 'string') {
    return false
  }

  // 检查文件名长度
  if (filename.length > 255) {
    return false
  }

  // 检查危险字符
  const dangerousChars = /[<>:"|?*\x00-\x1f]/
  if (dangerousChars.test(filename)) {
    return false
  }

  // 检查路径遍历攻击
  if (filename.includes('..') || filename.includes('./') || filename.includes('.\\')) {
    return false
  }

  // 检查保留名称（Windows）
  const reservedNames = /^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|$)/i
  if (reservedNames.test(filename)) {
    return false
  }

  return true
}

/**
 * Content Security Policy 配置生成器
 */
export const generateCSPHeader = (config: {
  scriptSrc?: string[]
  styleSrc?: string[]
  imgSrc?: string[]
  connectSrc?: string[]
  fontSrc?: string[]
  objectSrc?: string[]
  mediaSrc?: string[]
  frameSrc?: string[]
}) => {
  const directives = []
  
  // 默认源
  directives.push("default-src 'self'")
  
  // 脚本源
  const scriptSrc = config.scriptSrc || ["'self'", "'unsafe-eval'"]
  directives.push(`script-src ${scriptSrc.join(' ')}`)
  
  // 样式源
  const styleSrc = config.styleSrc || ["'self'", "'unsafe-inline'"]
  directives.push(`style-src ${styleSrc.join(' ')}`)
  
  // 图片源
  const imgSrc = config.imgSrc || ["'self'", "data:", "https:"]
  directives.push(`img-src ${imgSrc.join(' ')}`)
  
  // 连接源
  const connectSrc = config.connectSrc || ["'self'"]
  directives.push(`connect-src ${connectSrc.join(' ')}`)
  
  // 字体源
  const fontSrc = config.fontSrc || ["'self'", "data:", "https:"]
  directives.push(`font-src ${fontSrc.join(' ')}`)
  
  // 对象源
  const objectSrc = config.objectSrc || ["'none'"]
  directives.push(`object-src ${objectSrc.join(' ')}`)
  
  // 媒体源
  const mediaSrc = config.mediaSrc || ["'self'"]
  directives.push(`media-src ${mediaSrc.join(' ')}`)
  
  // 框架源
  const frameSrc = config.frameSrc || ["'none'"]
  directives.push(`frame-src ${frameSrc.join(' ')}`)
  
  // 基础安全指令
  directives.push("base-uri 'self'")
  directives.push("form-action 'self'")
  directives.push("frame-ancestors 'none'")
  directives.push("upgrade-insecure-requests")
  
  return directives.join('; ')
}

/**
 * 安全配置常量
 */
export const SECURITY_CONFIG = {
  // 最大输入长度
  MAX_INPUT_LENGTH: {
    TITLE: 100,
    DESCRIPTION: 500,
    CONTENT: 5000,
    URL: 2048,
    EMAIL: 254,
    FILENAME: 255
  },
  
  // 允许的文件类型
  ALLOWED_FILE_TYPES: {
    IMAGE: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'],
    DOCUMENT: ['pdf', 'doc', 'docx', 'txt', 'md'],
    ARCHIVE: ['zip', 'tar', 'gz']
  },
  
  // CSP配置
  DEFAULT_CSP: generateCSPHeader({
    connectSrc: ["'self'", "https://api.siliconflow.cn", "https://openrouter.ai", "https://api.openai.com"]
  })
} as const

export default {
  sanitizeHTML,
  sanitizeURL,
  escapeHTML,
  containsXSSVectors,
  sanitizeUserInput,
  isSecureFilename,
  generateCSPHeader,
  SECURITY_CONFIG
}
