"""
Video Composition Agent for Educational Videos
Combines Manim animations with LMNT audio narration
"""

import os
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Optional video processing imports
try:
    # Import MoviePy components (v1.0.3 compatible)
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
        concatenate_videoclips, ImageClip, ColorClip
    )
    HAS_MOVIEPY = True
    VIDEO_AVAILABLE = True
    TEXT_CLIP_AVAILABLE = True
    print("✅ MoviePy video composition available (v1.0.3)")
    
except ImportError as e:
    HAS_MOVIEPY = False
    VIDEO_AVAILABLE = False
    TEXT_CLIP_AVAILABLE = False
    print(f"⚠️ MoviePy not available - video composition will be simulated ({e})")
    # Create dummy classes for type annotations
    class VideoFileClip:
        pass
    class AudioFileClip:
        pass
    class TextClip:
        pass
    class CompositeVideoClip:
        pass
    class ImageClip:
        pass
    class ColorClip:
        pass
    def concatenate_videoclips(clips):
        pass
    print("⚠️  MoviePy not available - video composition will be simulated")

import numpy as np

from crewai import Agent
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class VideoComposerAgent(Agent):
    """
    Agent for composing final educational videos from all components.
    Handles synchronization, transitions, captions, and accessibility features.
    """
    
    def __init__(self, **kwargs):
        default_config = {
            "role": "Video Composition Specialist",
            "goal": "Create polished educational videos with perfect audio-visual synchronization",
            "backstory": """You are an expert in video production and educational media. 
            You excel at combining animations, narration, and educational content into 
            cohesive videos that maximize learning outcomes. You ensure all content is 
            accessible with captions, proper pacing, and visual clarity.""",
            "verbose": True,
            "allow_delegation": False,
        }
        config = {**default_config, **kwargs}
        super().__init__(**config)
        
        # Video settings (stored in private attributes)
        self._resolution = (1920, 1080)
        self._fps = 30
        self._transition_duration = 0.5
        
    async def compose_video(self, lesson_plan, animations: List, narration) -> Dict[str, Any]:
        """Compose final video from all components"""
        
        if not HAS_MOVIEPY or not VIDEO_AVAILABLE:
            # Simulate video creation for demo purposes
            print("Video composition not available - using simulation mode")
            return self._simulate_video_creation(lesson_plan, animations, narration)
        
        try:
            # Prepare output directory
            output_dir = Path("output_videos")
            output_dir.mkdir(exist_ok=True)
            
            # Create timeline from lesson plan and sync points
            timeline = self._create_timeline(lesson_plan, animations, narration)
            
            # Load and prepare video clips
            video_clips = self._prepare_video_clips(animations, timeline)
            
            # Load audio narration
            audio_clip = self._prepare_audio(narration)
            
            if audio_clip is None:
                print("Warning: No audio clip available, creating video without audio")
                
            # Create title and section cards
            title_clips = self._create_title_cards(lesson_plan, timeline)
            
            # Combine all video elements
            final_video = self._combine_clips(video_clips, title_clips, timeline)
            
            # Add captions/subtitles
            final_video = self._add_captions(final_video, narration)
            
            # Add audio to video if available
            if audio_clip is not None:
                final_video = final_video.set_audio(audio_clip)
            
            # Add branding/watermark
            final_video = self._add_branding(final_video)
            
            # Export final video
            output_path = output_dir / f"edu_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            
            # High-quality export settings
            final_video.write_videofile(
                str(output_path),
                fps=self._fps,
                codec='libx264',
                audio_codec='aac',
                bitrate="8000k",
                preset='medium',
                threads=4
            )
            
            # Generate accessibility files
            self._generate_accessibility_files(output_path, narration, lesson_plan)
            
            return {
                "video_path": str(output_path),
                "duration": final_video.duration,
                "resolution": self._resolution,
                "fps": self._fps,
                "size_mb": output_path.stat().st_size / (1024 * 1024),
                "accessibility_features": ["captions", "transcript", "chapter_markers"]
            }
            
        except Exception as e:
            print(f"Video composition error: {e}")
            return {
                "video_path": None,
                "error": str(e)
            }
    
    def _simulate_video_creation(self, lesson_plan, animations: List, narration) -> Dict[str, Any]:
        """Simulate video creation when MoviePy is not available"""
        output_dir = Path("output_videos")
        output_dir.mkdir(exist_ok=True)
        
        # Create a placeholder file
        output_path = output_dir / f"demo_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Write video metadata to text file for demo
        metadata = f"""
EduAgent AI - Educational Video (Simulated)
==========================================

Title: {lesson_plan.title}
Subject: {lesson_plan.subject}
Target Audience: {lesson_plan.target_audience}
Duration: {lesson_plan.total_duration} minutes

Sections:
{chr(10).join(f"- {section.title}" for section in lesson_plan.sections)}

Learning Objectives:
{chr(10).join(f"- {obj}" for obj in lesson_plan.learning_objectives)}

Generated: {datetime.now().isoformat()}

NOTE: This is a simulation. Install MoviePy for actual video generation.
"""
        
        output_path.write_text(metadata)
        
        return {
            "video_path": str(output_path),
            "duration": lesson_plan.total_duration * 60,
            "resolution": self._resolution,
            "fps": self._fps,
            "size_mb": 0.001,  # Tiny text file
            "accessibility_features": ["transcript", "chapter_markers"],
            "simulation": True
        }
    
    def _create_timeline(self, lesson_plan, animations, narration) -> List[Dict[str, Any]]:
        """Create unified timeline for all elements"""
        timeline = []
        current_time = 0.0
        
        # Add intro
        timeline.append({
            "type": "title",
            "start": 0,
            "duration": 3.0,
            "content": lesson_plan.title,
            "style": "intro"
        })
        current_time = 3.0
        
        # Process sections with animations
        for i, section in enumerate(lesson_plan.sections):
            # Section title card
            timeline.append({
                "type": "section_title",
                "start": current_time,
                "duration": 2.0,
                "content": section.title,
                "section_index": i
            })
            current_time += 2.0
            
            # Find corresponding animation
            section_animation = None
            for anim in animations:
                if hasattr(anim, 'metadata') and anim.metadata.get('section_index') == i:
                    section_animation = anim
                    break
            
            if section_animation and section_animation.video_path:
                # Add animation
                timeline.append({
                    "type": "animation",
                    "start": current_time,
                    "duration": section_animation.duration or 10.0,
                    "path": section_animation.video_path,
                    "concept": section_animation.concept
                })
                current_time += section_animation.duration or 10.0
            else:
                # Add placeholder or text slide
                timeline.append({
                    "type": "text_slide",
                    "start": current_time,
                    "duration": 5.0,
                    "content": section.content[:200],
                    "concept": section.visualization_concept
                })
                current_time += 5.0
            
            # Add pause between sections
            current_time += 0.5
        
        # Add conclusion
        timeline.append({
            "type": "conclusion",
            "start": current_time,
            "duration": 4.0,
            "content": "Key Takeaways",
            "points": lesson_plan.learning_objectives[:3]
        })
        
        return timeline
    
    def _prepare_video_clips(self, animations: List, timeline: List[Dict]) -> List[VideoFileClip]:
        """Load and prepare animation video clips"""
        clips = []
        
        for event in timeline:
            if event["type"] == "animation" and "path" in event:
                try:
                    clip = VideoFileClip(event["path"])
                    # Resize to standard resolution if needed
                    if clip.size != self._resolution:
                        clip = clip.resize(self._resolution)
                    
                    # Set timing
                    clip = clip.set_start(event["start"])
                    clip = clip.set_duration(event["duration"])
                    
                    # Note: Fade transitions disabled for MoviePy compatibility
                    
                    clips.append(clip)
                except Exception as e:
                    print(f"Error loading animation {event['path']}: {e}")
        
        return clips
    
    def _prepare_audio(self, narration) -> AudioFileClip:
        """Prepare audio narration clip"""
        try:
            audio = AudioFileClip(narration.audio_path)
            # Note: Audio effects disabled due to MoviePy import issues
            # Would normally add fade in/out here
            return audio
        except Exception as e:
            print(f"Error loading audio: {e}")
            # Return None - will be handled by caller
            return None
    
    def _create_title_cards(self, lesson_plan, timeline: List[Dict]) -> List[TextClip]:
        """Create title and section cards"""
        clips = []
        
        for event in timeline:
            if event["type"] in ["title", "section_title", "conclusion"]:
                # Create background
                bg = ColorClip(size=self._resolution, color=(25, 25, 25), duration=event["duration"])
                
                # Main text
                if event["type"] == "title":
                    txt_clip = TextClip(
                        event["content"],
                        fontsize=80,
                        color='white',
                        font='Arial-Bold',
                        size=self._resolution
                    ).set_position('center')
                    
                    # Add subtitle
                    subtitle = TextClip(
                        f"Grade: {lesson_plan.target_audience}",
                        fontsize=40,
                        color='gray',
                        font='Arial',
                        size=self._resolution
                    ).set_position(('center', 'bottom'))
                    
                    clip = CompositeVideoClip([bg, txt_clip, subtitle])
                    
                elif event["type"] == "section_title":
                    txt_clip = TextClip(
                        event["content"],
                        fontsize=60,
                        color='white',
                        font='Arial-Bold',
                        size=self._resolution
                    ).set_position('center')
                    
                    clip = CompositeVideoClip([bg, txt_clip])
                    
                elif event["type"] == "conclusion":
                    # Main title
                    title = TextClip(
                        event["content"],
                        fontsize=60,
                        color='white',
                        font='Arial-Bold',
                        size=self._resolution
                    ).set_position(('center', 200))
                    
                    # Learning objectives
                    objectives_text = "\n".join([f"• {obj}" for obj in event["points"]])
                    objectives = TextClip(
                        objectives_text,
                        fontsize=40,
                        color='white',
                        font='Arial',
                        size=(1600, 600),
                        method='caption'
                    ).set_position(('center', 400))
                    
                    clip = CompositeVideoClip([bg, title, objectives])
                
                # Set timing and transitions
                clip = clip.set_start(event["start"]).set_duration(event["duration"])
                # Note: Effects disabled for compatibility
                
                clips.append(clip)
            
            elif event["type"] == "text_slide":
                # Create educational text slide for sections without animations
                bg = ColorClip(size=self._resolution, color=(25, 25, 25), duration=event["duration"])
                
                text_clip = TextClip(
                    event["content"],
                    fontsize=45,
                    color='white',
                    font='Arial',
                    size=(1600, 800),
                    method='caption'
                ).set_position('center')
                
                clip = CompositeVideoClip([bg, text_clip])
                clip = clip.set_start(event["start"]).set_duration(event["duration"])
                # Note: Effects disabled for compatibility
                
                clips.append(clip)
        
        return clips
    
    def _combine_clips(self, video_clips: List, title_clips: List, timeline: List[Dict]) -> VideoFileClip:
        """Combine all clips into final video"""
        all_clips = video_clips + title_clips
        
        # Sort by start time
        all_clips.sort(key=lambda x: x.start)
        
        # Create composite
        final_video = CompositeVideoClip(all_clips)
        
        # Set total duration based on timeline
        total_duration = max(event["start"] + event["duration"] for event in timeline)
        final_video = final_video.set_duration(total_duration)
        
        return final_video
    
    def _add_captions(self, video: VideoFileClip, narration) -> VideoFileClip:
        """Add captions/subtitles to video"""
        # For full implementation, would use narration.segments
        # to create properly timed subtitles
        
        # Example: Add a sample caption
        if hasattr(narration, 'segments') and narration.segments:
            caption_clips = []
            
            for segment in narration.segments[:5]:  # Limit for demo
                if segment.text and segment.text != "[pause]":
                    caption = TextClip(
                        segment.text[:100],  # Truncate long captions
                        fontsize=35,
                        color='white',
                        font='Arial',
                        size=(1600, 100),
                        method='caption',
                        stroke_color='black',
                        stroke_width=2
                    ).set_position(('center', 'bottom')).set_start(segment.start_time).set_duration(segment.duration)
                    
                    caption_clips.append(caption)
            
            if caption_clips:
                video = CompositeVideoClip([video] + caption_clips)
        
        return video
    
    def _add_branding(self, video: VideoFileClip) -> VideoFileClip:
        """Add watermark/branding"""
        # Add small watermark
        watermark = TextClip(
            "EduAgent AI",
            fontsize=20,
            color='white',
            font='Arial',
            opacity=0.5
        ).set_position(('right', 'bottom')).set_duration(video.duration)
        
        return CompositeVideoClip([video, watermark])
    
    def _generate_accessibility_files(self, video_path: Path, narration, lesson_plan):
        """Generate transcript and other accessibility files"""
        base_path = video_path.parent / video_path.stem
        
        # Generate transcript
        transcript_path = f"{base_path}_transcript.txt"
        with open(transcript_path, 'w') as f:
            f.write(f"Transcript for: {lesson_plan.title}\n")
            f.write("=" * 50 + "\n\n")
            f.write(narration.transcript)
        
        # Generate chapter markers
        chapters_path = f"{base_path}_chapters.txt"
        with open(chapters_path, 'w') as f:
            f.write("Chapter Markers\n")
            f.write("=" * 30 + "\n")
            current_time = 3.0  # After intro
            for i, section in enumerate(lesson_plan.sections):
                minutes = int(current_time // 60)
                seconds = int(current_time % 60)
                f.write(f"{minutes:02d}:{seconds:02d} - {section.title}\n")
                current_time += section.duration_estimate * 60


# Standalone test function
async def test_video_composer():
    """Test video composition"""
    from art_lesson_planner_agent.lesson_planner_agent import LessonPlan, LessonSection
    from matt_manim_agent.manim_agent import ManimOutput
    from audio_narrator_lmnt import EnhancedAudioNarration, AudioSegment
    
    # Create sample data
    lesson_plan = LessonPlan(
        title="Introduction to Calculus",
        subject="Mathematics",
        target_audience="High School",
        total_duration=15.0,
        prerequisites=["Algebra"],
        learning_objectives=["Understand derivatives", "Apply chain rule"],
        sections=[
            LessonSection(
                title="What are Derivatives?",
                content="Derivatives measure rate of change...",
                visualization_concept="tangent line",
                duration_estimate=5.0
            )
        ],
        assessment_questions=[],
        resources=[]
    )
    
    # Mock animation output
    animation = ManimOutput(
        success=True,
        video_path="sample_animation.mp4",
        duration=10.0,
        concept="derivatives",
        visual_elements=["graph", "tangent"],
        metadata={"section_index": 0}
    )
    
    # Mock narration
    narration = EnhancedAudioNarration(
        audio_path="sample_narration.wav",
        duration=15.0,
        transcript="Welcome to calculus...",
        segments=[
            AudioSegment(
                text="Welcome to our lesson",
                start_time=0.0,
                duration=3.0
            )
        ],
        voice_config=None,
        sync_points=[]
    )
    
    # Create composer and test
    composer = VideoComposerAgent()
    result = await composer.compose_video(lesson_plan, [animation], narration)
    
    print(f"Video composition result: {result}")


if __name__ == "__main__":
    asyncio.run(test_video_composer())