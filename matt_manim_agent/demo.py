#!/usr/bin/env python3
"""
Manim Animation Agent Demo
UC Berkeley AI Hackathon 2025

This demo showcases the CrewAI Manim Agent's capabilities:
1. Standalone animation generation
2. Context-aware animations with script integration
3. Multi-agent simulation with rich context
4. Professional math visualizations with Claude AI
"""

import asyncio
import os
from dotenv import load_dotenv
from manim_agent import create_animation, ManimAgent
from context_handler import ManimTaskContext, ScriptContext, DirectorContext, TimingContext

load_dotenv()


async def demo_basic():
    """Demo 1: Basic animation generation"""
    print("🎬 Demo 1: Basic Animation Generation")
    print("-" * 50)
    
    result = await create_animation("Pythagorean theorem with visual proof")
    
    print(f"✅ Success: {result.success}")
    print(f"📹 Video: {result.video_path}")
    print(f"⏱️  Duration: {result.duration:.1f}s")
    print(f"🎨 Visual elements: {', '.join(result.visual_elements)}")
    print()


async def demo_with_context():
    """Demo 2: Animation with educational context"""
    print("🎓 Demo 2: Context-Aware Educational Animation")
    print("-" * 50)
    
    result = await create_animation(
        concept="derivatives as instantaneous rate of change",
        script_context="""
        Let's explore how derivatives capture the instantaneous rate of change.
        We'll start with a simple function f(x) = x², then show how the slope 
        of secant lines approaches the slope of the tangent line as we make 
        the interval smaller and smaller.
        """,
        duration=20.0,
        style_direction={
            "color_scheme": {
                "function": "#3B82F6",
                "tangent": "#EF4444",
                "secant": "#10B981"
            },
            "pace": "deliberate"
        }
    )
    
    print(f"✅ Success: {result.success}")
    print(f"📹 Video: {result.video_path}")
    print(f"📊 Context used: {result.metadata.get('context_used', [])}")
    print()


async def demo_multi_agent():
    """Demo 3: Multi-agent simulation"""
    print("🤖 Demo 3: Multi-Agent Context Integration")
    print("-" * 50)
    
    # Create structured context as if from multiple agents
    context = ManimTaskContext(
        concept="Fourier series decomposition",
        complexity_level="advanced",
        script_context=ScriptContext(
            narrative="Watch as we decompose a complex wave into simple sine components",
            key_points=["Frequency", "Amplitude", "Phase"],
            emphasis_timings={
                3.0: "show_original_wave",
                8.0: "begin_decomposition",
                15.0: "show_reconstruction"
            }
        ),
        director_context=DirectorContext(
            visual_style="3blue1brown",
            color_scheme={
                "original": "#8B5CF6",
                "component1": "#3B82F6",
                "component2": "#10B981",
                "component3": "#F59E0B"
            },
            pacing="moderate"
        ),
        timing_context=TimingContext(
            total_duration=25.0,
            segment_durations={
                "intro": 5.0,
                "decomposition": 12.0,
                "reconstruction": 8.0
            }
        )
    )
    
    # Create agent and execute
    from manim_agent import ManimAgentCore
    core = ManimAgentCore()
    result = await core.process_animation_task(context.to_agent_context())
    
    print(f"✅ Success: {result.success}")
    print(f"📹 Video: {result.video_path}")
    print(f"🎯 Sync points: {len(result.sync_points)}")
    print(f"🎨 Visual elements: {', '.join(result.visual_elements[:5])}...")
    print()


async def demo_creative():
    """Demo 4: Creative mathematical visualization"""
    print("✨ Demo 4: Creative Mathematical Art")
    print("-" * 50)
    
    result = await create_animation(
        concept="golden ratio spiral with Fibonacci sequence",
        script_context="Create a mesmerizing visualization of the golden ratio",
        style_direction={
            "visual_style": "artistic",
            "color_scheme": {
                "spiral": "#FFD700",
                "squares": "#4A5568",
                "numbers": "#FFFFFF"
            },
            "transitions": ["smooth", "fade"]
        },
        duration=15.0
    )
    
    print(f"✅ Success: {result.success}")
    print(f"📹 Video: {result.video_path}")
    if result.manim_code:
        print(f"💻 Generated {len(result.manim_code.split('\\n'))} lines of Manim code")
    print()


async def main():
    """Run all demos"""
    print("=" * 60)
    print("🚀 MANIM ANIMATION AGENT DEMO")
    print("UC Berkeley AI Hackathon 2025")
    print("=" * 60)
    print()
    
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: Please set ANTHROPIC_API_KEY in .env file")
        return
    
    # Run demos
    try:
        await demo_basic()
        await demo_with_context()
        await demo_multi_agent()
        await demo_creative()
        
        print("=" * 60)
        print("✅ All demos completed successfully!")
        print("🎬 Check the 'animations' folder for generated videos")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())