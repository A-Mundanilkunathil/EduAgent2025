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


async def targeted_integration_example():
    """Targeted example using topics that will definitely generate visualizations"""
    
    print("=== Targeted Integration Example ===\n")
    
    # Use topics that are guaranteed to have visual elements
    topics = [
        "Derivatives and tangent lines",
        "Fourier series decomposition", 
        "Vector fields and gradients",
        "Complex number multiplication"
    ]
    
    for topic in topics:
        print(f"\n--- Testing: {topic} ---")
        
        # Step 1: Create lesson plan
        print("1. Creating lesson plan...")
        lesson_plan = await create_lesson_plan(
            topic,
            subject="Mathematics",
            audience="College Students",
            duration=45,
            complexity="intermediate"
        )
        
        print(f"   ✓ Created lesson: {lesson_plan.title}")
        print(f"   ✓ Number of sections: {len(lesson_plan.sections)}")
        
        # Step 2: Extract visualization opportunities
        print("2. Finding visualization opportunities...")
        core = LessonPlannerCore()
        manim_requests = core.generate_manim_requests(lesson_plan)
        
        print(f"   ✓ Found {len(manim_requests)} visualization opportunities")
        
        # Step 3: Create animations for each opportunity
        if manim_requests:
            print("3. Creating animations...")
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
            
            print(f"\n   Results for {topic}:")
            print(f"   - Animations created: {len(animations)}")
            if animations:
                for i, anim in enumerate(animations, 1):
                    print(f"     {i}. {anim.concept} -> {anim.video_path}")
        else:
            print("3. No visualization opportunities found for this topic")
        
        print("\n" + "="*50)


async def manual_animation_creation():
    """Manually create animations for common mathematical concepts"""
    
    print("\n=== Manual Animation Creation ===")
    
    # Define common mathematical concepts that work well with Manim
    concepts = [
        {
            "concept": "derivative visualization",
            "script_context": "Show how the derivative represents the slope of a tangent line",
            "duration": 15.0
        },
        {
            "concept": "fourier series",
            "script_context": "Demonstrate how complex functions can be built from sine waves",
            "duration": 20.0
        },
        {
            "concept": "vector field",
            "script_context": "Show a 2D vector field with arrows indicating direction and magnitude",
            "duration": 12.0
        }
    ]
    
    animations = []
    
    for i, concept_data in enumerate(concepts, 1):
        print(f"\nCreating animation {i}: {concept_data['concept']}")
        
        animation = await create_animation(
            concept=concept_data['concept'],
            script_context=concept_data['script_context'],
            duration=concept_data['duration']
        )
        
        if animation.success:
            print(f"  ✓ Success! Video: {animation.video_path}")
            print(f"  ✓ Duration: {animation.duration:.1f} seconds")
            print(f"  ✓ Visual elements: {animation.visual_elements}")
            animations.append(animation)
        else:
            print(f"  ✗ Failed: {animation.error}")
    
    return animations


async def main():
    """Run the targeted integration examples"""
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Please set ANTHROPIC_API_KEY in .env file")
        return
    
    try:
        # Run targeted integration
        await targeted_integration_example()
        
        # Run manual animation creation
        animations = await manual_animation_creation()
        
        print(f"\n=== Final Summary ===")
        print(f"Total animations created: {len(animations)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 