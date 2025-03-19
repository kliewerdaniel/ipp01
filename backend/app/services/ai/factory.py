from typing import Optional, Dict, Any, Union
import os
import logging
from enum import Enum

from .base import BaseAIService, RateLimitConfig, CacheConfig
from .openai_service import OpenAIService, OpenAIOptions
from .mock_service import MockAIService
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """Enum of supported AI providers"""
    OPENAI = "openai"
    MOCK = "mock"


class AIServiceFactory:
    """
    Factory for creating AI service instances.
    This allows easy switching between different providers.
    """

    @staticmethod
    def create_service(
        provider: Union[str, AIProvider] = None,
        api_key: Optional[str] = None,
        rate_limit: Optional[RateLimitConfig] = None,
        cache_config: Optional[CacheConfig] = None,
        service_options: Optional[Dict[str, Any]] = None
    ) -> BaseAIService:
        """
        Create an AI service instance
        
        Args:
            provider: Service provider (openai, mock)
            api_key: API key for the service
            rate_limit: Rate limit configuration
            cache_config: Cache configuration
            service_options: Provider-specific options
            
        Returns:
            Configured AI service
        """
        # Get provider from config if not specified
        if not provider:
            provider = os.environ.get("AI_PROVIDER", "mock")
        
        # Convert string to enum if needed
        if isinstance(provider, str):
            try:
                provider = AIProvider(provider.lower())
            except ValueError:
                logger.warning(f"Unknown AI provider: {provider}. Falling back to mock.")
                provider = AIProvider.MOCK
        
        # Create the appropriate service
        service_options = service_options or {}
        
        if provider == AIProvider.OPENAI:
            # Get API key from params, env var, or settings
            api_key = api_key or os.environ.get("OPENAI_API_KEY") or getattr(settings, "OPENAI_API_KEY", None)
            
            if not api_key:
                logger.warning("No OpenAI API key found. Falling back to mock service.")
                return MockAIService(rate_limit=rate_limit, cache_config=cache_config)
            
            # Create OpenAI options if provided
            openai_options = None
            if service_options:
                openai_options = OpenAIOptions(**service_options)
                
            return OpenAIService(
                api_key=api_key,
                rate_limit=rate_limit,
                cache_config=cache_config,
                options=openai_options
            )
            
        elif provider == AIProvider.MOCK:
            # Create mock service
            dictionary_path = service_options.get("dictionary_path")
            latency = service_options.get("latency", (0.2, 1.5))
            error_rate = service_options.get("error_rate", 0.05)
            
            return MockAIService(
                dictionary_path=dictionary_path,
                rate_limit=rate_limit,
                cache_config=cache_config,
                latency=latency,
                error_rate=error_rate
            )
        
        # Default to mock if we somehow get here
        logger.warning(f"Unhandled provider: {provider}. Using mock service.")
        return MockAIService(rate_limit=rate_limit, cache_config=cache_config)


# Default instance configured from settings
default_ai_service = AIServiceFactory.create_service(
    provider=settings.AI_PROVIDER,
    api_key=settings.OPENAI_API_KEY,
    rate_limit=RateLimitConfig(
        requests_per_minute=settings.AI_RATE_LIMIT_REQUESTS_PER_MINUTE,
        requests_per_day=settings.AI_RATE_LIMIT_REQUESTS_PER_DAY
    ),
    cache_config=CacheConfig(
        enabled=settings.AI_CACHE_ENABLED,
        ttl=settings.AI_CACHE_TTL
    ),
    service_options={
        "model": settings.OPENAI_MODEL
    }
)
