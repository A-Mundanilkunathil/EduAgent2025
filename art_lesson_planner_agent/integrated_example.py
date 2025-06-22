import asyncio
import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import manim_agent
sys.path.append(str(Path(__file__).parent.parent))

# Import our agents
from lesson_planner_agent import LessonPlannerAgent, create_lesson_plan, LessonPlannerCore
from matt_manim_agent.manim_agent import ManimAgent, create_animation

# Import CrewAI components
from crewai import Crew, Task

load_dotenv()


async def integrated_lesson_creation():
    """Example 1: Integrated lesson creation with automatic animation generation"""
    print("\n=== Integrated Lesson Creation ===")
    
    # Step 1: Create lesson plan
    print("1. Creating lesson plan...")
    lesson_plan = await create_lesson_plan(
        "Derivatives as rates of change",
        subject="Calculus",
        audience="College Freshmen",
        duration=45,
        complexity="intermediate"
    )
    
    print(f"   ✓ Lesson: {lesson_plan.title}")
    print(f"   ✓ Sections: {len(lesson_plan.sections)}")
    
    # Step 2: Generate Manim requests from lesson plan
    print("\n2. Analyzing lesson for visualization opportunities...")
    core = LessonPlannerCore()
    manim_requests = core.generate_manim_requests(lesson_plan)
    
    print(f"   ✓ Visualization requests: {len(manim_requests)}")
    
    # Step 3: Create animations for each visualization request
    print("\n3. Creating animations...")
    animations = []
    
    for i, request in enumerate(manim_requests):
        print(f"   Creating animation {i+1}/{len(manim_requests)}: {request['manim_context']['concept']}")
        
        # Create animation using Manim agent
        animation = await create_animation(
            concept=request['manim_context']['concept'],
            script_context=request['manim_context']['script_context'],
            duration=request['manim_context']['duration'],
            complexity=request['manim_context']['complexity']
        )
        
        animations.append({
            'section_index': request['section_index'],
            'section_title': request['section_title'],
            'animation': animation
        })
        
        if animation.success:
            print(f"     ✓ Animation created: {animation.video_path}")
        else:
            print(f"     ✗ Animation failed: {animation.error}")
    
    # Step 4: Generate final integrated lesson
    print("\n4. Generating integrated lesson...")
    integrated_lesson = generate_integrated_lesson(lesson_plan, animations)
    
    print(f"   ✓ Integrated lesson created with {len(animations)} animations")
    
    return integrated_lesson


async def crew_based_integration():
    """Example 2: CrewAI-based integration with multiple agents"""
    print("\n=== CrewAI-Based Integration ===")
    
    # Create agents
    lesson_planner = LessonPlannerAgent(
        role="Educational Content Planner",
        goal="Create comprehensive lesson plans with visualization placeholders",
        verbose=True
    )
    
    manim_specialist = ManimAgent(
        role="Mathematical Animation Specialist", 
        goal="Create high-quality educational animations",
        verbose=True
    )
    
    # Create tasks
    planning_task = Task(
        description="Create a lesson plan on Fourier series with specific visualization requirements",
        agent=lesson_planner,
        expected_output="Lesson plan with detailed visualization specifications"
    )
    
    animation_task = Task(
        description="Create animations based on the lesson plan's visualization requirements",
        agent=manim_specialist,
        expected_output="Collection of educational animations",
        context=[]  # Will be populated by previous task
    )
    
    # Create crew
    crew = Crew(
        agents=[lesson_planner, manim_specialist],
        tasks=[planning_task, animation_task],
        verbose=True
    )
    
    # Execute crew
    print("Executing crew...")
    result = await crew.kickoff()
    
    print(f"Crew execution completed!")
    return result


