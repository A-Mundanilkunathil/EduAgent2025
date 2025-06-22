#!/usr/bin/env python3
"""
Test Web Interface Video Generation Status
Simple test to show exactly what the web interface produces
"""

import os
from web_interface import EduAgentInterface

def test_interface_status():
    """Test what the web interface will actually do"""
    
    print("🧪 Web Interface Status Test")
    print("=" * 40)
    
    # Check API status
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_lmnt = bool(os.getenv("LMNT_API_KEY"))
    demo_mode = not (has_anthropic and has_lmnt)
    
    print(f"🔑 API Keys:")
    print(f"   ANTHROPIC_API_KEY: {'✅ Set' if has_anthropic else '❌ Missing'}")
    print(f"   LMNT_API_KEY: {'✅ Set' if has_lmnt else '❌ Missing'}")
    
    print(f"\n🎯 Interface Mode:")
    if demo_mode:
        print(f"   📱 DEMO MODE")
        print(f"   • Web interface will show: 'DEMO MODE - Fast simulation'")
        print(f"   • Output: Text files with video metadata")
        print(f"   • Speed: Instant response")
    else:
        print(f"   🎬 REAL VIDEO MODE") 
        print(f"   • Web interface will show: 'REAL VIDEO MODE - Generating actual MP4'")
        print(f"   • Output: Attempts to create MP4 video files")
        print(f"   • Speed: Slower, may have errors")
    
    # Test the simulation function
    print(f"\n🧪 Testing Interface Components:")
    
    try:
        app = EduAgentInterface()
        print(f"   ✅ Interface created successfully")
        
        # Test simulation (this is what happens in demo mode)
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        mock_file = MockFile("test.pdf")
        result = app._simulate_video_generation(
            mock_file, "Math Teacher", "Mathematics", "High School",
            1.0, True, True, False
        )
        
        print(f"   ✅ Demo simulation works")
        print(f"   📄 Demo output type: {type(result[0])}")
        print(f"   💬 Status message: {result[1]}")
        print(f"   📊 Has metadata: {'Yes' if result[2] else 'No'}")
        
    except Exception as e:
        print(f"   ❌ Interface test failed: {e}")
    
    return demo_mode

def show_expected_behavior():
    """Show what user should expect"""
    
    demo_mode = test_interface_status()
    
    print(f"\n🎯 What You'll See in the Web Interface:")
    print(f"=" * 40)
    
    if demo_mode:
        print(f"📱 DEMO MODE BEHAVIOR:")
        print(f"   1. Orange banner: 'DEMO MODE - Fast simulation'")
        print(f"   2. Upload file → Instant processing")
        print(f"   3. Status: 'DEMO MODE: Simulating video generation'")
        print(f"   4. Result: 'Demo completed! Add API keys for real videos'")
        print(f"   5. Download: Text file with video structure")
        print(f"   6. No MP4 files created")
        print(f"")
        print(f"💡 Perfect for:")
        print(f"   • Hackathon presentations")
        print(f"   • Quick demos")
        print(f"   • Showing system architecture")
    else:
        print(f"🎬 REAL VIDEO MODE BEHAVIOR:")
        print(f"   1. Green banner: 'REAL VIDEO MODE - Generating actual MP4'")
        print(f"   2. Upload file → Slower processing")
        print(f"   3. Status: 'REAL VIDEO MODE: Generating actual MP4 video'")
        print(f"   4. Result: May succeed or fail depending on setup")
        print(f"   5. Download: MP4 file if successful")
        print(f"   6. Currently has audio processing issues")
        print(f"")
        print(f"💡 Currently:")
        print(f"   • Tries to generate real videos")
        print(f"   • May fail due to audio/ffmpeg issues")
        print(f"   • Better to use demo mode for presentations")

if __name__ == "__main__":
    show_expected_behavior()