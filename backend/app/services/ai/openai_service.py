import os
import json
import logging
from typing import Dict, Any, Optional, List, Tuple, Union, Literal
from pydantic import BaseModel, Field
import time
import httpx
import asyncio

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
    retry_on_error
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIOptions(BaseModel):
    """Configuration options for OpenAI API"""
    model: str = "gpt-4"  # Model to use (gpt-4, gpt-3.5-turbo, etc.)
    temperature: float = Field(0.7, ge=0.0, le=2.0)  # Controls randomness
    max_tokens: Optional[int] = None  # Max tokens to generate
    top_p: float = Field(1.0, ge=0.0, le=1.0)  # Controls diversity
    frequency_penalty: float = Field(0.0, ge=-2.0, le=2.0)  # Penalizes token frequency
    presence_penalty: float = Field(0.0, ge=-2.0, le=2.0)  # Penalizes new tokens
    stop: Optional[Union[str, List[str]]] = None  # Stop sequences
    response_format: Optional[Dict[str, str]] = None  # Format specifier (e.g. JSON)
    seed: Optional[int] = None  # Deterministic output seed
    n: Optional[int] = Field(1, ge=1, le=5)  # Number of completions
    stream: bool = False  # Stream tokens as they're generated


class OpenAIFeedbackTemplate(PromptTemplate):
    """Template for generating interview feedback"""
    
    def __init__(self, template_type: str = "general"):
        """
        Initialize a feedback template by type.
        
        Args:
            template_type: Type of template (general, technical, behavioral)
        """
        if template_type == "technical":
            template = """You are an expert technical interviewer evaluating candidates.

Question: {question}

Candidate's Answer: {answer}

Provide specific, constructive feedback on the candidate's technical answer:
1. Evaluate correctness and completeness
2. Assess approach and problem-solving methodology
3. Note any technical concepts missed or misunderstood
4. Evaluate code quality and implementation details (if applicable)

Format your response as a JSON object with the following structure:
{
  "feedback": "Detailed overall feedback here",
  "score": <0-100 score>,
  "strengths": ["Strength 1", "Strength 2", ...],
  "weaknesses": ["Weakness 1", "Weakness 2", ...],
  "improvement_suggestions": ["Suggestion 1", "Suggestion 2", ...]
}"""
            variables = ["question", "answer"]
            
        elif template_type == "behavioral":
            template = """You are an expert interviewer evaluating behavioral interview responses.

Question: {question}

Candidate's Answer: {answer}

Provide specific, constructive feedback on the candidate's behavioral answer:
1. Evaluate the structure (did they use STAR method effectively?)
2. Assess relevance to the question asked
3. Note communication effectiveness and clarity
4. Evaluate demonstration of soft skills and leadership qualities

Format your response as a JSON object with the following structure:
{
  "feedback": "Detailed overall feedback here",
  "score": <0-100 score>,
  "strengths": ["Strength 1", "Strength 2", ...],
  "weaknesses": ["Weakness 1", "Weakness 2", ...],
  "improvement_suggestions": ["Suggestion 1", "Suggestion 2", ...]
}"""
            variables = ["question", "answer"]
            
        else:  # general default
            template = """You are an expert interview coach evaluating interview answers.

Question: {question}

Candidate's Answer: {answer}

Provide specific, constructive feedback on the candidate's answer along with a score from 0-100.

Format your response as a JSON object with the following structure:
{
  "feedback": "Detailed overall feedback here",
  "score": <0-100 score>,
  "strengths": ["Strength 1", "Strength 2", ...],
  "weaknesses": ["Weakness 1", "Weakness 2", ...],
  "improvement_suggestions": ["Suggestion 1", "Suggestion 2", ...]
}"""
            variables = ["question", "answer"]
            
        super().__init__(template=template, variables=variables)


