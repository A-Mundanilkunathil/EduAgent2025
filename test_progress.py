#!/usr/bin/env python3
"""
Test script to verify progress indicators work correctly
"""

import asyncio
import time
from web_interface import EduAgentInterface
from pathlib import Path

async def test_progress_flow():
    """Test the complete progress flow"""
    
    print("🧪 Testing Progress Indicators")
    print("=" * 50)
    
    # Create interface
    interface = EduAgentInterface()
    
    # Test with existing sample file
    test_file_path = "lesson_pdfs/sample_calculus.pdf"
    if not Path(test_file_path).exists():
        print(f"❌ Test file not found: {test_file_path}")
        print("📝 Creating mock file object...")
        
        # Create a mock file object for testing
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        test_file = MockFile(test_file_path)
    else:
        class MockFile:
            def __init__(self, name):
                self.name = name
        test_file = MockFile(test_file_path)
    
    print(f"📁 Testing with file: {test_file.name}")
    print()
    
    # Test the generator function to see progress updates
    print("🔄 Starting progress test...")
    
    try:
        generator = interface.generate_video(
            test_file, 
            "Math Teacher", 
            "Mathematics", 
            "High School",
            1.0,  # 1 minute duration
            True,  # captions
            True,  # transcript
            False  # normal speed
        )
        
        # Iterate through progress updates
        for i, result in enumerate(generator):
            content_preview, status, metadata, download1, download2 = result
            print(f"Step {i+1}: {status}")
            
            # Add small delay to see progress
            if "timeout" not in status.lower() and "error" not in status.lower():
                time.sleep(0.5)
            
            # Break if we get final result or error
            if "complete" in status.lower() or "error" in status.lower() or "timeout" in status.lower():
                print(f"📊 Final metadata: {metadata}")
                break
        
        print("\n✅ Progress indicator test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_progress_flow())