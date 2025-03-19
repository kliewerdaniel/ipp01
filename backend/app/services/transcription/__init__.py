"""
Transcription service package for speech-to-text conversion.

This package provides abstraction layers for transcription services,
allowing easy switching between providers while maintaining a consistent interface.
"""

from .base import (
    BaseTranscriptionService,
    TranscriptionResult,
    RateLimitConfig,
    TranscriptionServiceError,
    RateLimitExceededError,
    TranscriptionFailedError,
    AudioProcessingError,
    retry_on_error
)

from .deepgram_service import DeepgramTranscriptionService, DeepgramOptions
from .mock_service import MockTranscriptionService
from .factory import TranscriptionServiceFactory, TranscriptionProvider, default_transcription_service

__all__ = [
    # Base classes and utilities
    "BaseTranscriptionService",
    "TranscriptionResult",
    "RateLimitConfig",
    "TranscriptionServiceError",
    "RateLimitExceededError",
    "TranscriptionFailedError",
    "AudioProcessingError",
    "retry_on_error",
    
    # Implementation classes
    "DeepgramTranscriptionService",
    "DeepgramOptions",
    "MockTranscriptionService",
    
    # Factory
    "TranscriptionServiceFactory",
    "TranscriptionProvider",
    "default_transcription_service",
]