class OpenAIService(BaseAIService):
    """
    OpenAI implementation of the AI service.
    
    Handles connecting to the OpenAI API and generating content using their models.
    """
    
    API_URL = "https://api.openai.com/v1/chat/completions"
    
    def __init__(
        self, 
        api_key: str = None, 
        rate_limit: Optional[RateLimitConfig] = None,
        cache_config: Optional[CacheConfig] = None,
        options: Optional[OpenAIOptions] = None
    ):
        super().__init__(api_key, rate_limit, cache_config)
        self.options = options or OpenAIOptions()
        
        # Use API key from settings or environment if not provided
        if not self.api_key:
            self.api_key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY in settings or environment.")
    
    @property
    def name(self) -> str:
        return "OpenAI"
    
    @property
    def available_models(self) -> List[str]:
        return [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "gpt-4o"
        ]
    
    @property
    def default_model(self) -> str:
        return self.options.model
    
    def clear_cache(self) -> None:
        """Clear the response cache"""
        if self._cache:
            self._cache.clear()
    
    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare HTTP headers for OpenAI API"""
        if not self.api_key:
            raise AIServiceError("OpenAI API key is required")
        
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _prepare_payload(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Prepare payload for OpenAI API request"""
        # Start with default options
        payload = {
            "model": kwargs.pop("model", self.options.model),
            "messages": messages,
            "temperature": kwargs.pop("temperature", self.options.temperature),
        }
        
        # Add conditional parameters
        if self.options.max_tokens is not None:
            payload["max_tokens"] = kwargs.pop("max_tokens", self.options.max_tokens)
            
        if kwargs.get("top_p", self.options.top_p) != 1.0:
            payload["top_p"] = kwargs.pop("top_p", self.options.top_p)
            
        if kwargs.get("frequency_penalty", self.options.frequency_penalty) != 0.0:
            payload["frequency_penalty"] = kwargs.pop("frequency_penalty", self.options.frequency_penalty)
            
        if kwargs.get("presence_penalty", self.options.presence_penalty) != 0.0:
            payload["presence_penalty"] = kwargs.pop("presence_penalty", self.options.presence_penalty)
            
        if "stop" in kwargs or self.options.stop:
            payload["stop"] = kwargs.pop("stop", self.options.stop)
            
        if "response_format" in kwargs or self.options.response_format:
            payload["response_format"] = kwargs.pop("response_format", self.options.response_format)
            
        if "seed" in kwargs or self.options.seed:
            payload["seed"] = kwargs.pop("seed", self.options.seed)
            
        if kwargs.get("n", self.options.n) != 1:
            payload["n"] = kwargs.pop("n", self.options.n)
            
        # Stream is False by default since we don't handle streaming here
        payload["stream"] = False
        
        # Add any remaining kwargs as-is
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
                
        return payload
    
    async def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Make a request to the OpenAI API"""
        # Check rate limit before making request
        allowed, reason = self._check_rate_limit()
        if not allowed:
            raise RateLimitExceededError(f"Rate limit exceeded: {reason}")
        
        # Prepare request
        url = self.API_URL
        headers = self._prepare_headers()
        payload = self._prepare_payload(messages, **kwargs)
        
        # Get model for caching purposes
        model = payload.get("model", self.default_model)
        
        # Format prompt for caching purposes
        # We join all user messages to create a cache key
        prompt = "\n".join([m["content"] for m in messages if m["role"] == "user"])
        
        # Try to get from cache
        cached_result = self._get_from_cache(prompt, model, **kwargs)
        if cached_result:
            return cached_result
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code == 429:
                    raise RateLimitExceededError("OpenAI API rate limit exceeded")
                    
                if response.status_code != 200:
                    error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise AIModelError(error_msg)
                
                response_data = response.json()
                
                # Parse the response
                content = response_data["choices"][0]["message"]["content"]
                usage = response_data.get("usage", {})
                
                # Create the result
                result = AIServiceResult(
                    content=content,
                    model=model,
                    usage=usage,
                    metadata={
                        "provider": "openai",
                        "finish_reason": response_data["choices"][0].get("finish_reason"),
                        "created": response_data.get("created"),
                        "id": response_data.get("id")
                    }
                )
                
                # Cache the result
                self._set_cache(prompt, model, result, **kwargs)
                
                return result
                
        except httpx.TimeoutException:
            raise AIModelError("Request to OpenAI API timed out")
        except httpx.RequestError as e:
            raise AIModelError(f"Request to OpenAI API failed: {str(e)}")
        except Exception as e:
            if isinstance(e, AIServiceError):
                raise
            else:
                raise AIModelError(f"Unexpected error: {str(e)}")
    
    @retry_on_error(max_retries=3, delay=1.0, backoff=2.0)
    async def generate(self, prompt: str, **kwargs) -> AIServiceResult:
        """
        Generate content from a prompt using OpenAI API
        
        Args:
            prompt: Text prompt to generate from
            **kwargs: Additional OpenAI-specific options
            
        Returns:
            AIServiceResult with the generated content and metadata
        """
        system_prompt = kwargs.pop("system_prompt", 
                                   "You are a helpful AI assistant that provides clear and concise responses.")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Set JSON response format by default (can be overridden)
        if "response_format" not in kwargs:
            kwargs["response_format"] = {"type": "json_object"}
        
        return await self._make_request(messages, **kwargs)
    
    @retry_on_error(max_retries=3, delay=1.0, backoff=2.0)
    async def generate_with_template(
        self, 
        template: Union[str, PromptTemplate], 
        **kwargs
    ) -> AIServiceResult:
        """
        Generate content using a prompt template
        
        Args:
            template: Template string or PromptTemplate object
            **kwargs: Variables for template and OpenAI-specific options
            
        Returns:
            AIServiceResult with the generated content and metadata
        """
        # Get system prompt from kwargs or use default
        system_prompt = kwargs.pop("system_prompt", 
                                   "You are a helpful AI assistant that provides clear and concise responses.")
        
        # Format the template
        if isinstance(template, str):
            # Convert to PromptTemplate if it's a string
            prompt_template = PromptTemplate(template=template)
            formatted_prompt = prompt_template.format(**kwargs)
        else:
            # It's already a PromptTemplate
            formatted_prompt = template.format(**kwargs)
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": formatted_prompt}
        ]
        
        # Set JSON response format by default (can be overridden)
        if "response_format" not in kwargs:
            kwargs["response_format"] = {"type": "json_object"}
        
        return await self._make_request(messages, **kwargs)
    
    async def generate_feedback(
        self, 
        question: str, 
        answer: str, 
        feedback_type: str = "general", 
        **kwargs
    ) -> AIServiceResult:
        """
        Generate feedback for an interview answer
        
        Args:
            question: The interview question
            answer: The candidate's answer
            feedback_type: Type of feedback (general, technical, behavioral)
            **kwargs: Additional OpenAI-specific options
            
        Returns:
            AIServiceResult with the generated feedback as JSON
        """
        # Create feedback template
        template = OpenAIFeedbackTemplate(template_type=feedback_type)
        
        # Set specific system prompt for feedback
        system_prompt = "You are an expert interview coach evaluating interview answers. Provide specific, constructive feedback."
        
        # Override with feedback-specific options
        kwargs.update({
            "question": question,
            "answer": answer,
            "system_prompt": system_prompt,
            "temperature": kwargs.get("temperature", 0.3),  # Lower temperature for consistency
            "response_format": {"type": "json_object"}
        })
        
        return await self.generate_with_template(template, **kwargs)
