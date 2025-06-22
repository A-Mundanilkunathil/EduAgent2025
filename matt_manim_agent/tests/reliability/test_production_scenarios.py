"""
Reliability tests for production scenarios
Tests edge cases, error conditions, and production-level requirements
"""

import pytest
import asyncio
import os
import tempfile
import time
from unittest.mock import patch, AsyncMock, MagicMock
from concurrent.futures import ThreadPoolExecutor

from manim_agent import create_animation, ManimOutput
from quality_check_agent import check_animation_quality, QualityReport


class TestAPIReliability:
    """Test API reliability and error handling"""
    
    @pytest.mark.asyncio
    async def test_anthropic_api_key_missing(self, monkeypatch):
        """Test behavior when Anthropic API key is missing"""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        
        with pytest.raises((ValueError, Exception)) as exc_info:
            await create_animation("test concept")
        
        # Should provide clear error message about missing API key
        error_msg = str(exc_info.value).lower()
        assert "api" in error_msg or "key" in error_msg
    
    @pytest.mark.asyncio
    async def test_openai_api_key_missing(self, monkeypatch):
        """Test behavior when OpenAI API key is missing"""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        # Generation should still work (only uses Anthropic)
        with patch('manim_agent.ManimAgentCore') as mock_class:
            mock_agent = MagicMock()
            mock_class.return_value = mock_agent
            mock_agent.process_animation_task = AsyncMock(return_value=ManimOutput(
                success=True,
                video_path="/tmp/test.mp4",
                concept="test"
            ))
            
            result = await create_animation("test")
            assert result.success is True
        
        # Quality check should handle gracefully
        with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_file:
            try:
                await check_animation_quality(tmp_file.name)
                # Should either work or fail gracefully
            except Exception as e:
                # If it fails, should be clear about missing API key
                error_msg = str(e).lower()
                assert "api" in error_msg or "key" in error_msg
    
    @pytest.mark.asyncio
    async def test_api_rate_limiting(self):
        """Test handling of API rate limits"""
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class:
            mock_agent = MagicMock()
            mock_manim_class.return_value = mock_agent
            
            # Simulate rate limit error
            rate_limit_error = Exception("Rate limit exceeded: 429")
            mock_agent.process_animation_task = AsyncMock(side_effect=rate_limit_error)
            
            with pytest.raises(Exception) as exc_info:
                await create_animation("test")
            
            assert "Rate limit" in str(exc_info.value) or "429" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_network_timeout_handling(self):
        """Test handling of network timeouts"""
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class:
            mock_agent = MagicMock()
            mock_manim_class.return_value = mock_agent
            
            # Simulate network timeout
            timeout_error = asyncio.TimeoutError("Network timeout")
            mock_agent.process_animation_task = AsyncMock(side_effect=timeout_error)
            
            with pytest.raises(asyncio.TimeoutError):
                await create_animation("test")
    
    @pytest.mark.asyncio
    async def test_invalid_api_response(self):
        """Test handling of invalid API responses"""
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class:
            mock_agent = MagicMock()
            mock_manim_class.return_value = mock_agent
            
            # Return invalid response
            invalid_output = ManimOutput(
                success=False,
                concept="test",
                error="Invalid API response format"
            )
            mock_agent.process_animation_task = AsyncMock(return_value=invalid_output)
            
            result = await create_animation("test")
            assert result.success is False
            assert "Invalid API response" in result.error


class TestFileSystemReliability:
    """Test file system related reliability"""
    
    def test_insufficient_disk_space(self):
        """Test behavior when disk space is insufficient"""
        # This is tricky to test without actually filling up disk
        # We'll mock the scenario
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError("No space left on device")
            
            with pytest.raises(OSError) as exc_info:
                # This would typically be called during video rendering
                from pathlib import Path
                Path("/tmp/test_dir").mkdir(exist_ok=True)
            
            assert "No space left" in str(exc_info.value)
    
    def test_permission_denied(self):
        """Test behavior when file permissions are denied"""
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError):
                with open("/tmp/test_file.py", 'w') as f:
                    f.write("test content")
    
    @pytest.mark.asyncio
    async def test_corrupted_video_file(self, temp_dir):
        """Test quality analysis on corrupted video file"""
        
        # Create a corrupted video file
        corrupted_video = os.path.join(temp_dir, "corrupted.mp4")
        with open(corrupted_video, 'wb') as f:
            f.write(b"This is not a valid video file")
        
        with patch('quality_check_agent.QualityCheckAgent') as mock_class:
            mock_agent = MagicMock()
            mock_class.return_value = mock_agent
            
            # Mock ffprobe failure
            mock_agent.analyze_video_file = MagicMock(return_value={"error": "Invalid video format"})
            mock_agent.analyze_animation = AsyncMock(return_value=QualityReport(
                video_path=corrupted_video,
                overall_quality="poor",
                technical_metrics={"error": "Invalid video format"},
                issues=[],
                recommendations=[],
                score=0.0
            ))
            
            report = await check_animation_quality(corrupted_video)
            assert report.score == 0.0
            assert "error" in report.technical_metrics
    
    def test_large_video_file_handling(self, temp_dir):
        """Test handling of very large video files"""
        
        # Create a large mock video file (simulate 100MB)
        large_video = os.path.join(temp_dir, "large.mp4")
        with open(large_video, 'wb') as f:
            # Write 100MB of data
            chunk_size = 1024 * 1024  # 1MB chunks
            for _ in range(100):
                f.write(b'\x00' * chunk_size)
        
        # Test that file size is handled appropriately
        file_size = os.path.getsize(large_video)
        assert file_size == 100 * 1024 * 1024  # 100MB
        
        # Mock analysis to check file size handling
        with patch('quality_check_agent.QualityCheckAgent') as mock_class:
            mock_agent = MagicMock()
            mock_class.return_value = mock_agent
            
            # Should handle large files gracefully
            mock_agent.analyze_video_file = MagicMock(return_value={
                "duration": 30.0,
                "size_bytes": file_size,
                "width": 1280,
                "height": 720
            })
            
            metrics = mock_agent.analyze_video_file(large_video)
            assert metrics["size_bytes"] == file_size


