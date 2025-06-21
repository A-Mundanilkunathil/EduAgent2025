import asyncio
import os
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
# from manim import *  # Will be imported when running
import tempfile

load_dotenv()

async def test_manim_generation():
    """Test simple Manim code generation"""
    
    # Create Claude client
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Test prompt
    prompt = """Create a simple Manim animation that shows a circle transforming into a square. 
    The animation should be about 5 seconds long and use smooth transitions.
    
    Return only the Python code for the Manim Scene class."""
    
    try:
        # Get Manim code from Claude
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        manim_code = response.content[0].text
        print("Generated Manim code:")
        print("-" * 50)
        print(manim_code)
        print("-" * 50)
        
        # Try to execute it
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(manim_code)
            temp_file = f.name
        
        print(f"\nCode saved to: {temp_file}")
        print("To render, run: manim -qm -p " + temp_file)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_manim_generation())