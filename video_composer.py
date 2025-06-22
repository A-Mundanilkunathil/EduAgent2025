"""
Simple Video Composer for EduAgent AI
Works without ImageMagick by using solid colors instead of text
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from crewai import Agent

try:
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, CompositeVideoClip,
        concatenate_videoclips, ColorClip
    )
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False

class VideoComposerAgent(Agent):
    """Video composer agent using simple composition without ImageMagick"""
    
    def __init__(self, **kwargs):
        # Set up default agent config
        default_config = {
            "role": "Video Composer",
            "goal": "Create engaging educational videos with animations and narration",
            "backstory": "Expert video editor specializing in educational content",
            "verbose": True,
            "allow_delegation": False,
        }
        config = {**default_config, **kwargs}
        super().__init__(**config)
        
        self._composer = SimpleVideoComposer()
    
    async def compose_video(self, lesson_plan, animations, narration):
        """Delegate to simple composer"""
        return await self._composer.compose_video(lesson_plan, animations, narration)

class SimpleVideoComposer:
    """Simplified video composer that works without ImageMagick"""
    
    def __init__(self):
        self.resolution = (1920, 1080)
        self.fps = 30
    
    async def compose_video(self, lesson_plan, animations: List, narration) -> Dict[str, Any]:
        """Create a simple video with animations and audio"""
        
        if not HAS_MOVIEPY:
            return self._simulate_video_creation(lesson_plan, animations, narration)
        
        try:
            # Create output directory
            output_dir = Path("output_videos")
            output_dir.mkdir(exist_ok=True)
            
            # Load audio
            audio_clip = None
            if narration and narration.audio_path and os.path.exists(narration.audio_path):
                try:
                    audio_clip = AudioFileClip(narration.audio_path)
                    duration = audio_clip.duration
                except Exception as e:
                    print(f"Audio load error: {e}")
                    duration = 30.0
            else:
                duration = 30.0
            
            # Create video clips
            clips = []
            
            # Title card (blue background instead of text)
            title_bg = ColorClip(size=self.resolution, color=(0, 50, 100), duration=3)
            clips.append(title_bg)
            
            # Animation clips or placeholders
            for i, animation in enumerate(animations[:5]):  # Limit to 5 animations
                if animation.video_path and os.path.exists(animation.video_path):
                    try:
                        clip = VideoFileClip(animation.video_path)
                        # Resize to fit
                        clip = clip.resize(self.resolution)
                        clips.append(clip)
                    except Exception as e:
                        print(f"Animation load error: {e}")
                        # Use colored placeholder
                        placeholder = ColorClip(
                            size=self.resolution, 
                            color=(50 + i*30, 50, 50), 
                            duration=5
                        )
                        clips.append(placeholder)
                else:
                    # Create colored placeholder for missing animation
                    placeholder = ColorClip(
                        size=self.resolution, 
                        color=(100, 50 + i*20, 50), 
                        duration=5
                    )
                    clips.append(placeholder)
            
            # Conclusion card (green background)
            conclusion_bg = ColorClip(size=self.resolution, color=(0, 100, 50), duration=3)
            clips.append(conclusion_bg)
            
            # Concatenate all clips
            if clips:
                final_video = concatenate_videoclips(clips, method="compose")
                
                # Set audio if available
                if audio_clip:
                    # Match video duration to audio
                    final_video = final_video.set_duration(audio_clip.duration)
                    final_video = final_video.set_audio(audio_clip)
                
                # Export video
                output_path = output_dir / f"edu_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                
                print(f"🎬 Exporting video to: {output_path}")
                final_video.write_videofile(
                    str(output_path),
                    fps=self.fps,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True
                )
                
                # Clean up
                final_video.close()
                if audio_clip:
                    audio_clip.close()
                
                return {
                    "video_path": str(output_path),
                    "duration": final_video.duration,
                    "resolution": self.resolution,
                    "fps": self.fps,
                    "success": True
                }
            else:
                raise Exception("No video clips created")
                
        except Exception as e:
            print(f"Video composition error: {e}")
            return self._simulate_video_creation(lesson_plan, animations, narration)
    
    def _simulate_video_creation(self, lesson_plan, animations, narration):
        """Fallback simulation"""
        output_path = Path("output_videos") / f"demo_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(f"Demo Video - {lesson_plan.title}\n")
            f.write(f"Duration: {narration.duration if narration else 30} seconds\n")
            f.write(f"Animations: {len(animations)}\n")
        
        return {
            "video_path": str(output_path),
            "duration": narration.duration if narration else 30,
            "resolution": self.resolution,
            "fps": self.fps,
            "success": False
        }