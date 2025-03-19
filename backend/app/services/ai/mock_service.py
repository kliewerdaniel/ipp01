import json
import random
import logging
import time
import os
from typing import Dict, Any, Optional, List, Union
import hashlib

from .base import (
    BaseAIService,
    AIServiceResult,
    PromptTemplate,
    RateLimitConfig,
    CacheConfig,
    AIServiceError
)

logger = logging.getLogger(__name__)


class MockAIService(BaseAIService):
    """
    Mock implementation of the AI service for local development.
    This service simulates AI responses without calling external APIs.
    """
    
    def __init__(
        self, 
        dictionary_path: Optional[str] = None,
        rate_limit: Optional[RateLimitConfig] = None,
        cache_config: Optional[CacheConfig] = None,
        latency: tuple = (0.2, 1.5),  # min and max latency in seconds
        error_rate: float = 0.05  # 5% chance of simulated error
    ):
        super().__init__(api_key="mock_key", rate_limit=rate_limit, cache_config=cache_config)
        self.latency = latency
        self.error_rate = error_rate
        self.dictionary_path = dictionary_path
        self.responses = self._load_responses()
    
    @property
    def name(self) -> str:
        return "Mock AI Service"
    
    @property
    def available_models(self) -> List[str]:
        return ["mock-model", "mock-model-fast", "mock-model-detailed"]
    
    @property
    def default_model(self) -> str:
        return "mock-model"
    
    def clear_cache(self) -> None:
        """Clear the response cache"""
        if self._cache:
            self._cache.clear()
    
    def _load_responses(self) -> Dict[str, Any]:
        """Load canned responses from file or use defaults"""
        default_responses = {
            "general_feedback": [
                {
                    "feedback": "Your answer demonstrates good technical knowledge, but could benefit from more specific examples. Try to structure your responses using the STAR method (Situation, Task, Action, Result) to make them more impactful. You articulated the main points well, but a more concise delivery would improve clarity.",
                    "score": 75,
                    "strengths": [
                        "Good technical understanding",
                        "Clear articulation of concepts",
                        "Logical flow of ideas"
                    ],
                    "weaknesses": [
                        "Lacks specific examples",
                        "Response could be more concise",
                        "Missing structured approach (STAR method)"
                    ],
                    "improvement_suggestions": [
                        "Include 1-2 specific work examples",
                        "Practice more concise delivery",
                        "Structure answers using STAR method"
                    ]
                },
                {
                    "feedback": "Your response showed strong problem-solving skills and a methodical approach. I appreciated how you walked through your thinking process. To strengthen your answer further, consider addressing potential challenges or edge cases. Your technical explanation was sound, but adding context about how this applies in real-world scenarios would make it more compelling.",
                    "score": 82,
                    "strengths": [
                        "Strong problem-solving approach",
                        "Clear explanation of technical concepts",
                        "Methodical thinking process"
                    ],
                    "weaknesses": [
                        "Limited discussion of potential challenges",
                        "Could improve real-world context",
                        "Some technical details needed more elaboration"
                    ],
                    "improvement_suggestions": [
                        "Discuss potential edge cases and solutions",
                        "Connect technical concepts to business impact",
                        "Provide more depth on key technical points"
                    ]
                },
                {
                    "feedback": "Your answer lacked sufficient detail and specificity. When discussing your experience, try to provide concrete examples rather than general statements. The technical concepts mentioned were correct, but the explanation was superficial. Remember to demonstrate not just what you know, but how you apply that knowledge in practical situations.",
                    "score": 58,
                    "strengths": [
                        "Basic understanding of concepts",
                        "Honest self-assessment",
                        "Clear communication style"
                    ],
                    "weaknesses": [
                        "Insufficient detail and specificity",
                        "Limited practical examples",
                        "Superficial explanation of technical concepts"
                    ],
                    "improvement_suggestions": [
                        "Prepare specific examples from past experience",
                        "Deepen technical explanations with implementation details",
                        "Practice explaining complex concepts clearly"
                    ]
                }
            ],
            "technical_feedback": [
                {
                    "feedback": "Your solution demonstrates a good understanding of the algorithm, but there are opportunities for optimization. The time complexity analysis was accurate, but consider discussing space complexity as well. Your approach to edge cases was thorough, though you could elaborate more on how you'd handle scaling issues with larger inputs.",
                    "score": 78,
                    "strengths": [
                        "Correct algorithm implementation",
                        "Accurate time complexity analysis",
                        "Good handling of edge cases"
                    ],
                    "weaknesses": [
                        "No discussion of space complexity",
                        "Limited optimization considerations",
                        "Insufficient scaling discussion"
                    ],
                    "improvement_suggestions": [
                        "Include space complexity in your analysis",
                        "Suggest optimizations for the algorithm",
                        "Discuss scaling approaches for larger inputs"
                    ]
                },
                {
                    "feedback": "Your code was well-structured and followed good practices like modularization and meaningful variable names. However, error handling was minimal, and you didn't discuss testing strategies. Your explanation of the design pattern was accurate, but consider explaining why you chose it over alternatives.",
                    "score": 85,
                    "strengths": [
                        "Well-structured, modular code",
                        "Good naming conventions",
                        "Appropriate use of design patterns"
                    ],
                    "weaknesses": [
                        "Minimal error handling",
                        "No discussion of testing approach",
                        "Limited justification for design choices"
                    ],
                    "improvement_suggestions": [
                        "Implement comprehensive error handling",
                        "Explain your testing strategy",
                        "Compare your chosen approach with alternatives"
                    ]
                }
            ],
            "behavioral_feedback": [
                {
                    "feedback": "Your response effectively used the STAR method and clearly illustrated your leadership skills. The situation was well-described, though you could provide more context about the stakes involved. Your explanation of the actions taken was detailed, but the results section could be strengthened with more specific metrics or outcomes.",
                    "score": 88,
                    "strengths": [
                        "Effective use of STAR method",
                        "Clear illustration of leadership skills",
                        "Detailed explanation of actions taken"
                    ],
                    "weaknesses": [
                        "Limited context about stakes or importance",
                        "Results section lacks specific metrics",
                        "Could better connect experience to the role"
                    ],
                    "improvement_suggestions": [
                        "Include specific metrics in your results",
                        "Establish stakes or importance early in the story",
                        "Connect the experience more explicitly to the job requirements"
                    ]
                },
                {
                    "feedback": "Your answer about conflict resolution was too general and didn't provide a specific example. Remember that behavioral questions are best answered with concrete situations from your experience. While you mentioned some good conflict resolution principles, without a real example, it's difficult to evaluate how you've applied these skills in practice.",
                    "score": 62,
                    "strengths": [
                        "Good understanding of conflict resolution principles",
                        "Clear communication style",
                        "Positive approach to problem-solving"
                    ],
                    "weaknesses": [
                        "Lacks a specific example",
                        "Too theoretical rather than experiential",
                        "Missing STAR method structure"
                    ],
                    "improvement_suggestions": [
                        "Prepare specific conflict resolution stories",
                        "Structure your answer using the STAR method",
                        "Include the outcome and what you learned"
                    ]
                }
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
                                default_responses[category] = responses
                    logger.info(f"Loaded custom responses from {self.dictionary_path}")
            except Exception as e:
                logger.warning(f"Failed to load custom responses from {self.dictionary_path}: {str(e)}")
        
        return default_responses
    
    def _simulate_processing_delay(self):
        """Simulate processing delay"""
        delay = random.uniform(self.latency[0], self.latency[1])
        time.sleep(delay)
    
    def _generate_mock_feedback(self, prompt: str, feedback_type: str = "general") -> str:
        """Generate a mock feedback response"""
        # Determine feedback type
        if "technical" in feedback_type.lower() or "code" in prompt.lower() or "algorithm" in prompt.lower():
            response_key = "technical_feedback"
        elif "behavioral" in feedback_type.lower() or "star method" in prompt.lower() or "leadership" in prompt.lower():
            response_key = "behavioral_feedback"
        else:
            response_key = "general_feedback"
        
        # Get responses for the category, fallback to general
        responses = self.responses.get(response_key, self.responses["general_feedback"])
        
        # Return a random response
        response = random.choice(responses)
        return json.dumps(response, indent=2)
    
    def _generate_deterministic_response(self, prompt: str, model: str) -> str:
        """Generate a deterministic response based on prompt hash"""
        # Create a hash of the prompt
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        
        # Use the first 8 characters of the hash as a seed
        seed = int(prompt_hash[:8], 16)
        random.seed(seed)
        
        # Generate some mock response text
        response_text = self._generate_mock_feedback(prompt)
        
        # Reset the random seed to avoid affecting other random operations
        random.seed()
        
        return response_text
    
    async def generate(self, prompt: str, **kwargs) -> AIServiceResult:
        """
        Generate mock content from a prompt
        
        Args:
            prompt: Text prompt to generate from
            **kwargs: Additional options (ignored in mock)
            
        Returns:
            AIServiceResult with simulated generated content
        """
        # Simulate processing delay
        self._simulate_processing_delay()
        
        # Random chance of error
        if random.random() < self.error_rate:
            raise AIServiceError("Simulated AI service error")
        
        # Get the model (or use default)
        model = kwargs.get("model", self.default_model)
        
        # Try to get from cache first
        cached_result = self._get_from_cache(prompt, model, **kwargs)
        if cached_result:
            return cached_result
        
        # Generate mock content (deterministic for the same prompt)
        content = self._generate_deterministic_response(prompt, model)
        
        # Simulate token usage
        token_estimate = len(prompt.split()) * 1.3  # rough estimate of tokens
        completion_tokens = len(content.split()) * 1.3
        total_tokens = token_estimate + completion_tokens
        
        result = AIServiceResult(
            content=content,
            model=model,
            usage={
                "prompt_tokens": int(token_estimate),
                "completion_tokens": int(completion_tokens),
                "total_tokens": int(total_tokens)
            },
            metadata={
                "provider": "mock",
                "is_cached": False,
                "timestamp": time.time()
            }
        )
        
        # Cache the result
        self._set_cache(prompt, model, result, **kwargs)
        
        return result
    
    async def generate_with_template(
        self, 
        template: Union[str, PromptTemplate], 
        **kwargs
    ) -> AIServiceResult:
        """
        Generate mock content using a prompt template
        
        Args:
            template: Template string or PromptTemplate object
            **kwargs: Variables for template (ignored in mock)
            
        Returns:
            AIServiceResult with simulated generated content
        """
        # Format the template
        if isinstance(template, str):
            # Convert to PromptTemplate if it's a string
            prompt_template = PromptTemplate(template=template)
            formatted_prompt = prompt_template.format(**kwargs)
        else:
            # It's already a PromptTemplate
            formatted_prompt = template.format(**kwargs)
        
        # Get feedback type from kwargs if provided
        feedback_type = kwargs.get("feedback_type", "general")
        
        # Get question and answer if provided (for richer mock responses)
        question = kwargs.get("question", "")
        answer = kwargs.get("answer", "")
        
        # If both question and answer are provided, append to the prompt
        if question and answer:
            formatted_prompt = f"Question: {question}\n\nAnswer: {answer}\n\n{formatted_prompt}"
        
        # Pass to generate method
        return await self.generate(formatted_prompt, feedback_type=feedback_type, **kwargs)
