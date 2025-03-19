"""
AI service package for generating content and feedback.

This package provides abstraction layers for AI services,
allowing easy switching between providers while maintaining a consistent interface.
"""

from .base import (
    BaseAIService,
    AIServiceResult,
    PromptTemplate,
    RateLimitConfig,
    CacheConfig,
    AIServiceError,
    RateLimitExceededError,
    AIModelError,
    PromptError,
    retry_on_error,
    SimpleMemoryCache
)

from .openai_service import OpenAIService, OpenAIOptions, OpenAIFeedbackTemplate
from .mock_service import MockAIService
from .factory import AIServiceFactory, AIProvider, default_ai_service

__all__ = [
    # Base classes and utilities
    "BaseAIService",
    "AIServiceResult",
    "PromptTemplate",
    "RateLimitConfig",
    "CacheConfig",
    "AIServiceError",
    "RateLimitExceededError",
    "AIModelError",
    "PromptError",
    "retry_on_error",
    "SimpleMemoryCache",
    
    # Implementation classes
    "OpenAIService",
    "OpenAIOptions",
    "OpenAIFeedbackTemplate",
    "MockAIService",
    
    # Factory
    "AIServiceFactory",
    "AIProvider",
    "default_ai_service",
]
