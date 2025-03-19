import os
import json
import random
from typing import Dict, Any, Optional, List, Tuple
import logging
import time
import asyncio
from pathlib import Path

from .base import (
    BaseTranscriptionService,
    TranscriptionResult,
    RateLimitConfig,
    TranscriptionServiceError,
    AudioProcessingError
)

logger = logging.getLogger(__name__)


class MockTranscriptionService(BaseTranscriptionService):
    """
    Mock implementation of the transcription service for local development.
    This service doesn't make actual API calls but simulates transcription responses.
    """
    
    def __init__(
        self, 
        dictionary_path: Optional[str] = None,
        rate_limit: Optional[RateLimitConfig] = None,
        latency: Tuple[float, float] = (0.5, 3.0),  # min and max latency in seconds
        error_rate: float = 0.05  # 5% chance of simulated error
    ):
        super().__init__(api_key="mock_key", rate_limit=rate_limit)
        self.latency = latency
        self.error_rate = error_rate
        self.dictionary_path = dictionary_path
        self.responses = self._load_responses()
    
    @property
    def name(self) -> str:
        return "Mock Transcription Service"
    
    @property
    def supports_streaming(self) -> bool:
        return True
    
    @property
    def supported_formats(self) -> List[str]:
        return ["wav", "mp3", "ogg", "flac", "aac", "m4a", "mp4"]
    
    @property
    def supported_languages(self) -> List[str]:
        return ["en", "es", "fr", "de", "it", "pt", "zh", "ja"]
    
    def _load_responses(self) -> Dict[str, Any]:
        """Load canned responses from file or use defaults"""
        canned_responses = {
            "generic": [
                "Thank you for the question. I would approach this by analyzing the key factors and developing a strategic solution.",
                "Based on my experience, I would tackle this problem methodically. First, I'd gather requirements, then design a solution.",
                "This is an interesting challenge. I would start by breaking it down into smaller components and addressing each one.",
                "In my previous role, I encountered similar situations. The key is to prioritize clearly and communicate effectively.",
                "I believe the best approach is to collaborate with stakeholders to understand their needs before implementing a solution."
            ],
            "software": [
                "I would implement this feature using a modular architecture to ensure maintainability and scalability.",
                "The algorithm complexity can be reduced from O(n²) to O(n log n) by using a more efficient data structure.",
                "For this backend system, I would use a microservice architecture with clear service boundaries and APIs.",
                "The bug is likely caused by race conditions in the concurrent processing. I would implement proper locking mechanisms.",
                "I would choose React for the frontend due to its component-based architecture and efficient rendering."
            ],
            "data": [
                "For this data pipeline, I would use Apache Spark to handle the large-scale processing requirements.",
                "The model accuracy could be improved by addressing class imbalance and feature engineering.",
                "I would normalize the data first, then apply principal component analysis to reduce dimensionality.",
                "This clustering problem would benefit from DBSCAN rather than K-means due to the non-spherical clusters.",
                "I would implement a data validation layer to ensure data quality before it enters the analytics pipeline."
            ],
            "management": [
                "When leading a team through this change, I would focus on clear communication and addressing concerns early.",
                "My project management approach involves setting clear milestones and having regular check-ins to track progress.",
                "I prioritize tasks based on business impact and technical dependencies to ensure efficient delivery.",
                "For remote teams, I establish clear communication channels and foster a culture of documentation.",
                "I would handle this conflict by facilitating a discussion to understand each perspective and find common ground."
            ]
        }
        
        # If a dictionary file is provided, try to load it
        if self.dictionary_path and os.path.exists(self.dictionary_path):
            try:
                with open(self.dictionary_path, 'r') as f:
                    custom_responses = json.load(f)
                    if isinstance(custom_responses, dict):
                        # Merge with defaults, prioritizing custom responses
                        for category, responses in custom_responses.items():
                            if isinstance(responses, list) and responses:
                                canned_responses[category] = responses
                    logger.info(f"Loaded custom responses from {self.dictionary_path}")
            except Exception as e:
                logger.warning(f"Failed to load custom responses from {self.dictionary_path}: {str(e)}")
        
        return canned_responses
    
    def _generate_mock_transcription(self, file_path: Optional[str] = None) -> str:
        """Generate a mock transcription based on file name or random selection"""
        # Try to infer category from file path
        category = "generic"
        
        if file_path:
            file_name = os.path.basename(file_path).lower()
            
            # Try to infer the topic from the filename
            if any(kw in file_name for kw in ["code", "program", "software", "dev", "api"]):
                category = "software"
            elif any(kw in file_name for kw in ["data", "model", "analysis", "ml", "ai"]):
                category = "data"
            elif any(kw in file_name for kw in ["manage", "lead", "team", "project"]):
                category = "management"
        
        # Get responses for the category, fallback to generic
        responses = self.responses.get(category, self.responses["generic"])
        
        # Return a random response
        return random.choice(responses)
    
    def _simulate_processing_delay(self):
        """Simulate processing delay"""
        delay = random.uniform(self.latency[0], self.latency[1])
        time.sleep(delay)
    
    def _create_mock_words_data(self, text: str) -> List[Dict[str, Any]]:
        """Create mock word-level data for the transcription"""
        words = []
        start_time = 0.0
        
        for i, word in enumerate(text.split()):
            # Strip punctuation for the word itself
            clean_word = word.strip(".,;:!?")
            if not clean_word:
                continue
                
            # Randomly generate duration between 0.2 and 0.6 seconds per word
            duration = random.uniform(0.2, 0.6)
            
            words.append({
                "word": clean_word,
                "start": start_time,
                "end": start_time + duration,
                "confidence": random.uniform(0.75, 1.0)
            })
            
            # Update start time for next word (add a small gap)
            start_time += duration + random.uniform(0.05, 0.2)
        
        return words
    
    async def transcribe(self, audio_data: bytes, **kwargs) -> TranscriptionResult:
        """
        Mock transcription of audio data
        
        Args:
            audio_data: Raw audio data bytes
            **kwargs: Additional options (ignored in mock)
            
        Returns:
            TranscriptionResult with simulated transcribed text
        """
        if not audio_data:
            raise AudioProcessingError("Empty audio data")
            
        # Simulate processing delay
        self._simulate_processing_delay()
        
        # Random chance of error
        if random.random() < self.error_rate:
            raise TranscriptionServiceError("Simulated transcription error")
        
        # Generate mock transcription
        text = self._generate_mock_transcription()
        
        # Generate mock word data
        words = self._create_mock_words_data(text)
        
        # Calculate mock confidence
        confidence = random.uniform(0.8, 0.98)
        
        return TranscriptionResult(
            text=text,
            confidence=confidence,
            language="en",
            words=words,
            metadata={
                "provider": "mock",
                "duration": len(words) * 0.5,  # Rough estimate of duration
                "channels": 1
            }
        )
    
    async def transcribe_file(self, file_path: str, **kwargs) -> TranscriptionResult:
        """
        Mock transcription of audio file
        
        Args:
            file_path: Path to audio file
            **kwargs: Additional options (ignored in mock)
            
        Returns:
            TranscriptionResult with simulated transcribed text
        """
        if not os.path.exists(file_path):
            raise AudioProcessingError(f"File not found: {file_path}")
            
        # Simulate reading the file
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise AudioProcessingError("Empty audio file")
        
        # Simulate processing delay scaled by file size
        delay_factor = min(5.0, file_size / (1024 * 1024))  # Cap at 5 seconds for large files
        time.sleep(random.uniform(self.latency[0], self.latency[1]) * delay_factor)
        
        # Random chance of error
        if random.random() < self.error_rate:
            raise TranscriptionServiceError("Simulated transcription error")
        
        # Generate mock transcription based on filename
        text = self._generate_mock_transcription(file_path)
        
        # Generate mock word data
        words = self._create_mock_words_data(text)
        
        # Calculate mock confidence
        confidence = random.uniform(0.8, 0.98)
        
        return TranscriptionResult(
            text=text,
            confidence=confidence,
            language="en",
            words=words,
            metadata={
                "provider": "mock",
                "file_path": file_path,
                "duration": len(words) * 0.5,  # Rough estimate of duration
                "channels": 1
            }
        )
