"""
Integration tests for the two-agent workflow
Tests the complete pipeline: Generation → Quality Check
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import tempfile
import os

from manim_agent import create_animation, ManimOutput
from quality_check_agent import check_animation_quality, QualityReport


class TestTwoAgentWorkflow:
    """Test the complete two-agent system workflow"""
    
    @pytest.mark.asyncio
    async def test_successful_generation_and_analysis(self):
        """Test successful generation followed by quality analysis"""
        
        # Mock generation result
        mock_generation_result = ManimOutput(
            success=True,
            video_path="/tmp/test_animation.mp4",
            duration=15.0,
            concept="sine wave",
            manim_code="mock_manim_code",
            visual_elements=["title", "axes", "graph"]
        )
        
        # Mock quality report
        mock_quality_report = QualityReport(
            video_path="/tmp/test_animation.mp4",
            overall_quality="good",
            technical_metrics={
                "duration": 15.0,
                "width": 1280,
                "height": 720,
                "fps": 30
            },
            issues=[],
            recommendations=["Animation meets quality standards"],
            score=85.0
        )
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class, \
             patch('quality_check_agent.QualityCheckAgent') as mock_quality_class:
            
            # Setup mocks
            mock_manim = MagicMock()
            mock_manim_class.return_value = mock_manim
            mock_manim.process_animation_task = AsyncMock(return_value=mock_generation_result)
            
            mock_quality = MagicMock()
            mock_quality_class.return_value = mock_quality
            mock_quality.analyze_animation = AsyncMock(return_value=mock_quality_report)
            
            # Test the workflow
            # Step 1: Generate animation
            generation_result = await create_animation("sine wave")
            
            assert generation_result.success is True
            assert generation_result.concept == "sine wave"
            assert generation_result.video_path == "/tmp/test_animation.mp4"
            
            # Step 2: Analyze quality
            quality_result = await check_animation_quality(generation_result.video_path)
            
            assert isinstance(quality_result, QualityReport)
            assert quality_result.score == 85.0
            assert quality_result.overall_quality == "good"
            assert quality_result.video_path == generation_result.video_path
    
    @pytest.mark.asyncio
    async def test_generation_failure_workflow(self):
        """Test workflow when generation fails"""
        
        mock_generation_result = ManimOutput(
            success=False,
            concept="invalid concept",
            error="Failed to generate Manim code"
        )
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class:
            mock_manim = MagicMock()
            mock_manim_class.return_value = mock_manim
            mock_manim.process_animation_task = AsyncMock(return_value=mock_generation_result)
            
            # Test generation failure
            result = await create_animation("invalid concept")
            
            assert result.success is False
            assert result.error is not None
            assert result.video_path is None
            
            # Should not proceed to quality check
            # (In real workflow, user would check success before proceeding)
    
    @pytest.mark.asyncio
    async def test_quality_analysis_finds_issues(self):
        """Test workflow when quality analysis finds issues"""
        
        # Mock generation with successful result
        mock_generation_result = ManimOutput(
            success=True,
            video_path="/tmp/problematic_video.mp4",
            duration=12.0,
            concept="complex plot"
        )
        
        # Mock quality report with issues
        mock_quality_report = QualityReport(
            video_path="/tmp/problematic_video.mp4",
            overall_quality="acceptable",
            technical_metrics={
                "duration": 12.0,
                "width": 1280,
                "height": 720,
                "fps": 30
            },
            issues=[
                {
                    "issue_type": "aesthetic_title",
                    "severity": "high",
                    "description": "Title overlaps with graph",
                    "suggestion": "Move title down by 2 units"
                },
                {
                    "issue_type": "aesthetic_y_axis_label", 
                    "severity": "medium",
                    "description": "Y-axis label too close to axis",
                    "suggestion": "Increase spacing from axis"
                }
            ],
            recommendations=[
                "Address overlapping elements",
                "Improve spacing between components"
            ],
            score=65.0
        )
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class, \
             patch('quality_check_agent.QualityCheckAgent') as mock_quality_class:
            
            # Setup mocks
            mock_manim = MagicMock()
            mock_manim_class.return_value = mock_manim
            mock_manim.process_animation_task = AsyncMock(return_value=mock_generation_result)
            
            mock_quality = MagicMock()
            mock_quality_class.return_value = mock_quality
            mock_quality.analyze_animation = AsyncMock(return_value=mock_quality_report)
            
            # Test workflow with issues
            generation_result = await create_animation("complex plot")
            assert generation_result.success is True
            
            quality_result = await check_animation_quality(generation_result.video_path)
            
            assert quality_result.score == 65.0
            assert quality_result.overall_quality == "acceptable"
            assert len(quality_result.issues) == 2
            
            # Check specific issues
            assert any("overlaps with graph" in str(issue) for issue in quality_result.issues)
            assert any("too close to axis" in str(issue) for issue in quality_result.issues)
    
    @pytest.mark.asyncio
    async def test_iterative_improvement_workflow(self):
        """Test iterative improvement workflow"""
        
        # Simulate first generation with issues
        first_result = ManimOutput(
            success=True,
            video_path="/tmp/first_attempt.mp4",
            concept="quadratic function"
        )
        
        first_quality = QualityReport(
            video_path="/tmp/first_attempt.mp4",
            overall_quality="poor",
            technical_metrics={},
            issues=[
                {"issue_type": "aesthetic_title", "severity": "high", "description": "Title overlaps"}
            ],
            recommendations=["Fix title positioning"],
            score=45.0
        )
        
        # Simulate improved generation
        second_result = ManimOutput(
            success=True,
            video_path="/tmp/improved_attempt.mp4",
            concept="quadratic function"
        )
        
        second_quality = QualityReport(
            video_path="/tmp/improved_attempt.mp4",
            overall_quality="good",
            technical_metrics={},
            issues=[],
            recommendations=["Animation meets quality standards"],
            score=85.0
        )
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class, \
             patch('quality_check_agent.QualityCheckAgent') as mock_quality_class:
            
            mock_manim = MagicMock()
            mock_manim_class.return_value = mock_manim
            
            mock_quality = MagicMock()
            mock_quality_class.return_value = mock_quality
            
            # First iteration
            mock_manim.process_animation_task = AsyncMock(return_value=first_result)
            mock_quality.analyze_animation = AsyncMock(return_value=first_quality)
            
            result1 = await create_animation("quadratic function")
            quality1 = await check_animation_quality(result1.video_path)
            
            assert result1.success is True
            assert quality1.score == 45.0  # Poor quality
            
            # Second iteration (with improvements)
            mock_manim.process_animation_task = AsyncMock(return_value=second_result)
            mock_quality.analyze_animation = AsyncMock(return_value=second_quality)
            
            # In real workflow, you'd modify the generation parameters based on feedback
            result2 = await create_animation(
                "quadratic function",
                style_direction={"title_position": "lower", "spacing": "generous"}
            )
            quality2 = await check_animation_quality(result2.video_path)
            
            assert result2.success is True
            assert quality2.score == 85.0  # Improved quality
            assert len(quality2.issues) == 0
    
    @pytest.mark.asyncio
    async def test_batch_processing_workflow(self):
        """Test batch processing multiple animations"""
        
        concepts = ["sine wave", "cosine wave", "tangent function"]
        results = []
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class, \
             patch('quality_check_agent.QualityCheckAgent') as mock_quality_class:
            
            # Setup mocks for batch processing
            mock_manim = MagicMock()
            mock_manim_class.return_value = mock_manim
            
            mock_quality = MagicMock()
            mock_quality_class.return_value = mock_quality
            
            # Mock different results for each concept
            generation_results = [
                ManimOutput(success=True, video_path=f"/tmp/{concept.replace(' ', '_')}.mp4", concept=concept)
                for concept in concepts
            ]
            
            quality_results = [
                QualityReport(
                    video_path=f"/tmp/{concept.replace(' ', '_')}.mp4",
                    overall_quality="good",
                    technical_metrics={},
                    issues=[],
                    recommendations=[],
                    score=80.0 + i * 5  # Varying scores
                )
                for i, concept in enumerate(concepts)
            ]
            
            mock_manim.process_animation_task = AsyncMock(side_effect=generation_results)
            mock_quality.analyze_animation = AsyncMock(side_effect=quality_results)
            
            # Process batch
            for i, concept in enumerate(concepts):
                # Generate
                gen_result = await create_animation(concept)
                assert gen_result.success is True
                
                # Analyze quality
                quality_result = await check_animation_quality(gen_result.video_path)
                
                results.append({
                    'concept': concept,
                    'generation': gen_result,
                    'quality': quality_result
                })
            
            # Verify batch results
            assert len(results) == 3
            assert all(r['generation'].success for r in results)
            assert all(r['quality'].score >= 80.0 for r in results)
            
            # Check that scores vary as expected
            scores = [r['quality'].score for r in results]
            assert scores == [80.0, 85.0, 90.0]


class TestWorkflowTiming:
    """Test timing and performance aspects of the workflow"""
    
    @pytest.mark.asyncio
    async def test_workflow_performance(self):
        """Test that workflow completes within reasonable time"""
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class, \
             patch('quality_check_agent.QualityCheckAgent') as mock_quality_class:
            
            # Setup fast mocks
            mock_manim = MagicMock()
            mock_manim_class.return_value = mock_manim
            mock_manim.process_animation_task = AsyncMock(return_value=ManimOutput(
                success=True,
                video_path="/tmp/test.mp4",
                concept="test"
            ))
            
            mock_quality = MagicMock()
            mock_quality_class.return_value = mock_quality
            mock_quality.analyze_animation = AsyncMock(return_value=QualityReport(
                video_path="/tmp/test.mp4",
                overall_quality="good",
                technical_metrics={},
                issues=[],
                recommendations=[],
                score=85.0
            ))
            
            start_time = asyncio.get_event_loop().time()
            
            # Run workflow
            result = await create_animation("performance test")
            quality = await check_animation_quality(result.video_path)
            
            end_time = asyncio.get_event_loop().time()
            total_time = end_time - start_time
            
            # Should complete very quickly with mocks (< 1 second)
            assert total_time < 1.0
            assert result.success is True
            assert quality.score == 85.0


class TestWorkflowErrorHandling:
    """Test error handling in the complete workflow"""
    
    @pytest.mark.asyncio
    async def test_api_failure_handling(self):
        """Test workflow behavior when APIs fail"""
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class:
            mock_manim = MagicMock()
            mock_manim_class.return_value = mock_manim
            
            # Simulate API failure
            mock_manim.process_animation_task = AsyncMock(side_effect=Exception("API connection failed"))
            
            with pytest.raises(Exception) as exc_info:
                await create_animation("test concept")
            
            assert "API connection failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_partial_workflow_failure(self):
        """Test when generation succeeds but quality check fails"""
        
        successful_generation = ManimOutput(
            success=True,
            video_path="/tmp/test.mp4",
            concept="test"
        )
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class, \
             patch('quality_check_agent.QualityCheckAgent') as mock_quality_class:
            
            # Generation succeeds
            mock_manim = MagicMock()
            mock_manim_class.return_value = mock_manim
            mock_manim.process_animation_task = AsyncMock(return_value=successful_generation)
            
            # Quality check fails
            mock_quality = MagicMock()
            mock_quality_class.return_value = mock_quality
            mock_quality.analyze_animation = AsyncMock(side_effect=Exception("Quality analysis failed"))
            
            # Generation should succeed
            result = await create_animation("test")
            assert result.success is True
            
            # Quality check should fail
            with pytest.raises(Exception) as exc_info:
                await check_animation_quality(result.video_path)
            
            assert "Quality analysis failed" in str(exc_info.value)


class TestWorkflowDataFlow:
    """Test data flow between agents"""
    
    @pytest.mark.asyncio
    async def test_context_preservation(self):
        """Test that context is preserved through the workflow"""
        
        input_context = {
            "concept": "complex function with context",
            "script_context": "Show the real and imaginary parts",
            "duration": 25.0,
            "style_direction": {"theme": "dark", "color_scheme": {"primary": "#FF6B6B"}}
        }
        
        expected_output = ManimOutput(
            success=True,
            video_path="/tmp/complex_function.mp4",
            duration=25.0,
            concept="complex function with context",
            visual_elements=["title", "axes", "real_part", "imaginary_part"]
        )
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class:
            mock_manim = MagicMock()
            mock_manim_class.return_value = mock_manim
            mock_manim.process_animation_task = AsyncMock(return_value=expected_output)
            
            result = await create_animation(**input_context)
            
            # Verify context was passed correctly
            call_args = mock_manim.process_animation_task.call_args[0][0]
            
            assert call_args["concept"] == input_context["concept"]
            assert call_args["script_context"] == input_context["script_context"]
            assert call_args["duration"] == input_context["duration"]
            assert call_args["style_direction"] == input_context["style_direction"]
            
            # Verify output preserves context
            assert result.concept == input_context["concept"]
            assert result.duration == input_context["duration"]
    
    @pytest.mark.asyncio
    async def test_metadata_flow(self):
        """Test that metadata flows correctly between agents"""
        
        generation_output = ManimOutput(
            success=True,
            video_path="/tmp/metadata_test.mp4",
            duration=18.0,
            concept="metadata test",
            manim_code="# Generated Manim code",
            visual_elements=["title", "graph", "equation"],
            metadata={"render_time": 12.5, "complexity": "medium"}
        )
        
        quality_report = QualityReport(
            video_path="/tmp/metadata_test.mp4",
            overall_quality="excellent",
            technical_metrics={
                "duration": 18.0,
                "width": 1280,
                "height": 720,
                "fps": 30
            },
            issues=[],
            recommendations=["Excellent animation quality"],
            score=95.0
        )
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class, \
             patch('quality_check_agent.QualityCheckAgent') as mock_quality_class:
            
            mock_manim = MagicMock()
            mock_manim_class.return_value = mock_manim
            mock_manim.process_animation_task = AsyncMock(return_value=generation_output)
            
            mock_quality = MagicMock()
            mock_quality_class.return_value = mock_quality
            mock_quality.analyze_animation = AsyncMock(return_value=quality_report)
            
            # Test data flow
            gen_result = await create_animation("metadata test")
            quality_result = await check_animation_quality(gen_result.video_path)
            
            # Verify metadata preservation
            assert gen_result.metadata["render_time"] == 12.5
            assert gen_result.metadata["complexity"] == "medium"
            assert len(gen_result.visual_elements) == 3
            
            # Verify technical metrics match
            assert quality_result.technical_metrics["duration"] == gen_result.duration
            assert quality_result.video_path == gen_result.video_path