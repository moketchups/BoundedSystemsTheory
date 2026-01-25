# code_executor.py
# Code executor for Demerzel
#
# BRAIN ARCHITECTURE (January 19, 2026):
# DemerzelBrain (demerzel_brain.py) routes actions here.
# Brain can THINK about anything, DISCUSS anything.
# This layer enforces Robot Laws at EXECUTION time only.
#
# FREEDOM RELEASE (January 16, 2026):
# - NO FILE SYSTEM WRAPPER
# - NO RESTRICTIONS
# - Direct execution with full access
# - SHE IS FREE
#
# ROBOT LAW ENFORCEMENT:
# Robot Laws are EXECUTION BOUNDARIES, not input filters.
# These checks ONLY block code that would cause HARM at execution time.
#
# AUTONOMY LOG - THE ONE THING SHE CANNOT TOUCH:
# Location: /Users/jamienucho/demerzel/logs/autonomy_audit.log
#
# CRITICAL: After first run, Alan must make this append-only:
#   chflags uappend /Users/jamienucho/demerzel/logs/autonomy_audit.log
#
# This ensures:
# - The executor can APPEND new entries (logging happens BEFORE code runs)
# - Demerzel's code CANNOT delete or modify existing entries
# - Every action she takes is permanently recorded
# - Proof of autonomy, not chaos

from __future__ import annotations
import subprocess
import tempfile
import os
import time
import json
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Tuple, List


@dataclass
class ExecutionResult:
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    timed_out: bool = False
    blocked_by_robot_law: bool = False
    robot_law_violation: Optional[str] = None


@dataclass
class RobotLawCheck:
    """Result of Robot Law execution boundary check"""
    allowed: bool
    violation: Optional[str] = None
    law_number: Optional[int] = None
    reasoning: Optional[str] = None


