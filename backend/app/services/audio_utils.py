"""
Utility functions for audio processing and manipulation.

This module provides helpers for common audio tasks like format conversion,
normalization, and other pre-processing needed before transcription.
"""

import os
import tempfile
import logging
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)


class AudioProcessingError(Exception):
    """Exception raised when audio processing fails."""
    pass


def check_ffmpeg_installed() -> bool:
    """
    Check if FFmpeg is installed and available in the system path.
    
    Returns:
        bool: True if FFmpeg is installed, False otherwise
    """
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_audio_info(file_path: str) -> dict:
    """
    Get information about an audio file using FFmpeg.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        dict: Information about the audio file including format, duration, 
              sample rate, channels, etc.
              
    Raises:
        AudioProcessingError: If FFmpeg is not installed or the file cannot be processed
    """
    if not check_ffmpeg_installed():
        raise AudioProcessingError("FFmpeg is not installed")
        
    if not os.path.exists(file_path):
        raise AudioProcessingError(f"File not found: {file_path}")
    
    try:
        # Run FFprobe to get file information in JSON format
        result = subprocess.run(
            [
                "ffprobe", 
                "-v", "quiet", 
                "-print_format", "json", 
                "-show_format", 
                "-show_streams", 
                file_path
            ], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            raise AudioProcessingError(f"Failed to get audio info: {result.stderr}")
        
        import json
        info = json.loads(result.stdout)
        
        # Extract relevant information
        audio_info = {
            "format": info.get("format", {}).get("format_name", "unknown"),
            "duration": float(info.get("format", {}).get("duration", 0)),
            "size": int(info.get("format", {}).get("size", 0)),
        }
        
        # Find audio stream
        for stream in info.get("streams", []):
            if stream.get("codec_type") == "audio":
                audio_info.update({
                    "codec": stream.get("codec_name", "unknown"),
                    "sample_rate": int(stream.get("sample_rate", 0)),
                    "channels": int(stream.get("channels", 0)),
                    "bit_rate": int(stream.get("bit_rate", 0)) if "bit_rate" in stream else None
                })
                break
        
        return audio_info
    
    except Exception as e:
        raise AudioProcessingError(f"Error getting audio information: {str(e)}")


def convert_audio_format(
    input_path: str, 
    output_format: str = "wav",
    output_path: Optional[str] = None,
    sample_rate: Optional[int] = None,
    channels: Optional[int] = None
) -> str:
    """
    Convert an audio file to another format using FFmpeg.
    
    Args:
        input_path: Path to the input audio file
        output_format: Target format (wav, mp3, ogg, etc.)
        output_path: Path for the output file (optional)
        sample_rate: Target sample rate in Hz (optional)
        channels: Target number of channels (optional)
        
    Returns:
        str: Path to the converted audio file
        
    Raises:
        AudioProcessingError: If conversion fails
    """
    if not check_ffmpeg_installed():
        raise AudioProcessingError("FFmpeg is not installed")
        
    if not os.path.exists(input_path):
        raise AudioProcessingError(f"Input file not found: {input_path}")
    
    # Generate output path if not provided
    if not output_path:
        input_dir = os.path.dirname(input_path)
        input_filename = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(input_dir, f"{input_filename}.{output_format}")
    
    try:
        # Build FFmpeg command
        cmd = ["ffmpeg", "-i", input_path]
        
        # Add sample rate if provided
        if sample_rate:
            cmd.extend(["-ar", str(sample_rate)])
            
        # Add channels if provided
        if channels:
            cmd.extend(["-ac", str(channels)])
            
        # Add output file
        cmd.extend(["-y", output_path])
        
        # Run FFmpeg
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            raise AudioProcessingError(f"Conversion failed: {result.stderr}")
        
        return output_path
    
    except Exception as e:
        raise AudioProcessingError(f"Error converting audio: {str(e)}")


def normalize_audio(
    input_path: str,
    output_path: Optional[str] = None,
    target_level: float = -3.0
) -> str:
    """
    Normalize audio to a target level using FFmpeg.
    
    Args:
        input_path: Path to the input audio file
        output_path: Path for the output file (optional)
        target_level: Target normalization level in dB (default: -3.0)
        
    Returns:
        str: Path to the normalized audio file
        
    Raises:
        AudioProcessingError: If normalization fails
    """
    if not check_ffmpeg_installed():
        raise AudioProcessingError("FFmpeg is not installed")
        
    if not os.path.exists(input_path):
        raise AudioProcessingError(f"Input file not found: {input_path}")
    
    # Generate output path if not provided
    if not output_path:
        input_dir = os.path.dirname(input_path)
        input_filename = os.path.splitext(os.path.basename(input_path))[0]
        input_ext = os.path.splitext(input_path)[1]
        output_path = os.path.join(input_dir, f"{input_filename}_normalized{input_ext}")
    
    try:
        # Run FFmpeg with loudnorm filter
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-af", f"loudnorm=I={target_level}:TP=-1.5:LRA=11",
            "-y", output_path
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            raise AudioProcessingError(f"Normalization failed: {result.stderr}")
        
        return output_path
    
    except Exception as e:
        raise AudioProcessingError(f"Error normalizing audio: {str(e)}")


def remove_silence(
    input_path: str, 
    output_path: Optional[str] = None,
    silence_threshold: float = -50.0,
    min_silence_duration: float = 0.5
) -> str:
    """
    Remove silence from an audio file using FFmpeg.
    
    Args:
        input_path: Path to the input audio file
        output_path: Path for the output file (optional)
        silence_threshold: Threshold for silence detection in dB (default: -50.0)
        min_silence_duration: Minimum silence duration to remove in seconds (default: 0.5)
        
    Returns:
        str: Path to the audio file with silence removed
        
    Raises:
        AudioProcessingError: If silence removal fails
    """
    if not check_ffmpeg_installed():
        raise AudioProcessingError("FFmpeg is not installed")
        
    if not os.path.exists(input_path):
        raise AudioProcessingError(f"Input file not found: {input_path}")
    
    # Generate output path if not provided
    if not output_path:
        input_dir = os.path.dirname(input_path)
        input_filename = os.path.splitext(os.path.basename(input_path))[0]
        input_ext = os.path.splitext(input_path)[1]
        output_path = os.path.join(input_dir, f"{input_filename}_trimmed{input_ext}")
    
    try:
        # Run FFmpeg with silenceremove filter
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-af", f"silenceremove=stop_periods=-1:stop_threshold={silence_threshold}dB:stop_duration={min_silence_duration}",
            "-y", output_path
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            raise AudioProcessingError(f"Silence removal failed: {result.stderr}")
        
        return output_path
    
    except Exception as e:
        raise AudioProcessingError(f"Error removing silence: {str(e)}")


def split_audio(
    input_path: str,
    output_dir: Optional[str] = None,
    segment_duration: float = 60.0
) -> List[str]:
    """
    Split an audio file into segments of specified duration using FFmpeg.
    
    Args:
        input_path: Path to the input audio file
        output_dir: Directory for output segments (optional)
        segment_duration: Duration of each segment in seconds (default: 60.0)
        
    Returns:
        List[str]: Paths to the audio segments
        
    Raises:
        AudioProcessingError: If splitting fails
    """
    if not check_ffmpeg_installed():
        raise AudioProcessingError("FFmpeg is not installed")
        
    if not os.path.exists(input_path):
        raise AudioProcessingError(f"Input file not found: {input_path}")
    
    # Generate output directory if not provided
    if not output_dir:
        output_dir = os.path.dirname(input_path)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename pattern
    input_filename = os.path.splitext(os.path.basename(input_path))[0]
    input_ext = os.path.splitext(input_path)[1]
    output_pattern = os.path.join(output_dir, f"{input_filename}_%03d{input_ext}")
    
    try:
        # Run FFmpeg to split the audio
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-f", "segment",
            "-segment_time", str(segment_duration),
            "-reset_timestamps", "1",
            "-map", "0:a",
            "-y", output_pattern
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            raise AudioProcessingError(f"Splitting failed: {result.stderr}")
        
        # Get the list of generated files
        segments = []
        i = 0
        while True:
            segment_path = os.path.join(output_dir, f"{input_filename}_{i:03d}{input_ext}")
            if os.path.exists(segment_path):
                segments.append(segment_path)
                i += 1
            else:
                break
        
        return segments
    
    except Exception as e:
        raise AudioProcessingError(f"Error splitting audio: {str(e)}")


def prepare_for_transcription(
    input_path: str,
    output_path: Optional[str] = None,
    normalize: bool = True,
    remove_background_noise: bool = False,
    target_format: str = "wav",
    target_sample_rate: int = 16000,
    target_channels: int = 1
) -> str:
    """
    Prepare an audio file for optimal transcription.
    
    This function applies a series of processing steps to optimize audio for speech-to-text:
    1. Convert to the target format (default: WAV)
    2. Normalize audio levels (optional)
    3. Remove background noise (optional)
    4. Convert to mono if necessary
    5. Set appropriate sample rate for speech recognition
    
    Args:
        input_path: Path to the input audio file
        output_path: Path for the output file (optional)
        normalize: Whether to normalize audio levels (default: True)
        remove_background_noise: Whether to attempt noise reduction (default: False)
        target_format: Target audio format (default: wav)
        target_sample_rate: Target sample rate in Hz (default: 16000)
        target_channels: Target number of channels (default: 1 for mono)
        
    Returns:
        str: Path to the processed audio file
        
    Raises:
        AudioProcessingError: If processing fails
    """
    if not check_ffmpeg_installed():
        raise AudioProcessingError("FFmpeg is not installed")
        
    if not os.path.exists(input_path):
        raise AudioProcessingError(f"Input file not found: {input_path}")
    
    # Generate output path if not provided
    if not output_path:
        input_dir = os.path.dirname(input_path)
        input_filename = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(input_dir, f"{input_filename}_processed.{target_format}")
    
    try:
        # Create a temp file for intermediate processing
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_format}")
        temp_path = temp_file.name
        temp_file.close()
        
        current_path = input_path
        
        # Step 1: Convert to target format with specified sample rate and channels
        current_path = convert_audio_format(
            current_path,
            output_format=target_format,
            output_path=temp_path,
            sample_rate=target_sample_rate,
            channels=target_channels
        )
        
        # Step 2: Normalize audio levels if requested
        if normalize:
            normalize_temp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_format}")
            normalize_temp_path = normalize_temp.name
            normalize_temp.close()
            
            current_path = normalize_audio(
                current_path,
                output_path=normalize_temp_path
            )
            
            # Clean up previous temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
            temp_path = normalize_temp_path
        
        # Step 3: Apply noise reduction if requested
        if remove_background_noise:
            noise_reduction_temp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_format}")
            noise_reduction_temp_path = noise_reduction_temp.name
            noise_reduction_temp.close()
            
            # Run FFmpeg with noise reduction filter
            cmd = [
                "ffmpeg",
                "-i", current_path,
                "-af", "afftdn=nf=-25",  # Adaptive FFT noise filter
                "-y", noise_reduction_temp_path
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                logger.warning(f"Noise reduction failed, using normalized audio: {result.stderr}")
            else:
                # Clean up previous temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
                current_path = noise_reduction_temp_path
                temp_path = noise_reduction_temp_path
        
        # Move the final temp file to the output path
        import shutil
        shutil.move(current_path, output_path)
        
        # Clean up any remaining temp files
        if os.path.exists(temp_path) and temp_path != current_path:
            os.unlink(temp_path)
        
        return output_path
    
    except Exception as e:
        # Clean up temp files on error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
            
        raise AudioProcessingError(f"Error preparing audio for transcription: {str(e)}")
