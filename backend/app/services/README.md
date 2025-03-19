# Service Integrations

This directory contains service integrations for the Interview Prep Platform.

## AI Services

The AI services provide natural language processing capabilities, primarily for generating personalized feedback on user answers.

### Usage

```python
from app.services.ai import default_ai_service

# Generate feedback for an answer
result = await default_ai_service.generate_feedback(
    question="Tell me about a time you solved a difficult problem.",
    answer="I encountered a critical bug in our production system...",
    feedback_type="behavioral"  # or "technical", "general"
)

# Parse response (JSON format)
feedback_data = json.loads(result.content)
print(f"Score: {feedback_data['score']}")
print(f"Feedback: {feedback_data['feedback']}")
```

### Features

- **Multiple Providers**: Easily switch between OpenAI and mock implementations
- **Template System**: Specialized prompt templates for different question types
- **Caching**: Efficient caching to avoid duplicate API calls and reduce costs
- **Rate Limiting**: Built-in rate limiting to manage API quotas
- **Error Handling**: Comprehensive error handling and retry logic

### Configuration

Configure the AI service in `.env` or through environment variables:

```
AI_PROVIDER=openai  # or "mock" for development
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4
AI_RATE_LIMIT_REQUESTS_PER_MINUTE=60
AI_RATE_LIMIT_REQUESTS_PER_DAY=1000
AI_CACHE_ENABLED=true
AI_CACHE_TTL=3600
```

## Transcription Services

The transcription services provide speech-to-text capabilities for analyzing audio responses.

### Usage

```python
from app.services.transcription import default_transcription_service

# Transcribe an audio file
result = await default_transcription_service.transcribe_file(
    file_path="path/to/audio.wav",
    language="en"
)

print(f"Transcription: {result.text}")
print(f"Confidence: {result.confidence}")
```

### Features

- **Multiple Providers**: Support for Deepgram with fallback to mock implementation
- **Audio Format Support**: Works with various audio formats
- **Error Handling**: Robust error handling and retry logic
- **Rate Limiting**: Built-in rate limiting to manage API quotas

### Configuration

Configure the transcription service in `.env` or through environment variables:

```
TRANSCRIPTION_PROVIDER=deepgram  # or "mock" for development
DEEPGRAM_API_KEY=your-api-key
TRANSCRIPTION_RATE_LIMIT_REQUESTS_PER_MINUTE=30
TRANSCRIPTION_RATE_LIMIT_REQUESTS_PER_DAY=500
```

## Audio Utilities

The platform includes audio processing utilities to optimize audio files for transcription.

### Usage

```python
from app.services import audio_utils

# Get information about an audio file
audio_info = audio_utils.get_audio_info("path/to/audio.mp3")
print(f"Duration: {audio_info['duration']} seconds")

# Prepare audio for optimal transcription
processed_path = audio_utils.prepare_for_transcription(
    input_path="path/to/audio.mp3",
    normalize=True,
    remove_background_noise=False,
    target_format="wav",
    target_sample_rate=16000,
    target_channels=1
)
```

### Features

- **Format Conversion**: Convert between audio formats
- **Normalization**: Adjust audio levels for better transcription
- **Noise Reduction**: Remove background noise
- **Silence Removal**: Trim silence from recordings
- **Split Audio**: Divide long recordings into manageable chunks

### Requirements

Audio processing features require FFmpeg to be installed on the system:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Development Guide

### Adding a New AI Provider

1. Create a new implementation in `app/services/ai/your_provider_service.py`
2. Inherit from `BaseAIService` and implement all required methods
3. Add your provider to the `AIProvider` enum in `factory.py`
4. Update the factory to handle the new provider

### Adding a New Transcription Provider

1. Create a new implementation in `app/services/transcription/your_provider_service.py`
2. Inherit from `BaseTranscriptionService` and implement all required methods
3. Add your provider to the `TranscriptionProvider` enum in `factory.py`
4. Update the factory to handle the new provider
