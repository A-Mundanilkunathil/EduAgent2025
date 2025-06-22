import os
import json
import subprocess
from typing import Dict, List, Any, Optional, ClassVar
from pathlib import Path
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
import tempfile

from crewai import Agent, Task, Crew
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class QualityIssue(BaseModel):
    """Represents a quality issue found in the animation"""
    issue_type: str = Field(description="Type: duration_mismatch, file_corrupted, low_quality, etc.")
    severity: str = Field(description="Severity: low, medium, high")
    description: str = Field(description="Detailed description of the issue")
    suggestion: str = Field(description="Suggested fix or improvement")


class AestheticIssue(BaseModel):
    """Represents an aesthetic/visual issue found in the animation"""
    frame_number: int = Field(description="Frame number where issue was detected")
    element: str = Field(description="Element with the issue: title, y_axis_label, equation, etc.")
    problem: str = Field(description="What the aesthetic problem is")
    severity: str = Field(description="Severity: high, medium, low")
    suggested_fix: str = Field(description="Suggested positioning or styling fix")


class QualityReport(BaseModel):
    """Complete quality analysis report for an animation"""
    video_path: str = Field(description="Path to the analyzed video")
    overall_quality: str = Field(description="Overall quality: excellent, good, acceptable, poor")
    technical_metrics: Dict[str, Any] = Field(description="Technical metrics: duration, resolution, fps, etc.")
    issues: List[QualityIssue] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    score: float = Field(description="Quality score from 0-100")
    timestamp: datetime = Field(default_factory=datetime.now)


