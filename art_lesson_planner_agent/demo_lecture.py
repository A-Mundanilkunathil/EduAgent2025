import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import manim_agent
sys.path.append(str(Path(__file__).parent.parent))

# Import our agents
from lesson_planner_agent import create_lesson_plan, LessonPlannerCore
from matt_manim_agent.manim_agent import create_animation

load_dotenv()


async def create_demo_lecture():
    """Create a demo lecture with animations"""
    
    print("🎓 Creating Demo Lecture: Derivatives and Tangent Lines")
    print("=" * 60)
    
    # Step 1: Create lesson plan
    print("\n📝 Step 1: Creating lesson plan...")
    lesson_plan = await create_lesson_plan(
        "Derivatives and tangent lines - understanding rates of change",
        subject="Calculus",
        audience="High School Students",
        duration=45,
        complexity="intermediate"
    )
    
    print(f"   ✅ Lesson: {lesson_plan.title}")
    print(f"   ✅ Sections: {len(lesson_plan.sections)}")
    print(f"   ✅ Duration: {lesson_plan.total_duration} minutes")
    
    # Step 2: Generate animations
    print("\n🎬 Step 2: Creating animations...")
    core = LessonPlannerCore()
    manim_requests = core.generate_manim_requests(lesson_plan)
    
    animations = []
    if manim_requests:
        print(f"   🎯 Found {len(manim_requests)} visualization opportunities")
        
        for i, request in enumerate(manim_requests, 1):
            print(f"   🎬 Creating animation {i}: {request['manim_context']['concept']}")
            
            animation = await create_animation(
                concept=request['manim_context']['concept'],
                script_context=request['manim_context']['script_context'],
                duration=request['manim_context']['duration']
            )
            
            if animation.success:
                print(f"      ✅ Success: {animation.video_path}")
                animations.append({
                    'section_index': request['section_index'],
                    'animation': animation
                })
            else:
                print(f"      ❌ Failed: {animation.error}")
    else:
        print("   ⚠️  No visualization opportunities found")
    
    # Step 3: Generate comprehensive markdown
    print("\n📚 Step 3: Generating comprehensive lecture...")
    markdown_content = generate_comprehensive_markdown(lesson_plan, animations)
    
    # Step 4: Save the lecture
    output_dir = Path("lectures")
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "demo_lecture_derivatives.md"
    with open(output_path, 'w') as f:
        f.write(markdown_content)
    
    print(f"\n📁 Lecture saved to: {output_path}")
    
    # Step 5: Summary
    print("\n🎉 Demo Lecture Complete!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   - Title: {lesson_plan.title}")
    print(f"   - Sections: {len(lesson_plan.sections)}")
    print(f"   - Animations: {len(animations)}")
    print(f"   - Duration: {lesson_plan.total_duration} minutes")
    
    if animations:
        print(f"\n🎬 Animations created:")
        for i, anim_data in enumerate(animations, 1):
            anim = anim_data['animation']
            print(f"   {i}. {anim.concept} -> {anim.video_path}")
    
    return lesson_plan, animations


