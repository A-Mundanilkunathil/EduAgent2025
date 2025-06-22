import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to import manim_agent
sys.path.append(str(Path(__file__).parent.parent))

# Import our agents
from lesson_planner_agent import create_lesson_plan, LessonPlannerCore
from matt_manim_agent.manim_agent import create_animation

load_dotenv()


class ComprehensiveLectureGenerator:
    """Generate comprehensive lectures with integrated animations"""
    
    def __init__(self):
        self.lesson_core = LessonPlannerCore()
        self.output_dir = Path("lectures")
        self.output_dir.mkdir(exist_ok=True)
    
    async def generate_lecture(self, topic: str, **context) -> dict:
        """Generate a complete lecture with animations"""
        
        print(f"🎓 Generating comprehensive lecture on: {topic}")
        
        # Step 1: Create lesson plan
        print("📝 Creating lesson plan...")
        lesson_plan = await create_lesson_plan(topic, **context)
        
        # Step 2: Generate animations
        print("🎬 Creating animations...")
        animations = await self._create_animations(lesson_plan)
        
        # Step 3: Generate comprehensive lecture
        print("📚 Generating comprehensive lecture...")
        lecture = self._create_comprehensive_lecture(lesson_plan, animations)
        
        return lecture
    
    async def _create_animations(self, lesson_plan) -> list:
        """Create animations for the lesson plan"""
        animations = []
        
        # Generate Manim requests
        manim_requests = self.lesson_core.generate_manim_requests(lesson_plan)
        
        if not manim_requests:
            print("   ⚠️  No visualization opportunities found")
            return animations
        
        print(f"   🎯 Found {len(manim_requests)} visualization opportunities")
        
        # Create animations for each request
        for i, request in enumerate(manim_requests, 1):
            print(f"   🎬 Creating animation {i}/{len(manim_requests)}: {request['manim_context']['concept']}")
            
            try:
                animation = await create_animation(
                    concept=request['manim_context']['concept'],
                    script_context=request['manim_context']['script_context'],
                    duration=request['manim_context']['duration']
                )
                
                if animation.success:
                    print(f"      ✅ Success: {animation.video_path}")
                    animations.append({
                        'section_index': request['section_index'],
                        'section_title': request['section_title'],
                        'animation': animation
                    })
                else:
                    print(f"      ❌ Failed: {animation.error}")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        return animations
    
    def _create_comprehensive_lecture(self, lesson_plan, animations) -> dict:
        """Create a comprehensive lecture structure"""
        
        # Map animations to sections
        animation_map = {}
        for anim_data in animations:
            section_idx = anim_data['section_index']
            if section_idx not in animation_map:
                animation_map[section_idx] = []
            animation_map[section_idx].append(anim_data['animation'])
        
        # Create comprehensive lecture structure
        lecture = {
            "metadata": {
                "title": lesson_plan.title,
                "subject": lesson_plan.subject,
                "target_audience": lesson_plan.target_audience,
                "total_duration": lesson_plan.total_duration,
                "generated_at": datetime.now().isoformat(),
                "animation_count": len(animations)
            },
            "overview": {
                "prerequisites": lesson_plan.prerequisites,
                "learning_objectives": lesson_plan.learning_objectives,
                "key_concepts": self._extract_key_concepts(lesson_plan)
            },
            "sections": [],
            "assessment": {
                "questions": lesson_plan.assessment_questions,
                "resources": lesson_plan.resources
            },
            "animations": []
        }
        
        # Process each section
        for i, section in enumerate(lesson_plan.sections):
            section_data = {
                "index": i,
                "title": section.title,
                "content": section.content,
                "duration_estimate": section.duration_estimate,
                "complexity": section.complexity,
                "animations": animation_map.get(i, []),
                "key_points": self._extract_key_points(section.content),
                "visualization_notes": self._generate_visualization_notes(section, animation_map.get(i, []))
            }
            lecture["sections"].append(section_data)
        
        # Add all animations to the lecture
        for anim_data in animations:
            lecture["animations"].append({
                "concept": anim_data['animation'].concept,
                "video_path": anim_data['animation'].video_path,
                "duration": anim_data['animation'].duration,
                "visual_elements": anim_data['animation'].visual_elements,
                "section_index": anim_data['section_index']
            })
        
        return lecture
    
    def _extract_key_concepts(self, lesson_plan) -> list:
        """Extract key concepts from the lesson plan"""
        concepts = []
        
        # Look for mathematical concepts in the content
        math_concepts = [
            'derivative', 'integral', 'limit', 'function', 'equation',
            'theorem', 'proof', 'series', 'sequence', 'vector',
            'matrix', 'eigenvalue', 'fourier', 'regression', 'probability'
        ]
        
        all_content = " ".join([section.content for section in lesson_plan.sections])
        all_content_lower = all_content.lower()
        
        for concept in math_concepts:
            if concept in all_content_lower:
                concepts.append(concept.title())
        
        return list(set(concepts))  # Remove duplicates
    
    def _extract_key_points(self, content: str) -> list:
        """Extract key points from section content"""
        # Simple extraction - look for sentences with key indicators
        sentences = content.split('. ')
        key_points = []
        
        key_indicators = ['important', 'key', 'essential', 'critical', 'main', 'primary']
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in key_indicators):
                key_points.append(sentence.strip())
        
        # If no key points found, take first few sentences
        if not key_points and sentences:
            key_points = [sent.strip() for sent in sentences[:2] if sent.strip()]
        
        return key_points
    
    def _generate_visualization_notes(self, section, animations) -> str:
        """Generate notes about visualizations for this section"""
        if not animations:
            return "No specific visualizations for this section."
        
        notes = []
        for anim in animations:
            notes.append(f"📹 **{anim.concept}**: {anim.video_path}")
            if anim.visual_elements:
                notes.append(f"   Visual elements: {', '.join(anim.visual_elements)}")
        
        return "\n".join(notes)
    
    async def save_lecture(self, lecture: dict, filename: str = None) -> Path:
        """Save the lecture in multiple formats"""
        
        if filename is None:
            safe_title = lecture["metadata"]["title"].replace(" ", "_").replace(":", "").lower()
            filename = f"lecture_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save as JSON
        json_path = self.output_dir / f"{filename}.json"
        with open(json_path, 'w') as f:
            json.dump(lecture, f, indent=2, default=str)
        
        # Save as Markdown
        md_path = self.output_dir / f"{filename}.md"
        await self._save_markdown_lecture(lecture, md_path)
        
        # Save as HTML
        html_path = self.output_dir / f"{filename}.html"
        await self._save_html_lecture(lecture, html_path)
        
        print(f"📁 Lecture saved to:")
        print(f"   📄 JSON: {json_path}")
        print(f"   📝 Markdown: {md_path}")
        print(f"   🌐 HTML: {html_path}")
        
        return md_path
    
    async def _save_markdown_lecture(self, lecture: dict, filepath: Path):
        """Save lecture as a well-formatted markdown document"""
        
        with open(filepath, 'w') as f:
            # Header
            f.write(f"# {lecture['metadata']['title']}\n\n")
            f.write(f"**Subject:** {lecture['metadata']['subject']}\n")
            f.write(f"**Target Audience:** {lecture['metadata']['target_audience']}\n")
            f.write(f"**Duration:** {lecture['metadata']['total_duration']} minutes\n")
            f.write(f"**Generated:** {lecture['metadata']['generated_at']}\n")
            f.write(f"**Animations:** {lecture['metadata']['animation_count']}\n\n")
            
            # Table of Contents
            f.write("## 📋 Table of Contents\n\n")
            for i, section in enumerate(lecture['sections'], 1):
                f.write(f"{i}. [{section['title']}](#section-{i})\n")
            f.write("\n")
            
            # Overview
            f.write("## 🎯 Learning Objectives\n\n")
            for obj in lecture['overview']['learning_objectives']:
                f.write(f"- {obj}\n")
            f.write("\n")
            
            if lecture['overview']['prerequisites']:
                f.write("## 📚 Prerequisites\n\n")
                for prereq in lecture['overview']['prerequisites']:
                    f.write(f"- {prereq}\n")
                f.write("\n")
            
            if lecture['overview']['key_concepts']:
                f.write("## 🔑 Key Concepts\n\n")
                for concept in lecture['overview']['key_concepts']:
                    f.write(f"- **{concept}**\n")
                f.write("\n")
            
            # Main Content
            f.write("## 📖 Lecture Content\n\n")
            
            for i, section in enumerate(lecture['sections'], 1):
                f.write(f"### Section {i}: {section['title']}\n\n")
                f.write(f"**Duration:** {section['duration_estimate']} minutes | **Complexity:** {section['complexity']}\n\n")
                
                # Section content
                f.write(f"{section['content']}\n\n")
                
                # Key points
                if section['key_points']:
                    f.write("**Key Points:**\n")
                    for point in section['key_points']:
                        f.write(f"- {point}\n")
                    f.write("\n")
                
                # Animations
                if section['animations']:
                    f.write("**📹 Visualizations:**\n")
                    for anim in section['animations']:
                        f.write(f"- **{anim.concept}**: `{anim.video_path}`\n")
                        f.write(f"  - Duration: {anim.duration:.1f} seconds\n")
                        if anim.visual_elements:
                            f.write(f"  - Elements: {', '.join(anim.visual_elements)}\n")
                    f.write("\n")
                
                f.write("---\n\n")
            
            # Assessment
            if lecture['assessment']['questions']:
                f.write("## 🧠 Assessment Questions\n\n")
                for i, question in enumerate(lecture['assessment']['questions'], 1):
                    f.write(f"{i}. {question}\n")
                f.write("\n")
            
            # Resources
            if lecture['assessment']['resources']:
                f.write("## 📚 Additional Resources\n\n")
                for resource in lecture['assessment']['resources']:
                    f.write(f"- {resource}\n")
                f.write("\n")
            
            # Animation Summary
            if lecture['animations']:
                f.write("## 🎬 Animation Summary\n\n")
                f.write(f"Total animations created: {len(lecture['animations'])}\n\n")
                for anim in lecture['animations']:
                    f.write(f"- **{anim['concept']}** (Section {anim['section_index'] + 1})\n")
                    f.write(f"  - File: `{anim['video_path']}`\n")
                    f.write(f"  - Duration: {anim['duration']:.1f} seconds\n")
                    f.write(f"  - Elements: {', '.join(anim['visual_elements'])}\n\n")
    
    async def _save_html_lecture(self, lecture: dict, filepath: Path):
        """Save lecture as an HTML document"""
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{lecture['metadata']['title']}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #2980b9; }}
        .metadata {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .section {{ margin: 30px 0; padding: 20px; border-left: 4px solid #3498db; background: #f8f9fa; }}
        .animation {{ background: #e8f4fd; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        .key-points {{ background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 5px 0; }}
        .toc {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{lecture['metadata']['title']}</h1>
        
        <div class="metadata">
            <strong>Subject:</strong> {lecture['metadata']['subject']}<br>
            <strong>Target Audience:</strong> {lecture['metadata']['target_audience']}<br>
            <strong>Duration:</strong> {lecture['metadata']['total_duration']} minutes<br>
            <strong>Animations:</strong> {lecture['metadata']['animation_count']}
        </div>
        
        <h2>Learning Objectives</h2>
        <ul>
"""
        
        for obj in lecture['overview']['learning_objectives']:
            html_content += f"            <li>{obj}</li>\n"
        
        html_content += """
        </ul>
        
        <h2>Lecture Content</h2>
"""
        
        for i, section in enumerate(lecture['sections'], 1):
            html_content += f"""
        <div class="section">
            <h3>Section {i}: {section['title']}</h3>
            <p><strong>Duration:</strong> {section['duration_estimate']} minutes | <strong>Complexity:</strong> {section['complexity']}</p>
            <p>{section['content']}</p>
"""
            
            if section['key_points']:
                html_content += """
            <div class="key-points">
                <strong>Key Points:</strong>
                <ul>
"""
                for point in section['key_points']:
                    html_content += f"                    <li>{point}</li>\n"
                html_content += """
                </ul>
            </div>
"""
            
            if section['animations']:
                html_content += """
            <div class="animation">
                <strong>📹 Visualizations:</strong>
                <ul>
"""
                for anim in section['animations']:
                    html_content += f"                    <li><strong>{anim.concept}</strong>: {anim.video_path}</li>\n"
                html_content += """
                </ul>
            </div>
"""
            
            html_content += """
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(filepath, 'w') as f:
            f.write(html_content)


async def main():
    """Generate a comprehensive lecture"""
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Please set ANTHROPIC_API_KEY in .env file")
        return
    
    # Create generator
    generator = ComprehensiveLectureGenerator()
    
    # Generate a comprehensive lecture
    lecture = await generator.generate_lecture(
        "Fourier Series and Signal Decomposition",
        subject="Advanced Mathematics",
        audience="Engineering Students",
        duration=60,
        complexity="advanced"
    )
    
    # Save the lecture
    await generator.save_lecture(lecture, "fourier_series_lecture")
    
    print("\n🎉 Comprehensive lecture generated successfully!")
    print(f"📊 Summary:")
    print(f"   - Title: {lecture['metadata']['title']}")
    print(f"   - Sections: {len(lecture['sections'])}")
    print(f"   - Animations: {lecture['metadata']['animation_count']}")
    print(f"   - Duration: {lecture['metadata']['total_duration']} minutes")


if __name__ == "__main__":
    asyncio.run(main()) 