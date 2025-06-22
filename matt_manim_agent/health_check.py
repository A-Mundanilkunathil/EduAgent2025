#!/usr/bin/env python3
"""
Health check system for Manim Agent
Monitors system health and provides diagnostic information
"""

import asyncio
import os
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Import our agents
try:
    from manim_agent import ManimAgentCore, create_animation
    from quality_check_agent import QualityCheckAgent, check_animation_quality
except ImportError as e:
    print(f"Warning: Could not import agents: {e}")


@dataclass
class HealthStatus:
    """Health status for a component"""
    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    response_time: Optional[float] = None
    last_check: Optional[datetime] = None
    details: Optional[Dict[str, Any]] = None


class SystemHealthMonitor:
    """System health monitoring and diagnostics"""
    
    def __init__(self):
        self.health_checks = []
        self.last_full_check = None
        
    async def check_full_system_health(self) -> Dict[str, HealthStatus]:
        """Run comprehensive health check of entire system"""
        
        print("🏥 SYSTEM HEALTH CHECK")
        print("=" * 40)
        
        checks = [
            self._check_environment,
            self._check_dependencies,
            self._check_api_connectivity,
            self._check_manim_installation,
            self._check_agent_initialization,
            self._check_file_system,
            self._check_basic_functionality
        ]
        
        results = {}
        for check_func in checks:
            try:
                status = await check_func if asyncio.iscoroutinefunction(check_func) else check_func()
                results[status.component] = status
                self._print_status(status)
            except Exception as e:
                error_status = HealthStatus(
                    component=check_func.__name__.replace('_check_', ''),
                    status="unhealthy",
                    message=f"Health check failed: {e}",
                    last_check=datetime.now()
                )
                results[error_status.component] = error_status
                self._print_status(error_status)
        
        self.last_full_check = datetime.now()
        
        # Print summary
        healthy_count = sum(1 for s in results.values() if s.status == "healthy")
        total_count = len(results)
        
        print("\n" + "=" * 40)
        print(f"📊 HEALTH SUMMARY: {healthy_count}/{total_count} components healthy")
        
        if healthy_count == total_count:
            print("✅ System is fully operational")
        elif healthy_count >= total_count * 0.8:
            print("⚠️  System is mostly operational with some issues")
        else:
            print("❌ System has significant health issues")
        
        return results
    
    def _check_environment(self) -> HealthStatus:
        """Check environment variables and configuration"""
        
        required_vars = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if not missing_vars:
            return HealthStatus(
                component="environment",
                status="healthy",
                message="All required environment variables are set",
                last_check=datetime.now()
            )
        else:
            return HealthStatus(
                component="environment",
                status="degraded",
                message=f"Missing environment variables: {', '.join(missing_vars)}",
                last_check=datetime.now(),
                details={"missing_vars": missing_vars}
            )
    
    def _check_dependencies(self) -> HealthStatus:
        """Check that all required dependencies are installed"""
        
        # Map package names to their import names
        packages_to_check = {
            "anthropic": "anthropic",
            "openai": "openai", 
            "crewai": "crewai",
            "manim": "manim",
            "opencv-python": "cv2",
            "pillow": "PIL",
            "numpy": "numpy",
            "pydantic": "pydantic"
        }
        
        missing_packages = []
        
        for package_name, import_name in packages_to_check.items():
            try:
                __import__(import_name)
            except ImportError:
                missing_packages.append(package_name)
        
        if not missing_packages:
            return HealthStatus(
                component="dependencies",
                status="healthy", 
                message="All required packages are installed",
                last_check=datetime.now()
            )
        else:
            return HealthStatus(
                component="dependencies",
                status="unhealthy",
                message=f"Missing packages: {', '.join(missing_packages)}",
                last_check=datetime.now(),
                details={"missing_packages": missing_packages}
            )
    
    def _check_api_connectivity(self) -> HealthStatus:
        """Check API connectivity (without making real calls)"""
        
        start_time = time.time()
        
        try:
            # Check if we can initialize API clients
            from anthropic import AsyncAnthropic
            from openai import OpenAI
            
            # Just check initialization, don't make actual calls
            if os.getenv("ANTHROPIC_API_KEY"):
                anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            if os.getenv("OPENAI_API_KEY"):
                openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response_time = time.time() - start_time
            
            return HealthStatus(
                component="api_connectivity",
                status="healthy",
                message="API clients initialized successfully",
                response_time=response_time,
                last_check=datetime.now()
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return HealthStatus(
                component="api_connectivity",
                status="unhealthy",
                message=f"API client initialization failed: {e}",
                response_time=response_time,
                last_check=datetime.now()
            )
    
    def _check_manim_installation(self) -> HealthStatus:
        """Check Manim installation and basic functionality"""
        
        start_time = time.time()
        
        try:
            # Check if manim command exists
            result = subprocess.run(
                ["manim", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            response_time = time.time() - start_time
            
            if result.returncode == 0:
                version = result.stdout.strip()
                return HealthStatus(
                    component="manim_installation",
                    status="healthy",
                    message=f"Manim is installed: {version}",
                    response_time=response_time,
                    last_check=datetime.now(),
                    details={"version": version}
                )
            else:
                return HealthStatus(
                    component="manim_installation",
                    status="unhealthy",
                    message="Manim command failed",
                    response_time=response_time,
                    last_check=datetime.now(),
                    details={"error": result.stderr}
                )
                
        except subprocess.TimeoutExpired:
            return HealthStatus(
                component="manim_installation",
                status="unhealthy",
                message="Manim command timed out",
                response_time=time.time() - start_time,
                last_check=datetime.now()
            )
        except FileNotFoundError:
            return HealthStatus(
                component="manim_installation",
                status="unhealthy",
                message="Manim command not found",
                response_time=time.time() - start_time,
                last_check=datetime.now()
            )
        except Exception as e:
            return HealthStatus(
                component="manim_installation",
                status="unhealthy",
                message=f"Manim check failed: {e}",
                response_time=time.time() - start_time,
                last_check=datetime.now()
            )
    
    def _check_agent_initialization(self) -> HealthStatus:
        """Check that agents can be initialized"""
        
        start_time = time.time()
        
        try:
            # Try to initialize both agents
            manim_agent = ManimAgentCore()
            quality_agent = QualityCheckAgent()
            
            response_time = time.time() - start_time
            
            return HealthStatus(
                component="agent_initialization", 
                status="healthy",
                message="Both agents initialized successfully",
                response_time=response_time,
                last_check=datetime.now()
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return HealthStatus(
                component="agent_initialization",
                status="unhealthy",
                message=f"Agent initialization failed: {e}",
                response_time=response_time,
                last_check=datetime.now()
            )
    
    def _check_file_system(self) -> HealthStatus:
        """Check file system access and permissions"""
        
        start_time = time.time()
        
        try:
            # Check if we can create temp files
            import tempfile
            
            # Test directory creation
            test_dir = Path("animations")
            test_dir.mkdir(exist_ok=True)
            
            # Test file creation and deletion
            with tempfile.NamedTemporaryFile(suffix=".mp4", dir=test_dir, delete=True) as tmp_file:
                tmp_file.write(b"test data")
                tmp_file.flush()
                
                # Check file exists and is readable
                assert os.path.exists(tmp_file.name)
                assert os.path.getsize(tmp_file.name) > 0
            
            response_time = time.time() - start_time
            
            return HealthStatus(
                component="file_system",
                status="healthy",
                message="File system access is working",
                response_time=response_time,
                last_check=datetime.now()
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return HealthStatus(
                component="file_system",
                status="unhealthy",
                message=f"File system check failed: {e}",
                response_time=response_time,
                last_check=datetime.now()
            )
    
    def _check_basic_functionality(self) -> HealthStatus:
        """Check basic functionality with mocked operations"""
        
        start_time = time.time()
        
        try:
            # This would ideally test with real but lightweight operations
            # For now, we'll just verify the functions can be called
            
            # Check if create_animation function exists and is callable
            assert callable(create_animation)
            assert callable(check_animation_quality)
            
            response_time = time.time() - start_time
            
            return HealthStatus(
                component="basic_functionality",
                status="healthy",
                message="Basic functionality checks passed",
                response_time=response_time,
                last_check=datetime.now()
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return HealthStatus(
                component="basic_functionality",
                status="unhealthy",
                message=f"Basic functionality check failed: {e}",
                response_time=response_time,
                last_check=datetime.now()
            )
    
    def _print_status(self, status: HealthStatus):
        """Print formatted status"""
        
        if status.status == "healthy":
            icon = "✅"
        elif status.status == "degraded":
            icon = "⚠️ "
        else:
            icon = "❌"
        
        time_str = f" ({status.response_time:.2f}s)" if status.response_time else ""
        print(f"{icon} {status.component}: {status.message}{time_str}")
    
    def save_health_report(self, results: Dict[str, HealthStatus], filename: str = "health_report.json"):
        """Save health check results to file"""
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self._calculate_overall_status(results),
            "components": {
                name: asdict(status) for name, status in results.items()
            }
        }
        
        # Convert datetime objects to strings for JSON serialization
        for component in report["components"].values():
            if component["last_check"]:
                component["last_check"] = component["last_check"].isoformat()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Health report saved to {filename}")
    
    def _calculate_overall_status(self, results: Dict[str, HealthStatus]) -> str:
        """Calculate overall system status"""
        
        healthy_count = sum(1 for s in results.values() if s.status == "healthy")
        total_count = len(results)
        
        if healthy_count == total_count:
            return "healthy"
        elif healthy_count >= total_count * 0.8:
            return "degraded"
        else:
            return "unhealthy"


async def main():
    """Main health check entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Manim Agent Health Check")
    parser.add_argument("--save-report", type=str, help="Save health report to file")
    parser.add_argument("--quiet", action="store_true", help="Reduce output")
    
    args = parser.parse_args()
    
    monitor = SystemHealthMonitor()
    
    if not args.quiet:
        print("Starting system health check...")
    
    results = await monitor.check_full_system_health()
    
    if args.save_report:
        monitor.save_health_report(results, args.save_report)
    
    # Return appropriate exit code
    overall_status = monitor._calculate_overall_status(results)
    
    if overall_status == "healthy":
        return 0
    elif overall_status == "degraded":
        return 1
    else:
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)