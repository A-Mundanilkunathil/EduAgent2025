#!/usr/bin/env python3
"""
Test the fixed video generation with validation
"""

import asyncio
import os
from pathlib import Path
import time

async def test_video_generation():
    """Test video generation with the new validation"""
    
    print("🎬 Testing Fixed Video Generation")
    print("=" * 50)
    
    from video_composer import SimpleVideoComposer
    
    composer = SimpleVideoComposer()
    
    # Create mock objects for testing
    class MockLessonPlan:
        title = "Test Derivatives Lesson"
    
    class MockAnimation:
        def __init__(self, path):
            self.video_path = path
            self.success = True
    
    class MockNarration:
        def __init__(self, audio_file):
            self.audio_path = audio_file
            self.duration = 30.0
    
    # Use existing files
    lesson = MockLessonPlan()
    
    # Find an existing animation file
    animation_files = list(Path("animations").glob("**/*.mp4"))
    if animation_files:
        animation = MockAnimation(str(animation_files[0]))
        print(f"📹 Using animation: {animation.video_path}")
    else:
        animation = MockAnimation(None)
        print("📹 No animation files found - using placeholder")
    
    # Find an existing audio file
    audio_files = [f for f in ["test_lmnt_output.wav", "narration_lmnt.wav"] if Path(f).exists()]
    if audio_files:
        narration = MockNarration(audio_files[0])
        print(f"🎙️ Using audio: {narration.audio_path}")
    else:
        narration = MockNarration(None)
        print("🎙️ No audio files found - video only")
    
    print()
    print("🔄 Starting video composition...")
    start_time = time.time()
    
    try:
        result = await composer.compose_video(lesson, [animation], narration)
        
        elapsed = time.time() - start_time
        print(f"⏱️ Generation took: {elapsed:.1f} seconds")
        print()
        
        if result["success"]:
            video_path = result["video_path"]
            print(f"✅ Video created: {video_path}")
            
            # Check if file exists and is valid
            if Path(video_path).exists():
                file_size = Path(video_path).stat().st_size / (1024*1024)
                print(f"📊 File size: {file_size:.1f} MB")
                
                # Test if video can be opened
                import subprocess
                try:
                    probe_result = subprocess.run([
                        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
                        '-show_entries', 'stream=duration,codec_name',
                        video_path
                    ], capture_output=True, text=True, timeout=5)
                    
                    if probe_result.returncode == 0:
                        print("✅ Video file is valid and can be opened!")
                        print("📹 Video details:")
                        for line in probe_result.stdout.strip().split('\n'):
                            if line.strip():
                                print(f"   {line}")
                    else:
                        print("❌ Video file is corrupted")
                        print(f"   Error: {probe_result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    print("⏱️ Video validation timeout")
                except FileNotFoundError:
                    print("⚠️ ffprobe not available - cannot validate")
                    
            else:
                print("❌ Video file was not created")
        else:
            print(f"❌ Video generation failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_video_generation())