#!/usr/bin/env python3
"""
Test video generation with simple composer
"""

import asyncio
from pathlib import Path
from video_composer_simple import SimpleVideoComposer
from audio_narrator_lmnt import EnhancedAudioNarration, LMNTVoiceConfig

async def test_simple_video():
    """Test creating a real video with the simple composer"""
    
    print("🎬 Testing Simple Video Composer")
    print("=" * 40)
    
    # Create test audio narration
    narration = EnhancedAudioNarration(
        audio_path="narration_lmnt.wav",  # Using existing audio file
        duration=10.0,
        transcript="Test narration",
        segments=[],
        voice_config=LMNTVoiceConfig(),
        sync_points=[],
        metadata={}
    )
    
    # Check if audio exists
    if Path(narration.audio_path).exists():
        print(f"✅ Audio file found: {narration.audio_path}")
        size = Path(narration.audio_path).stat().st_size
        print(f"   Size: {size / 1024:.1f} KB")
    else:
        print(f"❌ Audio file not found: {narration.audio_path}")
        return False
    
    # Create dummy lesson plan
    class DummyLessonPlan:
        title = "Test Lesson"
        subject = "Mathematics"
        target_audience = "High School"
    
    lesson_plan = DummyLessonPlan()
    
    # Create dummy animations
    animations = []
    
    # Create composer
    composer = SimpleVideoComposer()
    
    try:
        print("\n🚀 Composing video...")
        result = await composer.compose_video(lesson_plan, animations, narration)
        
        print(f"\n📊 Result:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Video path: {result.get('video_path', 'None')}")
        print(f"   Duration: {result.get('duration', 0)} seconds")
        
        if result.get('success') and result.get('video_path'):
            video_path = Path(result['video_path'])
            if video_path.exists() and video_path.suffix == '.mp4':
                size = video_path.stat().st_size
                print(f"\n🎬 REAL VIDEO CREATED!")
                print(f"   Path: {video_path}")
                print(f"   Size: {size / 1024 / 1024:.1f} MB")
                return True
            else:
                print(f"\n📄 Demo file created (not a real video)")
                return False
        else:
            print(f"\n❌ Video creation failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 Simple Video Generation Test")
    print("=" * 40)
    
    success = asyncio.run(test_simple_video())
    
    if success:
        print("\n🎉 SUCCESS! Real MP4 video was created!")
        print("The system can now generate actual videos!")
    else:
        print("\n❌ Video generation failed")
        print("Check the error messages above")

if __name__ == "__main__":
    main()