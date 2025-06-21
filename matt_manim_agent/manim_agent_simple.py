import os
import asyncio
import tempfile
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

from pydantic import BaseModel, Field
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()


class ManimOutput(BaseModel):
    """Structured output from Manim Agent"""
    success: bool = Field(description="Whether the animation was successfully created")
    video_path: Optional[str] = Field(default=None, description="Path to the generated MP4 file")
    duration: Optional[float] = Field(default=None, description="Duration of the video in seconds")
    concept: str = Field(description="Mathematical concept being visualized")
    manim_code: Optional[str] = Field(default=None, description="Generated Manim code")
    sync_points: List[Dict[str, Any]] = Field(default_factory=list, description="Synchronization points for other agents")
    visual_elements: List[str] = Field(default_factory=list, description="List of visual elements in the animation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class SimpleManimAgent:
    """Simplified Manim Agent without CrewAI inheritance issues"""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.system_prompt = """You are an expert Manim developer creating educational animations.

MANIM QUICK REFERENCE:
- Scene class: All animations inherit from Scene
- self.play(): Main animation method
- Create, Write, FadeIn, FadeOut: Basic animations
- Transform, ReplacementTransform: Morphing animations
- MathTex, Tex: LaTeX rendering
- NumberPlane, Axes: Coordinate systems
- Circle, Square, Rectangle, Line: Basic shapes
- VGroup: Group objects together
- self.wait(): Pause between animations

STYLE GUIDELINES:
- Use smooth transitions (run_time=1-2 seconds typically)
- Layer complexity gradually
- Use color to highlight important concepts
- Include helpful annotations and labels
- Follow 3Blue1Brown aesthetic principles

Generate clean, well-commented Manim code that renders successfully."""

    async def generate_manim_code(self, concept: str, context: Dict[str, Any] = None) -> str:
        """Generate Manim code for a concept"""
        
        # Build prompt
        prompt = f"Create a Manim animation to visualize: {concept}"
        
        if context:
            if "script_context" in context:
                prompt += f"\n\nScript context: {context['script_context']}"
            if "duration" in context:
                prompt += f"\n\nTarget duration: {context['duration']} seconds"
            if "style_direction" in context:
                prompt += f"\n\nStyle: {json.dumps(context['style_direction'])}"
        
        prompt += "\n\nReturn the complete Python code including 'from manim import *' at the top."
        
        # Generate code
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        
        code = response.content[0].text
        
        # Clean up code
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
        
        return code.strip()

    async def render_video(self, manim_code: str, output_name: str) -> Dict[str, Any]:
        """Render Manim code to video"""
        
        # Create output directory
        output_dir = Path("animations")
        output_dir.mkdir(exist_ok=True)
        
        # Write code to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(manim_code)
            temp_file = f.name
        
        try:
            # Extract scene name
            scene_name = None
            for line in manim_code.split('\n'):
                if 'class' in line and '(Scene)' in line:
                    scene_name = line.split('class')[1].split('(')[0].strip()
                    break
            
            if not scene_name:
                raise ValueError("No Scene class found")
            
            # Run Manim
            cmd = [
                "manim", "-qm",  # medium quality
                "--output_file", f"{output_name}.mp4",
                "--media_dir", str(output_dir),
                temp_file, scene_name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
            return {
                "success": True,
                "video_path": str(output_dir / f"{output_name}.mp4"),
                "duration": 10.0  # Estimate
            }
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    async def create_animation(self, concept: str, **context) -> ManimOutput:
        """Create animation for a concept"""
        
        try:
            # Generate code
            manim_code = await self.generate_manim_code(concept, context)
            
            # Render video
            safe_name = concept.lower().replace(" ", "_")[:30]
            render_result = await self.render_video(manim_code, safe_name)
            
            if render_result["success"]:
                return ManimOutput(
                    success=True,
                    video_path=render_result["video_path"],
                    duration=render_result.get("duration"),
                    concept=concept,
                    manim_code=manim_code,
                    metadata={"render_time": render_result.get("duration", 0)}
                )
            else:
                return ManimOutput(
                    success=False,
                    concept=concept,
                    error=render_result["error"],
                    manim_code=manim_code
                )
                
        except Exception as e:
            return ManimOutput(
                success=False,
                concept=concept,
                error=str(e),
                metadata={"exception_type": type(e).__name__}
            )


# Test function
async def test():
    agent = SimpleManimAgent()
    result = await agent.create_animation(
        "derivatives as slopes of tangent lines",
        duration=10.0
    )
    print(f"Success: {result.success}")
    print(f"Video: {result.video_path}")
    print(f"Error: {result.error}")
    if result.manim_code:
        print(f"\nGenerated code:\n{result.manim_code[:200]}...")


if __name__ == "__main__":
    asyncio.run(test())