class QualityCheckAgent(Agent):
    """
    CrewAI Agent for checking the quality of generated animations.
    Works independently from the Manim generation agent.
    """
    
    # Class-level quality thresholds to avoid Pydantic field errors
    MIN_DURATION: ClassVar[float] = 3.0  # seconds
    MAX_DURATION: ClassVar[float] = 300.0  # 5 minutes
    MIN_RESOLUTION: ClassVar[tuple] = (640, 480)
    TARGET_FPS: ClassVar[int] = 30
    _openai_client: ClassVar[Optional[OpenAI]] = None
    
    def __init__(self, **kwargs):
        # Default agent configuration
        default_config = {
            "role": "Animation Quality Analyst",
            "goal": "Ensure mathematical animations meet quality standards for educational effectiveness",
            "backstory": """You are a quality assurance specialist for educational content. 
            You analyze mathematical animations to ensure they are clear, accurate, and effective 
            for learning. You check technical quality, visual clarity, and educational value.""",
            "verbose": True,
            "allow_delegation": False,
        }
        
        # Merge with any provided kwargs
        config = {**default_config, **kwargs}
        super().__init__(**config)
        
        # Initialize OpenAI client for visual analysis (class-level to avoid Pydantic issues)
        if QualityCheckAgent._openai_client is None:
            QualityCheckAgent._openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def analyze_video_file(self, video_path: str) -> Dict[str, Any]:
        """Extract technical information about the video file"""
        
        if not os.path.exists(video_path):
            return {"error": "Video file not found"}
        
        try:
            # Use ffprobe to get video information
            cmd = [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # Extract relevant metrics
                video_stream = next((s for s in data.get("streams", []) if s["codec_type"] == "video"), None)
                
                if video_stream:
                    return {
                        "duration": float(data["format"].get("duration", 0)),
                        "size_bytes": int(data["format"].get("size", 0)),
                        "bitrate": int(data["format"].get("bit_rate", 0)),
                        "width": video_stream.get("width", 0),
                        "height": video_stream.get("height", 0),
                        "fps": eval(video_stream.get("r_frame_rate", "0/1")),
                        "codec": video_stream.get("codec_name", "unknown")
                    }
            
            return {"error": "Failed to analyze video"}
            
        except Exception as e:
            return {"error": str(e)}

    def check_technical_quality(self, metrics: Dict[str, Any]) -> List[QualityIssue]:
        """Check technical aspects of the video"""
        issues = []
        
        # Check duration
        duration = metrics.get("duration", 0)
        if duration < self.MIN_DURATION:
            issues.append(QualityIssue(
                issue_type="duration_too_short",
                severity="high",
                description=f"Video is only {duration:.1f}s, minimum recommended is {self.MIN_DURATION}s",
                suggestion="Extend animation with more content or slower pacing"
            ))
        elif duration > self.MAX_DURATION:
            issues.append(QualityIssue(
                issue_type="duration_too_long",
                severity="medium",
                description=f"Video is {duration:.1f}s, which may be too long for engagement",
                suggestion="Consider breaking into multiple shorter animations"
            ))
        
        # Check resolution
        width = metrics.get("width", 0)
        height = metrics.get("height", 0)
        if width < self.MIN_RESOLUTION[0] or height < self.MIN_RESOLUTION[1]:
            issues.append(QualityIssue(
                issue_type="low_resolution",
                severity="high",
                description=f"Resolution {width}x{height} is below minimum {self.MIN_RESOLUTION}",
                suggestion="Render at higher resolution for better quality"
            ))
        
        # Check FPS
        fps = metrics.get("fps", 0)
        if fps < self.TARGET_FPS * 0.8:
            issues.append(QualityIssue(
                issue_type="low_framerate",
                severity="medium",
                description=f"Framerate {fps} is below target {self.TARGET_FPS}",
                suggestion="Render at 30fps for smooth playback"
            ))
        
        # Check file size (warn if very large)
        size_mb = metrics.get("size_bytes", 0) / (1024 * 1024)
        if size_mb > 100:
            issues.append(QualityIssue(
                issue_type="large_file_size",
                severity="low",
                description=f"File size {size_mb:.1f}MB may be too large for web delivery",
                suggestion="Consider compression or lower bitrate"
            ))
        
        return issues

    def calculate_quality_score(self, metrics: Dict[str, Any], issues: List[QualityIssue]) -> float:
        """Calculate overall quality score from 0-100"""
        
        if "error" in metrics:
            return 0.0
        
        score = 100.0
        
        # Count different types of issues
        technical_issues = [i for i in issues if not i.issue_type.startswith("aesthetic_")]
        aesthetic_issues = [i for i in issues if i.issue_type.startswith("aesthetic_")]
        
        # Deduct points for technical issues (original scoring)
        for issue in technical_issues:
            if issue.severity == "high":
                score -= 20
            elif issue.severity == "medium":
                score -= 10
            elif issue.severity == "low":
                score -= 5
        
        # Deduct points for aesthetic issues (gentler scoring)
        aesthetic_penalty = 0
        for issue in aesthetic_issues:
            if issue.severity == "high":
                aesthetic_penalty += 8  # Reduced from 20
            elif issue.severity == "medium":
                aesthetic_penalty += 4  # Reduced from 10
            elif issue.severity == "low":
                aesthetic_penalty += 2  # Reduced from 5
        
        # Cap aesthetic penalty (don't let aesthetics dominate)
        aesthetic_penalty = min(aesthetic_penalty, 40)  # Max 40 points lost to aesthetics
        score -= aesthetic_penalty
        
        # Bonus points for good metrics
        if self.MIN_DURATION <= metrics.get("duration", 0) <= 60:
            score += 5  # Good duration
        
        if metrics.get("fps", 0) >= self.TARGET_FPS:
            score += 5  # Good framerate
        
        return max(20, min(100, score))  # Minimum score of 20

    def generate_recommendations(self, metrics: Dict[str, Any], issues: List[QualityIssue]) -> List[str]:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        # General recommendations based on metrics
        if metrics.get("duration", 0) > 30:
            recommendations.append("Consider adding chapter markers or visual breaks")
        
        if len(issues) == 0:
            recommendations.append("Animation meets all quality standards!")
        else:
            recommendations.append("Address the identified issues to improve quality")
        
        # Specific recommendations for common patterns
        if any(i.issue_type == "duration_too_short" for i in issues):
            recommendations.append("Add more explanatory pauses between concepts")
        
        return recommendations

    def extract_key_frames(self, video_path: str, num_frames: int = 5) -> List[np.ndarray]:
        """Extract key frames from video for visual analysis"""
        
        if not os.path.exists(video_path):
            return []
        
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames == 0:
                return []
            
            # Calculate frame indices to extract (beginning, middle, end + 2 in between)
            frame_indices = []
            if num_frames == 1:
                frame_indices = [total_frames // 2]  # Just middle
            else:
                step = total_frames // (num_frames - 1)
                frame_indices = [i * step for i in range(num_frames - 1)]
                frame_indices.append(total_frames - 1)  # Ensure we get the last frame
            
            frames = []
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
            
            cap.release()
            return frames
            
        except Exception as e:
            print(f"Error extracting frames: {e}")
            return []

    def frame_to_base64(self, frame: np.ndarray) -> str:
        """Convert OpenCV frame to base64 string for GPT-4o-mini"""
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(frame_rgb)
        
        # Convert to base64
        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str

    async def analyze_with_gpt4o_mini(self, frames: List[np.ndarray]) -> List[AestheticIssue]:
        """Use GPT-4o-mini to analyze frames for aesthetic issues"""
        
        if not frames:
            return []
        
        aesthetic_issues = []
        
        try:
            # Analyze multiple frames (cost-effective with GPT-4o-mini)
            for frame_idx, frame in enumerate(frames):
                frame_b64 = self.frame_to_base64(frame)
                
                prompt = """Analyze this mathematical animation frame for aesthetic issues:

LOOK FOR:
- Text overlapping with axes, graphs, or other mathematical objects
- Poor spacing between elements  
- Titles positioned too high or low
- Y-axis labels overlapping with content
- Equations positioned awkwardly
- Unreadable or too-small text

For each issue found, specify:
1. What element has the problem (title, y_axis_label, equation, etc.)
2. What the problem is (overlaps with graph, too close to axes, etc.)
3. Suggested fix (move down 1-2 units, increase spacing, etc.)

Format response as:
[element] - [problem] - [fix]

If no issues: "No aesthetic issues detected"
"""

                response = QualityCheckAgent._openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{frame_b64}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=300
                )
                
                analysis = response.choices[0].message.content
                
                # Parse GPT-4o-mini response
                if "No aesthetic issues detected" not in analysis:
                    # Parse formatted response
                    lines = analysis.strip().split('\n')
                    for line in lines:
                        if ' - ' in line and line.strip():
                            try:
                                parts = line.split(' - ')
                                if len(parts) >= 3:
                                    element = parts[0].strip()
                                    problem = parts[1].strip()
                                    fix = parts[2].strip()
                                    
                                    # Determine severity based on keywords
                                    severity = "high" if any(word in problem.lower() for word in ["overlap", "cover", "unreadable"]) else "medium"
                                    
                                    aesthetic_issues.append(AestheticIssue(
                                        frame_number=frame_idx + 1,
                                        element=element,
                                        problem=problem,
                                        severity=severity,
                                        suggested_fix=fix
                                    ))
                            except Exception as parse_error:
                                print(f"Error parsing line: {line} - {parse_error}")
        
        except Exception as e:
            print(f"Error in GPT-4o-mini visual analysis: {e}")
            # Add fallback issue
            aesthetic_issues.append(AestheticIssue(
                frame_number=1,
                element="unknown",
                problem="Visual analysis failed",
                severity="low",
                suggested_fix="Manually review for aesthetic issues"
            ))
        
        return aesthetic_issues

    async def check_visual_quality(self, video_path: str) -> List[QualityIssue]:
        """Simplified visual quality check using GPT-4o-mini"""
        
        all_issues = []
        
        # Extract key frames (more frames since GPT-4o-mini is cheap)
        frames = self.extract_key_frames(video_path, num_frames=5)
        
        if not frames:
            return [QualityIssue(
                issue_type="frame_extraction_failed",
                severity="medium",
                description="Could not extract frames for visual analysis",
                suggestion="Check video file integrity"
            )]
        
        # GPT-4o-mini aesthetic analysis
        aesthetic_issues = await self.analyze_with_gpt4o_mini(frames)
        
        # Convert AestheticIssue to QualityIssue for compatibility
        for aesthetic_issue in aesthetic_issues:
            quality_issue = QualityIssue(
                issue_type=f"aesthetic_{aesthetic_issue.element}",
                severity=aesthetic_issue.severity,
                description=f"Frame {aesthetic_issue.frame_number}: {aesthetic_issue.element} - {aesthetic_issue.problem}",
                suggestion=aesthetic_issue.suggested_fix
            )
            all_issues.append(quality_issue)
        
        return all_issues

    async def analyze_animation(self, video_path: str) -> QualityReport:
        """Main method to analyze an animation's quality"""
        
        # Get technical metrics
        metrics = self.analyze_video_file(video_path)
        
        # Check for technical issues
        issues = self.check_technical_quality(metrics) if "error" not in metrics else []
        
        # Check for visual quality issues (CV + Claude Vision)
        try:
            visual_issues = await self.check_visual_quality(video_path)
            issues.extend(visual_issues)
        except Exception as e:
            print(f"Visual quality check failed: {e}")
            # Add fallback issue
            issues.append(QualityIssue(
                issue_type="visual_check_failed",
                severity="low",
                description="Advanced visual analysis unavailable",
                suggestion="Manually review for overlapping elements and poor spacing"
            ))
        
        # Calculate quality score (including visual issues)
        score = self.calculate_quality_score(metrics, issues)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(metrics, issues)
        
        # Determine overall quality
        if score >= 90:
            overall_quality = "excellent"
        elif score >= 70:
            overall_quality = "good"
        elif score >= 50:
            overall_quality = "acceptable"
        else:
            overall_quality = "poor"
        
        return QualityReport(
            video_path=video_path,
            overall_quality=overall_quality,
            technical_metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            score=score
        )


# Convenience function for standalone usage
async def check_animation_quality(video_path: str) -> QualityReport:
    """Check quality of an animation with minimal setup"""
    agent = QualityCheckAgent()
    return await agent.analyze_animation(video_path)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        # Test with a sample video path
        test_video = "animations/test_animation.mp4"
        
        if os.path.exists(test_video):
            report = await check_animation_quality(test_video)
            print(f"Quality Score: {report.score}/100")
            print(f"Overall Quality: {report.overall_quality}")
            print(f"Issues Found: {len(report.issues)}")
            for issue in report.issues:
                print(f"  - {issue.description}")
        else:
            print(f"Test video not found: {test_video}")
    
    asyncio.run(test())