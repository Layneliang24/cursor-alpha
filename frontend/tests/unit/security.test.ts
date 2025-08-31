/**
 * 安全工具类测试
 * 测试XSS防护、数据转义和输入验证功能
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { 
  sanitizeHTML, 
  sanitizeURL, 
  escapeHTML, 
  containsXSSVectors,
  sanitizeUserInput,
  isSecureFilename,
  generateCSPHeader,
  SECURITY_CONFIG
} from '@/utils/security'

describe('Security Utils', () => {
  describe('sanitizeHTML', () => {
    it('应该清理XSS攻击向量', () => {
      const xssPayloads = [
        '<script>alert("xss")</script>',
        '<img src=x onerror=alert(1)>',
        '<iframe src="javascript:alert(1)"></iframe>',
        '<svg onload=alert(1)>',
        '<body onload=alert(1)>',
        '<div onclick="alert(1)">点击我</div>'
      ]
      
      xssPayloads.forEach(payload => {
        const result = sanitizeHTML(payload)
        expect(result).not.toContain('script')
        expect(result).not.toContain('onerror')
        expect(result).not.toContain('onload')
        expect(result).not.toContain('onclick')
        expect(result).not.toContain('javascript:')
      })
    })
    
    it('应该保留安全的HTML标签', () => {
      const safeHTML = '<p>这是<strong>安全的</strong><em>HTML</em>内容</p>'
      const result = sanitizeHTML(safeHTML)
      
      expect(result).toContain('<p>')
      expect(result).toContain('<strong>')
      expect(result).toContain('<em>')
      expect(result).toContain('安全的')
    })
    
    it('严格模式应该只保留基本格式标签', () => {
      const html = '<p>段落</p><strong>加粗</strong><a href="http://example.com">链接</a>'
      const result = sanitizeHTML(html, true)
      
      expect(result).toContain('<strong>')
      expect(result).not.toContain('<p>')
      expect(result).not.toContain('<a>')
    })
    
    it('应该处理空值和非字符串输入', () => {
      expect(sanitizeHTML('')).toBe('')
      expect(sanitizeHTML(null as any)).toBe('')
      expect(sanitizeHTML(undefined as any)).toBe('')
      expect(sanitizeHTML(123 as any)).toBe('')
    })
  })
  
  describe('sanitizeURL', () => {
    it('应该允许安全的URL', () => {
      const safeURLs = [
        'https://example.com',
        'http://localhost:3000',
        'mailto:test@example.com',
        'tel:+1234567890',
        './relative/path',
        '/absolute/path'
      ]
      
      safeURLs.forEach(url => {
        const result = sanitizeURL(url)
        expect(result).toBe(url)
      })
    })
    
    it('应该拒绝危险的URL', () => {
      const dangerousURLs = [
        'javascript:alert(1)',
        'data:text/html,<script>alert(1)</script>',
        'vbscript:msgbox(1)',
        'file:///etc/passwd',
        'ftp://malicious.com'
      ]
      
      dangerousURLs.forEach(url => {
        const result = sanitizeURL(url)
        expect(result).toBe('')
      })
    })
    
    it('应该处理空值和非字符串输入', () => {
      expect(sanitizeURL('')).toBe('')
      expect(sanitizeURL(null as any)).toBe('')
      expect(sanitizeURL(undefined as any)).toBe('')
    })
  })
  
  describe('escapeHTML', () => {
    it('应该转义HTML特殊字符', () => {
      const input = '<div>Hello & "World" \'test\' /path</div>'
      const result = escapeHTML(input)
      
      expect(result).toBe('&lt;div&gt;Hello &amp; &quot;World&quot; &#x27;test&#x27; &#x2F;path&lt;&#x2F;div&gt;')
    })
    
    it('应该处理空值', () => {
      expect(escapeHTML('')).toBe('')
      expect(escapeHTML(null as any)).toBe('')
    })
  })
  
  describe('containsXSSVectors', () => {
    it('应该检测XSS攻击向量', () => {
      const xssVectors = [
        '<script>alert(1)</script>',
        'javascript:alert(1)',
        '<img onerror=alert(1)>',
        '<iframe src="data:text/html,<script>alert(1)</script>">',
        '<object data="javascript:alert(1)">',
        '<embed src="javascript:alert(1)">',
        '<form action="javascript:alert(1)">',
        'vbscript:msgbox(1)',
        'expression(alert(1))'
      ]
      
      xssVectors.forEach(vector => {
        expect(containsXSSVectors(vector)).toBe(true)
      })
    })
    
    it('应该允许安全内容', () => {
      const safeContent = [
        '普通文本内容',
        'Hello World',
        '这是安全的内容',
        '数字123和符号!@#',
        'email@example.com'
      ]
      
      safeContent.forEach(content => {
        expect(containsXSSVectors(content)).toBe(false)
      })
    })
  })
  
  describe('sanitizeUserInput', () => {
    it('应该清理用户输入', () => {
      const input = '  <script>alert(1)</script>用户输入  '
      const result = sanitizeUserInput(input)
      
      expect(result).not.toContain('<script>')
      expect(result).toContain('用户输入')
      expect(result).not.toMatch(/^\s|\s$/) // 不应该有前后空白
    })
    
    it('应该限制输入长度', () => {
      const longInput = 'A'.repeat(2000)
      const result = sanitizeUserInput(longInput, 100)
      
      expect(result.length).toBeLessThanOrEqual(100)
    })
    
    it('应该移除控制字符', () => {
      const input = 'normal\x00text\x1fwith\x7fcontrol\x08chars'
      const result = sanitizeUserInput(input)
      
      expect(result).toBe('normaltextwithcontrolchars')
    })
  })
  
  describe('isSecureFilename', () => {
    it('应该允许安全的文件名', () => {
      const safeFilenames = [
        'document.pdf',
        'image_001.jpg',
        'data-file.json',
        'report_2024.xlsx',
        '配置文件.txt'
      ]
      
      safeFilenames.forEach(filename => {
        expect(isSecureFilename(filename)).toBe(true)
      })
    })
    
    it('应该拒绝危险的文件名', () => {
      const dangerousFilenames = [
        '../../../etc/passwd',
        'file<script>.txt',
        'document|pipe.pdf',
        'CON.txt',  // Windows保留名称
        'file?.txt',
        'very-long-filename-that-exceeds-the-maximum-allowed-length-for-filenames-in-most-filesystems-and-should-be-rejected.txt'.repeat(10)
      ]
      
      dangerousFilenames.forEach(filename => {
        expect(isSecureFilename(filename)).toBe(false)
      })
    })
  })
  
  describe('generateCSPHeader', () => {
    it('应该生成有效的CSP头', () => {
      const config = {
        scriptSrc: ["'self'", "'unsafe-eval'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", "data:", "https:"]
      }
      
      const csp = generateCSPHeader(config)
      
      expect(csp).toContain("default-src 'self'")
      expect(csp).toContain("script-src 'self' 'unsafe-eval'")
      expect(csp).toContain("style-src 'self' 'unsafe-inline'")
      expect(csp).toContain("object-src 'none'")
      expect(csp).toContain("frame-src 'none'")
    })
    
    it('应该使用默认配置', () => {
      const csp = generateCSPHeader({})
      
      expect(csp).toContain("default-src 'self'")
      expect(csp).toContain("upgrade-insecure-requests")
    })
  })
  
  describe('SECURITY_CONFIG', () => {
    it('应该包含正确的配置常量', () => {
      expect(SECURITY_CONFIG.MAX_INPUT_LENGTH.TITLE).toBe(100)
      expect(SECURITY_CONFIG.MAX_INPUT_LENGTH.EMAIL).toBe(254)
      expect(SECURITY_CONFIG.MAX_INPUT_LENGTH.URL).toBe(2048)
      
      expect(SECURITY_CONFIG.ALLOWED_FILE_TYPES.IMAGE).toContain('jpg')
      expect(SECURITY_CONFIG.ALLOWED_FILE_TYPES.IMAGE).toContain('png')
      
      expect(SECURITY_CONFIG.DEFAULT_CSP).toContain("default-src 'self'")
    })
  })
})

describe('Security Integration', () => {
  it('应该正确集成DOMPurify', () => {
    // 测试DOMPurify是否正确加载和配置
    const maliciousHTML = '<script>alert("xss")</script><p>正常内容</p>'
    const result = sanitizeHTML(maliciousHTML)
    
    expect(result).not.toContain('<script>')
    expect(result).toContain('<p>正常内容</p>')
  })
  
  it('应该在生产环境中启用严格模式', () => {
    // 模拟生产环境
    const originalNodeEnv = process.env.NODE_ENV
    process.env.NODE_ENV = 'production'
    
    try {
      // 在生产环境中，某些功能应该更严格
      const result = sanitizeHTML('<div onclick="alert(1)">内容</div>', true)
      expect(result).not.toContain('onclick')
    } finally {
      process.env.NODE_ENV = originalNodeEnv
    }
  })
})
