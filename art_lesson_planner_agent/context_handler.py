from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class LessonRequest(BaseModel):
    """User request for lesson planning"""
    topic: str = Field(description="Main topic or concept to teach")
    subject: str = Field(default="Mathematics", description="Subject area")
    audience: str = Field(default="High School", description="Target audience/grade level")
    duration: Optional[float] = Field(default=None, description="Target lesson duration in minutes")
    complexity: str = Field(default="intermediate", description="Complexity level")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisite knowledge")
    learning_goals: List[str] = Field(default_factory=list, description="Specific learning goals")
    include_visualizations: bool = Field(default=True, description="Include visualization placeholders")
    style_preference: str = Field(default="educational", description="Teaching style preference")
    
    @validator('complexity')
    def validate_complexity(cls, v):
        allowed = ["beginner", "intermediate", "advanced", "expert"]
        if v not in allowed:
            raise ValueError(f"Complexity must be one of {allowed}")
        return v


class VisualizationRequest(BaseModel):
    """Request for specific visualization"""
    concept: str = Field(description="Mathematical concept to visualize")
    context: str = Field(description="Educational context for the visualization")
    duration: float = Field(description="Duration in seconds")
    complexity: str = Field(default="intermediate", description="Complexity level")
    section_index: int = Field(description="Which section this visualization belongs to")
    section_title: str = Field(description="Title of the section")


class LessonContext(BaseModel):
    """Complete context for lesson planning task"""
    
    # Core request
    request: LessonRequest
    
    # Generated content
    lesson_plan: Optional[Dict[str, Any]] = None
    visualization_requests: List[VisualizationRequest] = Field(default_factory=list)
    
    # Integration metadata
    manim_agent_available: bool = Field(default=True, description="Whether Manim agent is available")
    collaboration_mode: str = Field(default="integrated", description="How to work with other agents")
    
    # Metadata
    request_id: Optional[str] = Field(default=None, description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def to_agent_context(self) -> Dict[str, Any]:
        """Convert to format expected by LessonPlannerAgent"""
        context = {
            "topic": self.request.topic,
            "subject": self.request.subject,
            "audience": self.request.audience,
            "complexity": self.request.complexity
        }
        
        if self.request.duration:
            context["duration"] = self.request.duration
        
        if self.request.prerequisites:
            context["prerequisites"] = self.request.prerequisites
        
        if self.request.learning_goals:
            context["learning_goals"] = self.request.learning_goals
        
        return context


class ContextParser:
    """Parses various context formats into LessonContext"""
    
    @staticmethod
    def parse_raw_context(raw_context: Dict[str, Any]) -> LessonContext:
        """Parse raw context dictionary into structured format"""
        
        # Handle simple case
        if isinstance(raw_context, str):
            request = LessonRequest(topic=raw_context)
            return LessonContext(request=request)
        
        # Extract core topic
        topic = raw_context.get("topic", raw_context.get("concept", raw_context.get("description", "")))
        
        # Build request
        request_data = {"topic": topic}
        
        # Add optional fields
        for field in ["subject", "audience", "duration", "complexity", "prerequisites", "learning_goals"]:
            if field in raw_context:
                request_data[field] = raw_context[field]
        
        request = LessonRequest(**request_data)
        
        # Build context
        context = LessonContext(request=request)
        
        # Add integration settings
        if "manim_agent_available" in raw_context:
            context.manim_agent_available = raw_context["manim_agent_available"]
        
        if "collaboration_mode" in raw_context:
            context.collaboration_mode = raw_context["collaboration_mode"]
        
        return context
    
    @staticmethod
    def merge_contexts(base: LessonContext, *updates: Dict[str, Any]) -> LessonContext:
        """Merge multiple context updates into base context"""
        
        merged = base.model_copy()
        
        for update in updates:
            if not update:
                continue
            
            # Update request fields
            for field in ["topic", "subject", "audience", "duration", "complexity"]:
                if field in update:
                    setattr(merged.request, field, update[field])
            
            # Merge lists
            for field in ["prerequisites", "learning_goals"]:
                if field in update:
                    current = getattr(merged.request, field)
                    current.extend(update[field])
                    setattr(merged.request, field, list(set(current)))  # Remove duplicates
        
        return merged


class LessonFormatter:
    """Formats lesson plans for different outputs"""
    
    @staticmethod
    def to_markdown(lesson_plan: Dict[str, Any]) -> str:
        """Convert lesson plan to markdown format"""
        md_parts = []
        
        # Title
        md_parts.append(f"# {lesson_plan.get('title', 'Lesson Plan')}")
        md_parts.append("")
        
        # Metadata
        md_parts.append(f"**Subject:** {lesson_plan.get('subject', 'Mathematics')}")
        md_parts.append(f"**Audience:** {lesson_plan.get('target_audience', 'Students')}")
        md_parts.append(f"**Duration:** {lesson_plan.get('total_duration', 0)} minutes")
        md_parts.append("")
        
        # Learning objectives
        if lesson_plan.get('learning_objectives'):
            md_parts.append("## Learning Objectives")
            for obj in lesson_plan['learning_objectives']:
                md_parts.append(f"- {obj}")
            md_parts.append("")
        
        # Prerequisites
        if lesson_plan.get('prerequisites'):
            md_parts.append("## Prerequisites")
            for prereq in lesson_plan['prerequisites']:
                md_parts.append(f"- {prereq}")
            md_parts.append("")
        
        # Sections
        if lesson_plan.get('sections'):
            md_parts.append("## Lesson Content")
            for i, section in enumerate(lesson_plan['sections']):
                md_parts.append(f"### {section.get('title', f'Section {i+1}')}")
                md_parts.append("")
                md_parts.append(section.get('content', ''))
                md_parts.append("")
        
        # Assessment
        if lesson_plan.get('assessment_questions'):
            md_parts.append("## Assessment Questions")
            for i, question in enumerate(lesson_plan['assessment_questions']):
                md_parts.append(f"{i+1}. {question}")
            md_parts.append("")
        
        # Resources
        if lesson_plan.get('resources'):
            md_parts.append("## Additional Resources")
            for resource in lesson_plan['resources']:
                md_parts.append(f"- {resource}")
            md_parts.append("")
        
        return "\n".join(md_parts)
    
    @staticmethod
    def to_json(lesson_plan: Dict[str, Any]) -> str:
        """Convert lesson plan to JSON format"""
        import json
        return json.dumps(lesson_plan, indent=2, default=str)