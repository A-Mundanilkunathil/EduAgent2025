# Testing Guide - Manim Agent System

## Overview

This document describes the comprehensive testing infrastructure for the Manim Agent system, which ensures reliability and quality of the two-agent animation generation and quality checking workflow.

## Test Architecture

### 4-Layer Testing Strategy

1. **Unit Tests** (`tests/unit/`) - Individual component testing
2. **Integration Tests** (`tests/integration/`) - End-to-end workflow testing  
3. **Reliability Tests** (`tests/reliability/`) - Production scenario testing
4. **Health Monitoring** (`health_check.py`) - System health validation

## Quick Start

### Run All Tests
```bash
python tests/test_runner.py
```

### Run Specific Test Suites
```bash
# Unit tests only (fastest)
python tests/test_runner.py --unit-only

# Smoke tests (basic functionality)
python tests/test_runner.py --smoke-only

# Generate detailed report
python tests/test_runner.py --report test_results.json
```

### System Health Check
```bash
# Full health check
python health_check.py

# Save health report
python health_check.py --save-report health.json
```

### Quick Validation
```bash
# Validate core functionality
python validate_system.py
```

## Test Structure

### Unit Tests (`tests/unit/`)

**test_manim_agent.py**
- Tests `ManimAgentCore` initialization and configuration
- Tests Manim code generation with various contexts
- Tests video rendering workflow
- Tests error handling and retry logic
- Tests `create_animation()` function

**test_quality_agent.py**
- Tests `QualityCheckAgent` initialization
- Tests video file analysis (ffprobe integration)
- Tests technical quality checks (resolution, fps, duration)
- Tests GPT-4o-mini visual analysis integration
- Tests quality scoring algorithm
- Tests data model validation

### Integration Tests (`tests/integration/`)

**test_two_agent_workflow.py**
- Tests complete generation → quality check workflow
- Tests error scenarios (generation fails, quality check fails)
- Tests iterative improvement workflows
- Tests batch processing scenarios
- Tests data flow between agents
- Tests performance characteristics

### Reliability Tests (`tests/reliability/`)

**test_production_scenarios.py**
- Tests API reliability (rate limits, timeouts, invalid keys)
- Tests file system edge cases (permissions, disk space, corruption)
- Tests concurrent operations and load handling
- Tests error recovery mechanisms  
- Tests resource constraints and memory usage
- Tests malicious input handling and data validation

### Health Monitoring (`health_check.py`)

**System Components Monitored:**
- Environment variables and configuration
- Required dependencies and packages
- API connectivity (Anthropic, OpenAI)
- Manim installation and functionality
- Agent initialization
- File system access and permissions
- Basic functionality validation

## Test Fixtures and Data

### Sample Data (`tests/fixtures/sample_data.py`)
- Sample Manim code snippets (simple, complex, invalid)
- Sample task contexts (basic, with context, full context)
- Sample quality issues and reports
- Performance benchmarks
- Error scenarios for reliability testing

### Shared Fixtures (`tests/conftest.py`)
- Temporary directories and files
- Mock video frames and sample data
- Mock API responses (Anthropic, OpenAI)
- Test environment setup
- Mock agent instances

## Running Tests

### Prerequisites
```bash
# Install testing dependencies
pip install pytest pytest-asyncio

# Ensure all system dependencies are installed
pip install -r requirements.txt
```

### Environment Setup
```bash
# Required environment variables
export ANTHROPIC_API_KEY="your_key_here"
export OPENAI_API_KEY="your_key_here"

# Optional: Set testing mode
export TESTING=true
```

### Test Commands

**Run all tests with coverage:**
```bash
cd tests
python -m pytest --cov=../ --cov-report=html
```

**Run specific test files:**
```bash
pytest tests/unit/test_manim_agent.py -v
pytest tests/integration/test_two_agent_workflow.py -v
```

**Run tests matching pattern:**
```bash
pytest -k "test_generation" -v
pytest -k "test_quality_check" -v
```

**Run tests with different verbosity:**
```bash
pytest -v              # Verbose
pytest -q              # Quiet
pytest --tb=short      # Short traceback
```

## Test Results and Reporting

### Test Runner Output
The test runner provides:
- ✅ Pass/fail status for each test suite
- ⏱️ Execution times
- 📊 Summary statistics
- 💾 Optional JSON report generation

### Health Check Output
The health check provides:
- 🏥 Component-by-component health status
- ⚡ Response times for each check
- 📄 Detailed health reports
- 🚨 Overall system status

### Validation Output
The validation script provides:
- 🔧 Import and initialization checks
- 🌍 Environment configuration validation
- 📊 Data model validation
- 🎯 Overall system readiness

## Performance Benchmarks

### Expected Performance
- **Generation time**: < 30 seconds per animation
- **Quality check time**: < 15 seconds per video
- **Total workflow**: < 45 seconds end-to-end
- **Memory usage**: < 500MB peak
- **Concurrent operations**: 5+ simultaneous

### Load Testing
```bash
# Run reliability tests with load scenarios
pytest tests/reliability/test_production_scenarios.py::TestConcurrencyAndLoad -v
```

## Troubleshooting

### Common Test Failures

**Import Errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python path includes project directory

**API Key Errors:**
- Verify environment variables are set correctly
- Check API key validity and permissions

**Manim Errors:**
- Ensure Manim is properly installed
- Check system dependencies (ffmpeg, cairo, etc.)

**Pydantic Errors:**
- Some mock/patch operations conflict with Pydantic validation
- These are test infrastructure issues, not system bugs

### Debug Mode
```bash
# Run tests with debug output
pytest --pdb                    # Drop to debugger on failure
pytest --capture=no             # Show print statements
pytest --log-cli-level=DEBUG    # Show debug logs
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Test Manim Agent System

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.12
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run health check
      run: python health_check.py
    
    - name: Run validation
      run: python validate_system.py
    
    - name: Run unit tests
      run: python tests/test_runner.py --unit-only
      env:
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Contributing

### Adding New Tests
1. Follow the existing test structure and naming conventions
2. Use appropriate fixtures from `conftest.py`
3. Mock external dependencies (APIs, file system)
4. Include both positive and negative test cases
5. Add performance assertions where relevant

### Test Guidelines
- **Unit tests**: Test individual functions/methods in isolation
- **Integration tests**: Test component interactions and workflows
- **Reliability tests**: Test edge cases and error conditions
- **Use mocks**: Avoid real API calls in automated tests
- **Be deterministic**: Tests should pass/fail consistently

## Monitoring in Production

### Health Check Endpoint
```python
# health_check.py can be used as a health endpoint
# Returns exit code: 0=healthy, 1=degraded, 2=unhealthy
```

### Continuous Monitoring
- Run health checks on a schedule (every 15-30 minutes)
- Monitor performance metrics and trends
- Alert on health degradation or failures
- Track API usage and rate limits

## Summary

This testing infrastructure provides comprehensive coverage of the Manim Agent system:

- ✅ **35+ unit tests** covering individual components
- ✅ **10+ integration tests** covering end-to-end workflows  
- ✅ **15+ reliability tests** covering production scenarios
- ✅ **Automated health monitoring** for system validation
- ✅ **Performance benchmarking** for SLA monitoring
- ✅ **CI/CD ready** for automated testing pipelines

The system ensures that both the Manim generation agent and GPT-4o-mini quality agent work reliably together to create high-quality educational animations.