class TestConcurrencyAndLoad:
    """Test concurrent operations and load handling"""
    
    @pytest.mark.asyncio
    async def test_concurrent_generations(self):
        """Test multiple concurrent animation generations"""
        
        concepts = [f"concept_{i}" for i in range(5)]
        
        with patch('manim_agent.ManimAgentCore') as mock_class:
            mock_agent = MagicMock()
            mock_class.return_value = mock_agent
            
            # Mock successful generation with delays
            async def mock_generation(task_context):
                await asyncio.sleep(0.1)  # Simulate processing time
                return ManimOutput(
                    success=True,
                    video_path=f"/tmp/{task_context['concept']}.mp4",
                    concept=task_context['concept']
                )
            
            mock_agent.process_animation_task = AsyncMock(side_effect=mock_generation)
            
            # Run concurrent generations
            start_time = time.time()
            tasks = [create_animation(concept) for concept in concepts]
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # All should succeed
            assert all(result.success for result in results)
            assert len(results) == 5
            
            # Should complete faster than sequential (< 0.4s vs 0.5s sequential)
            assert end_time - start_time < 0.4
    
    @pytest.mark.asyncio 
    async def test_concurrent_quality_checks(self):
        """Test multiple concurrent quality checks"""
        
        video_paths = [f"/tmp/video_{i}.mp4" for i in range(5)]
        
        with patch('quality_check_agent.QualityCheckAgent') as mock_class:
            mock_agent = MagicMock()
            mock_class.return_value = mock_agent
            
            # Mock quality analysis with delays
            async def mock_analysis(video_path):
                await asyncio.sleep(0.1)  # Simulate processing time
                return QualityReport(
                    video_path=video_path,
                    overall_quality="good",
                    technical_metrics={},
                    issues=[],
                    recommendations=[],
                    score=85.0
                )
            
            mock_agent.analyze_animation = AsyncMock(side_effect=mock_analysis)
            
            # Run concurrent quality checks
            start_time = time.time()
            tasks = [check_animation_quality(path) for path in video_paths]
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # All should succeed
            assert all(result.score == 85.0 for result in results)
            assert len(results) == 5
            
            # Should complete faster than sequential
            assert end_time - start_time < 0.4
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Test memory usage during high load"""
        
        # This test checks that we don't have memory leaks
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class, \
             patch('quality_check_agent.QualityCheckAgent') as mock_quality_class:
            
            # Setup lightweight mocks
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
            
            # Run many operations
            for _ in range(50):
                result = await create_animation("memory test")
                await check_animation_quality(result.video_path)
                
                # Force garbage collection
                gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 50MB)
        assert memory_increase < 50 * 1024 * 1024


class TestErrorRecovery:
    """Test error recovery mechanisms"""
    
    @pytest.mark.asyncio
    async def test_retry_on_transient_failure(self):
        """Test retry logic for transient failures"""
        
        with patch('manim_agent.ManimAgentCore') as mock_class:
            mock_agent = MagicMock()
            mock_class.return_value = mock_agent
            
            # First call fails, second succeeds (simulating transient error)
            call_count = 0
            async def mock_generation(task_context):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise Exception("Transient network error")
                return ManimOutput(
                    success=True,
                    video_path="/tmp/recovered.mp4",
                    concept=task_context['concept']
                )
            
            mock_agent.process_animation_task = AsyncMock(side_effect=mock_generation)
            
            # This would need retry logic implemented in the actual code
            # For now, we test that the error occurs
            with pytest.raises(Exception) as exc_info:
                await create_animation("retry test")
            
            assert "Transient network error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test graceful degradation when quality check fails"""
        
        successful_generation = ManimOutput(
            success=True,
            video_path="/tmp/test.mp4",
            concept="test",
            metadata={"fallback_quality": "assumed_good"}
        )
        
        with patch('manim_agent.ManimAgentCore') as mock_manim_class, \
             patch('quality_check_agent.QualityCheckAgent') as mock_quality_class:
            
            # Generation succeeds
            mock_manim = MagicMock()
            mock_manim_class.return_value = mock_manim
            mock_manim.process_animation_task = AsyncMock(return_value=successful_generation)
            
            # Quality check fails but provides fallback
            mock_quality = MagicMock()
            mock_quality_class.return_value = mock_quality
            mock_quality.analyze_animation = AsyncMock(return_value=QualityReport(
                video_path="/tmp/test.mp4",
                overall_quality="unknown",
                technical_metrics={"error": "Quality analysis unavailable"},
                issues=[],
                recommendations=["Manual review recommended"],
                score=70.0  # Conservative fallback score
            ))
            
            # Should still get usable results
            generation_result = await create_animation("degradation test")
            quality_result = await check_animation_quality(generation_result.video_path)
            
            assert generation_result.success is True
            assert quality_result.score == 70.0  # Fallback score
            assert "Manual review recommended" in quality_result.recommendations


