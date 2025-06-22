#!/usr/bin/env python3
"""
Basic functionality test without API dependencies
"""

import asyncio
import tempfile
from pathlib import Path

def test_models():
    """Test basic Pydantic models"""
    print("🧪 Testing Pydantic models...")
    
    try:
        from unified_edu_agent import EducationalContent, FinalVideo
        
        # Test EducationalContent
        content = EducationalContent(
            text_content="Sample educational content about calculus",
            concepts=["derivatives", "limits"],
            difficulty_level="high school",
            subject_area="Mathematics",
            visual_elements=["graph", "tangent line"]
        )
        print(f"✅ EducationalContent: {content.subject_area}")
        
        # Test FinalVideo
        video = FinalVideo(
            video_path="/path/to/video.mp4",
            duration=300.0,
            lesson_plan=None,
            animations=[],
            narration=None
        )
        print(f"✅ FinalVideo: {video.duration}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_lesson_plan_models():
    """Test lesson planning models"""
    print("🧪 Testing lesson plan models...")
    
    try:
        from art_lesson_planner_agent.lesson_planner_agent import LessonPlan, LessonSection
        
        # Test section
        section = LessonSection(
            title="Introduction to Derivatives",
            content="A derivative represents the rate of change...",
            visualization_concept="tangent line to curve",
            duration_estimate=5.0
        )
        print(f"✅ LessonSection: {section.title}")
        
        # Test lesson plan
        lesson = LessonPlan(
            title="Calculus Fundamentals",
            subject="Mathematics",
            target_audience="High School",
            total_duration=15.0,
            prerequisites=["Algebra"],
            learning_objectives=["Understand derivatives"],
            sections=[section],
            assessment_questions=["What is a derivative?"],
            resources=["Textbook chapter 3"]
        )
        print(f"✅ LessonPlan: {lesson.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lesson plan test failed: {e}")
        return False

def test_manim_models():
    """Test Manim models"""
    print("🧪 Testing Manim models...")
    
    try:
        from matt_manim_agent.manim_agent import ManimOutput
        
        output = ManimOutput(
            success=True,
            concept="derivative visualization",
            visual_elements=["graph", "tangent line"],
            sync_points=[],
            metadata={"test": True}
        )
        print(f"✅ ManimOutput: {output.concept}")
        
        return True
        
    except Exception as e:
        print(f"❌ Manim model test failed: {e}")
        return False

def test_file_operations():
    """Test basic file operations"""
    print("🧪 Testing file operations...")
    
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Sample educational content for testing")
            temp_path = f.name
        
        # Test reading
        content = Path(temp_path).read_text()
        print(f"✅ File operations: {len(content)} characters read")
        
        # Cleanup
        Path(temp_path).unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

async def test_async_operations():
    """Test async functionality"""
    print("🧪 Testing async operations...")
    
    try:
        # Simple async operation
        await asyncio.sleep(0.1)
        print("✅ Async operations working")
        return True
        
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        return False

def test_imports():
    """Test critical imports"""
    print("🧪 Testing imports...")
    
    imports_to_test = [
        ("crewai", "Agent"),
        ("pydantic", "BaseModel"),
        ("cv2", None),
        ("PIL", "Image"),
        ("numpy", None),
        ("gradio", None)
    ]
    
    successful = 0
    total = len(imports_to_test)
    
    for module_name, attr_name in imports_to_test:
        try:
            module = __import__(module_name)
            if attr_name:
                getattr(module, attr_name)
            print(f"✅ {module_name}")
            successful += 1
        except ImportError:
            print(f"❌ {module_name}: not installed")
        except AttributeError:
            print(f"⚠️  {module_name}: attribute {attr_name} not found")
        except Exception as e:
            print(f"❌ {module_name}: {e}")
    
    return successful, total

async def main():
    """Run all basic tests"""
    print("🚀 EduAgent AI - Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Models", test_models),
        ("Lesson Plans", test_lesson_plan_models),
        ("Manim Models", test_manim_models),
        ("File Operations", test_file_operations),
        ("Async Operations", test_async_operations)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if test_name == "Imports":
                successful, total = result
                results.append(successful >= total * 0.8)  # 80% success rate
                print(f"   Result: {successful}/{total} successful")
            else:
                results.append(result)
                print(f"   Result: {'✅ Pass' if result else '❌ Fail'}")
                
        except Exception as e:
            print(f"   Result: ❌ Error - {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(results)
    total_tests = len(results)
    
    print(f"Tests passed: {passed}/{total_tests}")
    
    if passed >= total_tests * 0.8:
        print("\n🎉 Basic functionality is working!")
        print("The system is ready for development and testing.")
        print("\nNext steps:")
        print("1. Set up API keys in .env file")
        print("2. Test with: python demo.py") 
        print("3. Launch web interface: python web_interface.py")
    else:
        print("\n⚠️  Some tests failed. Please address the issues above.")
    
    return passed >= total_tests * 0.8

if __name__ == "__main__":
    asyncio.run(main())