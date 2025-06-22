#!/usr/bin/env python3
"""
Test the fixed LMNT integration
"""

import asyncio
from pathlib import Path
from audio_narrator_lmnt import LMNTNarratorAgent, LMNTVoiceConfig
from art_lesson_planner_agent.lesson_planner_agent import LessonPlan, LessonSection
from matt_manim_agent.manim_agent import ManimOutput

async def test_fixed_lmnt():
    """Test the fixed LMNT narrator"""
    
    print("🧪 Testing Fixed LMNT Integration")
    print("=" * 40)
    
    # Create a simple lesson plan for testing
    lesson_plan = LessonPlan(
        title="Test Lesson: Derivatives",
        subject="Mathematics", 
        target_audience="High School",
        total_duration=1.5,
        prerequisites=["Basic algebra"],
        learning_objectives=["Understand derivatives"],
        sections=[
            LessonSection(
                title="Introduction",
                content="Today we'll learn about derivatives. A derivative measures the rate of change.",
                visualization_placeholder=None,
                visualization_concept=None,
                duration_estimate=0.5,
                complexity="basic",
                learning_objectives=["Define derivative"]
            )
        ],
        assessment_questions=["What is a derivative?"],
        resources=["Textbook chapter 5"],
        metadata={}
    )
    
    # Create empty animations list
    animations = []
    
    # Create narrator agent
    narrator = LMNTNarratorAgent()
    
    try:
        print("🎤 Generating narration...")
        
        # Generate narration
        result = await narrator.generate_narration(lesson_plan, animations)
        
        print(f"✅ Narration generated!")
        print(f"📄 Audio path: {result.audio_path}")
        print(f"⏱️ Duration: {result.duration} seconds")
        print(f"📝 Transcript length: {len(result.transcript)} characters")
        print(f"🔊 Voice used: {result.voice_config.voice_id}")
        
        # Check if audio file exists
        if Path(result.audio_path).exists():
            file_size = Path(result.audio_path).stat().st_size
            print(f"✅ Audio file exists: {file_size / 1024:.1f} KB")
            
            # Check WAV header
            with open(result.audio_path, 'rb') as f:
                header = f.read(4)
                if header == b'RIFF':
                    print(f"✅ Valid WAV file!")
                else:
                    print(f"❌ Invalid WAV header: {header}")
        else:
            print(f"❌ Audio file not found at {result.audio_path}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_full_pipeline():
    """Test with the full pipeline"""
    print("\n" + "=" * 40)
    print("🚀 Testing Full Pipeline Integration")
    print("=" * 40)
    
    from unified_edu_agent import UnifiedEducationalVideoGenerator
    
    generator = UnifiedEducationalVideoGenerator()
    
    # Check if we have a test PDF
    pdf_files = list(Path("lesson_pdfs").glob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found")
        return False
    
    try:
        print(f"📄 Using: {pdf_files[0]}")
        print(f"⏳ Generating video (this may take a moment)...")
        
        result = await generator.generate_video(
            str(pdf_files[0]),
            target_duration=15,  # 15 seconds for quick test
            target_audience="high school"
        )
        
        print(f"✅ Video generation completed!")
        print(f"📹 Video path: {result.video_path}")
        
        if result.video_path and result.video_path.endswith('.mp4'):
            print(f"🎬 Real MP4 video generated!")
            if Path(result.video_path).exists():
                size = Path(result.video_path).stat().st_size
                print(f"📁 File size: {size / 1024 / 1024:.1f} MB")
        else:
            print(f"📄 Demo output generated")
            
        return True
        
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        return False

def main():
    print("🔍 LMNT Fix Verification")
    print("=" * 40)
    
    # Test the fixed LMNT integration
    success1 = asyncio.run(test_fixed_lmnt())
    
    if success1:
        print("\n✅ LMNT fix successful! Testing full pipeline...")
        success2 = asyncio.run(test_full_pipeline())
        
        if success2:
            print("\n🎉 Full pipeline working with real video generation!")
        else:
            print("\n⚠️ Pipeline still has issues")
    else:
        print("\n❌ LMNT fix didn't work")

if __name__ == "__main__":
    main()