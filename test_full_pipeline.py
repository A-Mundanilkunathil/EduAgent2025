#!/usr/bin/env python3
"""
Test script for the full video generation pipeline
"""

import asyncio
from web_interface import EduAgentInterface
from pathlib import Path

async def test_full_pipeline():
    """Test the complete video generation pipeline"""
    
    print("🎬 Testing Full Video Generation Pipeline")
    print("=" * 60)
    
    # Create interface
    interface = EduAgentInterface()
    
    # Test with existing sample file
    test_file_path = "lesson_pdfs/sample_calculus.pdf"
    
    # Create a mock file object for testing
    class MockFile:
        def __init__(self, name):
            self.name = name
    
    test_file = MockFile(test_file_path)
    
    print(f"📁 Testing with file: {test_file.name}")
    print(f"🎯 Target: High School Mathematics, 1 minute duration")
    print()
    
    # Test the async video generation directly
    print("🔄 Starting full pipeline test...")
    
    try:
        print("⏱️  This may take 30-120 seconds for full video generation...")
        
        result = await interface._async_generate_video(
            test_file, 
            "Math Teacher",      # voice choice
            "Mathematics",       # subject
            "High School",       # grade level
            1.0,                # 1 minute duration
            True,               # captions
            True,               # transcript
            False               # normal speed
        )
        
        print("\n📊 Pipeline Test Results:")
        print("-" * 30)
        print(f"✅ Success: {result['success']}")
        
        if result["success"]:
            print(f"🎬 Video path: {result.get('video_path', 'Not generated')}")
            print(f"⏱️  Duration: {result.get('duration', 0):.1f} seconds")
            print(f"📦 File size: {result.get('size_mb', 0):.1f} MB")
            print(f"♿ Features: {result.get('accessibility_features', [])}")
            
            # Check if actual video was created
            video_path = result.get('video_path')
            if video_path and Path(video_path).exists():
                print(f"🎉 Real MP4 video created at: {video_path}")
            else:
                print("📝 Demo/simulation mode - no actual video file")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        print("\n✅ Full pipeline test completed!")
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())