"""
LMNT Audio Narration Agent for Educational Videos
Provides ultra-low latency, lifelike speech synthesis
"""

import os
import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import wave
import struct

from crewai import Agent
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class LMNTVoiceConfig(BaseModel):
    """LMNT voice configuration"""
    voice_id: str = Field(default="lily", description="LMNT voice ID")
    speed: float = Field(default=1.0, description="Speech speed multiplier")
    emotion: Optional[str] = Field(default=None, description="Emotion modifier")
    
    # Educational optimizations
    clarity_boost: bool = Field(default=True, description="Enhance clarity for education")
    pause_at_punctuation: bool = Field(default=True, description="Natural pauses")
    emphasis_keywords: List[str] = Field(default_factory=list, description="Words to emphasize")


class AudioSegment(BaseModel):
    """Individual audio segment with timing"""
    text: str = Field(description="Text for this segment")
    start_time: float = Field(description="Start time in seconds")
    duration: float = Field(description="Duration in seconds")
    audio_data: Optional[bytes] = Field(default=None, description="Audio data")
    sync_event: Optional[str] = Field(default=None, description="Associated visual event")


class EnhancedAudioNarration(BaseModel):
    """Enhanced audio narration with LMNT features"""
    audio_path: str = Field(description="Path to generated audio file")
    duration: float = Field(description="Total duration in seconds")
    transcript: str = Field(description="Full narration transcript")
    segments: List[AudioSegment] = Field(default_factory=list, description="Audio segments")
    voice_config: LMNTVoiceConfig = Field(description="Voice configuration used")
    sync_points: List[Dict[str, Any]] = Field(default_factory=list, description="Visual sync points")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LMNTNarratorAgent(Agent):
    """
    Advanced audio narration agent using LMNT's ultra-fast TTS
    Optimized for educational content with perfect visual synchronization
    """
    
    def __init__(self, **kwargs):
        default_config = {
            "role": "LMNT Audio Narration Specialist",
            "goal": "Create crystal-clear, engaging educational narration with perfect timing",
            "backstory": """You are an expert in educational audio production using cutting-edge 
            LMNT AI voices. You create narrations that enhance learning through optimal pacing, 
            emphasis, and synchronization with visual content. Your narrations make complex 
            concepts accessible and engaging.""",
            "verbose": True,
            "allow_delegation": False,
        }
        config = {**default_config, **kwargs}
        super().__init__(**config)
        
        # Store API configuration in private attributes
        self._api_key = os.getenv("LMNT_API_KEY")
        self._base_url = "https://api.lmnt.com"
        
        # Educational voice presets (stored in private attribute)
        self._voice_presets = {
            "math_teacher": {"voice_id": "lily", "speed": 0.95, "clarity_boost": True},
            "science_explainer": {"voice_id": "daniel", "speed": 1.0, "clarity_boost": True},
            "friendly_tutor": {"voice_id": "sarah", "speed": 1.05, "emotion": "friendly"},
            "professor": {"voice_id": "james", "speed": 0.9, "emotion": "professional"}
        }
    
    async def generate_narration(self, lesson_plan, animations, voice_preset="math_teacher") -> EnhancedAudioNarration:
        """Generate LMNT narration optimized for educational content"""
        
        # Select voice configuration
        voice_config = LMNTVoiceConfig(**self._voice_presets.get(voice_preset, self._voice_presets["math_teacher"]))
        
        # Create educational transcript with timing markers
        transcript, segments = self._create_educational_transcript(lesson_plan, animations)
        
        # Generate audio for each segment
        audio_segments = await self._generate_audio_segments(segments, voice_config)
        
        # Combine audio segments with proper timing
        final_audio_path = await self._combine_audio_segments(audio_segments)
        
        # Calculate total duration
        total_duration = sum(seg.duration for seg in audio_segments)
        
        # Create visual sync points
        sync_points = self._create_sync_points(audio_segments, animations)
        
        return EnhancedAudioNarration(
            audio_path=final_audio_path,
            duration=total_duration,
            transcript=transcript,
            segments=audio_segments,
            voice_config=voice_config,
            sync_points=sync_points,
            metadata={
                "voice_preset": voice_preset,
                "generation_method": "LMNT",
                "quality": "studio"
            }
        )
    
    def _create_educational_transcript(self, lesson_plan, animations):
        """Create transcript optimized for education with proper pacing"""
        
        transcript = f"Welcome to our lesson on {lesson_plan.title}. "
        transcript += "Let's explore this fascinating topic together.\n\n"
        
        segments = []
        current_time = 0.0
        
        # Introduction segment
        intro_text = f"Today, we'll learn about {lesson_plan.title}. "
        if lesson_plan.learning_objectives:
            intro_text += f"By the end of this lesson, you'll understand {lesson_plan.learning_objectives[0]}. "
        
        segments.append(AudioSegment(
            text=intro_text,
            start_time=current_time,
            duration=5.0,  # Estimated
            sync_event="intro_animation"
        ))
        current_time += 5.0
        
        # Process each section
        for i, section in enumerate(lesson_plan.sections):
            # Section introduction
            section_intro = f"\n\nNow, let's explore {section.title}. "
            
            # Add pause for visual transition
            segments.append(AudioSegment(
                text="[pause]",
                start_time=current_time,
                duration=1.0,
                sync_event=f"section_{i}_transition"
            ))
            current_time += 1.0
            
            # Main content with emphasis on key concepts
            content = self._add_educational_emphasis(section.content)
            
            # Check for visualization points
            if section.visualization_concept:
                # Split content around visualization
                parts = content.split("{visualization}")
                
                if len(parts) > 1:
                    # Before visualization
                    segments.append(AudioSegment(
                        text=section_intro + parts[0],
                        start_time=current_time,
                        duration=len(parts[0].split()) * 0.15,  # ~0.15s per word
                        sync_event=f"pre_animation_{i}"
                    ))
                    current_time += segments[-1].duration
                    
                    # During visualization - slower pace
                    viz_narration = f"Watch carefully as we visualize {section.visualization_concept}. "
                    segments.append(AudioSegment(
                        text=viz_narration,
                        start_time=current_time,
                        duration=3.0,
                        sync_event=f"animation_{i}_start"
                    ))
                    current_time += 3.0
                    
                    # After visualization
                    if len(parts) > 1 and parts[1]:
                        segments.append(AudioSegment(
                            text=parts[1],
                            start_time=current_time,
                            duration=len(parts[1].split()) * 0.15,
                            sync_event=f"post_animation_{i}"
                        ))
                        current_time += segments[-1].duration
                else:
                    # No visualization marker
                    segments.append(AudioSegment(
                        text=section_intro + content,
                        start_time=current_time,
                        duration=len(content.split()) * 0.15,
                        sync_event=f"section_{i}_content"
                    ))
                    current_time += segments[-1].duration
            
            transcript += section_intro + content
        
        # Conclusion
        conclusion = "\n\nLet's recap what we've learned today. "
        for obj in lesson_plan.learning_objectives[:2]:
            conclusion += f"{obj}. "
        
        segments.append(AudioSegment(
            text=conclusion,
            start_time=current_time,
            duration=5.0,
            sync_event="conclusion"
        ))
        
        transcript += conclusion
        
        return transcript, segments
    
    def _add_educational_emphasis(self, content: str) -> str:
        """Add emphasis markers for educational clarity"""
        
        # Keywords to emphasize in math/science
        emphasis_words = [
            "therefore", "because", "remember", "notice", "observe",
            "important", "key", "critical", "essential", "fundamental",
            "first", "second", "finally", "in conclusion"
        ]
        
        # Add slight pauses after important punctuation
        content = content.replace(". ", ". [pause] ")
        content = content.replace("? ", "? [pause] ")
        content = content.replace(": ", ": [pause] ")
        
        # Add emphasis markers
        for word in emphasis_words:
            content = content.replace(f" {word} ", f" *{word}* ")
            content = content.replace(f" {word.capitalize()} ", f" *{word.capitalize()}* ")
        
        return content
    
    async def _generate_audio_segments(self, segments: List[AudioSegment], voice_config: LMNTVoiceConfig) -> List[AudioSegment]:
        """Generate audio for each segment using LMNT API"""
        
        async with aiohttp.ClientSession() as session:
            audio_segments = []
            
            for segment in segments:
                if segment.text == "[pause]":
                    # Generate silence
                    segment.audio_data = self._generate_silence(segment.duration)
                else:
                    # Generate speech via LMNT
                    audio_data = await self._call_lmnt_api(session, segment.text, voice_config)
                    segment.audio_data = audio_data
                    
                    # Update duration based on actual audio
                    if audio_data:
                        segment.duration = self._calculate_audio_duration(audio_data)
                
                audio_segments.append(segment)
        
        return audio_segments
    
    async def _call_lmnt_api(self, session: aiohttp.ClientSession, text: str, voice_config: LMNTVoiceConfig) -> bytes:
        """Call LMNT API for text-to-speech"""
        
        headers = {
            "X-API-Key": self._api_key,
            "Content-Type": "application/json"
        }
        
        # Process emphasis markers
        text = text.replace("*", "")  # LMNT handles emphasis differently
        
        payload = {
            "text": text,
            "voice": voice_config.voice_id,
            "speed": voice_config.speed,
            "format": "wav",  # WAV for easier processing
            "sample_rate": 24000
        }
        
        if voice_config.emotion:
            payload["emotion"] = voice_config.emotion
        
        try:
            async with session.post(
                f"{self._base_url}/v1/ai/speech",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    # LMNT returns JSON with base64-encoded audio
                    response_data = await response.json()
                    if "audio" in response_data:
                        import base64
                        audio_base64 = response_data["audio"]
                        audio_bytes = base64.b64decode(audio_base64)
                        return audio_bytes
                    else:
                        print(f"LMNT API: No audio in response")
                        return b""
                else:
                    error_text = await response.text()
                    print(f"LMNT API error: {response.status} - {error_text}")
                    return b""
        except Exception as e:
            print(f"Error calling LMNT API: {e}")
            return b""
    
    def _generate_silence(self, duration: float) -> bytes:
        """Generate WAV silence of specified duration"""
        sample_rate = 24000
        num_samples = int(duration * sample_rate)
        
        # WAV header + silence
        wav_data = b'RIFF'
        wav_data += struct.pack('<I', 36 + num_samples * 2)
        wav_data += b'WAVEfmt '
        wav_data += struct.pack('<IHHIIHH', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16)
        wav_data += b'data'
        wav_data += struct.pack('<I', num_samples * 2)
        wav_data += b'\x00\x00' * num_samples
        
        return wav_data
    
    def _calculate_audio_duration(self, audio_data: bytes) -> float:
        """Calculate duration from WAV data"""
        try:
            # Parse WAV header
            sample_rate = struct.unpack('<I', audio_data[24:28])[0]
            data_size = struct.unpack('<I', audio_data[40:44])[0]
            duration = data_size / (sample_rate * 2)  # 16-bit samples
            return duration
        except:
            return 5.0  # Default fallback
    
    async def _combine_audio_segments(self, segments: List[AudioSegment]) -> str:
        """Combine audio segments into final file"""
        output_path = Path("narration_lmnt.wav")
        
        # In production, use pydub or similar for proper audio mixing
        # For now, save the first non-empty segment as demo
        for segment in segments:
            if segment.audio_data and len(segment.audio_data) > 1000:
                with open(output_path, 'wb') as f:
                    f.write(segment.audio_data)
                break
        
        return str(output_path)
    
    def _create_sync_points(self, segments: List[AudioSegment], animations) -> List[Dict[str, Any]]:
        """Create synchronization points between audio and visuals"""
        sync_points = []
        
        for segment in segments:
            if segment.sync_event:
                sync_points.append({
                    "time": segment.start_time,
                    "duration": segment.duration,
                    "event": segment.sync_event,
                    "type": "audio_visual_sync"
                })
        
        # Add animation-specific sync points
        for i, animation in enumerate(animations):
            if animation.sync_points:
                for sp in animation.sync_points:
                    sync_points.append({
                        "time": sp.get("time", 0),
                        "event": f"animation_{i}_{sp.get('event', 'unknown')}",
                        "type": "animation_event"
                    })
        
        # Sort by time
        sync_points.sort(key=lambda x: x["time"])
        
        return sync_points


# Standalone test function
async def test_lmnt_narration():
    """Test LMNT narration generation"""
    from art_lesson_planner_agent.lesson_planner_agent import LessonPlan, LessonSection
    
    # Create sample lesson plan
    lesson_plan = LessonPlan(
        title="Introduction to Derivatives",
        subject="Calculus",
        target_audience="High School",
        total_duration=10.0,
        prerequisites=["Algebra", "Functions"],
        learning_objectives=["Understand the concept of rate of change", "Calculate basic derivatives"],
        sections=[
            LessonSection(
                title="What is a Derivative?",
                content="A derivative represents the rate of change of a function. {visualization} Notice how the slope changes.",
                visualization_concept="tangent line to curve",
                duration_estimate=5.0
            )
        ],
        assessment_questions=["What does the derivative represent?"],
        resources=["Calculus textbook chapter 3"]
    )
    
    # Create narrator
    narrator = LMNTNarratorAgent()
    
    # Generate narration
    narration = await narrator.generate_narration(lesson_plan, [], voice_preset="math_teacher")
    
    print(f"Generated narration: {narration.audio_path}")
    print(f"Duration: {narration.duration} seconds")
    print(f"Sync points: {len(narration.sync_points)}")
    

if __name__ == "__main__":
    asyncio.run(test_lmnt_narration())