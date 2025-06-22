#!/usr/bin/env python3
"""
Test the fixed full pipeline
"""

import asyncio
import os
from pathlib import Path

async def test_fixed_pipeline():
    """Test the complete fixed pipeline"""
    
    print("🎬 Testing Fixed Full Pipeline")
    print("=" * 50)
    
    # Use the web interface method which should work
    from web_interface import EduAgentInterface
    
    interface = EduAgentInterface()
    
    # Create a mock file object
    class MockFile:
        def __init__(self, name):
            self.name = name
    
    test_file = MockFile("lesson_pdfs/sample_calculus.pdf")
    
    print(f"📁 Processing: {test_file.name}")
    print("⏱️  This should take 30-90 seconds...")
    print()
    
    try:
        # Use the web interface's async method
        result = await interface._async_generate_video(
            test_file,
            "Math Teacher",      # voice choice
            "Mathematics",       # subject  
            "High School",       # grade level
            1.0,                # duration
            True,               # captions
            True,               # transcript
            False               # normal speed
        )
        
        print("🎯 Final Results:")
        print("-" * 30)
        print(f"✅ Success: {result['success']}")
        
        if result['success']:
            video_path = result.get('video_path')
            print(f"🎬 Video: {video_path}")
            
            if video_path and Path(video_path).exists():
                file_size = Path(video_path).stat().st_size / (1024*1024)  # MB
                print(f"📊 Size: {file_size:.1f} MB")
                print(f"⏱️  Duration: {result.get('duration', 0):.1f} seconds")
                print()
                print("🎉 SUCCESS! Real video file created!")
            else:
                print("📝 Demo mode - no actual video file")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixed_pipeline())