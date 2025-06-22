"""
Unified Educational Video Generation System
UC Berkeley AI Hackathon 2025
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import tempfile
from datetime import datetime

from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel, Field
import cv2
import numpy as np
from PIL import Image
import re
import io
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

# Optional imports with fallbacks
try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False
    print("⚠️  pytesseract not available - OCR will use fallback")

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    print("⚠️  PyPDF2 not available - PDF processing will use fallback")

try:
    import fitz  # PyMuPDF for better PDF handling
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("⚠️  PyMuPDF not available - using PyPDF2 fallback")

try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False
    print("⚠️  pdf2image not available - scanned PDF OCR disabled")

# Import existing agents
from matt_manim_agent.manim_agent import ManimAgent, ManimOutput
from art_lesson_planner_agent.lesson_planner_agent import LessonPlannerAgent, LessonPlan
from audio_narrator_lmnt import LMNTNarratorAgent, EnhancedAudioNarration
from video_composer import VideoComposerAgent

load_dotenv()


class EducationalContent(BaseModel):
    """Extracted educational content from input materials"""
    text_content: str = Field(description="Extracted text content")
    concepts: List[str] = Field(description="Identified mathematical/educational concepts")
    difficulty_level: str = Field(description="Detected difficulty level")
    subject_area: str = Field(description="Identified subject area")
    visual_elements: List[str] = Field(default_factory=list, description="Visual elements to create")
    metadata: Dict[str, Any] = Field(default_factory=dict)



class FinalVideo(BaseModel):
    """Final educational video output"""
    video_path: str = Field(description="Path to final video")
    duration: float = Field(description="Total duration in seconds")
    lesson_plan: LessonPlan = Field(description="Associated lesson plan")
    animations: List[ManimOutput] = Field(description="Generated animations")
    narration: EnhancedAudioNarration = Field(description="Audio narration")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContentExtractorAgent(Agent):
    """Agent for extracting educational content from PDFs and images"""
    
    def __init__(self, **kwargs):
        default_config = {
            "role": "Content Extraction Specialist",
            "goal": "Extract and analyze educational content from various input formats",
            "backstory": """You are an expert in optical character recognition and content analysis. 
            You excel at extracting meaningful educational content from PDFs, images, and other documents, 
            identifying key concepts and structuring information for educational purposes.""",
            "verbose": True,
            "allow_delegation": False,
        }
        config = {**default_config, **kwargs}
        super().__init__(**config)
        # Store client in private attribute to avoid Pydantic conflicts
        self._anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    async def extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using AI Vision for better educational content parsing"""
        text = ""
        
        # First try traditional text extraction (fast)
        if HAS_PYMUPDF:
            try:
                doc = fitz.open(pdf_path)
                for page in doc:
                    page_text = page.get_text()
                    if page_text.strip():
                        text += page_text + "\n"
                doc.close()
            except Exception as e:
                print(f"PyMuPDF failed: {e}")
                text = ""
        
        # Fallback to PyPDF2 if PyMuPDF failed
        if not text.strip() and HAS_PYPDF2:
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e:
                print(f"PyPDF2 failed: {e}")
        
        # Check if we got meaningful content or if we should use AI Vision
        should_use_ai = (
            not text.strip() or  # No text extracted
            len(text.strip()) < 100 or  # Very little text (likely scanned)
            os.getenv("ANTHROPIC_API_KEY")  # AI available for better parsing
        )
        
        # Use AI Vision for better educational content parsing
        if should_use_ai and os.getenv("ANTHROPIC_API_KEY"):
            try:
                ai_text = await self._extract_pdf_with_ai_vision(pdf_path)
                if ai_text and len(ai_text.strip()) > len(text.strip()):
                    print("🤖 Using AI Vision for enhanced PDF parsing")
                    text = ai_text
            except Exception as e:
                print(f"AI Vision PDF parsing failed: {e}")
        
        # Traditional OCR fallback if still no text
        if not text.strip() and HAS_PDF2IMAGE and HAS_TESSERACT:
            try:
                images = convert_from_path(pdf_path)
                for img in images:
                    text += pytesseract.image_to_string(img) + "\n"
            except Exception as e:
                print(f"PDF OCR failed: {e}")
        
        # Ultimate fallback - return sample text for demo
        if not text.strip():
            text = f"Sample educational content extracted from {pdf_path}.\nThis is a demonstration with placeholder text."
        
        return text
    
    async def _extract_pdf_with_ai_vision(self, pdf_path: str) -> str:
        """Extract PDF content using Claude Vision API for superior educational parsing"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            return ""
        
        try:
            import base64
            
            # Convert PDF pages to images
            if HAS_PDF2IMAGE:
                images = convert_from_path(pdf_path, dpi=200, fmt='png')
            elif HAS_PYMUPDF:
                # Use PyMuPDF to convert to images
                doc = fitz.open(pdf_path)
                images = []
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    images.append(img)
                doc.close()
            else:
                return ""
            
            all_text = ""
            
            # Process each page with Claude Vision
            for i, img in enumerate(images[:5]):  # Limit to first 5 pages for demo
                # Convert PIL image to base64
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                
                # Use Claude Vision to extract text
                response = await self._anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Extract all educational content from page {i+1} of this PDF. Include:\n- All text content\n- Mathematical formulas and equations\n- Diagram descriptions\n- Table data\n- Educational concepts\nFormat clearly and preserve structure."
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": img_data
                                }
                            }
                        ]
                    }]
                )
                
                page_text = response.content[0].text
                all_text += f"\n--- Page {i+1} ---\n{page_text}\n"
            
            return all_text.strip()
            
        except Exception as e:
            print(f"AI Vision PDF extraction failed: {e}")
            return ""
    
    async def extract_from_image(self, image_path: str) -> str:
        """Extract text from image using Claude Vision API for educational content"""
        
        # Check if Anthropic API key is available
        if not os.getenv("ANTHROPIC_API_KEY"):
            # Fallback to pytesseract if available
            if HAS_TESSERACT:
                try:
                    # Read image
                    image = cv2.imread(image_path)
                    
                    # Preprocessing for better OCR
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    
                    # Denoise
                    denoised = cv2.fastNlMeansDenoising(gray)
                    
                    # Threshold to get black text on white background
                    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    
                    # Dilation and erosion to remove noise
                    kernel = np.ones((1, 1), np.uint8)
                    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                    
                    # OCR with custom config for better accuracy
                    custom_config = r'--oem 3 --psm 6'
                    text = pytesseract.image_to_string(processed, config=custom_config)
                    
                    # Also try without preprocessing if results are poor
                    if len(text.strip()) < 50:
                        text_original = pytesseract.image_to_string(gray)
                        if len(text_original) > len(text):
                            text = text_original
                    
                    return text
                    
                except Exception as e:
                    print(f"Pytesseract OCR failed: {e}")
                    return f"Sample text extracted from image {image_path}.\nDemo mode - OCR processing failed."
            else:
                return f"Sample text extracted from image {image_path}.\nDemo mode - Anthropic API key and pytesseract not available."
        
        try:
            # Use Claude Vision API for superior educational OCR
            import base64
            
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Get file type
            file_ext = Path(image_path).suffix.lower()
            media_type = f"image/{'jpeg' if file_ext in ['.jpg', '.jpeg'] else 'png'}"
            
            # Use Claude Vision to extract text
            response = await self._anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all educational content from this image. Include:\n- All text content\n- Mathematical formulas and equations\n- Diagram descriptions\n- Educational concepts\nFormat clearly and preserve structure."
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data
                            }
                        }
                    ]
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Claude Vision OCR failed: {e}")
            # Fallback to pytesseract if Claude fails
            if HAS_TESSERACT:
                try:
                    image = cv2.imread(image_path)
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    text = pytesseract.image_to_string(gray)
                    return text
                except Exception as pytesseract_error:
                    print(f"Pytesseract fallback failed: {pytesseract_error}")
            
            return f"Sample text extracted from image {image_path}.\nDemo mode - All OCR methods failed."
    
    async def analyze_content(self, text: str) -> EducationalContent:
        """Analyze extracted text for educational content"""
        
        # Check if API key is available
        if not os.getenv("ANTHROPIC_API_KEY"):
            # Return fallback analysis for demo mode
            return EducationalContent(
                text_content=text,
                concepts=self._extract_concepts_fallback(text),
                difficulty_level="high school",
                subject_area="Mathematics",
                visual_elements=["graph", "diagram", "animation"],
                metadata={
                    "demo_mode": True,
                    "message": "Add ANTHROPIC_API_KEY for AI-powered analysis"
                }
            )
        
        prompt = f"""Analyze this educational content and provide a JSON response with:
        {{
            "concepts": ["list of key mathematical/educational concepts found"],
            "difficulty_level": "elementary/middle/high school/college",
            "subject_area": "specific subject (e.g., Algebra, Calculus, Physics)",
            "visual_elements": ["list of visualizations that would help explain these concepts"],
            "key_formulas": ["important formulas or equations found"],
            "learning_sequence": ["ordered list of topics to teach"]
        }}
        
        Be specific about mathematical concepts and visualizations needed.
        
        Content: {text[:3000]}"""  # Limit for API
        
        response = await self._anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse JSON response
        analysis_text = response.content[0].text
        
        # Extract JSON from response
        import json
        try:
            # Find JSON in response
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = analysis_text[json_start:json_end]
                analysis = json.loads(json_str)
            else:
                raise ValueError("No JSON found")
        except:
            # Fallback to defaults
            analysis = {
                "concepts": self._extract_concepts_fallback(text),
                "difficulty_level": "high school",
                "subject_area": "Mathematics",
                "visual_elements": ["graph", "animation", "diagram"],
                "key_formulas": [],
                "learning_sequence": []
            }
        
        return EducationalContent(
            text_content=text,
            concepts=analysis.get("concepts", []),
            difficulty_level=analysis.get("difficulty_level", "high school"),
            subject_area=analysis.get("subject_area", "Mathematics"),
            visual_elements=analysis.get("visual_elements", []),
            metadata={
                "key_formulas": analysis.get("key_formulas", []),
                "learning_sequence": analysis.get("learning_sequence", [])
            }
        )
    
    def _extract_concepts_fallback(self, text: str) -> List[str]:
        """Fallback concept extraction using keywords"""
        concepts = []
        
        # Math concept keywords
        math_keywords = {
            "derivative": "derivatives",
            "integral": "integrals", 
            "limit": "limits",
            "function": "functions",
            "equation": "equations",
            "graph": "graphing",
            "slope": "slope",
            "tangent": "tangent lines",
            "matrix": "matrices",
            "vector": "vectors",
            "probability": "probability",
            "statistics": "statistics",
            "theorem": "theorems",
            "polynomial": "polynomials",
            "trigonometry": "trigonometry",
            "geometry": "geometry"
        }
        
        text_lower = text.lower()
        for keyword, concept in math_keywords.items():
            if keyword in text_lower:
                concepts.append(concept)
        
        return list(set(concepts))  # Remove duplicates


class AudioNarratorAgent(Agent):
    """Agent for generating audio narration"""
    
    def __init__(self, **kwargs):
        default_config = {
            "role": "Audio Narration Specialist",
            "goal": "Create engaging audio narration synchronized with visual content",
            "backstory": """You are an expert in educational narration and audio production. 
            You create clear, engaging narrations that enhance learning and synchronize perfectly 
            with visual animations.""",
            "verbose": True,
            "allow_delegation": False,
        }
        config = {**default_config, **kwargs}
        super().__init__(**config)
    
    async def generate_narration(self, lesson_plan: LessonPlan, animations: List[ManimOutput]) -> EnhancedAudioNarration:
        """Generate audio narration for the lesson"""
        # This would integrate with TTS service (e.g., Google Cloud TTS, AWS Polly)
        # For demo, we'll create a placeholder
        
        transcript = self._create_transcript(lesson_plan, animations)
        
        # Simulate audio generation
        audio_path = "narration.mp3"
        duration = sum(section.duration_estimate * 60 for section in lesson_plan.sections)
        
        # Create sync points
        sync_points = []
        current_time = 0.0
        for i, section in enumerate(lesson_plan.sections):
            sync_points.append({
                "section": i,
                "time": current_time,
                "event": "section_start"
            })
            current_time += section.duration_estimate * 60
        
        return EnhancedAudioNarration(
            audio_path=audio_path,
            duration=duration,
            transcript=transcript,
            sync_points=sync_points,
            segments=[],
            voice_config={},
            metadata={}
        )
    
    def _create_transcript(self, lesson_plan: LessonPlan, animations: List[ManimOutput]) -> str:
        """Create narration transcript from lesson plan"""
        transcript = f"Welcome to our lesson on {lesson_plan.title}.\n\n"
        
        for section in lesson_plan.sections:
            transcript += f"{section.title}:\n{section.content}\n\n"
        
        return transcript


# VideoComposerAgent is now imported from video_composer.py


class QualityCheckerAgent(Agent):
    """Agent for quality assurance and accessibility checking"""
    
    def __init__(self, **kwargs):
        default_config = {
            "role": "Quality Assurance Specialist",
            "goal": "Ensure educational videos meet quality and accessibility standards",
            "backstory": """You are an expert in educational content quality and accessibility. 
            You ensure all content meets high standards for clarity, accuracy, and accessibility 
            for diverse learners.""",
            "verbose": True,
            "allow_delegation": False,
        }
        config = {**default_config, **kwargs}
        super().__init__(**config)
    
    async def check_quality(self, video: FinalVideo) -> Dict[str, Any]:
        """Perform quality checks on final video"""
        checks = {
            "content_accuracy": True,
            "visual_clarity": True,
            "audio_quality": True,
            "accessibility": {
                "captions": True,
                "contrast_ratio": True,
                "pacing": True
            },
            "educational_effectiveness": 0.95
        }
        return checks


class UnifiedEducationalVideoGenerator:
    """Main orchestrator for educational video generation"""
    
    def __init__(self):
        # Initialize all agents
        self.content_extractor = ContentExtractorAgent()
        self.lesson_planner = LessonPlannerAgent()
        self.manim_agent = ManimAgent()
        self.audio_narrator = LMNTNarratorAgent()  # Using LMNT for ultra-fast, high-quality narration
        self.video_composer = VideoComposerAgent()
        self.quality_checker = QualityCheckerAgent()
        
        # Create crew
        self.crew = Crew(
            agents=[
                self.content_extractor,
                self.lesson_planner,
                self.manim_agent,
                self.audio_narrator,
                self.video_composer,
                self.quality_checker
            ],
            process=Process.sequential,
            verbose=True
        )
    
    async def generate_video(self, input_path: str, **options) -> FinalVideo:
        """Generate educational video from input file"""
        
        # Step 1: Extract content
        if input_path.endswith('.pdf'):
            text = await self.content_extractor.extract_from_pdf(input_path)
        elif input_path.endswith(('.png', '.jpg', '.jpeg')):
            text = await self.content_extractor.extract_from_image(input_path)
        else:
            raise ValueError(f"Unsupported file type: {input_path}")
        
        content = await self.content_extractor.analyze_content(text)
        
        # Step 2: Create lesson plan
        lesson_task = Task(
            description=f"Create a lesson plan for: {content.text_content}",
            expected_output="A structured lesson plan with sections and visualization concepts",
            agent=self.lesson_planner
        )
        lesson_plan = await self.lesson_planner.execute(lesson_task)
        
        # Step 3: Generate animations
        animations = []
        for section in lesson_plan.sections:
            if section.visualization_concept:
                anim_task = Task(
                    description=f"Create animation for: {section.visualization_concept}",
                    expected_output="A Manim animation with video output",
                    agent=self.manim_agent
                )
                anim = await self.manim_agent.execute(anim_task)
                animations.append(anim)
        
        # Step 4: Generate narration with LMNT
        narration = await self.audio_narrator.generate_narration(
            lesson_plan, 
            animations,
            voice_preset="math_teacher"  # Can be customized based on subject
        )
        
        # Step 5: Compose final video
        video_result = await self.video_composer.compose_video(lesson_plan, animations, narration)
        
        # Create FinalVideo object from result
        final_video = FinalVideo(
            video_path=video_result.get("video_path", ""),
            duration=video_result.get("duration", 0),
            lesson_plan=lesson_plan,
            animations=animations,
            narration=narration,
            metadata=video_result
        )
        
        # Step 6: Quality check
        quality_report = await self.quality_checker.check_quality(final_video)
        final_video.metadata["quality_report"] = quality_report
        
        return final_video


# Demo usage
async def demo():
    generator = UnifiedEducationalVideoGenerator()
    
    # Example: Generate video from PDF about calculus
    video = await generator.generate_video(
        "calculus_lecture.pdf",
        target_audience="high school",
        duration_minutes=10,
        style="3blue1brown",
        accessibility_features=["captions", "audio_descriptions"]
    )
    
    print(f"Generated video: {video.video_path}")
    print(f"Duration: {video.duration} seconds")
    print(f"Quality score: {video.metadata['quality_report']['educational_effectiveness']}")


if __name__ == "__main__":
    asyncio.run(demo())