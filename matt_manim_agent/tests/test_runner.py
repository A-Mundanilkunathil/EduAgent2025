#!/usr/bin/env python3
"""
Comprehensive test runner for the Manim Agent system
Runs all tests and provides detailed reporting
"""

import pytest
import sys
import os
import time
import subprocess
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRunner:
    """Comprehensive test runner with reporting"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {}
        
    def run_all_tests(self, verbose=True):
        """Run all test suites and collect results"""
        
        print("🧪 MANIM AGENT TEST SUITE")
        print("=" * 50)
        
        test_suites = [
            ("Unit Tests", "unit/", "🔧"),
            ("Integration Tests", "integration/", "🔗"),
            ("Reliability Tests", "reliability/", "🛡️"),
        ]
        
        total_start_time = time.time()
        all_passed = True
        
        for suite_name, suite_path, emoji in test_suites:
            print(f"\n{emoji} Running {suite_name}...")
            print("-" * 30)
            
            suite_start_time = time.time()
            
            try:
                result = self._run_test_suite(suite_path, verbose)
                suite_time = time.time() - suite_start_time
                
                self.results[suite_name] = {
                    "passed": result.returncode == 0,
                    "time": suite_time,
                    "output": result.stdout if result.stdout else "",
                    "errors": result.stderr if result.stderr else ""
                }
                
                if result.returncode == 0:
                    print(f"✅ {suite_name} passed in {suite_time:.1f}s")
                else:
                    print(f"❌ {suite_name} failed in {suite_time:.1f}s")
                    all_passed = False
                    if verbose and result.stderr:
                        print(f"Errors: {result.stderr}")
                        
            except Exception as e:
                print(f"❌ {suite_name} crashed: {e}")
                self.results[suite_name] = {
                    "passed": False,
                    "time": 0,
                    "output": "",
                    "errors": str(e)
                }
                all_passed = False
        
        total_time = time.time() - total_start_time
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print(f"Total time: {total_time:.1f}s")
        
        for suite_name, result in self.results.items():
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status} {suite_name}: {result['time']:.1f}s")
        
        if all_passed:
            print("\n🎉 ALL TESTS PASSED!")
            return True
        else:
            print("\n💥 SOME TESTS FAILED!")
            return False
    
    def _run_test_suite(self, suite_path, verbose=False):
        """Run a specific test suite"""
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / suite_path),
            "-v" if verbose else "-q",
            "--tb=short",
            "--disable-warnings"
        ]
        
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.test_dir.parent
        )
    
    def run_unit_tests_only(self):
        """Run only unit tests (fastest)"""
        print("🔧 Running Unit Tests Only...")
        result = self._run_test_suite("tests/unit/", verbose=True)
        return result.returncode == 0
    
    def run_smoke_tests(self):
        """Run minimal smoke tests to verify basic functionality"""
        print("💨 Running Smoke Tests...")
        
        # Test basic imports
        try:
            from manim_agent import create_animation, ManimOutput
            from quality_check_agent import check_animation_quality, QualityReport
            print("✅ Basic imports successful")
        except ImportError as e:
            print(f"❌ Import failed: {e}")
            return False
        
        # Test basic initialization
        try:
            from manim_agent import ManimAgentCore
            from quality_check_agent import QualityCheckAgent
            
            # These might fail if API keys are missing, which is OK for smoke test
            try:
                agent1 = ManimAgentCore()
                print("✅ Manim agent initialization successful")
            except Exception as e:
                print(f"⚠️  Manim agent initialization failed (likely missing API key): {e}")
            
            try:
                agent2 = QualityCheckAgent()
                print("✅ Quality agent initialization successful")
            except Exception as e:
                print(f"⚠️  Quality agent initialization failed (likely missing API key): {e}")
                
        except Exception as e:
            print(f"❌ Agent initialization failed: {e}")
            return False
        
        print("✅ Smoke tests passed")
        return True
    
    def generate_report(self, output_file="test_report.json"):
        """Generate detailed test report"""
        
        report = {
            "timestamp": time.time(),
            "summary": {
                "total_suites": len(self.results),
                "passed_suites": sum(1 for r in self.results.values() if r["passed"]),
                "failed_suites": sum(1 for r in self.results.values() if not r["passed"]),
                "total_time": sum(r["time"] for r in self.results.values())
            },
            "suites": self.results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Test report saved to {output_file}")
        return report


def main():
    """Main test runner entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Manim Agent tests")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument("--smoke-only", action="store_true", help="Run only smoke tests")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    parser.add_argument("--report", type=str, help="Generate JSON report file")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.smoke_only:
        success = runner.run_smoke_tests()
    elif args.unit_only:
        success = runner.run_unit_tests_only()
    else:
        success = runner.run_all_tests(verbose=not args.quiet)
    
    if args.report:
        runner.generate_report(args.report)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)