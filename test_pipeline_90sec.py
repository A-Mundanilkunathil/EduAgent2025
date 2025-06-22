#!/usr/bin/env python3
"""
Test Script for EduAgent AI Pipeline
Generates a 90-second educational video from PDF and text input
"""

import asyncio
import os
import time
from pathlib import Path
from unified_edu_agent import UnifiedEducationalVideoGenerator

async def test_90_second_video():
    """Test the pipeline with PDF input and generate 90-second video"""
    
    print("🎓 Testing EduAgent AI Pipeline - 90 Second Video Generation")
    print("=" * 60)
    
    # Initialize the generator
    print("🔧 Initializing video generator...")
    generator = UnifiedEducationalVideoGenerator()
    
    # Use the sample PDF from lesson_pdfs directory
    pdf_path = "lesson_pdfs/sample_calculus.pdf"
    
    # Check if PDF exists
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        print("Available files in lesson_pdfs:")
        for file in Path("lesson_pdfs").iterdir():
            print(f"   - {file.name}")
        return
    
    print(f"📄 Using PDF: {pdf_path}")
    
    # Additional text context for the lesson
    additional_text = """
    Focus on creating a clear, engaging 90-second explanation suitable for high school students.
    Cover the key concepts with visual animations that make calculus intuitive and accessible.
    Include practical applications to make the content relevant and memorable.
    """
    
    try:
        print("\n🚀 Starting video generation pipeline...")
        start_time = time.time()
        
        # Generate the video with 90-second target duration
        video_result = await generator.generate_video(
            pdf_path,
            target_duration=90,  # 90 seconds
            target_audience="high school",
            style="engaging",
            accessibility_features=["captions", "transcript"],
            additional_context=additional_text
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print("\n✅ Video generation completed!")
        print(f"📹 Video path: {video_result.video_path}")
        print(f"⏱️  Target duration: 90 seconds")
        print(f"⏱️  Actual duration: {video_result.duration:.1f} seconds")
        print(f"🔄 Processing time: {processing_time:.1f} seconds")
        print(f"📊 Subject: {video_result.lesson_plan.subject}")
        print(f"🎯 Difficulty: {video_result.lesson_plan.target_audience}")
        
        # Display lesson plan structure
        print(f"\n📋 Lesson Plan: {video_result.lesson_plan.title}")
        for i, section in enumerate(video_result.lesson_plan.sections, 1):
            print(f"   {i}. {section.title} ({section.duration_estimate:.1f} min)")
        
        # Display generated animations
        print(f"\n🎨 Generated Animations: {len(video_result.animations)}")
        for i, anim in enumerate(video_result.animations, 1):
            print(f"   {i}. {anim.script_path}")
        
        # Display quality metrics
        if "quality_report" in video_result.metadata:
            quality = video_result.metadata["quality_report"]
            print(f"\n✅ Quality Report:")
            print(f"   📈 Educational effectiveness: {quality.get('educational_effectiveness', 'N/A')}")
            print(f"   🔊 Audio quality: {'✅' if quality.get('audio_quality') else '❌'}")
            print(f"   👁️  Visual clarity: {'✅' if quality.get('visual_clarity') else '❌'}")
            print(f"   ♿ Accessibility: {'✅' if quality.get('accessibility', {}).get('captions') else '❌'}")
        
        # Show narration info
        print(f"\n🎙️ Narration:")
        print(f"   📝 Transcript length: {len(video_result.narration.transcript)} characters")
        print(f"   ⏱️  Audio duration: {video_result.narration.duration:.1f} seconds")
        print(f"   🔗 Sync points: {len(video_result.narration.sync_points)}")
        
        print(f"\n🎉 Success! Your 90-second educational video is ready!")
        print(f"📁 Check the output at: {video_result.video_path}")
        
        return video_result
        
    except Exception as e:
        print(f"❌ Error during video generation: {str(e)}")
        print(f"🔧 This might be due to missing dependencies or API keys")
        print(f"💡 Check README.md for setup instructions")
        raise


async def test_with_custom_text():
    """Test with custom text content instead of PDF"""
    
    print("\n" + "=" * 60)
    print("🎓 Testing with Custom Text Content")
    print("=" * 60)
    
    # Custom calculus content
    custom_content = """
    # Understanding Derivatives - A 90 Second Journey
    
    ## What is a Derivative?
    
    A derivative tells us how fast something is changing. Think of it as the slope of a curve at any point.
    
    ## The Mathematical Definition
    
    For a function f(x), the derivative f'(x) is:
    f'(x) = lim[h→0] (f(x+h) - f(x))/h
    
    ## Simple Example: The Power Rule
    
    If f(x) = x², then f'(x) = 2x
    
    This means:
    - At x = 1, the slope is 2
    - At x = 2, the slope is 4
    - At x = 3, the slope is 6
    
    ## Real-World Applications
    
    1. **Velocity**: How fast you're moving (derivative of position)
    2. **Acceleration**: How quickly your speed changes (derivative of velocity)
    3. **Economics**: Marginal cost and revenue
    4. **Physics**: Rate of change in any physical quantity
    
    ## Visual Understanding
    
    Imagine a hill. The derivative tells you how steep the hill is at each step.
    - Positive derivative = uphill
    - Negative derivative = downhill
    - Zero derivative = flat ground (local max/min)
    
    ## Key Takeaway
    
    Derivatives are everywhere! They help us understand change in our world.
    """
    
    # Save to temporary file
    temp_file = Path("temp_calculus_content.txt")
    temp_file.write_text(custom_content)
    
    try:
        generator = UnifiedEducationalVideoGenerator()
        
        print("🔧 Processing custom text content...")
        
        # For text files, we'll need to modify the generator slightly
        # This demonstrates how the system would handle direct text input
        
        # Extract and analyze content
        content = await generator.content_extractor.analyze_content(custom_content)
        
        print(f"📊 Content Analysis:")
        print(f"   🎯 Subject: {content.subject_area}")
        print(f"   📈 Difficulty: {content.difficulty_level}")
        print(f"   🧠 Concepts: {', '.join(content.concepts[:3])}...")
        print(f"   🎨 Visual elements: {', '.join(content.visual_elements[:3])}...")
        
        # Create lesson plan
        from crewai import Task
        lesson_task = Task(
            description=f"Create a lesson plan for: {content.text_content}",
            expected_output="A structured lesson plan with sections and visualization concepts",
            agent=generator.lesson_planner
        )
        lesson_plan = await generator.lesson_planner.execute(lesson_task)
        
        print(f"\n📋 Generated Lesson Plan: {lesson_plan.title}")
        print(f"   📚 {len(lesson_plan.sections)} sections")
        print(f"   ⏱️  Total duration: {sum(s.duration_estimate for s in lesson_plan.sections):.1f} minutes")
        
        print(f"\n✅ Text-based content processing successful!")
        print(f"💡 This content is ready for animation and narration generation")
        
    except Exception as e:
        print(f"❌ Error processing custom text: {e}")
        
    finally:
        # Cleanup
        if temp_file.exists():
            temp_file.unlink()


def show_usage_instructions():
    """Show how to use the pipeline"""
    
    print("\n" + "=" * 60)
    print("📖 How to Use the EduAgent AI Pipeline")
    print("=" * 60)
    
    print("""
🚀 Quick Start Options:

1. **Web Interface** (Easiest):
   python web_interface.py
   # Then open http://localhost:7860

2. **Command Line** (This script):
   python test_pipeline_90sec.py

3. **Python Integration**:
   ```python
   from unified_edu_agent import UnifiedEducationalVideoGenerator
   
   generator = UnifiedEducationalVideoGenerator()
   video = await generator.generate_video("your_file.pdf")
   ```

📁 Supported Input Formats:
   • PDF files (.pdf)
   • Images (.png, .jpg, .jpeg)
   • Text files (.txt, .md)

⚙️ Configuration Options:
   • target_duration: Duration in seconds (default: auto)
   • target_audience: "elementary", "middle", "high school", "college"
   • style: "engaging", "formal", "3blue1brown"
   • accessibility_features: ["captions", "transcript", "audio_descriptions"]

🔧 Setup Requirements:
   1. Install dependencies: pip install -r requirements.txt
   2. Set up API keys in .env file:
      - ANTHROPIC_API_KEY (for content analysis)
      - LMNT_API_KEY (for narration)
      - GOOGLE_CLOUD_CREDENTIALS (for OCR)
   3. Install system dependencies (see README.md)

💡 Tips for Best Results:
   • Use clear, well-structured PDFs
   • Specify target audience for appropriate difficulty
   • Add custom context text for specific focus areas
   • Test with shorter content first (90 seconds = ~200-300 words)
""")


async def main():
    """Main test function"""
    
    print("🎓 EduAgent AI Pipeline Test Suite")
    print("Generating 90-second educational videos")
    print("=" * 60)
    
    # Show usage instructions
    show_usage_instructions()
    
    # Test with PDF
    try:
        await test_90_second_video()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ PDF test failed: {e}")
        print("🔄 Continuing with text-based test...")
    
    # Test with custom text
    try:
        await test_with_custom_text()
    except Exception as e:
        print(f"\n❌ Text test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎬 Test completed! Check the generated videos.")
    print("💡 For more features, try the web interface:")
    print("   python web_interface.py")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())