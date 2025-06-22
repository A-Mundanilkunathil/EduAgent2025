#!/usr/bin/env python3
"""
Video Mode Detection Test
Shows exactly what mode the system is running in
"""

import os
import asyncio
from pathlib import Path
from unified_edu_agent import UnifiedEducationalVideoGenerator

def check_system_status():
    """Check current system configuration"""
    print("🔍 EduAgent AI - Video Generation Mode Check")
    print("=" * 50)
    
    # Check API keys
    print("\n🔑 API Keys Status:")
    api_keys = {
        "ANTHROPIC_API_KEY": "Content analysis & lesson planning",
        "LMNT_API_KEY": "Audio narration generation", 
        "OPENAI_API_KEY": "Advanced OCR & image processing",
        "GROQ_API_KEY": "Fast inference & quiz generation"
    }
    
    keys_available = 0
    for key, description in api_keys.items():
        if os.getenv(key):
            print(f"   ✅ {key}: Available")
            keys_available += 1
        else:
            print(f"   ❌ {key}: Missing")
    
    # Check MoviePy
    print(f"\n🎬 Video Processing:")
    try:
        from video_composer import HAS_MOVIEPY
        if HAS_MOVIEPY:
            print(f"   ✅ MoviePy: Available - Can generate real videos")
        else:
            print(f"   ❌ MoviePy: Missing - Video composition simulated")
    except Exception:
        print(f"   ❌ MoviePy: Error loading video composer")
    
    # Determine mode
    print(f"\n🎯 Current Mode:")
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_lmnt = bool(os.getenv("LMNT_API_KEY"))
    demo_mode = not (has_anthropic and has_lmnt)
    
    if demo_mode:
        print(f"   📱 DEMO MODE")
        print(f"   • Fast simulation (perfect for demos)")
        print(f"   • Shows system architecture & capabilities")
        print(f"   • Generates text files with video metadata")
        print(f"   • No actual MP4 files created")
    else:
        print(f"   🎬 REAL VIDEO MODE")
        print(f"   • Generates actual MP4 video files")
        print(f"   • Uses AI services for content & audio")
        print(f"   • Takes longer but produces real videos")
        print(f"   • Requires API keys for full functionality")
    
    print(f"\n📊 Summary:")
    print(f"   • API Keys: {keys_available}/4 available")
    print(f"   • Mode: {'Demo' if demo_mode else 'Real Video'}")
    print(f"   • Output: {'Text files' if demo_mode else 'MP4 videos'}")
    
    return demo_mode

async def test_video_generation():
    """Test actual video generation process"""
    print("\n" + "=" * 50)
    print("🧪 Testing Video Generation Process")
    print("=" * 50)
    
    generator = UnifiedEducationalVideoGenerator()
    
    # Check available input files
    pdf_files = list(Path("lesson_pdfs").glob("*.pdf")) if Path("lesson_pdfs").exists() else []
    
    if not pdf_files:
        print("❌ No PDF files found in lesson_pdfs/")
        return False
    
    pdf_file = pdf_files[0]
    print(f"📄 Testing with: {pdf_file}")
    
    try:
        print(f"🚀 Starting generation process...")
        
        # Generate with short duration for quick test
        result = await generator.generate_video(
            str(pdf_file),
            target_duration=15,  # 15 seconds for quick test
            target_audience="high school"
        )
        
        print(f"\n✅ Generation completed!")
        print(f"📹 Output: {result.video_path}")
        
        # Check if it's a real video file or demo file
        if result.video_path.endswith('.mp4'):
            print(f"🎬 REAL VIDEO GENERATED!")
            if Path(result.video_path).exists():
                file_size = Path(result.video_path).stat().st_size
                print(f"   📁 File size: {file_size / 1024 / 1024:.1f} MB")
            else:
                print(f"   ⚠️  Video file not found at path")
        else:
            print(f"📱 DEMO FILE GENERATED")
            print(f"   📄 Demo file with video metadata")
            if Path(result.video_path).exists():
                with open(result.video_path) as f:
                    content = f.read()
                    print(f"   📝 Content length: {len(content)} characters")
        
        print(f"⏱️  Duration: {result.duration} seconds")
        return True
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False

def show_output_directories():
    """Show where outputs are stored"""
    print("\n" + "=" * 50)
    print("📁 Output Directory Analysis")
    print("=" * 50)
    
    directories = [
        ("output_videos/", "Main video output directory"),
        ("demo_outputs/", "Demo simulation files"),
        ("animations/videos/", "Manim animation videos"),
    ]
    
    for dir_path, description in directories:
        path = Path(dir_path)
        if path.exists():
            files = list(path.glob("*"))
            print(f"\n📂 {dir_path} - {description}")
            print(f"   📊 Files: {len(files)}")
            
            # Show recent files
            recent_files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]
            for file in recent_files:
                if file.is_file():
                    size = file.stat().st_size
                    if file.suffix == '.mp4':
                        print(f"   🎬 {file.name} ({size / 1024 / 1024:.1f} MB)")
                    else:
                        print(f"   📄 {file.name} ({size} bytes)")
        else:
            print(f"\n📂 {dir_path} - {description}")
            print(f"   ❌ Directory not found")

def main():
    """Main function"""
    demo_mode = check_system_status()
    
    print(f"\n🎯 What This Means for You:")
    if demo_mode:
        print(f"   📱 Web interface runs in DEMO MODE")
        print(f"   • Upload files → Get instant simulation")
        print(f"   • Download demo files showing video structure")
        print(f"   • Perfect for hackathon presentations!")
        print(f"   • To get real videos: Add ANTHROPIC_API_KEY and LMNT_API_KEY")
    else:
        print(f"   🎬 Web interface will generate REAL VIDEOS")
        print(f"   • Upload files → Get actual MP4 videos")
        print(f"   • Takes longer but produces real content")
        print(f"   • Full AI-powered educational video generation")
    
    # Test the generation process
    success = asyncio.run(test_video_generation())
    
    # Show output directories
    show_output_directories()
    
    print(f"\n🎉 Test completed!")
    if demo_mode:
        print(f"💡 To test real video generation, set up API keys and run again")

if __name__ == "__main__":
    main()