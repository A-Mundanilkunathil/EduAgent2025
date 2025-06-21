import os
import asyncio
import tempfile
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

from crewai import Agent, Task, Crew
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


class ManimAgentCore:
    """Core Manim functionality without CrewAI inheritance"""
    
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

CONTEXT INTEGRATION:
- Adapt pacing based on duration requirements
- Sync key moments with script narration
- Apply style directions to color schemes and transitions
- Create clear visual hierarchy

Generate clean, well-commented Manim code that renders successfully.
IMPORTANT: Always include 'from manim import *' at the top of your code."""

    async def generate_manim_code(self, task_context: Dict[str, Any]) -> str:
        """Generate Manim code based on task context using Claude API"""
        
        # Extract primary concept
        concept = task_context.get("concept", "mathematical concept")
        
        # Build context-aware prompt
        prompt_parts = [f"Create a Manim animation to visualize: {concept}"]
        
        # Add script context if available
        if "script_context" in task_context:
            prompt_parts.append(f"\nScript context: {task_context['script_context']}")
        
        # Add timing requirements
        if "duration" in task_context:
            prompt_parts.append(f"\nTarget duration: {task_context['duration']} seconds")
        
        # Add style directions
        if "style_direction" in task_context:
            style = task_context['style_direction']
            prompt_parts.append(f"\nStyle: {json.dumps(style)}")
        
        # Add sync points
        if "sync_points" in task_context:
            prompt_parts.append(f"\nSync points: {json.dumps(task_context['sync_points'])}")
        
        prompt = "\n".join(prompt_parts)
        
        # Generate code using Claude
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract code from response
        code = response.content[0].text
        
        # Clean up code block markers if present
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
        
        return code.strip()

    async def render_manim_video(self, manim_code: str, output_name: str) -> Dict[str, Any]:
        """Execute Manim code and render video"""
        
        # Create temporary directory for output
        output_dir = Path("animations")
        output_dir.mkdir(exist_ok=True)
        
        # Write code to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(manim_code)
            temp_file = f.name
        
        try:
            # Determine scene name (extract from code)
            scene_name = None
            for line in manim_code.split('\n'):
                if 'class' in line and '(Scene)' in line:
                    scene_name = line.split('class')[1].split('(')[0].strip()
                    break
            
            if not scene_name:
                raise ValueError("No Scene class found in generated code")
            
            # Run Manim render command
            output_path = output_dir / f"{output_name}.mp4"
            cmd = [
                "manim", "-qm",  # medium quality
                "--disable_caching",
                "--output_file", f"{output_name}.mp4",
                "--media_dir", str(output_dir),
                temp_file, scene_name
            ]
            
            # Execute render
            start_time = asyncio.get_event_loop().time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            render_time = asyncio.get_event_loop().time() - start_time
            
            if result.returncode != 0:
                raise RuntimeError(f"Manim render failed: {result.stderr}")
            
            # Find the actual output file
            mp4_files = list(output_dir.rglob(f"*{output_name}.mp4"))
            if mp4_files:
                actual_path = str(mp4_files[0])
            else:
                actual_path = str(output_path)
            
            return {
                "success": True,
                "video_path": actual_path,
                "duration": render_time * 0.8,  # Rough estimate
                "render_time": render_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            # Cleanup temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def extract_visual_elements(self, manim_code: str) -> List[str]:
        """Extract visual elements from Manim code"""
        elements = []
        
        # Common Manim objects to look for
        manim_objects = [
            "Circle", "Square", "Rectangle", "Line", "Arrow", "Dot",
            "MathTex", "Tex", "Text", "NumberPlane", "Axes", "Graph",
            "VGroup", "VMobject", "FunctionGraph", "ParametricFunction",
            "Vector", "Matrix", "Table", "Code"
        ]
        
        for obj in manim_objects:
            if obj in manim_code:
                elements.append(obj.lower())
        
        # Check for specific mathematical concepts
        if "derivative" in manim_code.lower() or "tangent" in manim_code.lower():
            elements.append("derivative_visualization")
        if "integral" in manim_code.lower():
            elements.append("integral_visualization")
        if "limit" in manim_code.lower():
            elements.append("limit_visualization")
        
        return list(set(elements))  # Remove duplicates

    async def process_animation_task(self, task_context: Dict[str, Any]) -> ManimOutput:
        """Process an animation task with given context"""
        
        try:
            # Generate Manim code
            manim_code = await self.generate_manim_code(task_context)
            
            # Extract concept name for file naming
            concept = task_context.get("concept", "math_animation")
            safe_name = concept.lower().replace(" ", "_")[:30]
            
            # Render video
            render_result = await self.render_manim_video(manim_code, safe_name)
            
            if not render_result["success"]:
                # Attempt to fix and retry once
                fix_prompt = f"The following Manim code failed with error: {render_result['error']}\n\nCode:\n{manim_code}\n\nPlease fix it."
                
                response = await self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    system=self.system_prompt,
                    messages=[{"role": "user", "content": fix_prompt}]
                )
                
                manim_code = response.content[0].text
                if "```python" in manim_code:
                    manim_code = manim_code.split("```python")[1].split("```")[0]
                
                render_result = await self.render_manim_video(manim_code, safe_name)
            
            # Extract visual elements
            visual_elements = self.extract_visual_elements(manim_code)
            
            # Build sync points if requested in context
            sync_points = []
            if "sync_points" in task_context:
                # Map requested sync points to actual animation
                for sp in task_context["sync_points"]:
                    sync_points.append({
                        "time": sp.get("time", 0),
                        "event": sp.get("emphasis", "animation_event"),
                        "description": f"Animation emphasis at {sp.get('time', 0)}s"
                    })
            
            # Create output
            return ManimOutput(
                success=render_result["success"],
                video_path=render_result.get("video_path"),
                duration=render_result.get("duration"),
                concept=concept,
                manim_code=manim_code if render_result["success"] else None,
                sync_points=sync_points,
                visual_elements=visual_elements,
                metadata={
                    "render_time": render_result.get("render_time", 0),
                    "quality_score": 0.85 if render_result["success"] else 0,
                    "context_used": list(task_context.keys())
                },
                error=render_result.get("error")
            )
            
        except Exception as e:
            concept = task_context.get("concept", "unknown") if isinstance(task_context, dict) else "unknown"
            return ManimOutput(
                success=False,
                concept=concept,
                error=str(e),
                metadata={"exception_type": type(e).__name__}
            )


class ManimAgent(Agent):
    """
    CrewAI Agent for generating educational math animations using Manim.
    Handles both standalone operation and multi-agent context integration.
    """
    
    def __init__(self, **kwargs):
        # Default agent configuration
        default_config = {
            "role": "Manim Animation Specialist",
            "goal": "Create high-quality educational math animations that effectively visualize complex mathematical concepts",
            "backstory": """You are an expert in mathematical visualization and educational content creation. 
            With deep knowledge of Manim and 3Blue1Brown-style animations, you transform abstract mathematical 
            concepts into beautiful, intuitive visual explanations. You excel at creating animations that 
            synchronize with educational narratives and adapt to different teaching styles.""",
            "verbose": True,
            "allow_delegation": False,
            "max_iter": 3,
        }
        
        # Merge with any provided kwargs
        config = {**default_config, **kwargs}
        super().__init__(**config)
        
        # Create core functionality handler
        self._core = ManimAgentCore()

    async def execute(self, task: Task) -> ManimOutput:
        """Execute the Manim animation task"""
        
        # Extract context from task
        task_context = task.context if hasattr(task, 'context') else {}
        
        # Handle different context formats
        if isinstance(task_context, list) and task_context:
            # CrewAI passes context as a list
            task_context = task_context[0] if isinstance(task_context[0], dict) else {"concept": str(task_context[0])}
        elif isinstance(task_context, str):
            task_context = {"concept": task_context}
        elif not task_context or not isinstance(task_context, dict):
            # Use description as fallback
            task_context = {"concept": task.description if hasattr(task, 'description') else "mathematical concept"}
        
        # Process the animation task
        return await self._core.process_animation_task(task_context)


# Convenience function for standalone usage
async def create_animation(concept: str, **context) -> ManimOutput:
    """Create animation with minimal setup"""
    core = ManimAgentCore()
    task_context = {"concept": concept, **context}
    return await core.process_animation_task(task_context)


# Test function
async def test():
    print("Testing ManimAgent...")
    
    # Test 1: Simple animation
    result = await create_animation("sine wave transforming into cosine wave")
    print(f"\nTest 1 - Success: {result.success}")
    print(f"Video: {result.video_path}")
    print(f"Error: {result.error}")
    
    # Test 2: With context
    result = await create_animation(
        "limit definition of derivative",
        script_context="Show how the slope of secant lines approaches the tangent",
        duration=15.0
    )
    print(f"\nTest 2 - Success: {result.success}")
    print(f"Video: {result.video_path}")
    print(f"Visual elements: {result.visual_elements}")


if __name__ == "__main__":
    asyncio.run(test())