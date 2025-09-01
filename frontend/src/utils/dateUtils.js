/**
 * 日期工具函数
 */

/**
 * 格式化日期时间
 * @param {Date|string} date - 日期对象或日期字符串
 * @param {string} format - 格式化模式，默认为 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的日期字符串
 */
export function formatDateTime(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return ''
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化相对时间
 * @param {Date|string} date - 日期对象或日期字符串
 * @returns {string} 相对时间字符串
 */
export function formatRelativeTime(date) {
  if (!date) return ''
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const diffMinutes = Math.floor(diff / (1000 * 60))
  const diffHours = Math.floor(diff / (1000 * 60 * 60))
  const diffDays = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (diffMinutes < 1) return '刚刚'
  if (diffMinutes < 60) return `${diffMinutes}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  
  return formatDateTime(date, 'YYYY-MM-DD')
}

/**
 * 获取日期范围
 * @param {string} range - 范围类型：'today', 'yesterday', 'week', 'month', 'year'
 * @returns {Object} 包含开始和结束日期的对象
 */
export function getDateRange(range) {
  const now = new Date()
  const start = new Date()
  const end = new Date()
  
  switch (range) {
    case 'today':
      start.setHours(0, 0, 0, 0)
      end.setHours(23, 59, 59, 999)
      break
    case 'yesterday':
      start.setDate(start.getDate() - 1)
      start.setHours(0, 0, 0, 0)
      end.setDate(end.getDate() - 1)
      end.setHours(23, 59, 59, 999)
      break
    case 'week':
      const dayOfWeek = start.getDay()
      start.setDate(start.getDate() - dayOfWeek)
      start.setHours(0, 0, 0, 0)
      end.setDate(end.getDate() + (6 - dayOfWeek))
      end.setHours(23, 59, 59, 999)
      break
    case 'month':
      start.setDate(1)
      start.setHours(0, 0, 0, 0)
      end.setMonth(end.getMonth() + 1)
      end.setDate(0)
      end.setHours(23, 59, 59, 999)
      break
    case 'year':
      start.setMonth(0, 1)
      start.setHours(0, 0, 0, 0)
      end.setMonth(11, 31)
      end.setHours(23, 59, 59, 999)
      break
    default:
      return { start: null, end: null }
  }
  
  return { start, end }
}

/**
 * 检查日期是否有效
 * @param {Date|string} date - 日期对象或日期字符串
 * @returns {boolean} 是否有效
 */
export function isValidDate(date) {
  if (!date) return false
  const d = new Date(date)
  return !isNaN(d.getTime())
}

/**
 * 获取两个日期之间的天数差
 * @param {Date|string} date1 - 第一个日期
 * @param {Date|string} date2 - 第二个日期
 * @returns {number} 天数差
 */
export function getDaysDiff(date1, date2) {
  const d1 = new Date(date1)
  const d2 = new Date(date2)
  
  if (isNaN(d1.getTime()) || isNaN(d2.getTime())) return 0
  
  const diff = Math.abs(d2.getTime() - d1.getTime())
  return Math.floor(diff / (1000 * 60 * 60 * 24))
}

/**
 * 添加天数到日期
 * @param {Date|string} date - 日期对象或日期字符串
 * @param {number} days - 要添加的天数
 * @returns {Date} 新的日期对象
 */
export function addDays(date, days) {
  const d = new Date(date)
  d.setDate(d.getDate() + days)
  return d
}

/**
 * 获取月份名称
 * @param {number} month - 月份（0-11）
 * @param {string} locale - 语言环境，默认为 'zh-CN'
 * @returns {string} 月份名称
 */
export function getMonthName(month, locale = 'zh-CN') {
  const date = new Date(2021, month, 1)
  return date.toLocaleDateString(locale, { month: 'long' })
}

/**
 * 获取星期名称
 * @param {number} day - 星期（0-6）
 * @param {string} locale - 语言环境，默认为 'zh-CN'
 * @returns {string} 星期名称
 */
export function getDayName(day, locale = 'zh-CN') {
  const date = new Date(2021, 0, day + 1)
  return date.toLocaleDateString(locale, { weekday: 'long' })
}
