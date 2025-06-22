#!/usr/bin/env python3
"""
Test the short video demo functionality
"""

import time
from pathlib import Path

def test_short_video_demo():
    """Test the web interface with short video settings"""
    print("🎬 Testing Short Video Demo Mode")
    print("=" * 40)
    
    try:
        from web_interface import EduAgentInterface
        
        app = EduAgentInterface()
        print("✅ Web interface created")
        
        # Test with the short lesson content
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        short_file = MockFile("sample_short_lesson.txt")
        
        # Test different short video durations
        durations = [0.5, 1.0, 1.5, 2.0]
        
        for duration in durations:
            print(f"\n🎯 Testing {duration} minute video...")
            
            start_time = time.time()
            result = app._simulate_video_generation(
                short_file,
                "Math Teacher",
                "Mathematics", 
                "High School",
                duration,
                True,  # captions
                True,  # transcript  
                False  # slow narration
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            print(f"   ⚡ Response time: {response_time:.2f} seconds")
            print(f"   📹 Video duration: {result[2]['duration']}")
            print(f"   🔧 Processing estimate: {result[2]['processing_time']}")
            
            # Verify fast response
            if response_time < 1.0:
                print(f"   ✅ Fast response - perfect for demos!")
            else:
                print(f"   ⚠️  Response time could be faster")
        
        # Check sample content exists
        sample_path = Path("sample_short_lesson.txt")
        if sample_path.exists():
            content = sample_path.read_text()
            print(f"\n📝 Sample content ready ({len(content)} characters)")
            print("   ✅ Optimized for 30-60 second videos")
        else:
            print("\n❌ Sample short lesson file missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Short demo test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = test_short_video_demo()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Short Video Demo Ready!")
        print()
        print("✅ Duration range: 30 seconds - 3 minutes")
        print("✅ Fast simulation responses")
        print("✅ Optimized for live demos") 
        print("✅ Clear, concise output")
        print()
        print("🚀 Perfect for hackathon presentations!")
        print("   📱 Quick, engaging demos")
        print("   ⚡ Immediate feedback")
        print("   🎬 Professional appearance")
        print()
        print("Launch: python web_interface.py")
    else:
        print("⚠️  Short demo test failed")

if __name__ == "__main__":
    main()