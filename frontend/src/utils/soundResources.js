// 声音资源管理
export const SOUND_URL_PREFIX = '/sounds/'
export const KEY_SOUND_URL_PREFIX = '/sounds/keys/'

// 按键声音资源
export const keySoundResources = [
  {
    key: 'Default',
    filename: 'key-default.wav',
    name: '默认按键音'
  },
  {
    key: 'Mechanical',
    filename: 'key-mechanical.mp3', 
    name: '机械键盘音'
  },
  {
    key: 'Soft',
    filename: 'key-soft.mp3',
    name: '轻柔按键音'
  }
]

// 提示声音资源
export const hintSoundResources = [
  {
    key: 'Default',
    filename: 'hint-default.mp3',
    name: '默认提示音'
  },
  {
    key: 'Correct',
    filename: 'correct.wav',
    name: '正确提示音'
  },
  {
    key: 'Wrong',
    filename: 'beep.wav',
    name: '错误提示音'
  }
]

// 生成单词发音URL (使用有道词典API)
export function generateWordSoundSrc(word, type = 'us') {
  const pronunciationApi = 'https://dict.youdao.com/dictvoice?audio='
  switch (type) {
    case 'uk':
      return `${pronunciationApi}${word}&type=1`
    case 'us':
    default:
      return `${pronunciationApi}${word}&type=2`
  }
}

// 使用qwerty-learner的音频文件
export const defaultSounds = {
  keySound: '/sounds/key-default.wav',
  correctSound: '/sounds/correct.wav', 
  wrongSound: '/sounds/beep.wav'
}