def generate_integrated_lesson(lesson_plan, animations):
    """Generate a final integrated lesson with embedded animation references"""
    
    integrated_content = {
        "title": lesson_plan.title,
        "subject": lesson_plan.subject,
        "target_audience": lesson_plan.target_audience,
        "total_duration": lesson_plan.total_duration,
        "prerequisites": lesson_plan.prerequisites,
        "learning_objectives": lesson_plan.learning_objectives,
        "sections": [],
        "assessment_questions": lesson_plan.assessment_questions,
        "resources": lesson_plan.resources,
        "animations": []
    }
    
    # Process each section and integrate animations
    for i, section in enumerate(lesson_plan.sections):
        section_data = {
            "title": section.title,
            "content": section.content,
            "duration_estimate": section.duration_estimate,
            "complexity": section.complexity,
            "animation": None
        }
        
        # Find matching animation for this section
        for anim_data in animations:
            if anim_data['section_index'] == i and anim_data['animation'].success:
                section_data["animation"] = {
                    "video_path": anim_data['animation'].video_path,
                    "concept": anim_data['animation'].concept,
                    "duration": anim_data['animation'].duration,
                    "visual_elements": anim_data['animation'].visual_elements
                }
                integrated_content["animations"].append(anim_data['animation'])
                break
        
        integrated_content["sections"].append(section_data)
    
    return integrated_content


async def save_integrated_lesson(lesson_data, filename="integrated_lesson.json"):
    """Save the integrated lesson to a file"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / filename
    
    with open(output_path, 'w') as f:
        json.dump(lesson_data, f, indent=2, default=str)
    
    print(f"Integrated lesson saved to: {output_path}")
    return output_path


async def generate_markdown_lesson(lesson_data, filename="integrated_lesson.md"):
    """Generate a markdown version of the integrated lesson"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / filename
    
    with open(output_path, 'w') as f:
        f.write(f"# {lesson_data['title']}\n\n")
        f.write(f"**Subject:** {lesson_data['subject']}\n")
        f.write(f"**Audience:** {lesson_data['target_audience']}\n")
        f.write(f"**Duration:** {lesson_data['total_duration']} minutes\n\n")
        
        f.write("## Learning Objectives\n")
        for obj in lesson_data['learning_objectives']:
            f.write(f"- {obj}\n")
        f.write("\n")
        
        f.write("## Prerequisites\n")
        for prereq in lesson_data['prerequisites']:
            f.write(f"- {prereq}\n")
        f.write("\n")
        
        f.write("## Lesson Content\n\n")
        
        for i, section in enumerate(lesson_data['sections'], 1):
            f.write(f"### {i}. {section['title']}\n\n")
            f.write(f"{section['content']}\n\n")
            
            if section['animation']:
                f.write(f"**📹 Animation:** {section['animation']['concept']}\n")
                f.write(f"**Duration:** {section['animation']['duration']:.1f} seconds\n")
                f.write(f"**File:** {section['animation']['video_path']}\n\n")
            
            f.write(f"**Estimated Time:** {section['duration_estimate']} minutes\n\n")
        
        f.write("## Assessment Questions\n")
        for question in lesson_data['assessment_questions']:
            f.write(f"- {question}\n")
        f.write("\n")
        
        f.write("## Additional Resources\n")
        for resource in lesson_data['resources']:
            f.write(f"- {resource}\n")
        f.write("\n")
        
        f.write("## Animations Summary\n")
        f.write(f"Total animations created: {len(lesson_data['animations'])}\n")
        for anim in lesson_data['animations']:
            f.write(f"- {anim.concept}: {anim.video_path}\n")
    
    print(f"Markdown lesson saved to: {output_path}")
    return output_path


async def main():
    """Run the integrated examples"""
    
    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Please set ANTHROPIC_API_KEY in .env file")
        return
    
    try:
        # Example 1: Direct integration
        print("Running Example 1: Direct Integration")
        integrated_lesson = await integrated_lesson_creation()
        
        # Save results
        await save_integrated_lesson(integrated_lesson)
        await generate_markdown_lesson(integrated_lesson)
        
        # Example 2: CrewAI integration (commented out for now as it requires more setup)
        # print("\nRunning Example 2: CrewAI Integration")
        # crew_result = await crew_based_integration()
        # print(f"Crew result: {crew_result}")
        
    except Exception as e:
        print(f"Error running integrated examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 