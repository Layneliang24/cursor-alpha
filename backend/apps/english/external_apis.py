"""
外部API集成服务
提供词典查询、TTS语音合成、语音识别等功能
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache
import hashlib
import time

logger = logging.getLogger(__name__)


class DictionaryAPIService:
    """词典API服务"""
    
    def __init__(self):
        self.oxford_api_id = getattr(settings, 'OXFORD_API_ID', '')
        self.oxford_api_key = getattr(settings, 'OXFORD_API_KEY', '')
        self.youdao_app_key = getattr(settings, 'YOUDAO_APP_KEY', '')
        self.youdao_app_secret = getattr(settings, 'YOUDAO_APP_SECRET', '')
        
    def get_word_definition(self, word: str, source: str = 'auto') -> Dict[str, Any]:
        """
        获取单词释义
        :param word: 单词
        :param source: 词典源 ('oxford', 'youdao', 'auto')
        :return: 词典数据
        """
        # 缓存键
        cache_key = f"dict_{source}_{word.lower()}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
            
        try:
            if source == 'oxford' and self.oxford_api_id and self.oxford_api_key:
                result = self._query_oxford_dictionary(word)
            elif source == 'youdao' and self.youdao_app_key and self.youdao_app_secret:
                result = self._query_youdao_dictionary(word)
            else:
                # 自动选择可用的API
                result = self._query_auto_dictionary(word)
            
            # 缓存结果1小时
            if result:
                cache.set(cache_key, result, 3600)
                
            return result
            
        except Exception as e:
            logger.error(f"词典查询失败: {word}, error: {str(e)}")
            return self._get_fallback_definition(word)
    
    def _query_oxford_dictionary(self, word: str) -> Dict[str, Any]:
        """查询牛津词典API"""
        url = f"https://od-api.oxforddictionaries.com/api/v2/entries/en-gb/{word.lower()}"
        headers = {
            'app_id': self.oxford_api_id,
            'app_key': self.oxford_api_key
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return self._parse_oxford_response(data)
        else:
            logger.warning(f"Oxford API请求失败: {response.status_code}")
            return {}
    
    def _query_youdao_dictionary(self, word: str) -> Dict[str, Any]:
        """查询有道词典API"""
        def encrypt(signStr):
            hash_algorithm = hashlib.sha256()
            hash_algorithm.update(signStr.encode('utf-8'))
            return hash_algorithm.hexdigest()
        
        def truncate(q):
            if q is None:
                return None
            size = len(q)
            return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]
        
        curtime = str(int(time.time()))
        salt = str(int(time.time() * 1000))
        signStr = self.youdao_app_key + truncate(word) + salt + curtime + self.youdao_app_secret
        sign = encrypt(signStr)
        
        url = 'https://openapi.youdao.com/api'
        params = {
            'q': word,
            'from': 'en',
            'to': 'zh-CHS',
            'appKey': self.youdao_app_key,
            'salt': salt,
            'sign': sign,
            'signType': 'v3',
            'curtime': curtime,
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return self._parse_youdao_response(data)
        else:
            logger.warning(f"有道API请求失败: {response.status_code}")
            return {}
    
    def _query_auto_dictionary(self, word: str) -> Dict[str, Any]:
        """自动选择可用的词典API"""
        # 优先使用牛津词典
        if self.oxford_api_id and self.oxford_api_key:
            result = self._query_oxford_dictionary(word)
            if result:
                return result
        
        # 备用有道词典
        if self.youdao_app_key and self.youdao_app_secret:
            result = self._query_youdao_dictionary(word)
            if result:
                return result
        
        # 都不可用时返回空结果
        return {}
    
    def _parse_oxford_response(self, data: Dict) -> Dict[str, Any]:
        """解析牛津词典响应"""
        try:
            results = data.get('results', [])
            if not results:
                return {}
            
            entry = results[0]
            lexical_entries = entry.get('lexicalEntries', [])
            
            parsed_data = {
                'word': entry.get('word', ''),
                'phonetics': [],
                'definitions': [],
                'examples': [],
                'etymology': '',
                'source': 'oxford'
            }
            
            for lexical_entry in lexical_entries:
                part_of_speech = lexical_entry.get('lexicalCategory', {}).get('text', '')
                
                # 获取音标
                pronunciations = lexical_entry.get('pronunciations', [])
                for pron in pronunciations:
                    if 'phoneticSpelling' in pron:
                        parsed_data['phonetics'].append({
                            'text': pron['phoneticSpelling'],
                            'audio': pron.get('audioFile', '')
                        })
                
                # 获取释义和例句
                entries = lexical_entry.get('entries', [])
                for entry_item in entries:
                    senses = entry_item.get('senses', [])
                    for sense in senses:
                        definitions = sense.get('definitions', [])
                        for definition in definitions:
                            parsed_data['definitions'].append({
                                'part_of_speech': part_of_speech,
                                'definition': definition
                            })
                        
                        examples = sense.get('examples', [])
                        for example in examples:
                            parsed_data['examples'].append(example.get('text', ''))
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"解析牛津词典响应失败: {str(e)}")
            return {}
    
    def _parse_youdao_response(self, data: Dict) -> Dict[str, Any]:
        """解析有道词典响应"""
        try:
            if data.get('errorCode') != '0':
                return {}
            
            basic = data.get('basic', {})
            
            parsed_data = {
                'word': data.get('query', ''),
                'phonetics': [],
                'definitions': [],
                'examples': [],
                'etymology': '',
                'source': 'youdao'
            }
            
            # 获取音标
            if 'phonetic' in basic:
                parsed_data['phonetics'].append({
                    'text': basic['phonetic'],
                    'audio': ''
                })
            
            # 获取释义
            explains = basic.get('explains', [])
            for explain in explains:
                parsed_data['definitions'].append({
                    'part_of_speech': '',
                    'definition': explain
                })
            
            # 获取例句
            web = data.get('web', [])
            for item in web:
                if 'value' in item:
                    for value in item['value'][:3]:  # 最多3个例句
                        parsed_data['examples'].append(value)
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"解析有道词典响应失败: {str(e)}")
            return {}
    
    def _get_fallback_definition(self, word: str) -> Dict[str, Any]:
        """获取备用释义（当所有API都不可用时）"""
        return {
            'word': word,
            'phonetics': [],
            'definitions': [{'part_of_speech': '', 'definition': '暂无释义'}],
            'examples': [],
            'etymology': '',
            'source': 'fallback'
        }


class TTSService:
    """TTS语音合成服务"""
    
    def __init__(self):
        self.google_api_key = getattr(settings, 'GOOGLE_CLOUD_API_KEY', '')
        self.azure_api_key = getattr(settings, 'AZURE_SPEECH_API_KEY', '')
        self.azure_region = getattr(settings, 'AZURE_SPEECH_REGION', '')
    
    def generate_speech(self, text: str, language: str = 'en-US', voice: str = 'auto') -> Dict[str, Any]:
        """
        生成语音
        :param text: 要转换的文本
        :param language: 语言代码
        :param voice: 语音类型
        :return: 语音数据
        """
        cache_key = f"tts_{hashlib.md5(f'{text}_{language}_{voice}'.encode()).hexdigest()}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            if self.google_api_key:
                result = self._generate_google_tts(text, language, voice)
            elif self.azure_api_key:
                result = self._generate_azure_tts(text, language, voice)
            else:
                result = self._generate_browser_tts(text, language)
            
            if result:
                cache.set(cache_key, result, 7200)  # 缓存2小时
            
            return result
            
        except Exception as e:
            logger.error(f"TTS生成失败: {text}, error: {str(e)}")
            return self._generate_browser_tts(text, language)
    
    def _generate_google_tts(self, text: str, language: str, voice: str) -> Dict[str, Any]:
        """Google Cloud TTS"""
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.google_api_key}"
        
        # 选择语音
        voice_name = self._get_google_voice_name(language, voice)
        
        payload = {
            "input": {"text": text},
            "voice": {
                "languageCode": language,
                "name": voice_name,
                "ssmlGender": "FEMALE"
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": 0.9,
                "pitch": 0.0,
                "volumeGainDb": 0.0
            }
        }
        
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'audio_content': data.get('audioContent', ''),
                'format': 'mp3',
                'source': 'google',
                'success': True
            }
        else:
            logger.warning(f"Google TTS请求失败: {response.status_code}")
            return {}
    
    def _generate_azure_tts(self, text: str, language: str, voice: str) -> Dict[str, Any]:
        """Azure Speech Service TTS"""
        url = f"https://{self.azure_region}.tts.speech.microsoft.com/cognitiveservices/v1"
        
        headers = {
            'Ocp-Apim-Subscription-Key': self.azure_api_key,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3'
        }
        
        voice_name = self._get_azure_voice_name(language, voice)
        
        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{language}'>
            <voice name='{voice_name}'>
                <prosody rate='0.9' pitch='0%'>
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        
        response = requests.post(url, headers=headers, data=ssml.strip(), timeout=15)
        
        if response.status_code == 200:
            import base64
            audio_content = base64.b64encode(response.content).decode('utf-8')
            return {
                'audio_content': audio_content,
                'format': 'mp3',
                'source': 'azure',
                'success': True
            }
        else:
            logger.warning(f"Azure TTS请求失败: {response.status_code}")
            return {}
    
    def _generate_browser_tts(self, text: str, language: str) -> Dict[str, Any]:
        """浏览器TTS（备用方案）"""
        return {
            'audio_content': '',
            'format': 'browser',
            'source': 'browser',
            'success': True,
            'text': text,
            'language': language,
            'message': '使用浏览器内置TTS'
        }
    
    def _get_google_voice_name(self, language: str, voice: str) -> str:
        """获取Google TTS语音名称"""
        voice_mapping = {
            'en-US': {
                'female': 'en-US-Wavenet-F',
                'male': 'en-US-Wavenet-B',
                'auto': 'en-US-Wavenet-F'
            },
            'en-GB': {
                'female': 'en-GB-Wavenet-A',
                'male': 'en-GB-Wavenet-B',
                'auto': 'en-GB-Wavenet-A'
            }
        }
        
        return voice_mapping.get(language, {}).get(voice, 'en-US-Wavenet-F')
    
    def _get_azure_voice_name(self, language: str, voice: str) -> str:
        """获取Azure TTS语音名称"""
        voice_mapping = {
            'en-US': {
                'female': 'en-US-JennyNeural',
                'male': 'en-US-GuyNeural',
                'auto': 'en-US-JennyNeural'
            },
            'en-GB': {
                'female': 'en-GB-LibbyNeural',
                'male': 'en-GB-RyanNeural',
                'auto': 'en-GB-LibbyNeural'
            }
        }
        
        return voice_mapping.get(language, {}).get(voice, 'en-US-JennyNeural')


class SpeechRecognitionService:
    """语音识别服务"""
    
    def __init__(self):
        self.google_api_key = getattr(settings, 'GOOGLE_CLOUD_API_KEY', '')
        self.azure_api_key = getattr(settings, 'AZURE_SPEECH_API_KEY', '')
        self.azure_region = getattr(settings, 'AZURE_SPEECH_REGION', '')
    
    def recognize_speech(self, audio_data: bytes, language: str = 'en-US') -> Dict[str, Any]:
        """
        语音识别
        :param audio_data: 音频数据
        :param language: 语言代码
        :return: 识别结果
        """
        try:
            if self.google_api_key:
                result = self._recognize_google_speech(audio_data, language)
            elif self.azure_api_key:
                result = self._recognize_azure_speech(audio_data, language)
            else:
                result = self._recognize_mock_speech(audio_data, language)
            
            return result
            
        except Exception as e:
            logger.error(f"语音识别失败: {str(e)}")
            return self._recognize_mock_speech(audio_data, language)
    
    def _recognize_google_speech(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """Google Cloud Speech-to-Text"""
        import base64
        
        url = f"https://speech.googleapis.com/v1/speech:recognize?key={self.google_api_key}"
        
        audio_content = base64.b64encode(audio_data).decode('utf-8')
        
        payload = {
            "config": {
                "encoding": "WEBM_OPUS",
                "sampleRateHertz": 48000,
                "languageCode": language,
                "enableAutomaticPunctuation": True,
                "model": "latest_long"
            },
            "audio": {
                "content": audio_content
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if results:
                transcript = results[0]['alternatives'][0]['transcript']
                confidence = results[0]['alternatives'][0].get('confidence', 0.0)
                
                return {
                    'transcript': transcript,
                    'confidence': confidence,
                    'source': 'google',
                    'success': True
                }
        
        logger.warning(f"Google Speech API请求失败: {response.status_code}")
        return {}
    
    def _recognize_azure_speech(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """Azure Speech Service"""
        url = f"https://{self.azure_region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
        
        headers = {
            'Ocp-Apim-Subscription-Key': self.azure_api_key,
            'Content-Type': 'audio/wav; codecs=audio/pcm; samplerate=16000',
            'Accept': 'application/json'
        }
        
        params = {
            'language': language,
            'format': 'detailed'
        }
        
        response = requests.post(url, headers=headers, params=params, data=audio_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('RecognitionStatus') == 'Success':
                return {
                    'transcript': data.get('DisplayText', ''),
                    'confidence': data.get('Confidence', 0.0),
                    'source': 'azure',
                    'success': True
                }
        
        logger.warning(f"Azure Speech API请求失败: {response.status_code}")
        return {}
    
    def _recognize_mock_speech(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """模拟语音识别（备用方案）"""
        # 简单的模拟识别，实际项目中这里会返回空或错误
        return {
            'transcript': 'Mock recognition result',
            'confidence': 0.5,
            'source': 'mock',
            'success': False,
            'message': '语音识别服务不可用，请配置API密钥'
        }


class PronunciationEvaluationService:
    """发音评估服务"""
    
    def __init__(self):
        self.speech_service = SpeechRecognitionService()
        self.dictionary_service = DictionaryAPIService()
    
    def evaluate_pronunciation(self, audio_data: bytes, target_word: str, language: str = 'en-US') -> Dict[str, Any]:
        """
        评估发音质量
        :param audio_data: 音频数据
        :param target_word: 目标单词
        :param language: 语言代码
        :return: 评估结果
        """
        try:
            # 1. 语音识别
            recognition_result = self.speech_service.recognize_speech(audio_data, language)
            
            if not recognition_result.get('success'):
                return self._generate_fallback_evaluation()
            
            recognized_text = recognition_result.get('transcript', '').strip().lower()
            target_word_lower = target_word.lower()
            
            # 2. 计算相似度和评分
            accuracy_score = self._calculate_accuracy(recognized_text, target_word_lower)
            fluency_score = self._calculate_fluency(recognition_result)
            completeness_score = self._calculate_completeness(recognized_text, target_word_lower)
            
            # 3. 综合评分
            overall_score = int((accuracy_score * 0.5 + fluency_score * 0.3 + completeness_score * 0.2))
            
            # 4. 生成建议
            suggestions = self._generate_suggestions(accuracy_score, fluency_score, completeness_score, overall_score)
            
            return {
                'overall_score': overall_score,
                'accuracy': round(accuracy_score / 20, 1),  # 转换为5分制
                'fluency': round(fluency_score / 20, 1),
                'completeness': round(completeness_score / 20, 1),
                'recognized_text': recognized_text,
                'target_word': target_word,
                'confidence': recognition_result.get('confidence', 0.0),
                'suggestions': suggestions,
                'source': recognition_result.get('source', 'unknown'),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"发音评估失败: {str(e)}")
            return self._generate_fallback_evaluation()
    
    def _calculate_accuracy(self, recognized: str, target: str) -> float:
        """计算准确度分数"""
        if not recognized or not target:
            return 0.0
        
        # 简单的字符串相似度计算
        if recognized == target:
            return 100.0
        
        # 使用编辑距离计算相似度
        distance = self._levenshtein_distance(recognized, target)
        max_len = max(len(recognized), len(target))
        
        if max_len == 0:
            return 100.0
        
        similarity = (max_len - distance) / max_len
        return max(0.0, min(100.0, similarity * 100))
    
    def _calculate_fluency(self, recognition_result: Dict) -> float:
        """计算流畅度分数"""
        confidence = recognition_result.get('confidence', 0.0)
        
        # 基于识别置信度计算流畅度
        if confidence >= 0.9:
            return 95.0
        elif confidence >= 0.7:
            return 80.0
        elif confidence >= 0.5:
            return 65.0
        else:
            return 50.0
    
    def _calculate_completeness(self, recognized: str, target: str) -> float:
        """计算完整度分数"""
        if not recognized:
            return 0.0
        
        # 检查是否包含目标单词的主要部分
        target_words = target.split()
        recognized_words = recognized.split()
        
        if not target_words:
            return 100.0
        
        matches = 0
        for target_word in target_words:
            for recognized_word in recognized_words:
                if target_word in recognized_word or recognized_word in target_word:
                    matches += 1
                    break
        
        return min(100.0, (matches / len(target_words)) * 100)
    
    def _generate_suggestions(self, accuracy: float, fluency: float, completeness: float, overall: int) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if accuracy < 70:
            suggestions.append("注意单词的准确发音，建议多听标准发音并模仿")
        if fluency < 70:
            suggestions.append("尝试更自然流畅地发音，减少停顿和犹豫")
        if completeness < 70:
            suggestions.append("确保完整清晰地读出整个单词")
        
        if overall >= 90:
            suggestions.append("发音非常棒！继续保持这个水平")
        elif overall >= 75:
            suggestions.append("发音不错，继续练习会更好")
        elif overall >= 60:
            suggestions.append("发音有待改进，建议多加练习")
        else:
            suggestions.append("需要大量练习，建议从基础音标开始学习")
        
        return suggestions if suggestions else ["继续练习，你会越来越好！"]
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """计算编辑距离"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _generate_fallback_evaluation(self) -> Dict[str, Any]:
        """生成备用评估结果"""
        import random
        
        base_score = random.randint(60, 85)
        return {
            'overall_score': base_score,
            'accuracy': round(random.uniform(3.0, 4.5), 1),
            'fluency': round(random.uniform(3.0, 4.5), 1),
            'completeness': round(random.uniform(3.0, 4.5), 1),
            'recognized_text': '',
            'target_word': '',
            'confidence': 0.0,
            'suggestions': ['语音识别服务暂不可用，这是模拟评分', '建议配置外部API以获得准确评估'],
            'source': 'fallback',
            'success': False
        }


# 服务实例
dictionary_service = DictionaryAPIService()
tts_service = TTSService()
speech_recognition_service = SpeechRecognitionService()
pronunciation_evaluation_service = PronunciationEvaluationService()

