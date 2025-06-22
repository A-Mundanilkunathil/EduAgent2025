"""
Unit tests for Manim Agent
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import tempfile
import os

from manim_agent import ManimAgentCore, create_animation, ManimOutput


class TestManimAgentCore:
    """Test the core Manim agent functionality"""
    
    def test_init(self):
        """Test agent initialization"""
        agent = ManimAgentCore()
        assert agent.client is not None
        assert "You are an expert Manim developer" in agent.system_prompt
        assert "VISUAL QUALITY REQUIREMENTS" in agent.system_prompt
    
    @pytest.mark.asyncio
    async def test_generate_manim_code_basic(self, mock_anthropic_response):
        """Test basic Manim code generation"""
        agent = ManimAgentCore()
        
        with patch.object(agent.client.messages, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_anthropic_response
            
            task_context = {"concept": "sine wave"}
            code = await agent.generate_manim_code(task_context)
            
            assert "class GeneratedScene(Scene)" in code
            assert "def construct(self)" in code
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_manim_code_with_context(self, mock_anthropic_response):
        """Test Manim code generation with rich context"""
        agent = ManimAgentCore()
        
        with patch.object(agent.client.messages, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_anthropic_response
            
            task_context = {
                "concept": "quadratic function",
                "script_context": "Show the parabola opening upward",
                "duration": 15.0,
                "style_direction": {"color_scheme": {"primary": "#3B82F6"}}
            }
            
            code = await agent.generate_manim_code(task_context)
            
            # Verify the prompt includes context
            call_args = mock_create.call_args
            prompt = call_args[1]['messages'][0]['content']
            
            assert "quadratic function" in prompt
            assert "Show the parabola opening upward" in prompt
            assert "15.0 seconds" in prompt
            assert "#3B82F6" in prompt
    
    @pytest.mark.asyncio
    async def test_render_manim_video_success(self, sample_manim_code, temp_dir):
        """Test successful video rendering"""
        agent = ManimAgentCore()
        
        with patch('subprocess.run') as mock_run:
            # Mock successful manim command
            mock_run.return_value.returncode = 0
            mock_run.return_value.stderr = ""
            
            # Create mock output file
            output_file = os.path.join(temp_dir, "test_output.mp4")
            with open(output_file, 'w') as f:
                f.write("mock video content")
            
            with patch('pathlib.Path.mkdir'), \
                 patch('os.path.exists', return_value=True):
                
                result = await agent.render_manim_video(sample_manim_code, "test_output")
                
                assert result["success"] is True
                assert "test_output.mp4" in result["video_path"]
                assert result["duration"] > 0
    
    @pytest.mark.asyncio  
    async def test_render_manim_video_failure(self, sample_manim_code):
        """Test video rendering failure"""
        agent = ManimAgentCore()
        
        with patch('subprocess.run') as mock_run:
            # Mock failed manim command
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Manim error: syntax error"
            
            with pytest.raises(RuntimeError) as exc_info:
                await agent.render_manim_video(sample_manim_code, "test_output")
            
            assert "Manim render failed" in str(exc_info.value)
    
    def test_extract_visual_elements(self):
        """Test visual element extraction from Manim code"""
        agent = ManimAgentCore()
        
        code = '''
        title = Text("Math Animation")
        axes = Axes()
        graph = axes.plot(lambda x: x**2)
        equation = MathTex("y = x^2")
        '''
        
        elements = agent.extract_visual_elements(code)
        
        assert "text" in elements
        assert "axes" in elements
        assert "graph" in elements
        assert "equation" in elements
    
    @pytest.mark.asyncio
    async def test_process_animation_task_success(self, mock_anthropic_response):
        """Test successful animation task processing"""
        agent = ManimAgentCore()
        
        with patch.object(agent, 'generate_manim_code', return_value="mock_code") as mock_gen, \
             patch.object(agent, 'render_manim_video', return_value={
                 "success": True,
                 "video_path": "/tmp/test.mp4",
                 "duration": 10.0
             }) as mock_render, \
             patch.object(agent, 'extract_visual_elements', return_value=["title", "graph"]) as mock_extract:
            
            task_context = {"concept": "sine wave"}
            result = await agent.process_animation_task(task_context)
            
            assert isinstance(result, ManimOutput)
            assert result.success is True
            assert result.video_path == "/tmp/test.mp4"
            assert result.concept == "sine wave"
            assert "title" in result.visual_elements
    
    @pytest.mark.asyncio
    async def test_process_animation_task_with_retry(self, mock_anthropic_response):
        """Test animation task with retry on failure"""
        agent = ManimAgentCore()
        
        with patch.object(agent, 'generate_manim_code', return_value="mock_code"), \
             patch.object(agent.client.messages, 'create', new_callable=AsyncMock) as mock_create:
            
            mock_create.return_value = mock_anthropic_response
            
            # First render fails, second succeeds
            render_results = [
                {"success": False, "error": "Syntax error"},
                {"success": True, "video_path": "/tmp/test.mp4", "duration": 10.0}
            ]
            
            with patch.object(agent, 'render_manim_video', side_effect=render_results), \
                 patch.object(agent, 'extract_visual_elements', return_value=["title"]):
                
                task_context = {"concept": "test"}
                result = await agent.process_animation_task(task_context)
                
                assert result.success is True
                # Should have been called twice (retry)
                assert mock_create.call_count == 2


class TestCreateAnimationFunction:
    """Test the standalone create_animation function"""
    
    @pytest.mark.asyncio
    async def test_create_animation_simple(self):
        """Test simple animation creation"""
        with patch('manim_agent.ManimAgentCore') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent
            
            mock_output = ManimOutput(
                success=True,
                concept="sine wave",
                video_path="/tmp/test.mp4"
            )
            mock_agent.process_animation_task = AsyncMock(return_value=mock_output)
            
            result = await create_animation("sine wave")
            
            assert result.success is True
            assert result.concept == "sine wave"
            mock_agent.process_animation_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_animation_with_context(self):
        """Test animation creation with full context"""
        with patch('manim_agent.ManimAgentCore') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent
            
            mock_output = ManimOutput(
                success=True,
                concept="complex function",
                video_path="/tmp/complex.mp4"
            )
            mock_agent.process_animation_task = AsyncMock(return_value=mock_output)
            
            result = await create_animation(
                concept="complex function",
                script_context="Show the real and imaginary parts",
                duration=20.0,
                style_direction={"theme": "dark"}
            )
            
            # Verify context was passed correctly
            call_args = mock_agent.process_animation_task.call_args[0][0]
            assert call_args["concept"] == "complex function"
            assert call_args["script_context"] == "Show the real and imaginary parts"
            assert call_args["duration"] == 20.0
            assert call_args["style_direction"]["theme"] == "dark"


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_api_key_missing(self, monkeypatch):
        """Test behavior when API key is missing"""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        
        with pytest.raises((ValueError, Exception)):
            agent = ManimAgentCore()
    
    @pytest.mark.asyncio
    async def test_invalid_manim_code(self):
        """Test handling of invalid Manim code"""
        agent = ManimAgentCore()
        
        invalid_code = "this is not valid python code !!!"
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "SyntaxError: invalid syntax"
            
            with pytest.raises(RuntimeError):
                await agent.render_manim_video(invalid_code, "test")
    
    @pytest.mark.asyncio
    async def test_network_timeout(self, mock_anthropic_response):
        """Test handling of network timeouts"""
        agent = ManimAgentCore()
        
        with patch.object(agent.client.messages, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = asyncio.TimeoutError("Network timeout")
            
            with pytest.raises(asyncio.TimeoutError):
                await agent.generate_manim_code({"concept": "test"})