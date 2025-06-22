#!/usr/bin/env python3
"""
Simple Document Processor for EduAgent AI
Direct inference without complex pipeline
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, Any
import tempfile
import base64
from datetime import datetime

from dotenv import load_dotenv
from anthropic import AsyncAnthropic

load_dotenv()

class SimpleDocumentProcessor:
    """Simple document processor using direct API calls"""
    
    def __init__(self):
        self.anthropic = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    async def process_document(self, file_path: str, duration_minutes: float = 1.0, progress_callback=None) -> Dict[str, Any]:
        """Process a document and create educational content"""
        
        try:
            # Step 1: Extract content from document
            if progress_callback:
                await progress_callback("🔍 Extracting content from document...")
            content = await self._extract_content(file_path, progress_callback)
            
            # Step 2: Generate educational summary
            if progress_callback:
                await progress_callback("🤖 Analyzing educational content with Claude AI...")
            summary = await self._generate_educational_summary(content, duration_minutes)
            
            # Step 3: Create output
            if progress_callback:
                await progress_callback("📝 Generating structured learning content...")
            output_dir = Path("output_videos")
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / f"edu_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(output_file, 'w') as f:
                f.write(f"🎓 Educational Content Summary\n")
                f.write(f"=" * 50 + "\n\n")
                f.write(f"📄 Source: {Path(file_path).name}\n")
                f.write(f"⏱️ Target Duration: {duration_minutes} minutes\n")
                f.write(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"📝 Content:\n")
                f.write(f"-" * 20 + "\n")
                f.write(summary)
                f.write(f"\n\n💡 This content is ready for video creation!")
            
            return {
                "success": True,
                "output_path": str(output_file),
                "content": summary,
                "duration": duration_minutes * 60,  # Convert to seconds
                "processing_time": "< 10 seconds"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output_path": None
            }
    
    async def _extract_content(self, file_path: str, progress_callback=None) -> str:
        """Extract content from PDF or image"""
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            if progress_callback:
                await progress_callback("📄 Processing PDF document...")
            return await self._extract_from_pdf(file_path)
        elif file_ext in ['.png', '.jpg', '.jpeg']:
            if progress_callback:
                await progress_callback("🖼️ Processing image with AI Vision...")
            return await self._extract_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    async def _extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using simple method"""
        
        try:
            # Try PyMuPDF first
            import fitz
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except ImportError:
            pass
        
        try:
            # Fallback to PyPDF2
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            return text.strip()
        except ImportError:
            pass
        
        # Ultimate fallback
        return f"Content extracted from {Path(pdf_path).name} (text extraction not available)"
    
    async def _extract_from_image(self, image_path: str) -> str:
        """Extract text from image using Claude Vision"""
        
        if not os.getenv("ANTHROPIC_API_KEY"):
            return f"Image content from {Path(image_path).name} (Vision API not available)"
        
        try:
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Get file type
            file_ext = Path(image_path).suffix.lower()
            media_type = f"image/{'jpeg' if file_ext in ['.jpg', '.jpeg'] else 'png'}"
            
            # Use Claude Vision to extract text
            response = await self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text content from this image. Include any mathematical formulas, diagrams descriptions, and educational content. Format it clearly."
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
            return f"Image content from {Path(image_path).name} (extraction error: {e})"
    
    async def _generate_educational_summary(self, content: str, duration_minutes: float) -> str:
        """Generate educational summary using Claude"""
        
        if not os.getenv("ANTHROPIC_API_KEY"):
            return f"Educational content based on extracted text:\n\n{content[:500]}..."
        
        try:
            response = await self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{
                    "role": "user", 
                    "content": f"""Create an educational summary for a {duration_minutes}-minute video based on this content:

{content}

Format your response as:

# Main Topic
[Clear topic title]

## Key Learning Objectives
- [3-4 main learning goals]

## Content Breakdown
[Structured explanation suitable for {duration_minutes} minutes]

## Visual Elements Needed
- [Suggestions for animations/graphics]

## Key Takeaways
- [Main points students should remember]

Keep it concise but comprehensive for the time limit."""
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Educational summary (AI generation error: {e})\n\nExtracted content:\n{content[:1000]}..."

# Test function
async def test_processor():
    """Test the simple processor"""
    
    processor = SimpleDocumentProcessor()
    
    # Find a test file
    pdf_files = list(Path("lesson_pdfs").glob("*.pdf"))
    if pdf_files:
        result = await processor.process_document(str(pdf_files[0]), 1.5)
        print(f"Result: {result}")
        return result
    else:
        print("No test files found")
        return None

if __name__ == "__main__":
    asyncio.run(test_processor())