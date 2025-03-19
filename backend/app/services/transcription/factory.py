from typing import Optional, Dict, Any, Union
import os
import logging
from enum import Enum

from .base import BaseTranscriptionService, RateLimitConfig
from .deepgram_service import DeepgramTranscriptionService, DeepgramOptions
from .mock_service import MockTranscriptionService
from app.core.config import settings

logger = logging.getLogger(__name__)


class TranscriptionProvider(str, Enum):
    """Enum of supported transcription providers"""
    DEEPGRAM = "deepgram"
    MOCK = "mock"


class TranscriptionServiceFactory:
    """
    Factory for creating transcription service instances.
    This allows easy switching between different providers.
    """

    @staticmethod
    def create_service(
        provider: Union[str, TranscriptionProvider] = None,
        api_key: Optional[str] = None,
        rate_limit: Optional[RateLimitConfig] = None,
        service_options: Optional[Dict[str, Any]] = None
    ) -> BaseTranscriptionService:
        """
        Create a transcription service instance
        
        Args:
            provider: Service provider (deepgram, mock)
            api_key: API key for the service
            rate_limit: Rate limit configuration
            service_options: Provider-specific options
            
        Returns:
            Configured transcription service
        """
        # Get provider from config if not specified
        if not provider:
            provider = os.environ.get("TRANSCRIPTION_PROVIDER", "mock")
        
        # Convert string to enum if needed
        if isinstance(provider, str):
            try:
                provider = TranscriptionProvider(provider.lower())
            except ValueError:
                logger.warning(f"Unknown transcription provider: {provider}. Falling back to mock.")
                provider = TranscriptionProvider.MOCK
        
        # Create the appropriate service
        service_options = service_options or {}
        
        if provider == TranscriptionProvider.DEEPGRAM:
            # Get API key from params, env var, or settings
            api_key = api_key or os.environ.get("DEEPGRAM_API_KEY") or getattr(settings, "DEEPGRAM_API_KEY", None)
            
            if not api_key:
                logger.warning("No Deepgram API key found. Falling back to mock service.")
                return MockTranscriptionService(rate_limit=rate_limit)
            
            # Create Deepgram options if provided
            deepgram_options = None
            if service_options:
                deepgram_options = DeepgramOptions(**service_options)
                
            return DeepgramTranscriptionService(
                api_key=api_key,
                rate_limit=rate_limit,
                options=deepgram_options
            )
            
        elif provider == TranscriptionProvider.MOCK:
            # Create mock service
            dictionary_path = service_options.get("dictionary_path")
            latency = service_options.get("latency", (0.5, 3.0))
            error_rate = service_options.get("error_rate", 0.05)
            
            return MockTranscriptionService(
                dictionary_path=dictionary_path,
                rate_limit=rate_limit,
                latency=latency,
                error_rate=error_rate
            )
        
        # Default to mock if we somehow get here
        logger.warning(f"Unhandled provider: {provider}. Using mock service.")
        return MockTranscriptionService(rate_limit=rate_limit)


# Default instance configured from settings
default_transcription_service = TranscriptionServiceFactory.create_service(
    provider=settings.TRANSCRIPTION_PROVIDER,
    api_key=settings.DEEPGRAM_API_KEY,
    rate_limit=RateLimitConfig(
        requests_per_minute=settings.TRANSCRIPTION_RATE_LIMIT_REQUESTS_PER_MINUTE,
        requests_per_day=settings.TRANSCRIPTION_RATE_LIMIT_REQUESTS_PER_DAY
    ),
    service_options={
        "model": "nova",  # Default Deepgram model
        "smart_format": True,
        "punctuate": True
    }
)
