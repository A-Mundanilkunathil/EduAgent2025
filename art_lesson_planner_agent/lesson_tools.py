from typing import Dict, Any, List
from crewai.tools import tool
from lesson_planner_agent import create_lesson_plan, LessonPlannerCore
from context_handler import LessonContext, ContextParser


@tool("Create a comprehensive lesson plan with integrated visualizations for educational content")
def create_lesson_plan_tool(user_request: str, **context) -> str:
    """Create a comprehensive lesson plan with integrated visualizations"""
    import asyncio
    
    async def _create():
        core = LessonPlannerCore()
        lesson_plan = await core.generate_lesson_plan(user_request, context)
        return lesson_plan.model_dump()
    
    result = asyncio.run(_create())
    return f"Lesson plan created successfully:\n{result['title']}\nDuration: {result['total_duration']} minutes\nSections: {len(result['sections'])}"


@tool("Generate specific requests for Manim agent based on lesson plan")
def generate_visualization_requests_tool(lesson_plan_json: str) -> str:
    """Generate Manim agent requests for all visualizations in a lesson plan"""
    import json
    
    lesson_data = json.loads(lesson_plan_json)
    core = LessonPlannerCore()
    
    # Convert back to LessonPlan object
    from lesson_planner_agent import LessonPlan
    lesson_plan = LessonPlan(**lesson_data)
    
    requests = core.generate_manim_requests(lesson_plan)
    return f"Generated {len(requests)} visualization requests for Manim agent"


@tool("Format lesson plan in markdown or JSON format")
def format_lesson_plan_tool(lesson_plan_json: str, format_type: str = "markdown") -> str:
    """Format lesson plan in different output formats"""
    import json
    from context_handler import LessonFormatter
    
    lesson_data = json.loads(lesson_plan_json)
    
    if format_type.lower() == "markdown":
        return LessonFormatter.to_markdown(lesson_data)
    elif format_type.lower() == "json":
        return LessonFormatter.to_json(lesson_data)
    else:
        return f"Unsupported format: {format_type}"


def create_lesson_tools() -> List:
    """Create CrewAI tools for lesson planning"""
    
    tools = [
        create_lesson_plan_tool,
        generate_visualization_requests_tool,
        format_lesson_plan_tool
    ]
    
    return tools