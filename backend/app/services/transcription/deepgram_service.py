import os
import json
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List, Tuple, BinaryIO
import logging
from pydantic import BaseModel
import time
import httpx

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

logger = logging.getLogger(__name__)


class DeepgramOptions(BaseModel):
    """Configuration options for Deepgram API"""
    model: str = "nova"  # Model to use for transcription
    language: str = "en"  # Language code
    smart_format: bool = True  # Apply smart formatting
    punctuate: bool = True  # Add punctuation
    diarize: bool = False  # Speaker diarization
    detect_language: bool = False  # Auto-detect language
    utterances: bool = False  # Split into utterances
    profanity_filter: bool = False  # Filter profanity
    redact: List[str] = []  # List of PII to redact
    alternatives: int = 1  # Number of alternatives to return
    numerals: bool = True  # Convert numbers to digits
    paragraphs: bool = True  # Add paragraph breaks
    keywords: Optional[List[str]] = None  # Keywords to boost
    endpointing: Optional[int] = None  # Silence duration for endpointing (in ms)
    

class DeepgramTranscriptionService(BaseTranscriptionService):
    """
    Deepgram implementation of the transcription service.
    
    Docs: https://developers.deepgram.com/
    """
    
    BASE_URL = "https://api.deepgram.com/v1"
    
    def __init__(
        self, 
        api_key: str = None, 
        rate_limit: Optional[RateLimitConfig] = None,
        options: Optional[DeepgramOptions] = None
    ):
        super().__init__(api_key, rate_limit)
        self.options = options or DeepgramOptions()
        
        # Use API key from environment if not provided
        if not self.api_key:
            self.api_key = os.environ.get("DEEPGRAM_API_KEY")
            if not self.api_key:
                logger.warning("No Deepgram API key provided. Set DEEPGRAM_API_KEY environment variable.")
    
    @property
    def name(self) -> str:
        return "Deepgram"
    
    @property
    def supports_streaming(self) -> bool:
        return True
    
    @property
    def supported_formats(self) -> List[str]:
        return ["wav", "mp3", "ogg", "flac", "aac", "m4a", "mp4"]
    
    @property
    def supported_languages(self) -> List[str]:
        return [
            "en", "es", "fr", "de", "it", "pt", "nl", "ja", "ko",
            "zh", "hi", "ru", "tr", "pl", "ar", "id", "sv", "da"
        ]
    
    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare HTTP headers for Deepgram API"""
        if not self.api_key:
            raise TranscriptionServiceError("Deepgram API key is required")
        
        return {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _prepare_params(self, **kwargs) -> Dict[str, Any]:
        """Prepare parameters for Deepgram API request"""
        # Start with default options from service instance
        params = {
            "model": self.options.model,
            "language": self.options.language,
            "smart_format": self.options.smart_format,
            "punctuate": self.options.punctuate,
            "diarize": self.options.diarize,
        }
        
        # Add optional parameters if set
        if self.options.detect_language:
            params["detect_language"] = True
        
        if self.options.utterances:
            params["utterances"] = True
            
        if self.options.profanity_filter:
            params["profanity_filter"] = True
            
        if self.options.redact:
            params["redact"] = self.options.redact
            
        if self.options.alternatives > 1:
            params["alternatives"] = self.options.alternatives
            
        if self.options.numerals:
            params["numerals"] = True
            
        if self.options.paragraphs:
            params["paragraphs"] = True
            
        if self.options.keywords:
            params["keywords"] = self.options.keywords
            
        if self.options.endpointing:
            params["endpointing"] = self.options.endpointing
        
        # Override with any kwargs
        params.update(kwargs)
        
        return params
    
    async def _make_request(self, endpoint: str, data: bytes, **kwargs) -> Dict[str, Any]:
        """Make a request to the Deepgram API"""
        # Check rate limit before making request
        allowed, reason = self._check_rate_limit()
        if not allowed:
            raise RateLimitExceededError(f"Rate limit exceeded: {reason}")
        
        # Prepare request
        url = f"{self.BASE_URL}/{endpoint}"
        headers = self._prepare_headers()
        params = self._prepare_params(**kwargs)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=params,
                    content=data,
                    timeout=60.0  # Large audio files may take time to process
                )
                
                if response.status_code == 429:
                    raise RateLimitExceededError("Deepgram API rate limit exceeded")
                    
                if response.status_code != 200:
                    error_msg = f"Deepgram API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise TranscriptionFailedError(error_msg)
                
                return response.json()
                
        except httpx.TimeoutException:
            raise TranscriptionFailedError("Request to Deepgram API timed out")
        except httpx.RequestError as e:
            raise TranscriptionFailedError(f"Request to Deepgram API failed: {str(e)}")
        except Exception as e:
            raise TranscriptionFailedError(f"Unexpected error: {str(e)}")
    
    def _parse_response(self, response_data: Dict[str, Any]) -> TranscriptionResult:
        """Parse Deepgram API response into a standardized TranscriptionResult"""
        try:
            # Extract results from Deepgram response
            results = response_data.get("results", {})
            channels = results.get("channels", [])
            
            if not channels:
                raise TranscriptionFailedError("No transcription channels in response")
                
            # Get the first channel's alternatives
            alternatives = channels[0].get("alternatives", [])
            
            if not alternatives:
                raise TranscriptionFailedError("No transcription alternatives in response")
                
            # Get the first (best) alternative
            transcript = alternatives[0]
            
            # Extract the transcript text
            text = transcript.get("transcript", "")
            if not text:
                raise TranscriptionFailedError("Empty transcription result")
                
            # Extract confidence score
            confidence = transcript.get("confidence", 1.0)
            
            # Extract words data if available
            words = transcript.get("words", [])
            
            # Get detected language if available
            language = results.get("language", "en")
            
            # Create result
            return TranscriptionResult(
                text=text,
                confidence=confidence,
                language=language,
                words=words,
                metadata={
                    "provider": "deepgram",
                    "model": response_data.get("model", ""),
                    "duration": results.get("duration", 0),
                    "channels": len(channels)
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing Deepgram response: {str(e)}")
            raise TranscriptionFailedError(f"Error parsing transcription result: {str(e)}")
    
    @retry_on_error(max_retries=3, delay=1.0, backoff=2.0)
    async def transcribe(self, audio_data: bytes, **kwargs) -> TranscriptionResult:
        """
        Transcribe audio data using Deepgram API
        
        Args:
            audio_data: Raw audio data bytes
            **kwargs: Additional Deepgram-specific options
            
        Returns:
            TranscriptionResult with the transcribed text and metadata
        """
        if not audio_data:
            raise AudioProcessingError("Empty audio data")
            
        try:
            # Send prerecorded audio for transcription
            response_data = await self._make_request("listen", audio_data, **kwargs)
            
            # Parse the response
            return self._parse_response(response_data)
            
        except Exception as e:
            if isinstance(e, TranscriptionServiceError):
                raise
            else:
                logger.error(f"Transcription error: {str(e)}")
                raise TranscriptionFailedError(f"Failed to transcribe audio: {str(e)}")
    
    @retry_on_error(max_retries=3, delay=1.0, backoff=2.0)
    async def transcribe_file(self, file_path: str, **kwargs) -> TranscriptionResult:
        """
        Transcribe audio from a file using Deepgram API
        
        Args:
            file_path: Path to audio file
            **kwargs: Additional Deepgram-specific options
            
        Returns:
            TranscriptionResult with the transcribed text and metadata
        """
        if not os.path.exists(file_path):
            raise AudioProcessingError(f"File not found: {file_path}")
            
        try:
            # Read the file
            with open(file_path, "rb") as f:
                audio_data = f.read()
                
            # Send for transcription
            return await self.transcribe(audio_data, **kwargs)
            
        except Exception as e:
            if isinstance(e, TranscriptionServiceError):
                raise
            else:
                logger.error(f"File transcription error: {str(e)}")
                raise TranscriptionFailedError(f"Failed to transcribe file: {str(e)}")