def generate_comprehensive_markdown(lesson_plan, animations):
    """Generate a comprehensive, well-formatted markdown lecture"""
    
    # Map animations to sections
    animation_map = {}
    for anim_data in animations:
        section_idx = anim_data['section_index']
        if section_idx not in animation_map:
            animation_map[section_idx] = []
        animation_map[section_idx].append(anim_data['animation'])
    
    markdown = f"""# {lesson_plan.title}

## 📋 Lecture Information

- **Subject:** {lesson_plan.subject}
- **Target Audience:** {lesson_plan.target_audience}
- **Total Duration:** {lesson_plan.total_duration} minutes
- **Animations:** {len(animations)} created
- **Generated:** {asyncio.get_event_loop().time()}

---

## 🎯 Learning Objectives

"""
    
    if lesson_plan.learning_objectives:
        for obj in lesson_plan.learning_objectives:
            markdown += f"- {obj}\n"
    else:
        markdown += "- Understand the fundamental concepts of derivatives\n"
        markdown += "- Learn how to calculate derivatives of basic functions\n"
        markdown += "- Visualize the relationship between functions and their derivatives\n"
        markdown += "- Apply derivatives to solve real-world problems\n"
    
    markdown += "\n## 📚 Prerequisites\n\n"
    
    if lesson_plan.prerequisites:
        for prereq in lesson_plan.prerequisites:
            markdown += f"- {prereq}\n"
    else:
        markdown += "- Basic understanding of functions and graphs\n"
        markdown += "- Familiarity with slope and linear equations\n"
        markdown += "- Knowledge of basic algebra\n"
    
    markdown += "\n## 📖 Lecture Content\n\n"
    
    # Process each section
    for i, section in enumerate(lesson_plan.sections):
        markdown += f"### Section {i+1}: {section.title}\n\n"
        markdown += f"**Duration:** {section.duration_estimate} minutes | **Complexity:** {section.complexity}\n\n"
        
        # Clean up section content
        content = section.content.strip()
        if content:
            # Remove any raw formatting and clean up
            content = content.replace('{visualization}', '📹 **Visualization Point**')
            content = content.replace('{animation}', '🎬 **Animation Point**')
            markdown += f"{content}\n\n"
        else:
            markdown += f"*Content for {section.title}*\n\n"
        
        # Add animations for this section
        if i in animation_map:
            markdown += "**📹 Visualizations:**\n"
            for anim in animation_map[i]:
                markdown += f"- **{anim.concept}**: `{anim.video_path}`\n"
                markdown += f"  - Duration: {anim.duration:.1f} seconds\n"
                if anim.visual_elements:
                    markdown += f"  - Elements: {', '.join(anim.visual_elements)}\n"
            markdown += "\n"
        
        markdown += "---\n\n"
    
    # Assessment
    markdown += "## 🧠 Assessment Questions\n\n"
    
    if lesson_plan.assessment_questions:
        for i, question in enumerate(lesson_plan.assessment_questions, 1):
            markdown += f"{i}. {question}\n"
    else:
        markdown += "1. What is the derivative of f(x) = x²?\n"
        markdown += "2. How does the derivative relate to the slope of a tangent line?\n"
        markdown += "3. Explain the concept of instantaneous rate of change.\n"
        markdown += "4. What does a positive derivative tell us about a function?\n"
    
    markdown += "\n## 📚 Additional Resources\n\n"
    
    if lesson_plan.resources:
        for resource in lesson_plan.resources:
            markdown += f"- {resource}\n"
    else:
        markdown += "- Khan Academy: Derivatives and Differentiation\n"
        markdown += "- 3Blue1Brown: Essence of Calculus Series\n"
        markdown += "- MIT OpenCourseWare: Single Variable Calculus\n"
        markdown += "- Paul's Online Math Notes: Derivatives\n"
    
    # Animation summary
    if animations:
        markdown += "\n## 🎬 Animation Summary\n\n"
        markdown += f"Total animations created: {len(animations)}\n\n"
        
        for i, anim_data in enumerate(animations, 1):
            anim = anim_data['animation']
            markdown += f"### Animation {i}: {anim.concept}\n"
            markdown += f"- **File:** `{anim.video_path}`\n"
            markdown += f"- **Duration:** {anim.duration:.1f} seconds\n"
            markdown += f"- **Section:** {anim_data['section_index'] + 1}\n"
            if anim.visual_elements:
                markdown += f"- **Visual Elements:** {', '.join(anim.visual_elements)}\n"
            markdown += "\n"
    
    markdown += "\n---\n\n"
    markdown += "*This lecture was automatically generated using AI-powered educational content creation tools.*\n"
    
    return markdown


async def main():
    """Run the demo lecture creation"""
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Please set ANTHROPIC_API_KEY in .env file")
        return
    
    try:
        await create_demo_lecture()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 