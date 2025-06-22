#!/usr/bin/env python3
"""
Test the CV-Enhanced Quality Agent
Demonstrates computer vision analysis capabilities
"""

import asyncio
import os
from manim_agent import create_animation
from quality_check_agent import check_animation_quality, QualityCheckAgent

async def test_cv_features():
    """Test all CV analysis features"""
    print("🔍 CV-Enhanced Quality Agent Test Suite")
    print("=" * 50)
    
    # Create test agent
    agent = QualityCheckAgent()
    
    # Test 1: Frame extraction
    print("\n1️⃣ Testing Frame Extraction...")
    test_video = "animations/videos/tmplebqhuvh/720p30/exponential_function_e^x_with_.mp4"
    
    if os.path.exists(test_video):
        frames = agent.extract_key_frames(test_video, num_frames=3)
        print(f"✅ Extracted {len(frames)} frames")
        
        if frames:
            frame_shape = frames[0].shape
            print(f"📐 Frame dimensions: {frame_shape[1]}x{frame_shape[0]} pixels")
    else:
        print("⚠️  Test video not found")
    
    # Test 2: OpenCV Analysis
    print("\n2️⃣ Testing OpenCV Analysis...")
    if frames:
        cv_issues = agent.detect_overlapping_elements(frames[0])
        print(f"🔍 CV detected {len(cv_issues)} potential issues")
        for issue in cv_issues:
            print(f"   - {issue.issue_type}: {issue.description}")
    
    # Test 3: Full Visual Quality Check
    print("\n3️⃣ Testing Full Visual Quality Check...")
    try:
        visual_issues = await agent.check_visual_quality(test_video)
        print(f"📊 Total visual issues found: {len(visual_issues)}")
        
        for i, issue in enumerate(visual_issues):
            print(f"   {i+1}. [{issue.severity}] {issue.issue_type}")
            print(f"      {issue.description[:100]}...")
    except Exception as e:
        print(f"⚠️  Visual analysis error: {e}")
    
    # Test 4: Generate and Analyze New Animation
    print("\n4️⃣ Testing End-to-End with New Animation...")
    result = await create_animation("quadratic function with vertex form")
    
    if result.success:
        print(f"✅ Generated: {result.video_path}")
        
        # Full quality analysis with CV
        report = await check_animation_quality(result.video_path)
        
        print(f"📊 Quality Score: {report.score}/100")
        print(f"🎯 Overall Quality: {report.overall_quality}")
        print(f"🔍 Total Issues: {len(report.issues)}")
        
        # Categorize issues
        technical_issues = [i for i in report.issues if i.issue_type in ["duration_too_short", "low_resolution", "low_framerate"]]
        visual_issues = [i for i in report.issues if i.issue_type in ["potential_overlap", "text_near_axes", "visual_layout_issue"]]
        
        print(f"   - Technical issues: {len(technical_issues)}")
        print(f"   - Visual issues: {len(visual_issues)}")
        
        if visual_issues:
            print("\n📝 Visual Issues Detected:")
            for issue in visual_issues:
                print(f"   • {issue.description}")
                print(f"     💡 {issue.suggestion}")
    
    print("\n" + "=" * 50)
    print("✅ CV Quality Agent Test Complete!")
    print("\nCapabilities Demonstrated:")
    print("  🎥 Frame extraction from video files")
    print("  🔍 OpenCV-based overlap detection")
    print("  🤖 Claude Vision API integration")
    print("  📊 Comprehensive visual quality scoring")
    print("  ⚡ Integration with Manim generation pipeline")

async def test_cv_analysis_detail():
    """Test detailed CV analysis on a specific video"""
    print("\n🔬 Detailed CV Analysis Test")
    print("-" * 30)
    
    agent = QualityCheckAgent()
    test_video = "animations/videos/tmplebqhuvh/720p30/exponential_function_e^x_with_.mp4"
    
    if not os.path.exists(test_video):
        print("⚠️  Test video not found")
        return
    
    # Extract and analyze frames individually
    frames = agent.extract_key_frames(test_video, num_frames=5)
    
    for i, frame in enumerate(frames):
        print(f"\nFrame {i+1} Analysis:")
        
        # Basic frame info
        h, w = frame.shape[:2]
        print(f"  📐 Size: {w}x{h}")
        
        # CV analysis
        issues = agent.detect_overlapping_elements(frame)
        print(f"  🔍 Issues: {len(issues)}")
        
        for issue in issues:
            print(f"    - {issue.issue_type}: {issue.description}")
    
    print("\n✅ Detailed analysis complete!")

if __name__ == "__main__":
    asyncio.run(test_cv_features())
    asyncio.run(test_cv_analysis_detail())