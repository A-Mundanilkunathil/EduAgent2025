#!/usr/bin/env python3
"""
Test Both Demo and Real Video Modes
Shows exactly what happens in each mode
"""

import os
import tempfile
import asyncio
from pathlib import Path
from web_interface import EduAgentInterface

def test_demo_mode():
    """Test demo mode behavior"""
    print("📱 DEMO MODE TEST")
    print("-" * 30)
    
    # Temporarily unset API keys to force demo mode
    original_anthropic = os.environ.get("ANTHROPIC_API_KEY")
    original_lmnt = os.environ.get("LMNT_API_KEY")
    
    # Remove API keys
    if "ANTHROPIC_API_KEY" in os.environ:
        del os.environ["ANTHROPIC_API_KEY"]
    if "LMNT_API_KEY" in os.environ:
        del os.environ["LMNT_API_KEY"]
    
    try:
        app = EduAgentInterface()
        
        # Mock file upload
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        mock_file = MockFile("sample_calculus.pdf")
        
        # Test demo generation
        result = app.generate_video(
            mock_file, "Math Teacher", "Mathematics", "High School",
            1.0, True, True, False
        )
        
        print(f"✅ Demo mode completed")
        print(f"📄 Output type: {type(result[0])}")
        print(f"💬 Status: {result[1]}")
        print(f"📊 Metadata mode: {result[2].get('mode', 'Unknown')}")
        
        # Check if file was created
        if result[3] and hasattr(result[3], 'value'):
            print(f"📁 Demo file created: {result[3].value}")
        
    except Exception as e:
        print(f"❌ Demo test failed: {e}")
    
    finally:
        # Restore API keys
        if original_anthropic:
            os.environ["ANTHROPIC_API_KEY"] = original_anthropic
        if original_lmnt:
            os.environ["LMNT_API_KEY"] = original_lmnt

async def test_real_mode():
    """Test real video mode behavior"""
    print("\n🎬 REAL VIDEO MODE TEST")
    print("-" * 30)
    
    # Ensure API keys are set
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_lmnt = bool(os.getenv("LMNT_API_KEY"))
    
    if not (has_anthropic and has_lmnt):
        print("❌ API keys not available for real mode test")
        return
    
    app = EduAgentInterface()
    
    # Check if we have a PDF to test with
    pdf_files = list(Path("lesson_pdfs").glob("*.pdf")) if Path("lesson_pdfs").exists() else []
    if not pdf_files:
        print("❌ No PDF files available for real mode test")
        return
    
    # Create a mock file object like Gradio would
    class MockFile:
        def __init__(self, name):
            self.name = str(pdf_files[0])  # Use real PDF path
    
    mock_file = MockFile(str(pdf_files[0]))
    
    try:
        print(f"📄 Testing with: {mock_file.name}")
        print(f"🚀 Attempting real video generation...")
        
        # This will attempt real video generation
        result = await app._async_generate_video(
            mock_file, "Math Teacher", "Mathematics", "High School",
            0.5, True, True, False  # Short 30-second video
        )
        
        if result["success"]:
            print(f"✅ Real video generation succeeded!")
            print(f"📹 Video path: {result['video_path']}")
            
            # Check if it's actually an MP4
            if result['video_path'].endswith('.mp4'):
                print(f"🎬 Real MP4 video created!")
                if Path(result['video_path']).exists():
                    size = Path(result['video_path']).stat().st_size
                    print(f"📁 File size: {size / 1024 / 1024:.1f} MB")
                else:
                    print(f"⚠️ Video file not found at path")
            else:
                print(f"📄 Non-video output (likely demo fallback)")
        else:
            print(f"❌ Real video generation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Real mode test failed: {e}")

def show_summary():
    """Show clear summary of findings"""
    print("\n" + "=" * 50)
    print("📋 SUMMARY: Web Interface Video Generation")
    print("=" * 50)
    
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_lmnt = bool(os.getenv("LMNT_API_KEY"))
    demo_mode = not (has_anthropic and has_lmnt)
    
    print(f"🔧 Current Configuration:")
    print(f"   API Keys: {'✅ Available' if not demo_mode else '❌ Missing'}")
    print(f"   Mode: {'🎬 Real Video' if not demo_mode else '📱 Demo'}")
    
    print(f"\n🎯 What Happens When You Use Web Interface:")
    
    if demo_mode:
        print(f"   📱 DEMO MODE (Current)")
        print(f"   • Fast simulation - instant results")
        print(f"   • Text files with video metadata")
        print(f"   • Perfect for presentations!")
    else:
        print(f"   🎬 REAL VIDEO MODE (Current)")
        print(f"   • Attempts to create actual MP4 videos")
        print(f"   • May fail due to audio processing issues")
        print(f"   • Slower processing time")
    
    print(f"\n💡 Recommendations:")
    if demo_mode:
        print(f"   ✅ Current setup is PERFECT for hackathon demos")
        print(f"   ✅ Fast, reliable, shows full architecture")
        print(f"   • To get real videos: Add ANTHROPIC_API_KEY and LMNT_API_KEY")
    else:
        print(f"   ⚠️ Real video mode has audio processing issues")
        print(f"   💡 For reliable demos, consider temporarily removing API keys")
        print(f"   💡 Demo mode is more reliable for presentations")

def main():
    """Main test function"""
    print("🧪 EduAgent AI - Web Interface Mode Testing")
    print("=" * 50)
    
    # Test demo mode
    test_demo_mode()
    
    # Test real mode
    asyncio.run(test_real_mode())
    
    # Show summary
    show_summary()

if __name__ == "__main__":
    main()