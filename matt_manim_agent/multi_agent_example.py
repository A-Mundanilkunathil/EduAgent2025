#!/usr/bin/env python3
"""
Multi-Agent Example: Manim Generation + Quality Check
Demonstrates the two-agent architecture for fast generation with optional quality validation
"""

import asyncio
import os
from crewai import Crew, Task
from dotenv import load_dotenv

from manim_agent import ManimAgent, create_animation
from quality_check_agent import QualityCheckAgent, check_animation_quality
from quality_tools import create_quality_tools

load_dotenv()


async def example_fast_generation():
    """Example 1: Fast generation without quality check"""
    print("\n🚀 Example 1: Fast Generation Mode")
    print("=" * 50)
    
    start_time = asyncio.get_event_loop().time()
    
    # Generate animation quickly
    result = await create_animation(
        concept="derivative of x² at x=2",
        script_context="Show the tangent line and slope calculation"
    )
    
    end_time = asyncio.get_event_loop().time()
    
    print(f"✅ Generation complete in {end_time - start_time:.1f} seconds")
    print(f"📹 Video: {result.video_path}")
    print(f"📊 Success: {result.success}")
    
    return result.video_path if result.success else None


async def example_with_quality_check():
    """Example 2: Generation followed by quality check"""
    print("\n🔍 Example 2: Generation + Quality Check")
    print("=" * 50)
    
    # Step 1: Generate animation
    print("Step 1: Generating animation...")
    start_time = asyncio.get_event_loop().time()
    
    result = await create_animation(
        concept="Pythagorean theorem visual proof",
        duration=15.0
    )
    
    gen_time = asyncio.get_event_loop().time() - start_time
    print(f"✅ Generated in {gen_time:.1f} seconds")
    
    if result.success and result.video_path:
        # Step 2: Check quality
        print("\nStep 2: Checking quality...")
        quality_start = asyncio.get_event_loop().time()
        
        quality_report = await check_animation_quality(result.video_path)
        
        quality_time = asyncio.get_event_loop().time() - quality_start
        
        print(f"✅ Quality check complete in {quality_time:.1f} seconds")
        print(f"📊 Quality Score: {quality_report.score}/100")
        print(f"🎯 Overall Quality: {quality_report.overall_quality}")
        
        if quality_report.issues:
            print(f"\n⚠️  Issues Found ({len(quality_report.issues)}):")
            for issue in quality_report.issues[:3]:  # Show first 3 issues
                print(f"   - {issue.description}")
        
        if quality_report.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in quality_report.recommendations[:2]:
                print(f"   - {rec}")
    
    return result.video_path if result.success else None


def example_crewai_two_agents():
    """Example 3: Full CrewAI setup with both agents"""
    print("\n🤖 Example 3: CrewAI Two-Agent System")
    print("=" * 50)
    
    # Create agents
    manim_agent = ManimAgent(
        role="Animation Generator",
        goal="Create mathematical animations quickly"
    )
    
    quality_agent = QualityCheckAgent(
        role="Quality Assurance",
        goal="Ensure animations meet quality standards",
        tools=create_quality_tools()
    )
    
    # Create tasks
    generation_task = Task(
        description="Create an animation showing integration as area under a curve",
        agent=manim_agent,
        expected_output="A Manim animation video file"
    )
    
    quality_task = Task(
        description="Analyze the generated animation for quality issues",
        agent=quality_agent,
        expected_output="Quality report with score and recommendations"
    )
    
    # Create crew with sequential tasks
    crew = Crew(
        agents=[manim_agent, quality_agent],
        tasks=[generation_task, quality_task],
        verbose=True
    )
    
    print("✅ CrewAI setup complete!")
    print(f"Agents: {[agent.role for agent in crew.agents]}")
    print(f"Tasks: {[task.description[:50] + '...' for task in crew.tasks]}")
    
    # Note: crew.kickoff() would execute both tasks in sequence


async def example_conditional_quality():
    """Example 4: Conditional quality check based on complexity"""
    print("\n⚡ Example 4: Smart Quality Check (Complex Animations Only)")
    print("=" * 50)
    
    animations = [
        ("simple sine wave", False),  # Simple - skip quality check
        ("Fourier transform visualization with 10 harmonics", True),  # Complex - check quality
        ("unit circle", False),  # Simple
        ("3D vector field with curl and divergence", True)  # Complex
    ]
    
    for concept, needs_quality_check in animations:
        print(f"\n📐 Generating: {concept}")
        
        # Generate animation
        result = await create_animation(concept)
        
        if result.success:
            print(f"   ✅ Generated: {result.video_path}")
            
            if needs_quality_check:
                print("   🔍 Running quality check (complex animation)...")
                report = await check_animation_quality(result.video_path)
                print(f"   📊 Quality: {report.overall_quality} ({report.score:.0f}/100)")
            else:
                print("   ⏭️  Skipping quality check (simple animation)")


async def example_feedback_loop():
    """Example 5: Quality feedback loop for improvement"""
    print("\n🔄 Example 5: Quality Feedback Loop")
    print("=" * 50)
    
    concept = "matrix multiplication step by step"
    max_attempts = 2
    target_quality_score = 70
    
    for attempt in range(1, max_attempts + 1):
        print(f"\nAttempt {attempt}:")
        
        # Generate animation
        if attempt == 1:
            result = await create_animation(concept)
        else:
            # Add quality hints based on previous feedback
            result = await create_animation(
                concept,
                script_context="Ensure clear spacing between matrices and steps",
                style_direction={"spacing": "generous", "pace": "slower"}
            )
        
        if result.success:
            # Check quality
            report = await check_animation_quality(result.video_path)
            print(f"✅ Generated with quality score: {report.score}/100")
            
            if report.score >= target_quality_score:
                print(f"🎉 Target quality achieved!")
                break
            else:
                print(f"📝 Quality below target ({target_quality_score})")
                if report.issues:
                    print(f"   Issues to address: {report.issues[0].description}")


async def main():
    """Run all examples"""
    print("🎬 MULTI-AGENT SYSTEM DEMO")
    print("Manim Generator + Quality Checker")
    print("=" * 60)
    
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: Please set ANTHROPIC_API_KEY in .env file")
        return
    
    try:
        # Run examples
        await example_fast_generation()
        await example_with_quality_check()
        example_crewai_two_agents()
        await example_conditional_quality()
        await example_feedback_loop()
        
        print("\n" + "=" * 60)
        print("✅ Multi-Agent Demo Complete!")
        print("Benefits demonstrated:")
        print("  • Fast generation when quality check not needed")
        print("  • Optional quality validation for important content")
        print("  • Clean separation of concerns")
        print("  • Flexible workflow options")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())