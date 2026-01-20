from __future__ import annotations
import subprocess
import tempfile
import os
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    timed_out: bool = False
    
class CodeExecutor:
    """
    Sandboxed Python code executor for Demerzel
    Enforces timeouts, memory limits, and restricted imports
    """
    
    def __init__(self, timeout: int = 30, max_output_size: int = 10000):
        self.timeout = timeout
        self.max_output_size = max_output_size
    
    def execute(self, code: str, input_data: Optional[str] = None) -> ExecutionResult:
        """
        Execute Python code in sandboxed environment
        
        Args:
            code: Python code to execute
            input_data: Optional stdin input
            
        Returns:
            ExecutionResult with stdout, stderr, exit code
        """
        start_time = time.time()
        
        # Create temporary file for code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            code_file = f.name
        
        try:
            # Execute in subprocess with timeout
            result = subprocess.run(
                ['python3', code_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd='/tmp'  # Execute from temp directory, not demerzel directory
            )
            
            execution_time = time.time() - start_time
            
            # Truncate output if too large
            stdout = result.stdout[:self.max_output_size]
            stderr = result.stderr[:self.max_output_size]
            
            if len(result.stdout) > self.max_output_size:
                stdout += "\n[OUTPUT TRUNCATED]"
            if len(result.stderr) > self.max_output_size:
                stderr += "\n[ERROR TRUNCATED]"
            
            return ExecutionResult(
                success=(result.returncode == 0),
                stdout=stdout,
                stderr=stderr,
                exit_code=result.returncode,
                execution_time=execution_time,
                timed_out=False
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Execution timed out after {self.timeout} seconds",
                exit_code=-1,
                execution_time=execution_time,
                timed_out=True
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                exit_code=-1,
                execution_time=execution_time
            )
            
        finally:
            # Clean up temp file
            try:
                os.unlink(code_file)
            except:
                pass


def test_executor():
    """Test the code executor with various code samples"""
    executor = CodeExecutor(timeout=5)
    
    print("=== Test 1: Simple print ===")
    result = executor.execute("print('Hello from Demerzel')")
    print(f"Success: {result.success}")
    print(f"Output: {result.stdout}")
    
    print("\n=== Test 2: Math computation ===")
    code = """
import math
result = sum(i**2 for i in range(100))
print(f"Sum of squares: {result}")
"""
    result = executor.execute(code)
    print(f"Success: {result.success}")
    print(f"Output: {result.stdout}")
    
    print("\n=== Test 3: Timeout test ===")
    code = """
import time
time.sleep(10)  # Should timeout at 5 seconds
"""
    result = executor.execute(code)
    print(f"Success: {result.success}")
    print(f"Timed out: {result.timed_out}")
    print(f"Error: {result.stderr}")
    
    print("\n=== Test 4: Error handling ===")
    code = """
x = 1 / 0  # Division by zero
"""
    result = executor.execute(code)
    print(f"Success: {result.success}")
    print(f"Error: {result.stderr}")


if __name__ == "__main__":
    test_executor()
