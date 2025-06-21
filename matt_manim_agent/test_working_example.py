import asyncio
from manim_agent_simple import SimpleManimAgent

async def test_examples():
    agent = SimpleManimAgent()
    
    # Test 1: Simple concept
    print("=== Test 1: Circle to Square ===")
    result = await agent.create_animation(
        "circle transforming into a square",
        duration=5.0
    )
    print(f"Success: {result.success}")
    print(f"Video: {result.video_path}")
    if result.error:
        print(f"Error: {result.error[:200]}")
    print()
    
    # Test 2: Math concept
    print("=== Test 2: Pythagorean Theorem ===")
    result = await agent.create_animation(
        "Pythagorean theorem visualization",
        script_context="Show that a² + b² = c² for right triangles",
        style_direction={"color_scheme": {"triangle": "#3B82F6", "squares": "#10B981"}}
    )
    print(f"Success: {result.success}")
    print(f"Video: {result.video_path}")
    if result.error:
        print(f"Error: {result.error[:200]}")
    print()
    
    # Test 3: Simple working example
    print("=== Test 3: Simple Text Animation ===")
    result = await agent.create_animation(
        "text saying 'Hello Math!' with fade in effect"
    )
    print(f"Success: {result.success}")
    print(f"Video: {result.video_path}")
    if result.error:
        print(f"Error: {result.error[:200]}")
    if result.manim_code:
        print("\nGenerated code:")
        print(result.manim_code)

if __name__ == "__main__":
    asyncio.run(test_examples())