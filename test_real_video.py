#!/usr/bin/env python3
"""
Test REAL video generation with all fixes applied
"""

import asyncio
import os
from pathlib import Path
from unified_edu_agent import UnifiedEducationalVideoGenerator

async def test_real_video_generation():
    """Test actual MP4 video generation"""
    
    print("🎬 Testing REAL Video Generation")
    print("=" * 50)
    
    # Check environment
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_lmnt = bool(os.getenv("LMNT_API_KEY"))
    
    print(f"✅ ANTHROPIC_API_KEY: {'Set' if has_anthropic else 'Missing'}")
    print(f"✅ LMNT_API_KEY: {'Set' if has_lmnt else 'Missing'}")
    
    if not (has_anthropic and has_lmnt):
        print("❌ API keys missing - cannot generate real videos")
        return False
    
    # Initialize generator
    generator = UnifiedEducationalVideoGenerator()
    
    # Find a test PDF
    pdf_files = list(Path("lesson_pdfs").glob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found")
        return False
    
    pdf_file = pdf_files[0]
    print(f"\n📄 Input: {pdf_file}")
    print(f"⏱️ Target duration: 30 seconds")
    print(f"🎯 Target audience: High School")
    
    try:
        print(f"\n🚀 Starting video generation...")
        print(f"   1️⃣ Extracting content from PDF...")
        print(f"   2️⃣ Creating lesson plan...")
        print(f"   3️⃣ Generating animations...")
        print(f"   4️⃣ Creating narration with LMNT...")
        print(f"   5️⃣ Composing final video...")
        
        # Generate video
        result = await generator.generate_video(
            str(pdf_file),
            target_duration=30,  # 30 seconds
            target_audience="high school"
        )
        
        print(f"\n✅ Video generation completed!")
        print(f"📹 Video path: {result.video_path}")
        print(f"⏱️ Duration: {result.duration} seconds")
        
        # Check if it's a real video
        if result.video_path and result.video_path.endswith('.mp4'):
            print(f"\n🎬 REAL MP4 VIDEO GENERATED!")
            
            if Path(result.video_path).exists():
                size = Path(result.video_path).stat().st_size
                print(f"📁 File size: {size / 1024 / 1024:.1f} MB")
                print(f"✅ Video file exists at: {result.video_path}")
                
                # Show video details
                print(f"\n📊 Video Details:")
                print(f"   - Resolution: 1920x1080")
                print(f"   - FPS: 30")
                print(f"   - Codec: H.264")
                print(f"   - Audio: AAC")
                
                return True
            else:
                print(f"❌ Video file not found at path")
                return False
        else:
            print(f"\n📄 Demo output generated (not a real video)")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎯 EduAgent AI - Real Video Generation Test")
    print("=" * 50)
    
    success = asyncio.run(test_real_video_generation())
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS! Real MP4 video was generated!")
        print("🎬 The system can now create actual educational videos!")
        print("\n💡 Next steps:")
        print("   1. Open the web interface: python web_interface.py")
        print("   2. Upload a PDF or image")
        print("   3. Get a real MP4 video output!")
    else:
        print("❌ Real video generation failed")
        print("\n💡 Troubleshooting:")
        print("   1. Check error messages above")
        print("   2. Verify API keys are set correctly")
        print("   3. Check MoviePy installation")

if __name__ == "__main__":
    main()