#!/usr/bin/env python3
"""
System Testing Script for EduAgent AI
Tests all components to ensure they work properly
"""

import sys
import os
import traceback
from pathlib import Path

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    tests = [
        ("Core Python libraries", [
            "asyncio", "json", "tempfile", "pathlib", "datetime", "re", "io"
        ]),
        ("Data processing", [
            "numpy", "pandas"
        ]),
        ("AI/ML libraries", [
            "anthropic", "crewai", "pydantic"
        ]),
        ("Image/Video processing", [
            "cv2", "PIL", "pytesseract"
        ]),
        ("Audio libraries", [
            "aiohttp"
        ]),
        ("Web interface", [
            "gradio"
        ])
    ]
    
    results = {}
    
    for category, modules in tests:
        print(f"\n  📦 {category}:")
        category_results = {}
        
        for module in modules:
            try:
                __import__(module)
                print(f"    ✅ {module}")
                category_results[module] = True
            except ImportError as e:
                print(f"    ❌ {module}: {e}")
                category_results[module] = False
            except Exception as e:
                print(f"    ⚠️  {module}: {e}")
                category_results[module] = False
        
        results[category] = category_results
    
    return results

def test_optional_imports():
    """Test optional/advanced imports"""
    print("\n🔧 Testing optional imports...")
    
    optional_modules = [
        ("PyPDF2", "PDF processing"),
        ("fitz", "Advanced PDF processing (PyMuPDF)"),
        ("pdf2image", "PDF to image conversion"),
        ("moviepy.editor", "Video composition"),
        ("google.cloud.vision", "Google Cloud Vision"),
        ("groq", "Groq AI"),
    ]
    
    for module, description in optional_modules:
        try:
            __import__(module)
            print(f"    ✅ {module} ({description})")
        except ImportError:
            print(f"    ⚠️  {module} ({description}) - Optional, install if needed")
        except Exception as e:
            print(f"    ❌ {module} ({description}): {e}")

def test_environment_variables():
    """Test environment variables"""
    print("\n🔑 Testing environment variables...")
    
    required_vars = [
        "ANTHROPIC_API_KEY",
        "LMNT_API_KEY"
    ]
    
    optional_vars = [
        "GROQ_API_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "FETCH_AI_API_KEY",
        "OPENAI_API_KEY"
    ]
    
    print("  Required:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"    ✅ {var}: {'*' * min(len(value), 20)}")
        else:
            print(f"    ❌ {var}: Not set (REQUIRED)")
    
    print("  Optional:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"    ✅ {var}: {'*' * min(len(value), 20)}")
        else:
            print(f"    ⚠️  {var}: Not set (optional)")

def test_file_structure():
    """Test file structure"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "unified_edu_agent.py",
        "audio_narrator_lmnt.py", 
        "video_composer.py",
        "sponsor_integrations.py",
        "web_interface.py",
        "requirements.txt",
        "README.md"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"    ✅ {file_path}")
        else:
            print(f"    ❌ {file_path}: Missing")

def test_basic_functionality():
    """Test basic functionality without external APIs"""
    print("\n⚙️  Testing basic functionality...")
    
    try:
        # Test pydantic models
        print("    Testing Pydantic models...")
        from unified_edu_agent import EducationalContent, FinalVideo
        
        content = EducationalContent(
            text_content="Test content",
            concepts=["test"],
            difficulty_level="test",
            subject_area="test"
        )
        print("    ✅ EducationalContent model works")
        
        # Test lesson planner models
        from art_lesson_planner_agent.lesson_planner_agent import LessonPlan, LessonSection
        
        section = LessonSection(
            title="Test Section",
            content="Test content"
        )
        
        lesson = LessonPlan(
            title="Test Lesson",
            subject="Test",
            target_audience="Test",
            total_duration=10.0,
            prerequisites=[],
            learning_objectives=[],
            sections=[section],
            assessment_questions=[],
            resources=[]
        )
        print("    ✅ LessonPlan models work")
        
        # Test Manim models  
        from matt_manim_agent.manim_agent import ManimOutput
        
        anim = ManimOutput(
            success=True,
            concept="test",
            visual_elements=[]
        )
        print("    ✅ ManimOutput model works")
        
    except Exception as e:
        print(f"    ❌ Basic functionality test failed: {e}")
        traceback.print_exc()

def test_simplified_agents():
    """Test simplified agent creation"""
    print("\n🤖 Testing agent creation...")
    
    try:
        # Test content extractor
        from unified_edu_agent import ContentExtractorAgent
        extractor = ContentExtractorAgent()
        print("    ✅ ContentExtractorAgent created")
        
        # Test lesson planner
        from art_lesson_planner_agent.lesson_planner_agent import LessonPlannerAgent
        planner = LessonPlannerAgent()
        print("    ✅ LessonPlannerAgent created")
        
        # Test manim agent
        from matt_manim_agent.manim_agent import ManimAgent
        manim_agent = ManimAgent()
        print("    ✅ ManimAgent created")
        
        # Test LMNT narrator
        from audio_narrator_lmnt import LMNTNarratorAgent
        narrator = LMNTNarratorAgent()
        print("    ✅ LMNTNarratorAgent created")
        
        # Test video composer
        from video_composer import VideoComposerAgent
        composer = VideoComposerAgent()
        print("    ✅ VideoComposerAgent created")
        
    except Exception as e:
        print(f"    ❌ Agent creation failed: {e}")
        traceback.print_exc()

def create_simple_demo():
    """Create a simple demo that works without external dependencies"""
    print("\n🎬 Creating simple demo...")
    
    demo_content = """
# Simple Math Demo

## Basic Algebra

Solving for x in the equation: 2x + 5 = 15

Step 1: Subtract 5 from both sides
2x = 10

Step 2: Divide by 2
x = 5

Therefore, x = 5
"""
    
    # Create demo file
    demo_file = Path("demo_simple.txt")
    demo_file.write_text(demo_content)
    
    print(f"    ✅ Created demo file: {demo_file}")
    print(f"    📄 Content length: {len(demo_content)} characters")
    
    return str(demo_file)

def main():
    """Run all tests"""
    print("🧪 EduAgent AI System Testing")
    print("=" * 50)
    
    # Run tests
    import_results = test_imports()
    test_optional_imports()
    test_environment_variables()
    test_file_structure()
    test_basic_functionality()
    test_simplified_agents()
    demo_file = create_simple_demo()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    # Count successful imports
    total_imports = 0
    successful_imports = 0
    
    for category, results in import_results.items():
        for module, success in results.items():
            total_imports += 1
            if success:
                successful_imports += 1
    
    print(f"✅ Imports: {successful_imports}/{total_imports} successful")
    
    # Environment variables
    required_env_vars = ["ANTHROPIC_API_KEY", "LMNT_API_KEY"]
    env_vars_set = sum(1 for var in required_env_vars if os.getenv(var))
    print(f"🔑 Environment: {env_vars_set}/{len(required_env_vars)} required variables set")
    
    # Overall status
    if successful_imports >= total_imports * 0.8 and env_vars_set >= 1:
        print("\n🎉 System is ready for basic testing!")
        print(f"📁 Demo file created: {demo_file}")
        print("\nNext steps:")
        print("1. Set missing environment variables")
        print("2. Install missing optional dependencies")
        print("3. Run: python demo.py")
    else:
        print("\n⚠️  System needs attention before full functionality")
        print("Please address the issues above first.")

if __name__ == "__main__":
    main()