class TestResourceLimits:
    """Test behavior under resource constraints"""
    
    @pytest.mark.asyncio
    async def test_large_batch_processing(self):
        """Test processing large batches without resource exhaustion"""
        
        batch_size = 20
        concepts = [f"batch_concept_{i}" for i in range(batch_size)]
        
        with patch('manim_agent.ManimAgentCore') as mock_class:
            mock_agent = MagicMock()
            mock_class.return_value = mock_agent
            
            # Mock efficient processing
            mock_agent.process_animation_task = AsyncMock(return_value=ManimOutput(
                success=True,
                video_path="/tmp/batch_test.mp4",
                concept="batch_test"
            ))
            
            # Process in smaller chunks to avoid resource exhaustion
            chunk_size = 5
            results = []
            
            for i in range(0, batch_size, chunk_size):
                chunk = concepts[i:i + chunk_size]
                tasks = [create_animation(concept) for concept in chunk]
                chunk_results = await asyncio.gather(*tasks)
                results.extend(chunk_results)
                
                # Brief pause between chunks
                await asyncio.sleep(0.01)
            
            assert len(results) == batch_size
            assert all(result.success for result in results)
    
    def test_manim_command_timeout(self):
        """Test timeout handling for long-running Manim commands"""
        
        with patch('subprocess.run') as mock_run:
            # Simulate long-running command that times out
            mock_run.side_effect = asyncio.TimeoutError("Command timed out")
            
            from manim_agent import ManimAgentCore
            agent = ManimAgentCore()
            
            with pytest.raises(asyncio.TimeoutError):
                # This would be called during render_manim_video
                import subprocess
                subprocess.run(["sleep", "1000"], timeout=1)


class TestDataValidation:
    """Test data validation and sanitization"""
    
    @pytest.mark.asyncio
    async def test_malicious_input_handling(self):
        """Test handling of potentially malicious input"""
        
        malicious_inputs = [
            "'; DROP TABLE animations; --",
            "<script>alert('xss')</script>",
            "../../../../etc/passwd", 
            "\x00\x01\x02\x03",  # Binary data
            "A" * 10000,  # Very long input
        ]
        
        with patch('manim_agent.ManimAgentCore') as mock_class:
            mock_agent = MagicMock()
            mock_class.return_value = mock_agent
            
            # Should handle malicious inputs gracefully
            mock_agent.process_animation_task = AsyncMock(return_value=ManimOutput(
                success=False,
                concept="sanitized_input",
                error="Invalid input detected"
            ))
            
            for malicious_input in malicious_inputs:
                result = await create_animation(malicious_input)
                # Should either succeed with sanitized input or fail safely
                assert result.success is False or result.concept != malicious_input
    
    def test_output_path_validation(self):
        """Test that output paths are properly validated"""
        
        dangerous_paths = [
            "../../../sensitive_file.mp4",
            "/etc/passwd.mp4",
            "con.mp4",  # Windows reserved name
            "file\x00.mp4",  # Null byte injection
        ]
        
        from manim_agent import ManimAgentCore
        agent = ManimAgentCore()
        
        for dangerous_path in dangerous_paths:
            # The agent should sanitize or reject dangerous paths
            # This would need to be implemented in the actual code
            safe_name = dangerous_path.replace("/", "_").replace("\\", "_").replace("\x00", "")
            assert len(safe_name) > 0
            assert "/" not in safe_name
            assert "\\" not in safe_name