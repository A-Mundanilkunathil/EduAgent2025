#!/usr/bin/env python3
"""
Debug script to trace video generation issues
"""

import asyncio
import os
from pathlib import Path
from unified_edu_agent import UnifiedEducationalVideoGenerator

async def debug_video_generation():
    """Debug each step of video generation"""
    
    print("🐛 Debugging Video Generation Pipeline")
    print("=" * 60)
    
    try:
        generator = UnifiedEducationalVideoGenerator()
        
        # Test file
        test_file = "lesson_pdfs/sample_calculus.pdf"
        
        print(f"📁 Processing: {test_file}")
        print()
        
        # Step 1: Test content extraction
        print("🔍 Step 1: Content Extraction")
        print("-" * 30)
        if test_file.endswith('.pdf'):
            text = await generator.content_extractor.extract_from_pdf(test_file)
        else:
            text = await generator.content_extractor.extract_from_image(test_file)
        
        print(f"✅ Extracted {len(text)} characters")
        content = await generator.content_extractor.analyze_content(text)
        print(f"✅ Subject: {content.subject_area}")
        print(f"✅ Concepts: {content.concepts[:3]}...")
        print()
        
        # Step 2: Test lesson planning
        print("📚 Step 2: Lesson Planning")
        print("-" * 30)
        try:
            from crewai import Task
            lesson_task = Task(
                description=f"Create a lesson plan for: {content.text_content[:200]}...",
                expected_output="A structured lesson plan with sections and visualization concepts",
                agent=generator.lesson_planner
            )
            # This might fail due to CrewAI issues, but let's see
            print("⚠️  CrewAI Task creation may have issues - checking manually...")
            print()
        except Exception as e:
            print(f"❌ Lesson planning issue: {e}")
            print()
        
        # Step 3: Test Manim agent directly
        print("🎨 Step 3: Manim Animation Generation")
        print("-" * 30)
        try:
            # Test if Manim agent can create a simple animation
            test_concept = "derivative of x squared"
            manim_agent = generator.manim_agent
            
            print(f"🧪 Testing Manim with concept: {test_concept}")
            
            # Check if Manim agent has the right methods
            print(f"✅ Manim agent type: {type(manim_agent).__name__}")
            print(f"✅ Has generate_animation: {hasattr(manim_agent, 'generate_animation')}")
            
            # Look for animation files in common locations
            animation_dirs = [
                Path("matt_manim_agent/animations"),
                Path("animations"), 
                Path("media"),
                Path("output_videos")
            ]
            
            for anim_dir in animation_dirs:
                if anim_dir.exists():
                    mp4_files = list(anim_dir.glob("**/*.mp4"))
                    if mp4_files:
                        print(f"📹 Found {len(mp4_files)} MP4 files in {anim_dir}:")
                        for mp4 in mp4_files[:3]:  # Show first 3
                            print(f"   - {mp4}")
            print()
            
        except Exception as e:
            print(f"❌ Manim test error: {e}")
            print()
        
        # Step 4: Test LMNT audio generation
        print("🎙️ Step 4: LMNT Audio Generation")
        print("-" * 30)
        try:
            audio_agent = generator.audio_narrator
            print(f"✅ LMNT agent type: {type(audio_agent).__name__}")
            print(f"✅ Has generate_narration: {hasattr(audio_agent, 'generate_narration')}")
            
            # Check for audio files
            audio_files = list(Path(".").glob("**/*.mp3")) + list(Path(".").glob("**/*.wav"))
            if audio_files:
                print(f"🎵 Found {len(audio_files)} audio files:")
                for audio in audio_files[:3]:
                    print(f"   - {audio}")
            else:
                print("⚠️  No audio files found")
            print()
            
        except Exception as e:
            print(f"❌ LMNT test error: {e}")
            print()
        
        # Step 5: Test video composer
        print("🎬 Step 5: Video Composition")
        print("-" * 30)
        try:
            video_composer = generator.video_composer
            print(f"✅ Video composer type: {type(video_composer).__name__}")
            print(f"✅ Has compose_video: {hasattr(video_composer, 'compose_video')}")
            
            # Check MoviePy availability
            try:
                from moviepy.editor import VideoFileClip, AudioFileClip, ColorClip
                print("✅ MoviePy is available")
            except ImportError as e:
                print(f"❌ MoviePy import error: {e}")
            
            # Check for final video files
            video_files = list(Path("output_videos").glob("**/*.mp4")) if Path("output_videos").exists() else []
            if video_files:
                print(f"🎬 Found {len(video_files)} final video files:")
                for video in video_files[:3]:
                    print(f"   - {video} ({video.stat().st_size} bytes)")
            else:
                print("⚠️  No final video files found in output_videos/")
            print()
            
        except Exception as e:
            print(f"❌ Video composer test error: {e}")
            print()
        
        print("🎯 Debug Summary:")
        print("- Check if Manim is actually generating MP4 files")
        print("- Check if LMNT is creating audio files") 
        print("- Check if video composer is finding and combining them")
        print("- Verify MoviePy can handle the files")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_video_generation())