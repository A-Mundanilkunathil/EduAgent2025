import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import manim_agent
sys.path.append(str(Path(__file__).parent.parent))

# Import our agents
from lesson_planner_agent import create_lesson_plan, LessonPlannerCore
from matt_manim_agent.manim_agent import create_animation

load_dotenv()


async def simple_integration_example():
    """Simple example showing how lesson planner and Manim agent work together"""
    
    print("=== Simple Integration Example ===\n")
    
    # Step 1: Create a lesson plan
    print("1. Creating lesson plan...")
    lesson_plan = await create_lesson_plan(
        "Linear regression and least squares",
        subject="Statistics",
        audience="High School Students",
        duration=30,
        complexity="intermediate"
    )
    
    print(f"   ✓ Created lesson: {lesson_plan.title}")
    print(f"   ✓ Number of sections: {len(lesson_plan.sections)}")
    
    # Step 2: Extract visualization opportunities
    print("\n2. Finding visualization opportunities...")
    core = LessonPlannerCore()
    manim_requests = core.generate_manim_requests(lesson_plan)
    
    print(f"   ✓ Found {len(manim_requests)} visualization opportunities")
    
    # Step 3: Create animations for each opportunity
    print("\n3. Creating animations...")
    animations = []
    
    for i, request in enumerate(manim_requests):
        print(f"   Creating animation {i+1}: {request['manim_context']['concept']}")
        
        # Create the animation
        animation = await create_animation(
            concept=request['manim_context']['concept'],
            script_context=request['manim_context']['script_context'],
            duration=request['manim_context']['duration']
        )
        
        if animation.success:
            print(f"     ✓ Success! Video saved to: {animation.video_path}")
            animations.append(animation)
        else:
            print(f"     ✗ Failed: {animation.error}")
    
    # Step 4: Display results
    print(f"\n=== Results ===")
    print(f"Lesson: {lesson_plan.title}")
    print(f"Total sections: {len(lesson_plan.sections)}")
    print(f"Animations created: {len(animations)}")
    
    if animations:
        print("\nAnimation files:")
        for i, anim in enumerate(animations, 1):
            print(f"  {i}. {anim.concept} -> {anim.video_path}")
    
    return lesson_plan, animations


async def test_manim_agent():
    """Test the Manim agent independently"""
    print("\n=== Testing Manim Agent ===")
    
    # Test a simple animation
    result = await create_animation(
        "sine wave",
        script_context="Show a simple sine wave animation",
        duration=10.0
    )
    
    print(f"Success: {result.success}")
    if result.success:
        print(f"Video: {result.video_path}")
        print(f"Duration: {result.duration} seconds")
        print(f"Visual elements: {result.visual_elements}")
    else:
        print(f"Error: {result.error}")
    
    return result


async def main():
    """Run the integration examples"""
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Please set ANTHROPIC_API_KEY in .env file")
        return
    
    try:
        # Test Manim agent first
        await test_manim_agent()
        
        # Run the integration example
        await simple_integration_example()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 