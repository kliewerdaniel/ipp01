from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Union
from pydantic import BaseModel, Field
import logging
import time
import json
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)


class PromptTemplate(BaseModel):
    """Base class for prompt templates"""
    template: str
    variables: List[str] = Field(default_factory=list)

    def format(self, **kwargs) -> str:
        """Format the template with the given variables"""
        template = self.template
        for var in self.variables:
            if var in kwargs:
                template = template.replace(f"{{{var}}}", str(kwargs[var]))
        return template


class AIServiceResult(BaseModel):
    """Result model for AI service responses"""
    content: str
    model: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class RateLimitConfig(BaseModel):
    """Configuration for rate limiting"""
    requests_per_minute: int = 60
    requests_per_day: int = 1000
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds


class CacheConfig(BaseModel):
    """Configuration for response caching"""
    enabled: bool = True
    ttl: int = 3600  # Time to live in seconds (1 hour default)
    max_size: int = 1000  # Maximum number of cache entries


class AIServiceError(Exception):
    """Base exception for AI service errors"""
    pass


class RateLimitExceededError(AIServiceError):
    """Exception raised when rate limit is exceeded"""
    pass


class AIModelError(AIServiceError):
    """Exception raised when the AI model returns an error"""
    pass


class PromptError(AIServiceError):
    """Exception raised when there's an issue with the prompt"""
    pass


def retry_on_error(max_retries=3, delay=1.0, backoff=2.0, 
                  exceptions=(AIServiceError,)):
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


class SimpleMemoryCache:
    """Simple in-memory cache implementation"""
    
    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
        self.max_size = max_size
    
    def _generate_key(self, prompt: str, model: str, **kwargs) -> str:
        """Generate a cache key from prompt and parameters"""
        # Include relevant parameters in the key
        key_data = {
            "prompt": prompt,
            "model": model,
            **{k: v for k, v in kwargs.items() if k not in ['stream', 'user']}
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, prompt: str, model: str, **kwargs) -> Optional[AIServiceResult]:
        """Get a cached result if it exists and is not expired"""
        key = self._generate_key(prompt, model, **kwargs)
        
        if key in self.cache:
            entry = self.cache[key]
            if time.time() < entry["expiry"]:
                logger.debug(f"Cache hit for key: {key[:8]}...")
                return entry["result"]
            else:
                # Remove expired entry
                logger.debug(f"Removing expired cache entry: {key[:8]}...")
                del self.cache[key]
        
        return None
    
    def set(self, prompt: str, model: str, result: AIServiceResult, **kwargs) -> None:
        """Store a result in the cache"""
        key = self._generate_key(prompt, model, **kwargs)
        
        # Enforce cache size limit
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["expiry"])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            "result": result,
            "expiry": time.time() + self.ttl
        }
        logger.debug(f"Cached result for key: {key[:8]}...")
    
    def clear(self) -> None:
        """Clear all cached entries"""
        self.cache.clear()
        logger.debug("Cache cleared")


class BaseAIService(ABC):
    """
    Abstract base class for AI services.
    All AI service providers should implement this interface.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        rate_limit: Optional[RateLimitConfig] = None,
        cache_config: Optional[CacheConfig] = None
    ):
        self.api_key = api_key
        self.rate_limit = rate_limit or RateLimitConfig()
        self.cache_config = cache_config or CacheConfig()
        
        # Rate limiting state
        self._request_timestamps: List[float] = []
        
        # Initialize cache if enabled
        self._cache = None
        if self.cache_config.enabled:
            self._cache = SimpleMemoryCache(
                ttl=self.cache_config.ttl,
                max_size=self.cache_config.max_size
            )
    
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
    
    def _get_from_cache(self, prompt: str, model: str, **kwargs) -> Optional[AIServiceResult]:
        """Try to get a result from cache if enabled"""
        if self._cache and not kwargs.get("skip_cache", False):
            return self._cache.get(prompt, model, **kwargs)
        return None
    
    def _set_cache(self, prompt: str, model: str, result: AIServiceResult, **kwargs) -> None:
        """Add a result to cache if enabled"""
        if self._cache and not kwargs.get("skip_cache", False):
            self._cache.set(prompt, model, result, **kwargs)
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> AIServiceResult:
        """
        Generate content from a prompt
        
        Args:
            prompt: Text prompt to generate from
            **kwargs: Additional provider-specific options
            
        Returns:
            AIServiceResult with the generated content and metadata
            
        Raises:
            AIServiceError: If generation fails
        """
        pass
    
    @abstractmethod
    async def generate_with_template(
        self, 
        template: Union[str, PromptTemplate], 
        **kwargs
    ) -> AIServiceResult:
        """
        Generate content using a prompt template
        
        Args:
            template: Template string or PromptTemplate object
            **kwargs: Variables for template and provider-specific options
            
        Returns:
            AIServiceResult with the generated content and metadata
            
        Raises:
            AIServiceError: If generation fails
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the service provider name"""
        pass
    
    @property
    @abstractmethod
    def available_models(self) -> List[str]:
        """List of available model identifiers"""
        pass
    
    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model identifier"""
        pass
    
    @abstractmethod
    def clear_cache(self) -> None:
        """Clear the response cache"""
        pass
