"""
Sample test data and fixtures
"""

# Sample Manim code snippets for testing
SAMPLE_MANIM_CODES = {
    "simple": '''
from manim import *

class SimpleScene(Scene):
    def construct(self):
        title = Text("Simple Animation")
        self.play(Create(title))
        self.wait(2)
''',
    
    "with_math": '''
from manim import *

class MathScene(Scene):
    def construct(self):
        equation = MathTex("y = x^2")
        self.play(Write(equation))
        self.wait(2)
''',
    
    "complex": '''
from manim import *

class ComplexScene(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-1, 9, 1],
            axis_config={"color": BLUE}
        )
        
        func = axes.plot(lambda x: x**2, color=RED)
        equation = MathTex("f(x) = x^2").to_corner(UL)
        
        self.play(Create(axes))
        self.play(Create(func))
        self.play(Write(equation))
        self.wait(2)
''',
    
    "invalid": '''
from manim import *

class InvalidScene(Scene):
    def construct(self):
        # This will cause errors
        invalid_object = NonExistentClass()
        self.play(Create(invalid_object))
'''
}

# Sample task contexts for testing
SAMPLE_TASK_CONTEXTS = {
    "basic": {
        "concept": "sine wave"
    },
    
    "with_context": {
        "concept": "quadratic function",
        "script_context": "Show how the parabola opens upward",
        "duration": 15.0
    },
    
    "full_context": {
        "concept": "derivative visualization",
        "script_context": "Demonstrate how the tangent line represents the derivative",
        "duration": 20.0,
        "style_direction": {
            "color_scheme": {"function": "#3B82F6", "tangent": "#EF4444"},
            "animation_speed": "slow"
        },
        "sync_points": [
            {"time": 5.0, "emphasis": "show_function"},
            {"time": 10.0, "emphasis": "show_tangent"},
            {"time": 15.0, "emphasis": "show_derivative"}
        ]
    }
}

# Sample quality issues for testing
SAMPLE_QUALITY_ISSUES = [
    {
        "issue_type": "aesthetic_title",
        "severity": "high", 
        "description": "Title overlaps with graph content",
        "suggestion": "Move title down by 2 units"
    },
    {
        "issue_type": "aesthetic_y_axis_label",
        "severity": "medium",
        "description": "Y-axis label too close to axis line", 
        "suggestion": "Increase spacing from axis"
    },
    {
        "issue_type": "duration_too_short",
        "severity": "high",
        "description": "Animation duration is only 2.5s, minimum recommended is 3.0s",
        "suggestion": "Extend animation with more content or slower pacing"
    },
    {
        "issue_type": "low_resolution",
        "severity": "high",
        "description": "Resolution 480x360 is below minimum (640, 480)",
        "suggestion": "Render at higher resolution for better quality"
    }
]

# Sample video metadata for testing
SAMPLE_VIDEO_METRICS = {
    "good_video": {
        "duration": 15.0,
        "width": 1280,
        "height": 720,
        "fps": 30,
        "size_bytes": 5000000,
        "codec": "h264"
    },
    
    "poor_video": {
        "duration": 2.0,  # Too short
        "width": 400,     # Too low resolution
        "height": 300,
        "fps": 15,        # Too low fps
        "size_bytes": 200000000,  # Too large
        "codec": "h264"
    },
    
    "corrupted_video": {
        "error": "Could not analyze video file"
    }
}

# Sample aesthetic issues for GPT-4o-mini responses
SAMPLE_GPT_RESPONSES = {
    "no_issues": "No aesthetic issues detected",
    
    "with_issues": '''title - overlaps with graph - move down 2 units
y_axis_label - too close to axis - increase spacing by 1 unit
equation - positioned awkwardly - move to upper left corner''',
    
    "single_issue": "title - positioned too high - move down 1-2 units",
    
    "complex_issues": '''1. Title - overlaps with content - move down 2 units for better visibility
2. Y-axis label - overlaps with graph - move left 1 unit to avoid interference  
3. X-axis label - too close to bottom edge - move up 0.5 units
4. Equation text - overlaps with function curve - reposition to top-right corner'''
}

