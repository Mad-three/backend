"""
오디오 처리 유틸리티 함수들
Google Cloud Speech-to-Text API를 사용한 단일 오디오 파일 처리
"""

from google.cloud import speech


async def transcribe_audio(audio_data: bytes, language_code: str = "ko-KR") -> str:
    """
    오디오 데이터를 텍스트로 변환하는 함수 (배치 처리용)
    
    Args:
        audio_data: 오디오 바이너리 데이터
        language_code: 언어 코드 (기본값: 한국어)
    
    Returns:
        변환된 텍스트 문자열
    """
    try:
        # Google STT API 클라이언트 생성
        speech_client = speech.SpeechClient()
        
        # Google STT API 설정
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code=language_code,
            enable_automatic_punctuation=True,
            enable_word_time_offsets=False,
        )
        
        # 오디오 데이터 설정
        audio = speech.RecognitionAudio(content=audio_data)
        
        # 음성 인식 실행
        response = speech_client.recognize(config=config, audio=audio)
        
        # 결과 처리
        if response.results:
            transcript = response.results[0].alternatives[0].transcript
            confidence = response.results[0].alternatives[0].confidence
            print(f"배치 음성 인식 결과: {transcript} (신뢰도: {confidence:.2f})")
            return transcript
        else:
            print("음성 인식 결과가 없습니다.")
            return ""
            
    except Exception as e:
        print(f"음성 인식 오류: {str(e)}")
        return f"음성 인식 처리 중 오류가 발생했습니다: {str(e)}"


def validate_audio_format(audio_format: str) -> bool:
    """
    지원되는 오디오 형식인지 검증
    
    Args:
        audio_format: 오디오 형식 문자열 (예: "audio/webm")
    
    Returns:
        지원 여부 (True/False)
    """
    supported_formats = [
        "audio/webm",
        "audio/wav", 
        "audio/mp3",
        "audio/ogg",
        "audio/flac"
    ]
    return audio_format.lower() in supported_formats


def get_supported_languages():
    """
    지원되는 언어 코드 목록 반환
    
    Returns:
        지원되는 언어 코드 딕셔너리
    """
    return {
        "ko-KR": "한국어",
        "en-US": "영어 (미국)",
        "ja-JP": "일본어",
        "zh-CN": "중국어 (간체)",
        "es-ES": "스페인어",
        "fr-FR": "프랑스어",
        "de-DE": "독일어",
        "it-IT": "이탈리아어",
        "pt-BR": "포르투갈어 (브라질)",
        "ru-RU": "러시아어"
    }


def validate_language_code(language_code: str) -> bool:
    """
    언어 코드가 유효한지 검증
    
    Args:
        language_code: 언어 코드 (예: "ko-KR")
    
    Returns:
        유효 여부 (True/False)
    """
    supported_languages = get_supported_languages()
    return language_code in supported_languages


def get_audio_encoding_from_format(audio_format: str) -> speech.RecognitionConfig.AudioEncoding:
    """
    오디오 형식에 따른 Google STT 인코딩 타입 반환
    
    Args:
        audio_format: 오디오 형식 문자열
    
    Returns:
        Google STT AudioEncoding 열거형
    """
    format_mapping = {
        "audio/webm": speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        "audio/wav": speech.RecognitionConfig.AudioEncoding.LINEAR16,
        "audio/mp3": speech.RecognitionConfig.AudioEncoding.MP3,
        "audio/ogg": speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        "audio/flac": speech.RecognitionConfig.AudioEncoding.FLAC,
    }
    
    return format_mapping.get(
        audio_format.lower(), 
        speech.RecognitionConfig.AudioEncoding.WEBM_OPUS  # 기본값
    )
