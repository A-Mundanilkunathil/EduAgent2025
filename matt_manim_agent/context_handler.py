from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ScriptContext(BaseModel):
    """Context from Script Agent"""
    narrative: str = Field(description="Educational narrative text")
    key_points: List[str] = Field(default_factory=list, description="Key educational points")
    emphasis_timings: Dict[float, str] = Field(default_factory=dict, description="When to emphasize concepts")
    tone: str = Field(default="educational", description="Tone of the script")


class DirectorContext(BaseModel):
    """Context from Director Agent"""
    visual_style: str = Field(default="3blue1brown", description="Visual style preference")
    color_scheme: Dict[str, str] = Field(default_factory=dict, description="Color mappings")
    pacing: str = Field(default="moderate", description="Animation pacing")
    transitions: List[str] = Field(default_factory=list, description="Preferred transition types")
    camera_movements: Optional[List[Dict[str, Any]]] = Field(default=None, description="Camera positioning")


class TimingContext(BaseModel):
    """Timing and synchronization context"""
    total_duration: float = Field(description="Total animation duration")
    start_time: float = Field(default=0.0, description="When this animation starts in larger video")
    segment_durations: Dict[str, float] = Field(default_factory=dict, description="Duration for each segment")
    sync_with: Optional[str] = Field(default=None, description="ID of element to sync with")


class ManimTaskContext(BaseModel):
    """Complete context for Manim animation task"""
    
    # Core concept
    concept: str = Field(description="Mathematical concept to visualize")
    complexity_level: str = Field(default="intermediate", description="Complexity level")
    
    # Multi-agent contexts
    script_context: Optional[ScriptContext] = None
    director_context: Optional[DirectorContext] = None
    timing_context: Optional[TimingContext] = None
    
    # Additional requirements
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisite concepts")
    learning_objectives: List[str] = Field(default_factory=list, description="What students should learn")
    interactive_elements: bool = Field(default=False, description="Include interactive elements")
    
    # Metadata
    request_id: Optional[str] = Field(default=None, description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @validator('complexity_level')
    def validate_complexity(cls, v):
        allowed = ["beginner", "intermediate", "advanced", "expert"]
        if v not in allowed:
            raise ValueError(f"Complexity must be one of {allowed}")
        return v
    
    def to_agent_context(self) -> Dict[str, Any]:
        """Convert to format expected by ManimAgent"""
        context = {
            "concept": self.concept,
            "complexity": self.complexity_level
        }
        
        # Add script context
        if self.script_context:
            context["script_context"] = self.script_context.narrative
            if self.script_context.emphasis_timings:
                context["emphasis_points"] = [
                    {"time": t, "text": text}
                    for t, text in self.script_context.emphasis_timings.items()
                ]
        
        # Add director context
        if self.director_context:
            context["style_direction"] = {
                "visual_style": self.director_context.visual_style,
                "color_scheme": self.director_context.color_scheme,
                "pace": self.director_context.pacing
            }
        
        # Add timing context
        if self.timing_context:
            context["duration"] = self.timing_context.total_duration
            context["start_time"] = self.timing_context.start_time
        
        # Add sync points from various sources
        sync_points = []
        if self.script_context and self.script_context.emphasis_timings:
            for time, emphasis in self.script_context.emphasis_timings.items():
                sync_points.append({
                    "time": time,
                    "emphasis": emphasis,
                    "source": "script"
                })
        
        if sync_points:
            context["sync_points"] = sync_points
        
        return context


class ContextParser:
    """Parses various context formats into ManimTaskContext"""
    
    @staticmethod
    def parse_raw_context(raw_context: Dict[str, Any]) -> ManimTaskContext:
        """Parse raw context dictionary into structured format"""
        
        # Handle simple case
        if isinstance(raw_context, str):
            return ManimTaskContext(concept=raw_context)
        
        # Extract core concept
        concept = raw_context.get("concept", raw_context.get("description", ""))
        
        # Build structured context
        task_context = ManimTaskContext(concept=concept)
        
        # Parse script context if present
        if "script_context" in raw_context or "narrative" in raw_context:
            script_data = raw_context.get("script_context", {})
            if isinstance(script_data, str):
                script_data = {"narrative": script_data}
            elif "narrative" in raw_context:
                script_data = {"narrative": raw_context["narrative"]}
            
            task_context.script_context = ScriptContext(**script_data)
        
        # Parse director context
        if any(key in raw_context for key in ["style_direction", "visual_style", "color_scheme"]):
            director_data = raw_context.get("style_direction", {})
            if "visual_style" in raw_context:
                director_data["visual_style"] = raw_context["visual_style"]
            if "color_scheme" in raw_context:
                director_data["color_scheme"] = raw_context["color_scheme"]
            
            task_context.director_context = DirectorContext(**director_data)
        
        # Parse timing context
        if any(key in raw_context for key in ["duration", "start_time", "total_duration"]):
            timing_data = {
                "total_duration": raw_context.get("duration", raw_context.get("total_duration", 10.0)),
                "start_time": raw_context.get("start_time", 0.0)
            }
            task_context.timing_context = TimingContext(**timing_data)
        
        # Add additional fields
        for field in ["complexity_level", "prerequisites", "learning_objectives"]:
            if field in raw_context:
                setattr(task_context, field, raw_context[field])
        
        return task_context
    
    @staticmethod
    def merge_contexts(base: ManimTaskContext, *updates: Dict[str, Any]) -> ManimTaskContext:
        """Merge multiple context updates into base context"""
        
        merged = base.model_copy()
        
        for update in updates:
            if not update:
                continue
                
            # Update simple fields
            for field in ["concept", "complexity_level"]:
                if field in update:
                    setattr(merged, field, update[field])
            
            # Merge lists
            for field in ["prerequisites", "learning_objectives"]:
                if field in update:
                    current = getattr(merged, field)
                    current.extend(update[field])
                    setattr(merged, field, list(set(current)))  # Remove duplicates
            
            # Update nested contexts
            if "script_context" in update:
                if merged.script_context:
                    # Merge existing
                    for key, value in update["script_context"].items():
                        setattr(merged.script_context, key, value)
                else:
                    merged.script_context = ScriptContext(**update["script_context"])
            
            if "director_context" in update:
                if merged.director_context:
                    for key, value in update["director_context"].items():
                        setattr(merged.director_context, key, value)
                else:
                    merged.director_context = DirectorContext(**update["director_context"])
        
        return merged