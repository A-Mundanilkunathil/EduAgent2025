import asyncio
import os
from crewai import Crew, Task
from dotenv import load_dotenv

from lesson_planner_agent import LessonPlannerAgent, create_lesson_plan, LessonPlannerCore
from lesson_tools import create_lesson_tools
from context_handler import LessonContext, ContextParser

load_dotenv()


async def example_standalone_simple():
    """Example 1: Simple standalone usage"""
    print("\n=== Example 1: Simple Standalone Usage ===")
    
    # Create lesson plan with minimal context
    result = await create_lesson_plan("Linear regression creates a line of best fit through all data points")
    
    print(f"Title: {result.title}")
    print(f"Duration: {result.total_duration} minutes")
    print(f"Sections: {len(result.sections)}")
    print(f"Learning objectives: {result.learning_objectives}")


async def example_standalone_with_context():
    """Example 2: Standalone with rich context"""
    print("\n=== Example 2: Standalone with Context ===")
    
    # Create lesson plan with additional context
    result = await create_lesson_plan(
        "Derivatives as rates of change",
        subject="Calculus",
        audience="College Freshmen",
        duration=45,
        complexity="intermediate"
    )
    
    print(f"Title: {result.title}")
    print(f"Subject: {result.subject}")
    print(f"Audience: {result.target_audience}")
    print(f"Prerequisites: {result.prerequisites}")


async def example_crewai_integration():
    """Example 3: Full CrewAI integration"""
    print("\n=== Example 3: CrewAI Integration ===")
    
    # Create agent
    lesson_agent = LessonPlannerAgent(
        role="Educational Content Creator",
        goal="Create engaging lesson plans with integrated visualizations",
        verbose=True
    )
    
    # Create task
    task = Task(
        description="Create a lesson plan on the Pythagorean theorem with visualizations",
        agent=lesson_agent,
        expected_output="A comprehensive lesson plan with visualization placeholders"
    )
    
    # Execute task
    result = await lesson_agent.execute(task)
    
    print(f"Title: {result.title}")
    print(f"Sections: {len(result.sections)}")
    for i, section in enumerate(result.sections):
        print(f"  Section {i+1}: {section.title}")
        if section.visualization_concept:
            print(f"    Visualization: {section.visualization_concept}")


async def example_manim_integration():
    """Example 4: Integration with Manim agent"""
    print("\n=== Example 4: Manim Integration ===")
    
    # Create lesson plan
    result = await create_lesson_plan(
        "Fourier series and signal decomposition",
        subject="Advanced Mathematics",
        audience="Engineering Students",
        duration=60,
        complexity="advanced"
    )
    
    # Generate Manim requests
    core = LessonPlannerCore()
    manim_requests = core.generate_manim_requests(result)
    
    print(f"Lesson: {result.title}")
    print(f"Manim requests generated: {len(manim_requests)}")
    
    for req in manim_requests:
        print(f"  Section {req['section_index']}: {req['manim_context']['concept']}")
        print(f"    Duration: {req['manim_context']['duration']} seconds")
        print(f"    Context: {req['manim_context']['script_context'][:100]}...")


def example_crew_setup():
    """Example 5: Complete Crew setup"""
    print("\n=== Example 5: Crew Setup ===")
    
    # Create agents
    lesson_agent = LessonPlannerAgent(
        role="Lesson Planner",
        goal="Create comprehensive educational content",
        tools=create_lesson_tools()
    )
    
    # Create tasks
    task1 = Task(
        description="Create lesson plan on quadratic equations",
        agent=lesson_agent,
        expected_output="Lesson plan with visualization placeholders"
    )
    
    task2 = Task(
        description="Create lesson plan on complex numbers",
        agent=lesson_agent,
        expected_output="Lesson plan with visualization placeholders"
    )
    
    # Create crew
    crew = Crew(
        agents=[lesson_agent],
        tasks=[task1, task2],
        verbose=True
    )
    
    print("Crew setup complete!")
    print(f"Agents: {[agent.role for agent in crew.agents]}")
    print(f"Tasks: {[task.description for task in crew.tasks]}")


async def example_formatted_output():
    """Example 6: Formatted lesson plan output"""
    print("\n=== Example 6: Formatted Output ===")
    
    # Create lesson plan
    result = await create_lesson_plan(
        "Neural networks and backpropagation",
        subject="Machine Learning",
        audience="Graduate Students",
        duration=90,
        complexity="advanced"
    )
    
    # Convert to markdown
    from context_handler import LessonFormatter
    markdown_output = LessonFormatter.to_markdown(result.model_dump())
    
    print("Markdown output:")
    print("=" * 50)
    print(markdown_output[:500] + "...")


async def main():
    """Run all examples"""
    
    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Please set ANTHROPIC_API_KEY in .env file")
        print("Copy .env.example to .env and add your API key")
        return
    
    # Run examples
    try:
        await example_standalone_simple()
        await example_standalone_with_context()
        await example_crewai_integration()
        await example_manim_integration()
        example_crew_setup()
        await example_formatted_output()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())