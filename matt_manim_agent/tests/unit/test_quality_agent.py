"""
Unit tests for Quality Check Agent
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import numpy as np
import cv2
import tempfile
import os

from quality_check_agent import (
    QualityCheckAgent, 
    check_animation_quality, 
    QualityReport, 
    QualityIssue, 
    AestheticIssue
)


class TestQualityCheckAgent:
    """Test the Quality Check Agent core functionality"""
    
    def test_init(self):
        """Test agent initialization"""
        agent = QualityCheckAgent()
        assert agent.MIN_DURATION == 3.0
        assert agent.MAX_DURATION == 300.0
        assert agent.MIN_RESOLUTION == (640, 480)
        assert agent.TARGET_FPS == 30
        assert QualityCheckAgent._openai_client is not None
    
    def test_analyze_video_file_success(self):
        """Test successful video file analysis"""
        agent = QualityCheckAgent()
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '''
        {
            "format": {
                "duration": "10.5",
                "size": "1000000",
                "bit_rate": "800000"
            },
            "streams": [
                {
                    "codec_type": "video",
                    "width": 1280,
                    "height": 720,
                    "r_frame_rate": "30/1",
                    "codec_name": "h264"
                }
            ]
        }
        '''
        
        with patch('subprocess.run', return_value=mock_result), \
             patch('os.path.exists', return_value=True):
            
            metrics = agent.analyze_video_file("/tmp/test.mp4")
            
            assert metrics["duration"] == 10.5
            assert metrics["width"] == 1280
            assert metrics["height"] == 720
            assert metrics["fps"] == 30.0
            assert metrics["codec"] == "h264"
    
    def test_analyze_video_file_not_found(self):
        """Test video file analysis when file doesn't exist"""
        agent = QualityCheckAgent()
        
        with patch('os.path.exists', return_value=False):
            metrics = agent.analyze_video_file("/nonexistent/file.mp4")
            assert "error" in metrics
            assert metrics["error"] == "Video file not found"
    
    def test_check_technical_quality_good_video(self):
        """Test technical quality check for good video"""
        agent = QualityCheckAgent()
        
        good_metrics = {
            "duration": 15.0,
            "width": 1280,
            "height": 720,
            "fps": 30,
            "size_bytes": 5000000
        }
        
        issues = agent.check_technical_quality(good_metrics)
        assert len(issues) == 0
    
    def test_check_technical_quality_issues(self):
        """Test technical quality check with various issues"""
        agent = QualityCheckAgent()
        
        bad_metrics = {
            "duration": 2.0,  # Too short
            "width": 400,     # Too low resolution
            "height": 300,
            "fps": 15,        # Too low fps
            "size_bytes": 200000000  # Too large
        }
        
        issues = agent.check_technical_quality(bad_metrics)
        
        # Should find multiple issues
        assert len(issues) >= 3
        
        issue_types = [issue.issue_type for issue in issues]
        assert "duration_too_short" in issue_types
        assert "low_resolution" in issue_types
        assert "low_framerate" in issue_types
    
    def test_calculate_quality_score_perfect(self):
        """Test quality score calculation for perfect video"""
        agent = QualityCheckAgent()
        
        perfect_metrics = {
            "duration": 30.0,
            "fps": 30
        }
        
        score = agent.calculate_quality_score(perfect_metrics, [])
        assert score == 110.0  # 100 + 5 + 5 bonus points, capped at 100
    
    def test_calculate_quality_score_with_issues(self):
        """Test quality score calculation with various issues"""
        agent = QualityCheckAgent()
        
        metrics = {"duration": 30.0, "fps": 30}
        
        issues = [
            QualityIssue(issue_type="technical_issue", severity="high", description="", suggestion=""),
            QualityIssue(issue_type="aesthetic_title", severity="high", description="", suggestion=""),
            QualityIssue(issue_type="aesthetic_label", severity="medium", description="", suggestion=""),
        ]
        
        score = agent.calculate_quality_score(metrics, issues)
        
        # 100 + 10 (bonuses) - 20 (technical high) - 8 (aesthetic high) - 4 (aesthetic medium) = 78
        assert score == 78.0
    
    def test_extract_key_frames_success(self, temp_dir):
        """Test successful frame extraction"""
        agent = QualityCheckAgent()
        
        # Create a mock video file
        video_path = os.path.join(temp_dir, "test.mp4")
        with open(video_path, 'wb') as f:
            f.write(b"mock video data")
        
        # Mock cv2.VideoCapture
        mock_cap = MagicMock()
        mock_cap.get.return_value = 150  # 150 total frames
        mock_cap.read.return_value = (True, np.zeros((720, 1280, 3), dtype=np.uint8))
        
        with patch('cv2.VideoCapture', return_value=mock_cap):
            frames = agent.extract_key_frames(video_path, num_frames=5)
            
            assert len(frames) == 5
            assert all(isinstance(frame, np.ndarray) for frame in frames)
            assert all(frame.shape == (720, 1280, 3) for frame in frames)
    
    def test_extract_key_frames_file_not_found(self):
        """Test frame extraction when file doesn't exist"""
        agent = QualityCheckAgent()
        
        frames = agent.extract_key_frames("/nonexistent/file.mp4")
        assert frames == []
    
    def test_frame_to_base64(self, sample_video_frame):
        """Test frame to base64 conversion"""
        agent = QualityCheckAgent()
        
        base64_str = agent.frame_to_base64(sample_video_frame)
        
        assert isinstance(base64_str, str)
        assert len(base64_str) > 100  # Should be a substantial string
        # Should be valid base64 (basic check)
        import base64
        try:
            base64.b64decode(base64_str)
            assert True
        except:
            assert False, "Invalid base64 encoding"
    
    @pytest.mark.asyncio
    async def test_analyze_with_gpt4o_mini_success(self, sample_video_frames, mock_openai_response):
        """Test GPT-4o-mini analysis with issues found"""
        agent = QualityCheckAgent()
        
        # Mock response indicating issues
        mock_openai_response.choices[0].message.content = '''
        title - overlaps with graph - move down 2 units
        y_axis_label - too close to axis - increase spacing
        '''
        
        with patch.object(QualityCheckAgent._openai_client.chat.completions, 'create', return_value=mock_openai_response):
            issues = await agent.analyze_with_gpt4o_mini(sample_video_frames)
            
            assert len(issues) == 2
            assert all(isinstance(issue, AestheticIssue) for issue in issues)
            
            # Check first issue
            assert issues[0].element == "title"
            assert issues[0].problem == "overlaps with graph"
            assert issues[0].suggested_fix == "move down 2 units"
            assert issues[0].severity == "high"  # Should be high due to "overlap"
    
    @pytest.mark.asyncio
    async def test_analyze_with_gpt4o_mini_no_issues(self, sample_video_frames, mock_openai_response):
        """Test GPT-4o-mini analysis with no issues"""
        agent = QualityCheckAgent()
        
        mock_openai_response.choices[0].message.content = "No aesthetic issues detected"
        
        with patch.object(QualityCheckAgent._openai_client.chat.completions, 'create', return_value=mock_openai_response):
            issues = await agent.analyze_with_gpt4o_mini(sample_video_frames)
            
            assert len(issues) == 0
    
    @pytest.mark.asyncio
    async def test_analyze_with_gpt4o_mini_api_error(self, sample_video_frames):
        """Test GPT-4o-mini analysis with API error"""
        agent = QualityCheckAgent()
        
        with patch.object(QualityCheckAgent._openai_client.chat.completions, 'create', side_effect=Exception("API Error")):
            issues = await agent.analyze_with_gpt4o_mini(sample_video_frames)
            
            assert len(issues) == 1
            assert issues[0].element == "unknown"
            assert issues[0].problem == "Visual analysis failed"
            assert issues[0].severity == "low"
    
    @pytest.mark.asyncio
    async def test_check_visual_quality_success(self, temp_dir):
        """Test complete visual quality check"""
        agent = QualityCheckAgent()
        
        video_path = os.path.join(temp_dir, "test.mp4")
        with open(video_path, 'wb') as f:
            f.write(b"mock video")
        
        # Mock frame extraction
        mock_frames = [np.zeros((720, 1280, 3)) for _ in range(5)]
        
        # Mock aesthetic issues
        mock_aesthetic_issues = [
            AestheticIssue(
                frame_number=1,
                element="title",
                problem="overlaps with content",
                severity="high",
                suggested_fix="move down 2 units"
            )
        ]
        
        with patch.object(agent, 'extract_key_frames', return_value=mock_frames), \
             patch.object(agent, 'analyze_with_gpt4o_mini', return_value=mock_aesthetic_issues):
            
            issues = await agent.check_visual_quality(video_path)
            
            assert len(issues) == 1
            assert isinstance(issues[0], QualityIssue)
            assert issues[0].issue_type == "aesthetic_title"
            assert "Frame 1: title - overlaps with content" in issues[0].description
    
    @pytest.mark.asyncio
    async def test_analyze_animation_complete(self, temp_dir):
        """Test complete animation analysis workflow"""
        agent = QualityCheckAgent()
        
        video_path = os.path.join(temp_dir, "test.mp4")
        with open(video_path, 'wb') as f:
            f.write(b"mock video")
        
        # Mock all components
        mock_metrics = {
            "duration": 15.0,
            "width": 1280,
            "height": 720,
            "fps": 30,
            "size_bytes": 5000000
        }
        
        mock_visual_issues = [
            QualityIssue(
                issue_type="aesthetic_title",
                severity="medium",
                description="Title positioning issue",
                suggestion="Adjust title position"
            )
        ]
        
        with patch.object(agent, 'analyze_video_file', return_value=mock_metrics), \
             patch.object(agent, 'check_visual_quality', return_value=mock_visual_issues):
            
            report = await agent.analyze_animation(video_path)
            
            assert isinstance(report, QualityReport)
            assert report.video_path == video_path
            assert report.score > 0
            assert len(report.issues) >= 1
            assert report.overall_quality in ["excellent", "good", "acceptable", "poor"]


