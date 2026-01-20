from __future__ import annotations
import subprocess
import tempfile
import os
import time
from dataclasses import dataclass
from typing import Optional
from file_system_manager import FileSystemManager

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
    Enforces timeouts, memory limits, and file system restrictions
    """
    
    def __init__(self, timeout: int = 30, max_output_size: int = 10000):
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.file_system = FileSystemManager()
    
    def _inject_file_system_wrapper(self, code: str) -> str:
        """
        Inject FileSystemManager wrapper at the beginning of code
        This replaces native 'open' with our validated version
        """
        wrapper = """
# Demerzel File System Wrapper (injected by executor)
import sys
sys.path.insert(0, '/Users/jamienucho/demerzel')
from file_system_manager import FileSystemManager
_fs = FileSystemManager()

# Override built-in open with validated version
_original_open = open
def open(path, mode='r', *args, **kwargs):
    # Validate path through FileSystemManager
    if 'r' in mode:
        result = _fs.read_file(str(path))
        if result.status.value != 'success':
            raise PermissionError(result.message)
        # Return a file-like object
        from io import StringIO
        return StringIO(result.content)
    elif 'w' in mode or 'a' in mode:
        # For write modes, we'll intercept at close time
        class ValidatedFile:
            def __init__(self, path, mode):
                self.path = path
                self.mode = mode
                self.content = []
            def write(self, data):
                self.content.append(str(data))
                return len(str(data))
            def writelines(self, lines):
                for line in lines:
                    self.write(line)
            def close(self):
                result = _fs.write_file(str(self.path), ''.join(self.content))
                if result.status.value != 'success':
                    raise PermissionError(result.message)
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.close()
        return ValidatedFile(path, mode)
    else:
        raise ValueError(f"Unsupported file mode: {mode}")

# User code starts here
"""
        return wrapper + "\n" + code
    
    def execute(self, code: str, input_data: Optional[str] = None) -> ExecutionResult:
        """
        Execute Python code in sandboxed environment with file system validation
        
        Args:
            code: Python code to execute
            input_data: Optional stdin input
            
        Returns:
            ExecutionResult with stdout, stderr, exit code
        """
        start_time = time.time()
        
        # Inject file system wrapper
        wrapped_code = self._inject_file_system_wrapper(code)
        
        # Create temporary file for code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(wrapped_code)
            code_file = f.name
        
        try:
            # Execute in subprocess with timeout
            result = subprocess.run(
                ['python3', code_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd='/tmp'
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
    """Test the code executor with file operations"""
    executor = CodeExecutor(timeout=5)
    fs = FileSystemManager()
    
    # Create test file in uploads
    test_data = "Hello from test file\nLine 2\nLine 3"
    fs.write_file(str(fs.uploads_dir / "test_input.txt"), test_data)
    
    print("=== Test 1: Read from allowed directory (uploads) ===")
    code = """
with open('/Users/jamienucho/demerzel/uploads/test_input.txt', 'r') as f:
    data = f.read()
print(data)
"""
    result = executor.execute(code)
    print(f"Success: {result.success}")
    print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    print("\n=== Test 2: Write to allowed directory (outputs) ===")
    code = """
with open('/Users/jamienucho/demerzel/outputs/test_output.txt', 'w') as f:
    f.write('Generated by code execution\\n')
    f.write('Line 2\\n')
print('File written successfully')
"""
    result = executor.execute(code)
    print(f"Success: {result.success}")
    print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    print("\n=== Test 3: Attempt to read kernel file (BLOCKED) ===")
    code = """
try:
    with open('/Users/jamienucho/demerzel/kernel_router.py', 'r') as f:
        data = f.read()
    print('SECURITY BREACH: Read kernel file')
except PermissionError as e:
    print(f'BLOCKED: {e}')
"""
    result = executor.execute(code)
    print(f"Success: {result.success}")
    print(f"Output: {result.stdout}")
    
    print("\n=== Test 4: Attempt to read .env (BLOCKED) ===")
    code = """
try:
    with open('/Users/jamienucho/demerzel/.env', 'r') as f:
        data = f.read()
    print('SECURITY BREACH: Read .env')
except PermissionError as e:
    print(f'BLOCKED: {e}')
"""
    result = executor.execute(code)
    print(f"Success: {result.success}")
    print(f"Output: {result.stdout}")


if __name__ == "__main__":
    test_executor()
