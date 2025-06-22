"""
Pytest configuration and shared fixtures
"""

import pytest
import os
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
import cv2
import numpy as np

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from manim_agent import ManimAgentCore, ManimOutput
from quality_check_agent import QualityCheckAgent, QualityReport, QualityIssue, AestheticIssue


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_manim_code():
    """Sample valid Manim code for testing"""
    return '''
from manim import *

class TestScene(Scene):
    def construct(self):
        title = Text("Test Animation")
        self.play(Create(title))
        self.wait(2)
'''


@pytest.fixture
def sample_video_frame():
    """Create a sample video frame for testing"""
    # Create a simple 720p frame with some content
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    
    # Add some geometric shapes to simulate math content
    cv2.rectangle(frame, (100, 100), (200, 200), (255, 255, 255), 2)  # White rectangle
    cv2.line(frame, (0, 360), (1280, 360), (128, 128, 128), 2)  # Horizontal axis
    cv2.line(frame, (640, 0), (640, 720), (128, 128, 128), 2)  # Vertical axis
    
    # Add some text-like regions
    cv2.putText(frame, "y = x²", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, "Title", (600, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
    
    return frame


@pytest.fixture
def sample_video_frames(sample_video_frame):
    """Create multiple sample frames"""
    frames = []
    for i in range(5):
        # Create variations of the base frame
        frame = sample_video_frame.copy()
        # Add frame number
        cv2.putText(frame, f"Frame {i+1}", (50, 650), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        frames.append(frame)
    return frames


@pytest.fixture
def mock_manim_agent():
    """Create a mock Manim agent for testing"""
    agent = MagicMock(spec=ManimAgentCore)
    
    # Mock successful generation
    agent.generate_manim_code = AsyncMock(return_value="mock_manim_code")
    agent.render_manim_video = AsyncMock(return_value={
        "success": True,
        "video_path": "/tmp/test_video.mp4",
        "duration": 10.0
    })
    
    return agent


@pytest.fixture
def mock_quality_agent():
    """Create a mock Quality agent for testing"""
    agent = MagicMock(spec=QualityCheckAgent)
    
    # Mock analysis methods
    agent.analyze_video_file = MagicMock(return_value={
        "duration": 10.0,
        "width": 1280,
        "height": 720,
        "fps": 30,
        "size_bytes": 1000000
    })
    
    agent.extract_key_frames = MagicMock(return_value=[np.zeros((720, 1280, 3))])
    
    return agent


@pytest.fixture
def sample_quality_report():
    """Create a sample quality report"""
    return QualityReport(
        video_path="/tmp/test_video.mp4",
        overall_quality="good",
        technical_metrics={
            "duration": 10.0,
            "width": 1280,
            "height": 720,
            "fps": 30
        },
        issues=[
            QualityIssue(
                issue_type="test_issue",
                severity="medium",
                description="Sample test issue",
                suggestion="Fix the test issue"
            )
        ],
        recommendations=["Test recommendation"],
        score=75.0
    )


@pytest.fixture
def sample_aesthetic_issues():
    """Create sample aesthetic issues"""
    return [
        AestheticIssue(
            frame_number=1,
            element="title",
            problem="overlaps with graph",
            severity="high",
            suggested_fix="move down 2 units"
        ),
        AestheticIssue(
            frame_number=2,
            element="y_axis_label",
            problem="too close to axis",
            severity="medium",
            suggested_fix="increase spacing"
        )
    ]


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response"""
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = '''
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Generated Animation")
        self.play(Create(title))
        self.wait(2)
'''
    return mock_response


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = "title - overlaps with graph - move down 2 units"
    return mock_response


# Event loop fixture for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Environment setup
@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    
    # Ensure we don't accidentally make real API calls in tests
    monkeypatch.setenv("TESTING", "true")