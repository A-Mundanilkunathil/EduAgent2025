import asyncio
import os
from dotenv import load_dotenv

from lesson_planner_agent import create_lesson_plan, LessonPlannerCore
from context_handler import LessonFormatter

load_dotenv()


async def demo_linear_regression():
    """Demo: Create a lesson plan on linear regression"""
    print("🎓 Creating Lesson Plan: Linear Regression")
    print("=" * 50)
    
    # Create lesson plan
    result = await create_lesson_plan(
        "Linear regression creates a line of best fit through all data points",
        subject="Statistics",
        audience="High School",
        duration=30,
        complexity="intermediate"
    )
    
    print(f"📚 Lesson: {result.title}")
    print(f"⏱️  Duration: {result.total_duration} minutes")
    print(f"📖 Sections: {len(result.sections)}")
    print()
    
    # Show sections with visualizations
    for i, section in enumerate(result.sections):
        print(f"📝 Section {i+1}: {section.title}")
        print(f"   Content: {section.content[:100]}...")
        if section.visualization_concept:
            print(f"   🎬 Visualization: {section.visualization_concept}")
        print()
    
    # Generate Manim requests
    core = LessonPlannerCore()
    manim_requests = core.generate_manim_requests(result)
    
    print(f"�� Generated {len(manim_requests)} visualization requests:")
    for req in manim_requests:
        print(f"   - {req['manim_context']['concept']} ({req['manim_context']['duration']}s)")
    
    # Show formatted output
    print("\n📄 Formatted Lesson Plan:")
    print("-" * 30)
    markdown = LessonFormatter.to_markdown(result.model_dump())
    print(markdown[:800] + "...")


async def demo_calculus():
    """Demo: Create a lesson plan on calculus"""
    print("\n🎓 Creating Lesson Plan: Calculus Derivatives")
    print("=" * 50)
    
    result = await create_lesson_plan(
        "Derivatives as rates of change and slopes of tangent lines",
        subject="Calculus",
        audience="College Freshmen",
        duration=45,
        complexity="intermediate"
    )
    
    print(f"📚 Lesson: {result.title}")
    print(f"🎯 Learning Objectives:")
    for obj in result.learning_objectives:
        print(f"   • {obj}")
    
    print(f"\n📋 Prerequisites:")
    for prereq in result.prerequisites:
        print(f"   • {prereq}")
    
    print(f"\n❓ Assessment Questions:")
    for i, question in enumerate(result.assessment_questions[:3]):
        print(f"   {i+1}. {question}")


async def demo_integration():
    """Demo: Show integration with Manim agent"""
    print("\n🔗 Integration Demo: Lesson + Manim")
    print("=" * 50)
    
    # Create lesson plan
    lesson = await create_lesson_plan(
        "Fourier series and signal decomposition",
        subject="Advanced Mathematics",
        audience="Engineering Students",
        duration=60,
        complexity="advanced"
    )
    
    # Generate Manim requests
    core = LessonPlannerCore()
    requests = core.generate_manim_requests(lesson)
    
    print(f"📚 Lesson: {lesson.title}")
    print(f"🎬 Visualization Requests: {len(requests)}")
    
    # Simulate sending to Manim agent
    for i, req in enumerate(requests):
        print(f"\n🎬 Request {i+1}:")
        print(f"   Concept: {req['manim_context']['concept']}")
        print(f"   Duration: {req['manim_context']['duration']} seconds")
        print(f"   Context: {req['manim_context']['script_context'][:80]}...")
        print(f"   Section: {req['section_title']}")
        
        # Simulate Manim response
        print(f"   ✅ Would generate: {req['manim_context']['concept']}_animation.mp4")


async def main():
    """Run all demos"""
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: Please set ANTHROPIC_API_KEY in .env file")
        return
    
    try:
        await demo_linear_regression()
        await demo_calculus()
        await demo_integration()
        
        print("\n🎉 Demo completed successfully!")
        print("The lesson planner agent is ready to create educational content with integrated visualizations!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())