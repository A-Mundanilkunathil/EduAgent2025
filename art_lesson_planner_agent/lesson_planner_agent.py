import os
import asyncio
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

from crewai import Agent, Task, Crew
from pydantic import BaseModel, Field
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()


class LessonSection(BaseModel):
    """A section of the lesson with potential visualization"""
    title: str = Field(description="Section title")
    content: str = Field(description="Educational content")
    visualization_placeholder: Optional[str] = Field(default=None, description="Placeholder for visualization")
    visualization_concept: Optional[str] = Field(default=None, description="Mathematical concept to visualize")
    duration_estimate: float = Field(default=5.0, description="Estimated duration in minutes")
    complexity: str = Field(default="intermediate", description="Complexity level")
    learning_objectives: List[str] = Field(default_factory=list, description="Specific learning objectives")


class LessonPlan(BaseModel):
    """Complete lesson plan with integrated visualizations"""
    title: str = Field(description="Lesson title")
    subject: str = Field(description="Subject area")
    target_audience: str = Field(description="Target audience/grade level")
    total_duration: float = Field(description="Total lesson duration in minutes")
    prerequisites: List[str] = Field(description="Prerequisite knowledge")
    learning_objectives: List[str] = Field(description="Overall learning objectives")
    sections: List[LessonSection] = Field(description="Lesson sections")
    assessment_questions: List[str] = Field(description="Assessment questions")
    resources: List[str] = Field(description="Additional resources")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LessonPlannerCore:
    """Core lesson planning functionality without CrewAI inheritance"""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.system_prompt = """You are an expert educational content creator specializing in lesson planning with integrated visualizations.

LESSON PLANNING GUIDELINES:
- Create engaging, structured lessons that build concepts progressively
- Identify natural visualization opportunities for mathematical concepts
- Use clear, accessible language appropriate for the target audience
- Include specific learning objectives for each section
- Structure content to flow logically from simple to complex
- Estimate realistic time allocations for each section

VISUALIZATION INTEGRATION:
- Identify key mathematical concepts that benefit from visual explanation
- Create placeholder text like "{visualization}" or "{animation}" where visualizations should appear
- Provide specific concepts for the Manim agent to visualize
- Ensure visualizations support and enhance the educational narrative
- Consider timing and pacing for visual elements

CONTENT STRUCTURE:
- Start with clear learning objectives
- Build foundational concepts before advanced topics
- Include practical examples and applications
- End with assessment questions to check understanding
- Provide additional resources for further learning

Generate comprehensive lesson plans that seamlessly integrate text and visualizations."""

    async def generate_lesson_plan(self, user_request: str, context: Dict[str, Any] = None) -> LessonPlan:
        """Generate a complete lesson plan based on user request"""
        
        # Build context-aware prompt
        prompt_parts = [
            f"Create a comprehensive lesson plan for: {user_request}",
            "\nThe lesson should include integrated visualizations where appropriate.",
            "Use placeholders like {visualization} or {animation} where visual elements should appear.",
            "For each visualization, provide a specific mathematical concept to visualize."
        ]
        
        if context:
            if "subject" in context:
                prompt_parts.append(f"\nSubject: {context['subject']}")
            if "audience" in context:
                prompt_parts.append(f"\nTarget audience: {context['audience']}")
            if "duration" in context:
                prompt_parts.append(f"\nTarget duration: {context['duration']} minutes")
            if "complexity" in context:
                prompt_parts.append(f"\nComplexity level: {context['complexity']}")
        
        prompt = "\n".join(prompt_parts)
        
        # Generate lesson plan using Claude
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse the response into structured format
        lesson_text = response.content[0].text
        return self._parse_lesson_response(lesson_text, user_request, context)

    def _parse_lesson_response(self, lesson_text: str, user_request: str, context: Dict[str, Any] = None) -> LessonPlan:
        """Parse Claude's response into structured LessonPlan"""
        
        # Extract basic information
        title = self._extract_title(lesson_text, user_request)
        subject = context.get("subject", "Mathematics") if context else "Mathematics"
        audience = context.get("audience", "High School") if context else "High School"
        
        # Parse sections
        sections = self._parse_sections(lesson_text)
        
        # Extract other components
        learning_objectives = self._extract_learning_objectives(lesson_text)
        prerequisites = self._extract_prerequisites(lesson_text)
        assessment_questions = self._extract_assessment_questions(lesson_text)
        resources = self._extract_resources(lesson_text)
        
        # Calculate total duration
        total_duration = sum(section.duration_estimate for section in sections)
        
        return LessonPlan(
            title=title,
            subject=subject,
            target_audience=audience,
            total_duration=total_duration,
            prerequisites=prerequisites,
            learning_objectives=learning_objectives,
            sections=sections,
            assessment_questions=assessment_questions,
            resources=resources,
            metadata={"source_request": user_request, "context": context or {}}
        )

    def _extract_title(self, text: str, user_request: str) -> str:
        """Extract lesson title from response"""
        # Look for title patterns
        title_patterns = [
            r"#\s*(.+?)\n",
            r"Title:\s*(.+?)\n",
            r"Lesson:\s*(.+?)\n",
            r"##\s*(.+?)\n"
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback to user request
        return f"Lesson on {user_request}"

    def _parse_sections(self, text: str) -> List[LessonSection]:
        """Parse lesson sections from text"""
        sections = []
        
        # Split by section headers
        section_pattern = r"(?:##\s*|Section\s*\d+[:\s]*|Part\s*\d+[:\s]*)(.+?)(?=\n##\s*|Section\s*\d+[:\s]*|Part\s*\d+[:\s]*|$)"
        section_matches = re.findall(section_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if not section_matches:
            # Fallback: split by paragraphs
            paragraphs = text.split('\n\n')
            for i, para in enumerate(paragraphs[:5]):  # Limit to 5 sections
                if para.strip():
                    sections.append(LessonSection(
                        title=f"Section {i+1}",
                        content=para.strip(),
                        duration_estimate=5.0
                    ))
        else:
            for i, section_text in enumerate(section_matches):
                title = self._extract_section_title(section_text)
                content = self._extract_section_content(section_text)
                visualization_concept = self._extract_visualization_concept(section_text)
                
                sections.append(LessonSection(
                    title=title,
                    content=content,
                    visualization_concept=visualization_concept,
                    duration_estimate=5.0 + (i * 2),  # Progressive timing
                    complexity="intermediate"
                ))
        
        return sections

    def _extract_section_title(self, section_text: str) -> str:
        """Extract section title"""
        lines = section_text.strip().split('\n')
        first_line = lines[0].strip()
        
        # Clean up common patterns
        title = re.sub(r'^[#\s]*', '', first_line)
        title = re.sub(r'[:\-]+$', '', title)
        
        return title if title else "Section"

    def _extract_section_content(self, section_text: str) -> str:
        """Extract section content"""
        lines = section_text.strip().split('\n')
        
        # Skip the first line (title) and join the rest
        content_lines = lines[1:] if lines else []
        content = '\n'.join(content_lines).strip()
        
        # Add visualization placeholder if concept is mentioned
        if any(word in content.lower() for word in ['graph', 'plot', 'visualize', 'show', 'demonstrate']):
            if '{visualization}' not in content and '{animation}' not in content:
                # Insert placeholder at appropriate location
                sentences = content.split('. ')
                if len(sentences) > 1:
                    # Insert after first sentence
                    sentences.insert(1, "{visualization}")
                    content = '. '.join(sentences)
        
        return content

    def _extract_visualization_concept(self, section_text: str) -> Optional[str]:
        """Extract mathematical concept for visualization"""
        # Look for mathematical concepts
        math_concepts = [
            'linear regression', 'derivative', 'integral', 'limit', 'function',
            'graph', 'plot', 'equation', 'formula', 'theorem', 'proof',
            'slope', 'intercept', 'curve', 'line', 'point', 'vector',
            'matrix', 'eigenvalue', 'fourier', 'series', 'sequence'
        ]
        
        text_lower = section_text.lower()
        for concept in math_concepts:
            if concept in text_lower:
                return concept
        
        return None

    def _extract_learning_objectives(self, text: str) -> List[str]:
        """Extract learning objectives"""
        objectives = []
        
        # Look for objectives section
        obj_pattern = r"(?:Learning Objectives?|Objectives?|Goals?)[:\s]*\n((?:[-*]\s*.+?\n?)+)"
        match = re.search(obj_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            obj_text = match.group(1)
            objectives = re.findall(r'[-*]\s*(.+?)(?=\n[-*]|\n\n|$)', obj_text, re.DOTALL)
            objectives = [obj.strip() for obj in objectives if obj.strip()]
        
        return objectives

    def _extract_prerequisites(self, text: str) -> List[str]:
        """Extract prerequisites"""
        prereq_pattern = r"(?:Prerequisites?|Requirements?)[:\s]*\n((?:[-*]\s*.+?\n?)+)"
        match = re.search(prereq_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            prereq_text = match.group(1)
            prereqs = re.findall(r'[-*]\s*(.+?)(?=\n[-*]|\n\n|$)', prereq_text, re.DOTALL)
            return [prereq.strip() for prereq in prereqs if prereq.strip()]
        
        return []

    def _extract_assessment_questions(self, text: str) -> List[str]:
        """Extract assessment questions"""
        questions = []
        
        # Look for assessment section
        assess_pattern = r"(?:Assessment|Questions?|Practice)[:\s]*\n((?:[-*]\s*.+?\n?)+)"
        match = re.search(assess_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            assess_text = match.group(1)
            questions = re.findall(r'[-*]\s*(.+?)(?=\n[-*]|\n\n|$)', assess_text, re.DOTALL)
            questions = [q.strip() for q in questions if q.strip()]
        
        return questions

    def _extract_resources(self, text: str) -> List[str]:
        """Extract additional resources"""
        resources = []
        
        # Look for resources section
        res_pattern = r"(?:Resources?|References?|Further Reading)[:\s]*\n((?:[-*]\s*.+?\n?)+)"
        match = re.search(res_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            res_text = match.group(1)
            resources = re.findall(r'[-*]\s*(.+?)(?=\n[-*]|\n\n|$)', res_text, re.DOTALL)
            resources = [r.strip() for r in resources if r.strip()]
        
        return resources

    def generate_manim_requests(self, lesson_plan: LessonPlan) -> List[Dict[str, Any]]:
        """Generate Manim agent requests for all visualizations in the lesson"""
        requests = []
        
        for i, section in enumerate(lesson_plan.sections):
            if section.visualization_concept:
                # Create context for Manim agent
                manim_context = {
                    "concept": section.visualization_concept,
                    "script_context": section.content,
                    "duration": section.duration_estimate * 60,  # Convert to seconds
                    "complexity": section.complexity,
                    "section_index": i,
                    "section_title": section.title
                }
                
                requests.append({
                    "section_index": i,
                    "section_title": section.title,
                    "manim_context": manim_context
                })
        
        return requests


class LessonPlannerAgent(Agent):
    """
    CrewAI Agent for creating comprehensive lesson plans with integrated visualizations.
    Works with Manim agent to create educational content.
    """
    
    def __init__(self, **kwargs):
        # Default agent configuration
        default_config = {
            "role": "Educational Content Planner",
            "goal": "Create engaging lesson plans that seamlessly integrate text and visualizations for effective learning",
            "backstory": """You are an expert educational content creator with deep knowledge of curriculum design 
            and pedagogical best practices. You excel at identifying opportunities for visual learning and creating 
            structured lessons that build concepts progressively. You work closely with animation specialists to 
            create compelling educational experiences.""",
            "verbose": True,
            "allow_delegation": True,
            "max_iter": 3,
        }
        
        # Merge with any provided kwargs
        config = {**default_config, **kwargs}
        super().__init__(**config)
        
        # Create core functionality handler
        self._core = LessonPlannerCore()

    async def execute(self, task: Task) -> LessonPlan:
        """Execute the lesson planning task"""
        
        # Extract context from task
        task_context = task.context if hasattr(task, 'context') else {}
        
        # Ensure context is a dict
        if not isinstance(task_context, dict):
            task_context = {}
        
        # Handle different context formats
        if isinstance(task_context, list) and task_context:
            # CrewAI passes context as a list
            user_request = task_context[0] if isinstance(task_context[0], str) else str(task_context[0])
        elif isinstance(task_context, str):
            user_request = task_context
        else:
            # Use description as fallback
            user_request = task.description if hasattr(task, 'description') else "mathematical concept"
        
        # Generate lesson plan
        return await self._core.generate_lesson_plan(user_request, task_context)


# Convenience function for standalone usage
async def create_lesson_plan(user_request: str, **context) -> LessonPlan:
    """Create lesson plan with minimal setup"""
    core = LessonPlannerCore()
    return await core.generate_lesson_plan(user_request, context)


# Test function
async def test():
    print("Testing LessonPlannerAgent...")
    
    # Create core instance
    core = LessonPlannerCore()
    
    # Test 1: Simple lesson plan
    result = await create_lesson_plan("Linear regression creates a line of best fit through all data points")
    print(f"\nTest 1 - Title: {result.title}")
    print(f"Sections: {len(result.sections)}")
    print(f"Total duration: {result.total_duration} minutes")
    
    # Test 2: With context
    result = await create_lesson_plan(
        "Derivatives as rates of change",
        subject="Calculus",
        audience="College Freshmen",
        duration=45,
        complexity="intermediate"
    )
    print(f"\nTest 2 - Title: {result.title}")
    print(f"Learning objectives: {result.learning_objectives}")
    
    # Test 3: Generate Manim requests
    manim_requests = core.generate_manim_requests(result)
    print(f"\nTest 3 - Manim requests: {len(manim_requests)}")
    for req in manim_requests:
        print(f"  Section {req['section_index']}: {req['manim_context']['concept']}")


if __name__ == "__main__":
    asyncio.run(test())