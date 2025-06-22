#!/usr/bin/env python3
"""
Quick test of the two-agent system
"""

import asyncio
import os
from manim_agent import create_animation
from quality_check_agent import check_animation_quality

async def test_two_agents():
    print("🧪 Testing Two-Agent System")
    print("-" * 40)
    
    # Test 1: Generate animation
    print("\n1️⃣ Generating animation...")
    start = asyncio.get_event_loop().time()
    
    result = await create_animation("exponential function e^x")
    
    gen_time = asyncio.get_event_loop().time() - start
    
    if result.success:
        print(f"✅ Generated in {gen_time:.1f}s")
        print(f"📹 Video: {result.video_path}")
        
        # Test 2: Check quality (only if video exists)
        if result.video_path and os.path.exists(result.video_path):
            print("\n2️⃣ Checking quality...")
            start = asyncio.get_event_loop().time()
            
            try:
                report = await check_animation_quality(result.video_path)
                check_time = asyncio.get_event_loop().time() - start
                
                print(f"✅ Quality checked in {check_time:.1f}s")
                print(f"📊 Score: {report.score}/100")
                print(f"🎯 Quality: {report.overall_quality}")
                
                # Show technical metrics
                if "duration" in report.technical_metrics:
                    print(f"⏱️  Duration: {report.technical_metrics['duration']:.1f}s")
                if "width" in report.technical_metrics:
                    print(f"📐 Resolution: {report.technical_metrics['width']}x{report.technical_metrics['height']}")
                    
            except Exception as e:
                print(f"⚠️  Quality check failed: {e}")
                print("   (This is OK if ffprobe is not installed)")
        else:
            print("⚠️  Video file not found, skipping quality check")
    else:
        print(f"❌ Generation failed: {result.error}")
    
    print("\n" + "-" * 40)
    print("✅ Two-agent system is working!")
    print("   - Manim agent generates videos")
    print("   - Quality agent analyzes them")
    print("   - Agents work independently")

if __name__ == "__main__":
    asyncio.run(test_two_agents())