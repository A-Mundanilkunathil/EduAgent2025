from typing import Type, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json
import asyncio

from quality_check_agent import QualityCheckAgent, QualityReport


class VideoQualityInput(BaseModel):
    """Input schema for video quality check tool"""
    video_path: str = Field(description="Path to the video file to analyze")


class VideoQualityTool(BaseTool):
    """
    CrewAI tool for checking video quality.
    Wraps the QualityCheckAgent for use in CrewAI workflows.
    """
    
    name: str = "Check Video Quality"
    description: str = """Analyzes the quality of a generated animation video.
    
    Input:
    - video_path: Path to the video file
    
    Returns detailed quality report including:
    - Overall quality score (0-100)
    - Technical metrics (duration, resolution, framerate)
    - List of quality issues found
    - Recommendations for improvement
    """
    
    args_schema: Type[BaseModel] = VideoQualityInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._agent = QualityCheckAgent()
    
    def _run(self, video_path: str) -> str:
        """
        Synchronous wrapper for the async quality check.
        Returns JSON string for CrewAI compatibility.
        """
        
        # Run async execution in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            report: QualityReport = loop.run_until_complete(
                self._agent.analyze_animation(video_path)
            )
            
            # Convert to dict and return as JSON string
            return json.dumps(report.model_dump(), indent=2, default=str)
        finally:
            loop.close()


class QuickQualityInput(BaseModel):
    """Input schema for quick quality check"""
    video_path: str = Field(description="Path to the video file")
    check_type: str = Field(
        default="basic",
        description="Type of check: 'basic' (fast) or 'detailed' (thorough)"
    )


class QuickQualityCheckTool(BaseTool):
    """
    Quick quality check tool for fast validation.
    """
    
    name: str = "Quick Quality Check"
    description: str = """Performs a quick quality check on an animation.
    
    Inputs:
    - video_path: Path to the video file
    - check_type: 'basic' or 'detailed'
    
    Returns:
    - Pass/Fail status
    - Major issues only
    - Quick recommendations
    """
    
    args_schema: Type[BaseModel] = QuickQualityInput
    
    def _run(self, video_path: str, check_type: str = "basic") -> str:
        """Quick quality validation"""
        
        import os
        
        # Basic file validation
        if not os.path.exists(video_path):
            return json.dumps({
                "status": "fail",
                "reason": "Video file not found",
                "recommendation": "Check file path and ensure video was generated"
            })
        
        file_size = os.path.getsize(video_path)
        
        # Basic checks
        if file_size < 1000:  # Less than 1KB
            return json.dumps({
                "status": "fail",
                "reason": "Video file too small, likely corrupted",
                "recommendation": "Regenerate the animation"
            })
        
        if file_size > 100 * 1024 * 1024:  # More than 100MB
            return json.dumps({
                "status": "warning",
                "reason": "Video file very large",
                "recommendation": "Consider compression or shorter duration"
            })
        
        # If basic checks pass
        return json.dumps({
            "status": "pass",
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "recommendation": "Video appears valid, run detailed check for full analysis"
        })


class BatchQualityInput(BaseModel):
    """Input schema for batch quality checking"""
    video_paths: list[str] = Field(description="List of video paths to analyze")
    output_format: str = Field(
        default="summary",
        description="Output format: 'summary' or 'detailed'"
    )


class BatchQualityTool(BaseTool):
    """
    Tool for checking multiple videos at once.
    """
    
    name: str = "Batch Quality Check"
    description: str = """Analyzes quality of multiple animation videos.
    
    Inputs:
    - video_paths: List of video file paths
    - output_format: 'summary' (overview) or 'detailed' (full reports)
    
    Returns consolidated quality report for all videos.
    """
    
    args_schema: Type[BaseModel] = BatchQualityInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._agent = QualityCheckAgent()
    
    def _run(self, video_paths: list[str], output_format: str = "summary") -> str:
        """Check multiple videos"""
        
        results = []
        
        for video_path in video_paths:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                report = loop.run_until_complete(
                    self._agent.analyze_animation(video_path)
                )
                
                if output_format == "summary":
                    results.append({
                        "video": video_path,
                        "score": report.score,
                        "quality": report.overall_quality,
                        "issues_count": len(report.issues)
                    })
                else:
                    results.append(report.model_dump())
                    
            except Exception as e:
                results.append({
                    "video": video_path,
                    "error": str(e)
                })
            finally:
                loop.close()
        
        # Calculate overall statistics
        valid_scores = [r["score"] for r in results if "score" in r]
        
        summary = {
            "total_videos": len(video_paths),
            "analyzed": len(valid_scores),
            "average_score": sum(valid_scores) / len(valid_scores) if valid_scores else 0,
            "results": results
        }
        
        return json.dumps(summary, indent=2)


# Factory function for creating quality tools
def create_quality_tools() -> list:
    """Create all quality-related tools for CrewAI"""
    return [
        VideoQualityTool(),
        QuickQualityCheckTool(),
        BatchQualityTool()
    ]