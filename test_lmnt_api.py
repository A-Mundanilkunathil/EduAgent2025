#!/usr/bin/env python3
"""
Test LMNT API directly to diagnose issues
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_lmnt_api():
    """Test the LMNT API with a simple request"""
    
    api_key = os.getenv("LMNT_API_KEY")
    if not api_key:
        print("❌ LMNT_API_KEY not found")
        return
    
    print(f"✅ LMNT_API_KEY loaded: {api_key[:4]}...")
    
    # Test the API
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": "Hello, this is a test of the LMNT text to speech API.",
        "voice": "lily",
        "speed": 1.0,
        "format": "wav",
        "sample_rate": 24000
    }
    
    print("\n🧪 Testing LMNT API...")
    print(f"Endpoint: https://api.lmnt.com/v1/ai/speech")
    print(f"Voice: lily")
    print(f"Text: {payload['text']}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "https://api.lmnt.com/v1/ai/speech",
                headers=headers,
                json=payload
            ) as response:
                print(f"\n📡 Response Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    audio_data = await response.read()
                    print(f"✅ Success! Audio data received: {len(audio_data)} bytes")
                    
                    # Save test audio
                    with open("test_lmnt_output.wav", "wb") as f:
                        f.write(audio_data)
                    print(f"💾 Audio saved to: test_lmnt_output.wav")
                    
                    # Check if it's valid WAV
                    if audio_data[:4] == b'RIFF':
                        print(f"✅ Valid WAV file detected")
                    else:
                        print(f"⚠️ Data doesn't start with WAV header")
                        print(f"First 20 bytes: {audio_data[:20]}")
                    
                else:
                    error_text = await response.text()
                    print(f"❌ API Error: {error_text}")
                    
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print(f"Error type: {type(e).__name__}")

async def test_lmnt_voices():
    """Test available voices"""
    
    api_key = os.getenv("LMNT_API_KEY")
    headers = {
        "X-API-Key": api_key,
    }
    
    print("\n🎤 Checking available voices...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                "https://api.lmnt.com/v1/ai/voices",
                headers=headers
            ) as response:
                if response.status == 200:
                    voices = await response.json()
                    print(f"✅ Available voices:")
                    for voice in voices[:5]:  # Show first 5
                        print(f"   - {voice}")
                else:
                    print(f"❌ Could not fetch voices: {response.status}")
        except Exception as e:
            print(f"❌ Error fetching voices: {e}")

def main():
    print("🔍 LMNT API Diagnostic Test")
    print("=" * 40)
    
    # Run the test
    asyncio.run(test_lmnt_api())
    asyncio.run(test_lmnt_voices())
    
    print("\n🎯 Next Steps:")
    print("1. If API works, the issue is in the integration")
    print("2. If API fails, check the API key or endpoint")

if __name__ == "__main__":
    main()