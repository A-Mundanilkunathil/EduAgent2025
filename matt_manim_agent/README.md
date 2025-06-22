# Manim Animation Agent for CrewAI

A sophisticated two-agent system for creating and validating educational math animations using Manim and Claude API. Built for the UC Berkeley AI Hackathon 2025.

## 🏗️ Two-Agent Architecture

This project implements a **separation of concerns** approach with two specialized agents:

1. **Manim Generation Agent** - Fast animation creation (3-10 seconds)
2. **Quality Check Agent** - Optional quality validation (1-3 seconds)

This architecture provides flexibility: generate quickly for demos, or add quality checks for production content.

## Features

- **Standalone Operation**: Works independently for quick animation generation
- **Multi-Agent Integration**: Accepts rich context from Script, Director, and other agents
- **Claude-Powered**: Uses Claude API for intelligent Manim code generation
- **Context-Aware**: Adapts animations based on narrative, timing, and style requirements
- **Auto-Debugging**: Automatically fixes common Manim errors
- **3Blue1Brown Style**: Creates professional educational animations

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd matt_manim_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys:
# - ANTHROPIC_API_KEY (required)
# - OPENAI_API_KEY (optional, for CrewAI)
```

4. Install Manim (if not already installed):
```bash
# macOS
brew install py3cairo ffmpeg
pip install manim

# Linux
sudo apt update
sudo apt install libcairo2-dev libpango1.0-dev ffmpeg
pip install manim

# Windows
# Follow instructions at https://docs.manim.community/en/stable/installation/windows.html
```

## Two-Agent System

### Why Two Agents?

**Problem**: Quality checking slows down generation, but skipping it risks poor output.

**Solution**: Separate agents that can work independently or together.

### Agent 1: Manim Generator
- **Focus**: Speed and flexibility
- **Time**: 3-10 seconds per animation
- **Output**: MP4 video + metadata

### Agent 2: Quality Checker
- **Focus**: Validation and improvement
- **Time**: 1-3 seconds per check
- **Output**: Quality report with score and recommendations

### Usage Patterns

```python
# Pattern 1: Fast generation only (demos, prototypes)
result = await create_animation("sine wave")

# Pattern 2: Generation + quality check (production)
result = await create_animation("complex proof")
if result.success:
    report = await check_animation_quality(result.video_path)
    
# Pattern 3: Conditional quality (smart workflow)
if is_complex(concept):
    # Check quality for complex animations
    report = await check_animation_quality(video_path)
```

## Quick Start

### Simple Standalone Usage

```python
import asyncio
from manim_agent import create_animation

async def main():
    result = await create_animation("derivatives as slopes")
    print(f"Video created: {result.video_path}")

asyncio.run(main())
```

### With Context

```python
result = await create_animation(
    concept="Pythagorean theorem proof",
    script_context="Let's see why a² + b² = c² always holds for right triangles",
    duration=15.0,
    style_direction={"color_scheme": {"triangle": "#3B82F6", "squares": "#10B981"}}
)
```

### CrewAI Integration

```python
from crewai import Crew, Task
from manim_agent import ManimAgent

# Create agent
agent = ManimAgent(
    role="Lead Animator",
    goal="Create compelling math visualizations"
)

# Create task with multi-agent context
task = Task(
    description="Animate calculus concept",
    agent=agent,
    context={
        "concept": "integration as area under curve",
        "script_context": "Integration finds the accumulated area...",
        "duration": 20.0,
        "sync_points": [{"time": 5.0, "emphasis": "show_riemann_sum"}]
    }
)

# Execute
crew = Crew(agents=[agent], tasks=[task])
crew.kickoff()
```

## Architecture

### Core Components

1. **ManimAgent**: Main CrewAI agent class
   - Inherits from CrewAI Agent
   - Manages Claude API integration
   - Handles animation generation workflow

2. **Context Handler**: Parses and manages multi-agent context
   - `ScriptContext`: Narrative and educational content
   - `DirectorContext`: Visual style and pacing
   - `TimingContext`: Duration and synchronization

3. **Manim Tools**: CrewAI tool wrappers
   - `ManimAnimationTool`: Main animation creation tool
   - `ManimDebugTool`: Error fixing tool

### Output Format

```python
{
    "success": True,
    "video_path": "animations/derivative_concept.mp4",
    "duration": 14.7,
    "concept": "derivatives",
    "manim_code": "class DerivativeScene(Scene):...",
    "sync_points": [{"time": 3.0, "event": "tangent_appears"}],
    "visual_elements": ["function", "tangent_line", "slope_calculation"],
    "metadata": {"render_time": 8.3, "quality_score": 0.92}
}
```

## Context Integration

The agent accepts context from other agents in the system:

### From Script Agent
```python
"script_context": {
    "narrative": "The main educational narrative...",
    "key_points": ["concept1", "concept2"],
    "emphasis_timings": {3.0: "highlight_key_formula"}
}
```

### From Director Agent
```python
"director_context": {
    "visual_style": "3blue1brown",
    "color_scheme": {"primary": "#3B82F6"},
    "pacing": "moderate",
    "transitions": ["smooth", "morph"]
}
```

### From Timing Coordinator
```python
"timing_context": {
    "total_duration": 30.0,
    "start_time": 45.0,  # Start at 45s in full video
    "segment_durations": {"intro": 5.0, "main": 20.0}
}
```

## Examples

### Basic Examples
```bash
# Original examples (single agent)
python example_usage.py

# Multi-agent examples
python multi_agent_example.py
```

### Two-Agent Workflow Example

```python
from manim_agent import create_animation
from quality_check_agent import check_animation_quality

# Step 1: Fast generation
animation = await create_animation("Fourier series visualization")

# Step 2: Optional quality check
if animation.success:
    quality = await check_animation_quality(animation.video_path)
    print(f"Quality score: {quality.score}/100")
    
    if quality.score < 70:
        # Regenerate with improvements
        animation = await create_animation(
            "Fourier series visualization",
            style_direction={"spacing": "generous"}
        )
```

This demonstrates:
1. Simple standalone usage
2. Context-rich animations
3. Full CrewAI integration
4. Multi-agent simulation
5. Complete crew setup

## Development

### Project Structure
```
matt_manim_agent/
├── manim_agent.py       # Main agent implementation
├── manim_tools.py       # CrewAI tool wrappers
├── context_handler.py   # Context parsing and management
├── example_usage.py     # Usage examples
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
└── README.md           # This file
```

### Adding New Features

1. **New Visual Styles**: Update `manim_system_prompt` in `ManimAgent`
2. **New Context Types**: Extend models in `context_handler.py`
3. **New Tools**: Add to `manim_tools.py` and `create_manim_tools()`

## Troubleshooting

### Common Issues

1. **Manim not found**: Ensure Manim is properly installed
2. **API key errors**: Check .env file has valid keys
3. **Render failures**: Agent auto-retries with fixes
4. **Missing dependencies**: Run `pip install -r requirements.txt`

### Debug Mode

Enable verbose output:
```python
agent = ManimAgent(verbose=True)
```

## Performance Tips

1. **Batch Animations**: Process multiple concepts together
2. **Cache Results**: Reuse generated animations
3. **Optimize Quality**: Use `-qm` (medium) for drafts, `-qh` (high) for final
4. **Parallel Rendering**: Run multiple agents concurrently

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## License

MIT License - See LICENSE file

## Acknowledgments

- Built for UC Berkeley AI Hackathon 2025
- Inspired by 3Blue1Brown's manim
- Powered by Anthropic's Claude API
- CrewAI framework for multi-agent orchestration