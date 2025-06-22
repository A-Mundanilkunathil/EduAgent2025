#!/usr/bin/env python3
"""
Test individual agents to see which one is causing issues
"""

import asyncio
import os
from pathlib import Path
from unified_edu_agent import UnifiedEducationalVideoGenerator

async def test_individual_agents():
    """Test each agent individually"""
    
    print("🧪 Testing Individual Agents")
    print("=" * 50)
    
    generator = UnifiedEducationalVideoGenerator()
    
    # Test content
    test_content = """
    Introduction to Derivatives
    A derivative represents the instantaneous rate of change of a function.
    For f(x) = x², the derivative is f'(x) = 2x.
    """
    
    # 1. Test Content Extractor
    print("🔍 Testing Content Extractor...")
    try:
        content = await generator.content_extractor.analyze_content(test_content)
        print(f"✅ Content analysis successful: {content.subject_area}")
    except Exception as e:
        print(f"❌ Content extractor failed: {e}")
    print()
    
    # 2. Test Lesson Planner (this might be the issue)
    print("📚 Testing Lesson Planner...")
    try:
        from crewai import Task
        lesson_task = Task(
            description=f"Create a lesson plan for: {test_content}",
            expected_output="A structured lesson plan with sections and visualization concepts",
            agent=generator.lesson_planner
        )
        
        print("⚠️  Trying to execute lesson planning task...")
        # This is where it might be failing
        lesson_plan = await generator.lesson_planner.execute(lesson_task)
        print(f"✅ Lesson plan created: {lesson_plan.title if hasattr(lesson_plan, 'title') else 'Success'}")
    except Exception as e:
        print(f"❌ Lesson planner failed: {e}")
        print("   This is likely where the pipeline is breaking!")
    print()
    
    # 3. Test Manim Agent directly  
    print("🎨 Testing Manim Agent...")
    try:
        from crewai import Task
        anim_task = Task(
            description="Create animation for: derivative of x squared",
            expected_output="A Manim animation with video output",
            agent=generator.manim_agent
        )
        
        print("⚠️  Trying to execute Manim task...")
        anim = await generator.manim_agent.execute(anim_task)
        print(f"✅ Animation created: {anim}")
    except Exception as e:
        print(f"❌ Manim agent failed: {e}")
    print()
    
    # 4. Test LMNT Audio
    print("🎙️ Testing LMNT Audio...")
    try:
        # Create a mock lesson plan
        class MockLessonPlan:
            def __init__(self):
                self.title = "Test Lesson"
                self.sections = []
        
        class MockSection:
            def __init__(self):
                self.title = "Introduction"
                self.content = "This is a test lesson about derivatives"
                self.duration_estimate = 1.0
        
        mock_lesson = MockLessonPlan()
        mock_lesson.sections = [MockSection()]
        
        narration = await generator.audio_narrator.generate_narration(
            mock_lesson, 
            [],  # no animations yet
            voice_preset="math_teacher"
        )
        print(f"✅ Audio narration created: {narration.audio_path if hasattr(narration, 'audio_path') else 'Success'}")
    except Exception as e:
        print(f"❌ LMNT audio failed: {e}")
    print()
    
    # 5. Test Video Composer
    print("🎬 Testing Video Composer...")
    try:
        # Use mock objects
        class MockLessonPlan:
            title = "Test Video"
            
        class MockAnimation:
            def __init__(self, path):
                self.video_path = path
                self.success = True
                
        class MockNarration:
            def __init__(self):
                self.audio_path = "test_lmnt_output.wav"  # Use existing audio file
                self.duration = 30.0
        
        mock_lesson = MockLessonPlan()
        mock_animations = [MockAnimation("animations/videos/tmpxpxwodj5/720p30/create_animation_for:_derivati.mp4")]
        mock_narration = MockNarration()
        
        video_result = await generator.video_composer.compose_video(
            mock_lesson, 
            mock_animations, 
            mock_narration
        )
        print(f"✅ Video composition: {video_result.get('success', False)}")
        if video_result.get('video_path'):
            print(f"   Video saved to: {video_result['video_path']}")
    except Exception as e:
        print(f"❌ Video composer failed: {e}")
    print()
    
    print("🎯 Summary: Check which agent is failing and fix that specific component")

if __name__ == "__main__":
    asyncio.run(test_individual_agents())