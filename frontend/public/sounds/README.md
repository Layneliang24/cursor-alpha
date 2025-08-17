# 本地音频文件目录

## 目录结构
```
frontend/public/sounds/
├── words/                    # 单词发音文件
│   ├── hello.mp3            # 单词 "hello" 的发音
│   ├── world.mp3            # 单词 "world" 的发音
│   └── ...                  # 其他单词的发音文件
├── key-sound/                # 键盘声音
│   └── key-default.wav      # 按键音
├── correct.wav               # 正确音效
└── beep.wav                  # 错误音效
```

## 发音文件要求

### 1. 文件格式
- **推荐**: MP3格式（文件小，兼容性好）
- **备选**: WAV格式（音质好，文件大）

### 2. 文件命名
- 使用小写字母
- 单词之间用连字符分隔（如果需要）
- 例如：`hello.mp3`, `good-morning.mp3`

### 3. 音质要求
- **采样率**: 44.1kHz 或 48kHz
- **比特率**: 128kbps 或以上
- **声道**: 单声道或立体声

### 4. 获取方式

#### 方式1: 从qwerty-learner项目复制
```bash
# 复制qwerty-learner的音频文件
cp -r qwerty-learner/public/audio/* frontend/public/sounds/words/
```

#### 方式2: 使用有道词典API下载
```javascript
// 可以编写脚本批量下载单词发音
const word = 'hello'
const url = `https://dict.youdao.com/dictvoice?audio=${word}&type=2`
// 下载并保存为 MP3 文件
```

#### 方式3: 使用在线TTS服务
- Google Translate TTS
- Microsoft Azure Speech
- Amazon Polly

## 性能优化

### 1. 预加载
- 系统会自动预加载常用单词的发音
- 减少播放延迟

### 2. 缓存机制
- 音频文件会被浏览器缓存
- 重复播放无需重新下载

### 3. 压缩优化
- 使用适当的压缩比例
- 平衡文件大小和音质

## 注意事项

1. **文件大小**: 单个文件建议不超过100KB
2. **网络请求**: 本地文件不会产生网络请求
3. **兼容性**: MP3格式在几乎所有浏览器中都支持
4. **版权**: 确保音频文件的版权合规性


