import asyncio
import os
from crewai import Crew, Task
from dotenv import load_dotenv

from manim_agent import ManimAgent, create_animation
from manim_tools import create_manim_tools
from context_handler import ManimTaskContext, ScriptContext, DirectorContext, TimingContext, ContextParser

load_dotenv()


async def example_standalone_simple():
    """Example 1: Simple standalone usage"""
    print("\n=== Example 1: Simple Standalone Usage ===")
    
    # Create animation with minimal context
    result = await create_animation("Neural network with 2 input nodes, 3 hidden layers with 5 nodes each, and 1 output node")
    
    print(f"Success: {result.success}")
    print(f"Video Path: {result.video_path}")
    print(f"Duration: {result.duration}s")
    print(f"Visual Elements: {result.visual_elements}")


async def example_standalone_with_context():
    """Example 2: Standalone with rich context"""
    print("\n=== Example 2: Standalone with Context ===")
    
    # Create animation with additional context
    result = await create_animation(
        concept="the fundamental theorem of calculus",
        script_context="Now we'll see how integration and differentiation are inverse operations...",
        duration=20.0,
        style_direction={"color_scheme": {"primary": "#3B82F6", "accent": "#F59E0B"}, "pace": "slow"}
    )
    
    print(f"Success: {result.success}")
    print(f"Concept: {result.concept}")
    print(f"Metadata: {result.metadata}")


async def example_crewai_integration():
    """Example 3: Full CrewAI integration"""
    print("\n=== Example 3: CrewAI Integration ===")
    
    # Create agent
    manim_agent = ManimAgent(
        role="Lead Animation Engineer",
        goal="Create stunning mathematical visualizations that enhance learning",
        verbose=True
    )
    
    # Create structured context
    context = ManimTaskContext(
        concept="Fourier series and signal decomposition",
        complexity_level="advanced",
        script_context=ScriptContext(
            narrative="Let's explore how any periodic signal can be decomposed into simple sine waves",
            key_points=["Frequency components", "Amplitude and phase", "Convergence"],
            emphasis_timings={3.0: "highlight_fundamental", 8.0: "show_harmonics"}
        ),
        director_context=DirectorContext(
            visual_style="3blue1brown",
            color_scheme={"wave": "#00D9FF", "component": "#FFB86C", "sum": "#50FA7B"},
            pacing="moderate",
            transitions=["smooth", "morph"]
        ),
        timing_context=TimingContext(
            total_duration=30.0,
            segment_durations={"intro": 5.0, "decomposition": 15.0, "synthesis": 10.0}
        ),
        learning_objectives=["Understand Fourier decomposition", "Visualize frequency domain"]
    )
    
    # Create task with context
    task = Task(
        description="Create Fourier series visualization",
        agent=manim_agent,
        expected_output="A Manim animation video file visualizing Fourier series"
    )
    
    # Set context separately
    task.context = [context.to_agent_context()]
    
    # Execute task
    result = await manim_agent.execute(task)
    
    print(f"Success: {result.success}")
    print(f"Video Path: {result.video_path}")
    print(f"Sync Points: {result.sync_points}")
    print(f"Visual Elements: {result.visual_elements}")


async def example_multi_agent_simulation():
    """Example 4: Simulated multi-agent context"""
    print("\n=== Example 4: Multi-Agent Simulation ===")
    
    # Simulate receiving context from other agents
    script_agent_output = {
        "concept": "limit definition of derivative",
        "script_context": """
        The derivative at a point represents the instantaneous rate of change.
        We can understand this by looking at the limit as h approaches zero
        of the difference quotient: [f(x+h) - f(x)] / h
        """,
        "emphasis_points": [
            {"time": 2.0, "text": "Show secant line"},
            {"time": 5.0, "text": "Animate h approaching zero"},
            {"time": 8.0, "text": "Reveal tangent line"}
        ]
    }
    
    director_agent_output = {
        "style_direction": {
            "visual_style": "minimalist",
            "color_scheme": {"function": "#8B5CF6", "tangent": "#EC4899", "text": "#F3F4F6"},
            "pace": "deliberate"
        },
        "duration": 12.0,
        "camera_angles": ["standard", "zoom_to_point", "pull_back"]
    }
    
    # Parse and merge contexts
    parser = ContextParser()
    base_context = parser.parse_raw_context(script_agent_output)
    merged_context = parser.merge_contexts(base_context, director_agent_output)
    
    # Create agent and execute
    agent = ManimAgent()
    
    # Create a simple task-like object for execution
    class SimpleTask:
        def __init__(self, description, context):
            self.description = description
            self.context = context
    
    task = SimpleTask(
        description="Create limit definition animation",
        context=merged_context.to_agent_context()
    )
    
    result = await agent.execute(task)
    
    print(f"Success: {result.success}")
    print(f"Duration: {result.duration}s")
    print(f"Context Used: {result.metadata.get('context_used', [])}")


def example_crew_setup():
    """Example 5: Complete Crew setup (sync version for CrewAI)"""
    print("\n=== Example 5: Crew Setup ===")
    
    # Create agents
    manim_agent = ManimAgent(
        role="Mathematical Animator",
        goal="Transform abstract math into beautiful visualizations",
        tools=create_manim_tools()
    )
    
    # Create tasks
    task1 = Task(
        description="Create animation for quadratic formula derivation",
        agent=manim_agent,
        expected_output="A Manim animation video showing quadratic formula derivation"
    )
    
    task2 = Task(
        description="Create animation for complex number visualization",
        agent=manim_agent,
        expected_output="A Manim animation video showing complex numbers on the complex plane"
    )
    
    # Create crew
    crew = Crew(
        agents=[manim_agent],
        tasks=[task1, task2],
        verbose=True
    )
    
    print("Crew setup complete!")
    print(f"Agents: {[agent.role for agent in crew.agents]}")
    print(f"Tasks: {[task.description for task in crew.tasks]}")
    
    # Note: crew.kickoff() would execute all tasks


async def main():
    """Run all examples"""
    
    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Please set ANTHROPIC_API_KEY in .env file")
        print("Copy .env.example to .env and add your API key")
        return
    
    # Run examples
    try:
        await example_standalone_simple()
        await example_standalone_with_context()
        await example_crewai_integration()
        await example_multi_agent_simulation()
        example_crew_setup()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run async examples
    asyncio.run(main())