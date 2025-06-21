from typing import Dict, Any, Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import asyncio
import json

from manim_agent import ManimAgent, ManimOutput


class ManimToolInput(BaseModel):
    """Input schema for Manim animation tool"""
    concept: str = Field(description="Mathematical concept to visualize")
    script_context: Optional[str] = Field(default=None, description="Educational narrative context")
    duration: Optional[float] = Field(default=None, description="Target duration in seconds")
    style_direction: Optional[Dict[str, Any]] = Field(default=None, description="Visual style preferences")
    sync_points: Optional[list] = Field(default=None, description="Synchronization points for multi-agent coordination")


class ManimAnimationTool(BaseTool):
    """
    CrewAI tool for generating Manim animations.
    Wraps the ManimAgent for use in CrewAI workflows.
    """
    
    name: str = "Create Manim Animation"
    description: str = """Creates educational math animations using Manim.
    
    Inputs:
    - concept: The mathematical concept to visualize (required)
    - script_context: Educational narrative or explanation text (optional)
    - duration: Target video duration in seconds (optional)
    - style_direction: Visual style preferences like color scheme, pace (optional)
    - sync_points: Time-based synchronization points for coordination (optional)
    
    Returns structured output with video path, duration, and metadata.
    """
    
    args_schema: Type[BaseModel] = ManimToolInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use the core directly to avoid CrewAI agent issues
        from manim_agent import ManimAgentCore
        self._core = ManimAgentCore()
    
    def _run(
        self,
        concept: str,
        script_context: Optional[str] = None,
        duration: Optional[float] = None,
        style_direction: Optional[Dict[str, Any]] = None,
        sync_points: Optional[list] = None
    ) -> str:
        """
        Synchronous wrapper for the async Manim agent execution.
        Returns JSON string for CrewAI compatibility.
        """
        # Build context
        context = {"concept": concept}
        
        if script_context:
            context["script_context"] = script_context
        if duration:
            context["duration"] = duration
        if style_direction:
            context["style_direction"] = style_direction
        if sync_points:
            context["sync_points"] = sync_points
        
        # Run async execution in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result: ManimOutput = loop.run_until_complete(
                self._core.process_animation_task(context)
            )
            
            # Convert to dict and return as JSON string
            return json.dumps(result.model_dump(), indent=2)
        finally:
            loop.close()


class ManimDebugTool(BaseTool):
    """
    Tool for debugging and fixing Manim code.
    Useful when animations fail to render.
    """
    
    name: str = "Debug Manim Code"
    description: str = """Debugs and fixes Manim animation code that failed to render.
    
    Input:
    - error_message: The error message from the failed render
    - manim_code: The Manim code that failed
    
    Returns fixed Manim code or explanation of the issue.
    """
    
    def _run(self, error_message: str, manim_code: str) -> str:
        """Debug and fix Manim code"""
        # This would integrate with Claude to fix code
        # For now, return a placeholder
        return f"Debugging Manim code with error: {error_message}"


# Factory function for creating tools
def create_manim_tools() -> list:
    """Create all Manim-related tools for CrewAI"""
    return [
        ManimAnimationTool(),
        ManimDebugTool()
    ]