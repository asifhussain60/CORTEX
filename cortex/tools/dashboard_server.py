#!/usr/bin/env python3
"""
Dashboard Server Management Tool
Exposed via MCP for dashboard lifecycle management and testing.

Features:
- Kill all HTTP processes on specified ports
- Start HTTP server on port 8080
- Health checks (server running, logs clean, data loading)
- Automated tab generation validation
- Launch dashboard in browser
"""

import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests


class DashboardStatus(Enum):
    """Dashboard health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check operation."""
    status: DashboardStatus
    message: str
    details: Dict[str, any]
    timestamp: float


class DashboardServerTool:
    """MCP Tool for dashboard server management."""

    def __init__(self):
        self.dashboards_dir = Path(__file__).parent.parent.parent / "company" / "dashboards"
        self.log_file = Path("/tmp/dashboard_server.log")
        self.server_pid: Optional[int] = None
        self.port = 8080

    def kill_all_http_processes(self, ports: List[int] = None) -> Tuple[bool, str]:
        """
        Kill all HTTP processes on specified ports.

        Args:
            ports: List of ports to kill processes on (default: [8080, 8888, 8888])

        Returns:
            (success: bool, message: str)
        """
        if ports is None:
            ports = [8080, 8888, 8888]

        killed_count = 0
        errors = []

        for port in ports:
            try:
                # Find processes on port
                result = subprocess.run(
                    f"lsof -i :{port} | grep -v COMMAND | awk '{{print $2}}' | xargs kill -9 2>/dev/null || true",
                    shell=True,
                    capture_output=True,
                    timeout=5
                )

                # Count killed (approximate)
                lsof_result = subprocess.run(
                    f"lsof -i :{port}",
                    shell=True,
                    capture_output=True,
                    timeout=5
                )

                if lsof_result.returncode != 0:
                    killed_count += 1

            except subprocess.TimeoutExpired:
                errors.append(f"Timeout killing port {port}")
            except Exception as e:
                errors.append(f"Error killing port {port}: {e}")

        time.sleep(1)  # Let processes terminate

        success = len(errors) == 0
        message = f"✅ Killed processes on {killed_count} ports" if success else f"⚠️ Errors: {', '.join(errors)}"

        return success, message

    def start_server(self) -> Tuple[bool, str, int]:
        """
        Start HTTP server on port 8080.

        Returns:
            (success: bool, message: str, pid: int)
        """
        try:
            # Ensure dashboards dir exists
            if not self.dashboards_dir.exists():
                return False, f"❌ Dashboards dir not found: {self.dashboards_dir}", 0

            # Clear old log
            self.log_file.write_text("")

            # Start server in background
            proc = subprocess.Popen(
                ["python3", "-m", "http.server", str(self.port)],
                cwd=str(self.dashboards_dir),
                stdout=open(str(self.log_file), "a"),
                stderr=subprocess.STDOUT,
                preexec_fn=lambda: None  # Allow process to detach
            )

            self.server_pid = proc.pid

            # Wait for startup
            time.sleep(2)

            # Verify it's running
            ps_result = subprocess.run(
                f"ps -p {proc.pid} > /dev/null",
                shell=True,
                capture_output=True
            )

            if ps_result.returncode == 0:
                return True, f"✅ Server started on port {self.port} (PID: {proc.pid})", proc.pid
            else:
                return False, "❌ Server failed to start", 0

        except Exception as e:
            return False, f"❌ Error starting server: {e}", 0

    def check_server_running(self) -> HealthCheckResult:
        """Check if server is running on port 8080."""
        try:
            response = requests.get(f"http://localhost:{self.port}/", timeout=5)

            if response.status_code == 200:
                return HealthCheckResult(
                    status=DashboardStatus.HEALTHY,
                    message=f"✅ Server is running on port {self.port}",
                    details={"status_code": response.status_code, "response_size": len(response.text)},
                    timestamp=time.time()
                )
            else:
                return HealthCheckResult(
                    status=DashboardStatus.DEGRADED,
                    message=f"⚠️ Server returned status {response.status_code}",
                    details={"status_code": response.status_code},
                    timestamp=time.time()
                )
        except requests.exceptions.ConnectionError:
            return HealthCheckResult(
                status=DashboardStatus.FAILED,
                message=f"❌ Cannot connect to server on port {self.port}",
                details={"port": self.port},
                timestamp=time.time()
            )
        except Exception as e:
            return HealthCheckResult(
                status=DashboardStatus.UNKNOWN,
                message=f"❌ Error checking server: {e}",
                details={"error": str(e)},
                timestamp=time.time()
            )

    def check_logs_clean(self) -> HealthCheckResult:
        """Check if server logs have errors."""
        try:
            if not self.log_file.exists():
                return HealthCheckResult(
                    status=DashboardStatus.DEGRADED,
                    message="⚠️ Log file not found",
                    details={"log_file": str(self.log_file)},
                    timestamp=time.time()
                )

            log_content = self.log_file.read_text()

            # Check for server startup
            if "Serving HTTP" in log_content:
                startup_ok = True
            else:
                startup_ok = False

            # Check for errors
            error_patterns = ["ERROR", "FAILED", "Exception", "Traceback", "Address already in use"]
            has_errors = any(pattern in log_content for pattern in error_patterns)

            if has_errors:
                return HealthCheckResult(
                    status=DashboardStatus.FAILED,
                    message="❌ Errors detected in logs",
                    details={
                        "log_file": str(self.log_file),
                        "errors_found": True,
                        "startup_ok": startup_ok
                    },
                    timestamp=time.time()
                )
            elif startup_ok:
                return HealthCheckResult(
                    status=DashboardStatus.HEALTHY,
                    message="✅ Logs are clean - server started successfully",
                    details={"log_file": str(self.log_file), "startup_ok": True},
                    timestamp=time.time()
                )
            else:
                return HealthCheckResult(
                    status=DashboardStatus.UNKNOWN,
                    message="❓ Logs available but startup message not found",
                    details={"log_file": str(self.log_file)},
                    timestamp=time.time()
                )

        except Exception as e:
            return HealthCheckResult(
                status=DashboardStatus.UNKNOWN,
                message=f"❌ Error checking logs: {e}",
                details={"error": str(e)},
                timestamp=time.time()
            )

    def check_dashboard_data_loaded(self, repo: str = "KSESSIONS") -> HealthCheckResult:
        """Check if dashboard data is loaded."""
        try:
            response = requests.get(
                f"http://localhost:{self.port}/spa/dashboard.html?repo={repo}",
                timeout=5
            )

            if response.status_code != 200:
                return HealthCheckResult(
                    status=DashboardStatus.FAILED,
                    message=f"❌ Cannot fetch dashboard (status {response.status_code})",
                    details={"status_code": response.status_code},
                    timestamp=time.time()
                )

            html = response.text

            # Check for embedded data script
            if 'id="dashboard-data"' not in html:
                return HealthCheckResult(
                    status=DashboardStatus.DEGRADED,
                    message="⚠️ Dashboard data script not found",
                    details={"has_data_script": False},
                    timestamp=time.time()
                )

            # Try to extract and parse data
            data_match = re.search(r'id="dashboard-data"[^>]*>([^<]+)</script>', html)
            if data_match:
                data_str = data_match.group(1)
                try:
                    data = json.loads(data_str)

                    if data and data != {}:
                        return HealthCheckResult(
                            status=DashboardStatus.HEALTHY,
                            message="✅ Dashboard data loaded successfully",
                            details={
                                "has_data": True,
                                "repo": data.get("repo", {}).get("display_name", "unknown"),
                                "has_metrics": "metrics" in data
                            },
                            timestamp=time.time()
                        )
                    else:
                        return HealthCheckResult(
                            status=DashboardStatus.DEGRADED,
                            message="⚠️ Dashboard data is empty",
                            details={"has_data": False},
                            timestamp=time.time()
                        )
                except json.JSONDecodeError:
                    return HealthCheckResult(
                        status=DashboardStatus.DEGRADED,
                        message="⚠️ Dashboard data is invalid JSON",
                        details={"data_snippet": data_str[:100]},
                        timestamp=time.time()
                    )
            else:
                return HealthCheckResult(
                    status=DashboardStatus.DEGRADED,
                    message="⚠️ Cannot extract dashboard data",
                    details={"found_script": True, "extracted": False},
                    timestamp=time.time()
                )

        except requests.exceptions.ConnectionError:
            return HealthCheckResult(
                status=DashboardStatus.FAILED,
                message="❌ Cannot connect to dashboard",
                details={"port": self.port},
                timestamp=time.time()
            )
        except Exception as e:
            return HealthCheckResult(
                status=DashboardStatus.UNKNOWN,
                message=f"❌ Error checking dashboard data: {e}",
                details={"error": str(e)},
                timestamp=time.time()
            )

    def verify_tabs_generated(self) -> HealthCheckResult:
        """Verify all 8 tabs are generated and visible."""
        try:
            response = requests.get(
                "http://localhost:8080/spa/dashboard.html",
                timeout=5
            )

            if response.status_code != 200:
                return HealthCheckResult(
                    status=DashboardStatus.FAILED,
                    message="❌ Cannot fetch dashboard",
                    details={"status_code": response.status_code},
                    timestamp=time.time()
                )

            html = response.text

            # Expected tabs
            expected_tabs = [
                ("overview-tab", "Overview"),
                ("metrics-tab", "Metrics"),
                ("security-tab", "Security"),
                ("dependencies-tab", "Dependencies"),
                ("quality-tab", "Quality"),
                ("use-cases-tab", "Use Cases"),
                ("lens-tab", "LENS"),
                ("refactoring-tab", "Refactoring")
            ]

            missing_tabs = []
            hidden_tabs = []

            for tab_id, tab_name in expected_tabs:
                # Check if tab exists
                if f'id="{tab_id}"' not in html:
                    missing_tabs.append(tab_name)
                else:
                    # Check if it has inline display:none
                    # Look for the specific button element
                    pattern = f'id="{tab_id}"[^>]*style="[^"]*display\\s*:\\s*none'
                    if re.search(pattern, html):
                        hidden_tabs.append(tab_name)

            if not missing_tabs and not hidden_tabs:
                return HealthCheckResult(
                    status=DashboardStatus.HEALTHY,
                    message="✅ All 8 tabs generated and visible",
                    details={
                        "total_tabs": len(expected_tabs),
                        "missing": 0,
                        "hidden": 0
                    },
                    timestamp=time.time()
                )
            else:
                status = DashboardStatus.DEGRADED if hidden_tabs else DashboardStatus.FAILED
                message = f"❌ Tab issues: {len(missing_tabs)} missing, {len(hidden_tabs)} hidden"

                return HealthCheckResult(
                    status=status,
                    message=message,
                    details={
                        "total_tabs": len(expected_tabs),
                        "missing_tabs": missing_tabs,
                        "hidden_tabs": hidden_tabs
                    },
                    timestamp=time.time()
                )

        except Exception as e:
            return HealthCheckResult(
                status=DashboardStatus.UNKNOWN,
                message=f"❌ Error verifying tabs: {e}",
                details={"error": str(e)},
                timestamp=time.time()
            )

    def run_full_health_check(self, repo: str = "KSESSIONS") -> Dict:
        """
        Run full health check suite.

        Returns:
            Dict with all check results
        """
        checks = {
            "server_running": self.check_server_running(),
            "logs_clean": self.check_logs_clean(),
            "data_loaded": self.check_dashboard_data_loaded(repo),
            "tabs_generated": self.verify_tabs_generated()
        }

        # Determine overall status
        statuses = [c.status for c in checks.values()]
        if all(s == DashboardStatus.HEALTHY for s in statuses):
            overall = DashboardStatus.HEALTHY
        elif any(s == DashboardStatus.FAILED for s in statuses):
            overall = DashboardStatus.FAILED
        else:
            overall = DashboardStatus.DEGRADED

        return {
            "overall_status": overall.value,
            "checks": {
                name: {
                    "status": result.status.value,
                    "message": result.message,
                    "details": result.details
                }
                for name, result in checks.items()
            },
            "summary": f"{overall.value.upper()}: {len([s for s in statuses if s == DashboardStatus.HEALTHY])}/{len(checks)} checks passed"
        }

    def launch_dashboard(self, repo: str = "KSESSIONS") -> Tuple[bool, str]:
        """Launch dashboard in browser."""
        try:
            dashboard_url = f"http://localhost:{self.port}/spa/dashboard.html?repo={repo}"
            subprocess.run(["open", dashboard_url], check=False)
            return True, f"✅ Launched dashboard: {dashboard_url}"
        except Exception as e:
            return False, f"❌ Error launching dashboard: {e}"


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Dashboard Server Management Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Kill command
    kill_parser = subparsers.add_parser("kill", help="Kill HTTP processes")
    kill_parser.add_argument("--ports", nargs="+", type=int, default=[8080, 8888],
                            help="Ports to kill processes on")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start HTTP server")

    # Health check command
    health_parser = subparsers.add_parser("health", help="Run health checks")
    health_parser.add_argument("--repo", default="KSESSIONS", help="Repository name")

    # Launch command
    launch_parser = subparsers.add_parser("launch", help="Launch dashboard")
    launch_parser.add_argument("--repo", default="KSESSIONS", help="Repository name")

    # Full command
    full_parser = subparsers.add_parser("full", help="Full cycle: kill, start, health check, launch")
    full_parser.add_argument("--repo", default="KSESSIONS", help="Repository name")

    args = parser.parse_args()

    tool = DashboardServerTool()

    if args.command == "kill":
        success, message = tool.kill_all_http_processes(args.ports)
        print(message)
        return 0 if success else 1

    elif args.command == "start":
        success, message, pid = tool.start_server()
        print(message)
        return 0 if success else 1

    elif args.command == "health":
        result = tool.run_full_health_check(args.repo)
        print(json.dumps(result, indent=2))
        return 0 if result["overall_status"] == "healthy" else 1

    elif args.command == "launch":
        success, message = tool.launch_dashboard(args.repo)
        print(message)
        return 0 if success else 1

    elif args.command == "full":
        print("🚀 Starting full dashboard server lifecycle...")

        # Kill
        print("\n[1/4] Killing existing processes...")
        tool.kill_all_http_processes()

        # Start
        print("[2/4] Starting server...")
        success, message, pid = tool.start_server()
        print(message)
        if not success:
            return 1

        # Health check
        print("\n[3/4] Running health checks...")
        health = tool.run_full_health_check(args.repo)
        print(json.dumps(health, indent=2))

        # Launch
        print("\n[4/4] Launching dashboard...")
        tool.launch_dashboard(args.repo)
        print(f"✅ Dashboard ready at http://localhost:8080/spa/dashboard.html?repo={args.repo}")

        return 0

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