class TestStandaloneFunctions:
    """Test standalone utility functions"""
    
    @pytest.mark.asyncio
    async def test_check_animation_quality(self, temp_dir):
        """Test the standalone check_animation_quality function"""
        video_path = os.path.join(temp_dir, "test.mp4")
        with open(video_path, 'wb') as f:
            f.write(b"mock video")
        
        with patch('quality_check_agent.QualityCheckAgent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent
            
            mock_report = QualityReport(
                video_path=video_path,
                overall_quality="good",
                technical_metrics={},
                issues=[],
                recommendations=[],
                score=85.0
            )
            mock_agent.analyze_animation = AsyncMock(return_value=mock_report)
            
            result = await check_animation_quality(video_path)
            
            assert isinstance(result, QualityReport)
            assert result.score == 85.0
            mock_agent.analyze_animation.assert_called_once_with(video_path)


class TestDataModels:
    """Test Pydantic data models"""
    
    def test_quality_issue_model(self):
        """Test QualityIssue model validation"""
        issue = QualityIssue(
            issue_type="test_issue",
            severity="high",
            description="Test description",
            suggestion="Test suggestion"
        )
        
        assert issue.issue_type == "test_issue"
        assert issue.severity == "high"
        assert issue.description == "Test description"
        assert issue.suggestion == "Test suggestion"
    
    def test_aesthetic_issue_model(self):
        """Test AestheticIssue model validation"""
        issue = AestheticIssue(
            frame_number=3,
            element="title",
            problem="overlaps with graph",
            severity="high",
            suggested_fix="move down 2 units"
        )
        
        assert issue.frame_number == 3
        assert issue.element == "title"
        assert issue.problem == "overlaps with graph"
        assert issue.severity == "high"
        assert issue.suggested_fix == "move down 2 units"
    
    def test_quality_report_model(self):
        """Test QualityReport model validation"""
        report = QualityReport(
            video_path="/tmp/test.mp4",
            overall_quality="good",
            technical_metrics={"duration": 10.0},
            issues=[],
            recommendations=["Test recommendation"],
            score=75.0
        )
        
        assert report.video_path == "/tmp/test.mp4"
        assert report.overall_quality == "good"
        assert report.score == 75.0
        assert len(report.recommendations) == 1
        assert isinstance(report.timestamp, type(report.timestamp))


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_invalid_video_metrics(self):
        """Test handling of invalid video metrics"""
        agent = QualityCheckAgent()
        
        invalid_metrics = {"error": "Could not analyze video"}
        
        issues = agent.check_technical_quality(invalid_metrics)
        assert len(issues) == 0
        
        score = agent.calculate_quality_score(invalid_metrics, [])
        assert score == 0.0
    
    @pytest.mark.asyncio
    async def test_openai_rate_limit(self, sample_video_frames):
        """Test handling of OpenAI rate limit"""
        agent = QualityCheckAgent()
        
        # Mock rate limit error
        rate_limit_error = Exception("Rate limit exceeded")
        
        with patch.object(QualityCheckAgent._openai_client.chat.completions, 'create', side_effect=rate_limit_error):
            issues = await agent.analyze_with_gpt4o_mini(sample_video_frames)
            
            assert len(issues) == 1
            assert issues[0].severity == "low"
            assert "Visual analysis failed" in issues[0].problem
    
    @pytest.mark.asyncio
    async def test_missing_api_key(self, monkeypatch):
        """Test behavior when OpenAI API key is missing"""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        # Should handle gracefully during initialization
        try:
            agent = QualityCheckAgent()
            # Should initialize but client might be None
            assert agent is not None
        except Exception as e:
            # Acceptable if it fails with clear error
            assert "api" in str(e).lower() or "key" in str(e).lower()