# Sample animation outputs for testing
SAMPLE_ANIMATION_OUTPUTS = {
    "successful": {
        "success": True,
        "video_path": "/tmp/test_animation.mp4",
        "duration": 15.0,
        "concept": "sine wave",
        "manim_code": SAMPLE_MANIM_CODES["simple"],
        "visual_elements": ["title", "axes", "graph"],
        "metadata": {"render_time": 8.5, "complexity": "medium"}
    },
    
    "failed": {
        "success": False,
        "concept": "invalid concept",
        "error": "Failed to generate valid Manim code",
        "video_path": None,
        "duration": None
    }
}

# Sample quality reports for testing
SAMPLE_QUALITY_REPORTS = {
    "excellent": {
        "video_path": "/tmp/excellent_video.mp4",
        "overall_quality": "excellent",
        "technical_metrics": SAMPLE_VIDEO_METRICS["good_video"],
        "issues": [],
        "recommendations": ["Animation meets all quality standards"],
        "score": 95.0
    },
    
    "with_issues": {
        "video_path": "/tmp/problematic_video.mp4", 
        "overall_quality": "acceptable",
        "technical_metrics": SAMPLE_VIDEO_METRICS["good_video"],
        "issues": SAMPLE_QUALITY_ISSUES[:2],  # First 2 issues
        "recommendations": [
            "Address overlapping elements",
            "Improve spacing between components"
        ],
        "score": 65.0
    },
    
    "poor": {
        "video_path": "/tmp/poor_video.mp4",
        "overall_quality": "poor", 
        "technical_metrics": SAMPLE_VIDEO_METRICS["poor_video"],
        "issues": SAMPLE_QUALITY_ISSUES,  # All issues
        "recommendations": [
            "Fix technical quality issues first",
            "Address all aesthetic problems",
            "Consider regenerating the animation"
        ],
        "score": 25.0
    }
}

# Test scenarios for integration testing
TEST_SCENARIOS = {
    "happy_path": {
        "description": "Normal workflow with good results",
        "input": SAMPLE_TASK_CONTEXTS["with_context"],
        "expected_generation": SAMPLE_ANIMATION_OUTPUTS["successful"],
        "expected_quality": SAMPLE_QUALITY_REPORTS["excellent"]
    },
    
    "generation_failure": {
        "description": "Generation fails due to invalid input",
        "input": {"concept": "invalid/malicious*concept"},
        "expected_generation": SAMPLE_ANIMATION_OUTPUTS["failed"],
        "expected_quality": None  # Should not reach quality check
    },
    
    "quality_issues": {
        "description": "Generation succeeds but quality issues found",
        "input": SAMPLE_TASK_CONTEXTS["basic"],
        "expected_generation": SAMPLE_ANIMATION_OUTPUTS["successful"],
        "expected_quality": SAMPLE_QUALITY_REPORTS["with_issues"]
    },
    
    "poor_quality": {
        "description": "Multiple quality issues detected",
        "input": SAMPLE_TASK_CONTEXTS["basic"],
        "expected_generation": SAMPLE_ANIMATION_OUTPUTS["successful"],
        "expected_quality": SAMPLE_QUALITY_REPORTS["poor"]
    }
}

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "generation_time_max": 30.0,  # seconds
    "quality_check_time_max": 15.0,  # seconds
    "total_workflow_time_max": 45.0,  # seconds
    "memory_usage_max": 500 * 1024 * 1024,  # 500MB
    "concurrent_operations_max": 5
}

# Error scenarios for reliability testing
ERROR_SCENARIOS = {
    "api_timeout": {
        "error_type": "TimeoutError",
        "message": "API request timed out",
        "expected_behavior": "Should fail gracefully with clear error message"
    },
    
    "rate_limit": {
        "error_type": "RateLimitError", 
        "message": "Rate limit exceeded",
        "expected_behavior": "Should provide retry guidance"
    },
    
    "invalid_api_key": {
        "error_type": "AuthenticationError",
        "message": "Invalid API key",
        "expected_behavior": "Should provide clear configuration instructions"
    },
    
    "network_error": {
        "error_type": "ConnectionError",
        "message": "Network connection failed",
        "expected_behavior": "Should suggest network troubleshooting"
    }
}