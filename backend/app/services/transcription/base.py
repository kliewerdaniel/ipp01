from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


class TranscriptionResult(BaseModel):
    """Result model for transcription services"""
    text: str
    confidence: float = 1.0
    language: str = "en"
    words: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class RateLimitConfig(BaseModel):
    """Configuration for rate limiting"""
    requests_per_minute: int = 60
    requests_per_day: int = 1000
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds


class TranscriptionServiceError(Exception):
    """Base exception for transcription service errors"""
    pass


class RateLimitExceededError(TranscriptionServiceError):
    """Exception raised when rate limit is exceeded"""
    pass


class TranscriptionFailedError(TranscriptionServiceError):
    """Exception raised when transcription fails"""
    pass


class AudioProcessingError(TranscriptionServiceError):
    """Exception raised when audio processing fails"""
    pass


def retry_on_error(max_retries=3, delay=1.0, backoff=2.0, 
                  exceptions=(TranscriptionServiceError,)):
    """
    Decorator to retry a function on specific exceptions
    
    Args:
        max_retries: Maximum number of retries
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}: {str(e)}")
                        raise
                    
                    logger.warning(f"Retry {retries}/{max_retries} for {func.__name__} after error: {str(e)}")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator


class BaseTranscriptionService(ABC):
    """
    Abstract base class for transcription services.
    All transcription service providers should implement this interface.
    """
    
    def __init__(self, api_key: str = None, rate_limit: Optional[RateLimitConfig] = None):
        self.api_key = api_key
        self.rate_limit = rate_limit or RateLimitConfig()
        
        # Rate limiting state
        self._request_timestamps: List[float] = []
        
    def _check_rate_limit(self) -> Tuple[bool, str]:
        """
        Check if current request would exceed rate limits
        
        Returns:
            Tuple of (is_allowed, reason)
        """
        now = time.time()
        
        # Remove timestamps older than a day
        day_ago = now - 86400  # 24 hours in seconds
        self._request_timestamps = [ts for ts in self._request_timestamps if ts > day_ago]
        
        # Check daily limit
        if len(self._request_timestamps) >= self.rate_limit.requests_per_day:
            return False, "Daily rate limit exceeded"
        
        # Check per-minute limit
        minute_ago = now - 60
        recent_requests = sum(1 for ts in self._request_timestamps if ts > minute_ago)
        if recent_requests >= self.rate_limit.requests_per_minute:
            return False, "Per-minute rate limit exceeded"
        
        # Request is allowed, add timestamp
        self._request_timestamps.append(now)
        return True, ""
        
    @abstractmethod
    async def transcribe(self, audio_data: bytes, **kwargs) -> TranscriptionResult:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Raw audio data bytes
            **kwargs: Additional provider-specific options
            
        Returns:
            TranscriptionResult with the transcribed text and metadata
            
        Raises:
            TranscriptionServiceError: If transcription fails
        """
        pass
    
    @abstractmethod
    async def transcribe_file(self, file_path: str, **kwargs) -> TranscriptionResult:
        """
        Transcribe audio from a file
        
        Args:
            file_path: Path to audio file
            **kwargs: Additional provider-specific options
            
        Returns:
            TranscriptionResult with the transcribed text and metadata
            
        Raises:
            TranscriptionServiceError: If transcription fails
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the service provider name"""
        pass
    
    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Whether the service supports streaming audio transcription"""
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """List of supported audio formats (e.g. ['mp3', 'wav', 'ogg'])"""
        pass
    
    @property
    @abstractmethod
    def supported_languages(self) -> List[str]:
        """List of supported language codes (e.g. ['en', 'es', 'fr'])"""
        pass