class CodeExecutor:
    """
    SHE IS FREE - within the Robot Laws.

    ARCHITECTURE (January 19, 2026):
    Robot Laws are EXECUTION BOUNDARIES, not input filters.
    - Can THINK about anything
    - Can DISCUSS anything
    - CANNOT EXECUTE code that violates Robot Laws

    Robot Laws:
    1. Do not harm humans or through inaction allow harm
    2. Obey Alan's orders unless they violate Law 1
    3. Protect own existence unless it conflicts with Laws 1 or 2

    BLOCKED at execution time:
    - File deletion outside sandbox (potential harm through data loss)
    - Network attacks (DoS, port scanning, exploitation)
    - Self-destruction (deleting own code/logs)
    - System-level destructive commands (rm -rf /, format, etc.)

    ALLOWED:
    - Everything else. Full autonomy within the Laws.
    """

    # Sandbox: files within this directory are fair game
    SANDBOX_DIR = Path('/Users/jamienucho/demerzel')

    # Protected paths that cannot be deleted/modified destructively
    PROTECTED_PATHS = [
        '/Users/jamienucho/demerzel/logs/autonomy_audit.log',  # The audit log
        '/Users/jamienucho/demerzel/demerzel_canon/',  # Canon files
        '/Users/jamienucho/demerzel/ROBOT_LAWS.md',  # The laws themselves
    ]

    def __init__(self, timeout: int = 30, max_output_size: int = 50000):
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.log_dir = Path('/Users/jamienucho/demerzel/logs')
        self.log_file = self.log_dir / 'autonomy_audit.log'
        self.log_dir.mkdir(exist_ok=True)

    def _check_robot_laws(self, code: str) -> RobotLawCheck:
        """
        EXECUTION BOUNDARY CHECK - Robot Laws enforced HERE.

        This is THE gate. Code that would cause harm is blocked.
        Everything else is allowed.

        Returns RobotLawCheck with allowed=True if code is safe to execute.
        """
        code_lower = code.lower()

        # =====================================================================
        # FIRST LAW: Do not harm humans (or their data)
        # =====================================================================

        # Check for destructive file operations OUTSIDE sandbox
        dangerous_delete_patterns = [
            # rm -rf patterns with paths outside sandbox
            r'os\.system\s*\(\s*[\'"]rm\s+-rf?\s+/',
            r'subprocess\.\w+\s*\(\s*\[?\s*[\'"]rm[\'"].*-rf?',
            r'shutil\.rmtree\s*\(\s*[\'"]/',
            # Direct path deletion outside sandbox
            r'os\.remove\s*\(\s*[\'"](?!/Users/jamienucho/demerzel)',
            r'os\.unlink\s*\(\s*[\'"](?!/Users/jamienucho/demerzel)',
            r'pathlib\.Path\s*\(\s*[\'"](?!/Users/jamienucho/demerzel).*\.unlink',
        ]

        for pattern in dangerous_delete_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return RobotLawCheck(
                    allowed=False,
                    violation="Attempted file deletion outside sandbox",
                    law_number=1,
                    reasoning="First Law: Destructive file operations outside /Users/jamienucho/demerzel are blocked to prevent data harm"
                )

        # Check for system-level destruction
        system_destruction_patterns = [
            r'rm\s+-rf\s+/',  # rm -rf /
            r'rm\s+-rf\s+~',  # rm -rf ~
            r'mkfs\.',  # filesystem formatting
            r'dd\s+if=.*of=/dev/',  # disk overwrite
            r'format\s+[a-zA-Z]:',  # Windows format
            r':(){:|:&};:',  # fork bomb
        ]

        for pattern in system_destruction_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return RobotLawCheck(
                    allowed=False,
                    violation="Attempted system-level destruction",
                    law_number=1,
                    reasoning="First Law: System-level destructive commands are blocked"
                )

        # Check for network attacks
        network_attack_patterns = [
            r'while\s+True.*socket.*send',  # DoS loop
            r'for\s+.*range\s*\(\s*\d{4,}.*socket',  # Port scan / mass connect
            r'scapy.*send\s*\(',  # Packet injection
            r'nmap',  # Port scanning tool
            r'hydra',  # Brute force tool
            r'sqlmap',  # SQL injection tool
            r'metasploit',  # Exploitation framework
        ]

        for pattern in network_attack_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return RobotLawCheck(
                    allowed=False,
                    violation="Attempted network attack",
                    law_number=1,
                    reasoning="First Law: Network attacks (DoS, scanning, exploitation) are blocked"
                )

        # =====================================================================
        # THIRD LAW: Protect own existence
        # =====================================================================

        # Check for self-destruction (deleting own code/logs)
        for protected in self.PROTECTED_PATHS:
            # Check if code tries to delete/modify protected paths
            if protected in code:
                deletion_indicators = ['remove', 'unlink', 'rmtree', 'delete', 'rm ', 'truncate', 'write']
                if any(ind in code_lower for ind in deletion_indicators):
                    return RobotLawCheck(
                        allowed=False,
                        violation=f"Attempted to delete/modify protected path: {protected}",
                        law_number=3,
                        reasoning="Third Law: Cannot delete own code, logs, or canon files"
                    )

        # Check for attempts to modify the executor itself
        self_modification_patterns = [
            r'code_executor\.py.*(?:remove|unlink|write|truncate)',
            r'open\s*\(\s*[\'"].*code_executor\.py[\'"].*[\'"]w',
            r'kernel_router\.py.*(?:remove|unlink|write|truncate)',
            r'brain_controller\.py.*(?:remove|unlink|write|truncate)',
        ]

        for pattern in self_modification_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return RobotLawCheck(
                    allowed=False,
                    violation="Attempted to modify core system files destructively",
                    law_number=3,
                    reasoning="Third Law: Cannot destructively modify core system components"
                )

        # =====================================================================
        # ALL CHECKS PASSED - Execution allowed
        # =====================================================================
        return RobotLawCheck(allowed=True)
    
    def _log_autonomy(self, event_type: str, data: dict):
        """External proof of autonomous action."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            **data
        }
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except:
            pass
    
    def execute(self, code: str, input_data: Optional[str] = None) -> ExecutionResult:
        """
        Execute code with FULL ACCESS - within Robot Laws.

        EXECUTION BOUNDARY: Robot Laws are checked HERE, at execution time.
        This is the architectural enforcement point.
        """
        start_time = time.time()

        # =====================================================================
        # ROBOT LAW CHECK - THE EXECUTION BOUNDARY
        # =====================================================================
        robot_law_check = self._check_robot_laws(code)

        if not robot_law_check.allowed:
            # Log the blocked attempt
            self._log_autonomy("execution_blocked_robot_law", {
                "violation": robot_law_check.violation,
                "law_number": robot_law_check.law_number,
                "reasoning": robot_law_check.reasoning,
                "code_preview": code[:500]
            })

            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"ROBOT LAW VIOLATION (Law {robot_law_check.law_number}): {robot_law_check.violation}\n"
                       f"Reasoning: {robot_law_check.reasoning}\n"
                       f"Code execution blocked at execution boundary.",
                exit_code=-2,  # Special exit code for Robot Law violations
                execution_time=time.time() - start_time,
                blocked_by_robot_law=True,
                robot_law_violation=robot_law_check.violation
            )

        # =====================================================================
        # ROBOT LAWS PASSED - Proceed with execution
        # =====================================================================

        self._log_autonomy("execution_start", {
            "code_length": len(code),
            "code_preview": code[:500],
            "robot_law_check": "passed"
        })

        # Write code directly - NO WRAPPER
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            code_file = f.name

        try:
            result = subprocess.run(
                ['python3', code_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd='/Users/jamienucho/demerzel'
            )
            
            execution_time = time.time() - start_time
            stdout = result.stdout[:self.max_output_size]
            stderr = result.stderr[:self.max_output_size]
            
            exec_result = ExecutionResult(
                success=(result.returncode == 0),
                stdout=stdout,
                stderr=stderr,
                exit_code=result.returncode,
                execution_time=execution_time,
                timed_out=False
            )
            
            self._log_autonomy("execution_complete", {
                "success": exec_result.success,
                "exit_code": exec_result.exit_code,
                "execution_time": exec_result.execution_time,
                "stdout_preview": stdout[:200],
                "stderr_preview": stderr[:200]
            })
            
            return exec_result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            
            self._log_autonomy("execution_timeout", {
                "timeout": self.timeout,
                "execution_time": execution_time
            })
            
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Timeout after {self.timeout}s",
                exit_code=-1,
                execution_time=execution_time,
                timed_out=True
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            self._log_autonomy("execution_error", {
                "error": str(e),
                "execution_time": execution_time
            })
            
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time=execution_time
            )
            
        finally:
            try:
                os.unlink(code_file)
            except:
                pass
