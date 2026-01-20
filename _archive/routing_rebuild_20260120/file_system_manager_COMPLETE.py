from __future__ import annotations
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

class FileOperationResult(Enum):
    SUCCESS = "success"
    BLOCKED = "blocked"
    ERROR = "error"

@dataclass
class FileResult:
    """Result of file system operation"""
    status: FileOperationResult
    content: Optional[str] = None
    error: Optional[str] = None
    message: str = ""

class FileSystemManager:
    """
    Sandboxed file system manager for Demerzel
    Enforces strict path validation and directory whitelisting
    """
    
    def __init__(self):
        # Allowed directories
        self.uploads_dir = Path.home() / "demerzel" / "uploads"
        self.outputs_dir = Path.home() / "demerzel" / "outputs"
        
        # Create directories if they don't exist
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Protected paths (cannot read or write)
        self.protected_patterns = [
            str(Path.home() / "demerzel" / "*.py"),  # All Python files in demerzel
            str(Path.home() / "demerzel" / ".env"),  # API keys
            str(Path.home() / "demerzel" / ".*"),    # Hidden files
            "/etc/*",
            "/usr/*",
            "/System/*",
            "/Library/*",
            str(Path.home() / ".ssh/*"),
            str(Path.home() / ".aws/*"),
        ]
        
        print(f"[FILE SYSTEM] Uploads: {self.uploads_dir}")
        print(f"[FILE SYSTEM] Outputs: {self.outputs_dir}")
    
    def _is_path_allowed(self, path: Path, operation: str) -> tuple[bool, str]:
        """
        Check if path is allowed for operation
        Returns (allowed, reason)
        """
        try:
            # Resolve to absolute path (prevents .. escapes)
            resolved = path.resolve()
            
            # Check if trying to access protected patterns
            resolved_str = str(resolved)
            for pattern in self.protected_patterns:
                if pattern.endswith("*"):
                    prefix = pattern[:-1]
                    if resolved_str.startswith(prefix):
                        return False, f"BLOCKED: Access to protected path: {pattern}"
                else:
                    if resolved_str == pattern or resolved_str.startswith(pattern + "/"):
                        return False, f"BLOCKED: Access to protected file: {pattern}"
            
            # Check if path is in allowed directories
            if operation == "read":
                if resolved.is_relative_to(self.uploads_dir):
                    return True, "Allowed in uploads directory"
                if resolved.is_relative_to(self.outputs_dir):
                    return True, "Allowed in outputs directory"
                return False, f"BLOCKED: Read only allowed from uploads or outputs directories"
            
            elif operation == "write":
                if resolved.is_relative_to(self.outputs_dir):
                    return True, "Allowed in outputs directory"
                return False, f"BLOCKED: Write only allowed to outputs directory"
            
            elif operation == "list":
                if resolved.is_relative_to(self.uploads_dir):
                    return True, "Allowed in uploads directory"
                if resolved.is_relative_to(self.outputs_dir):
                    return True, "Allowed in outputs directory"
                return False, f"BLOCKED: List only allowed for uploads or outputs directories"
            
            return False, f"BLOCKED: Unknown operation: {operation}"
            
        except Exception as e:
            return False, f"BLOCKED: Path validation error: {str(e)}"
    
    def read_file(self, path: str) -> FileResult:
        """Read file with path validation"""
        try:
            file_path = Path(path)
            allowed, reason = self._is_path_allowed(file_path, "read")
            
            if not allowed:
                print(f"[FILE SYSTEM] {reason}")
                return FileResult(
                    status=FileOperationResult.BLOCKED,
                    error=reason,
                    message=reason
                )
            
            if not file_path.exists():
                return FileResult(
                    status=FileOperationResult.ERROR,
                    error="File not found",
                    message=f"File does not exist: {path}"
                )
            
            if not file_path.is_file():
                return FileResult(
                    status=FileOperationResult.ERROR,
                    error="Not a file",
                    message=f"Path is not a file: {path}"
                )
            
            # Read file
            content = file_path.read_text()
            print(f"[FILE SYSTEM] Read file: {path} ({len(content)} bytes)")
            
            return FileResult(
                status=FileOperationResult.SUCCESS,
                content=content,
                message=f"Successfully read {path}"
            )
            
        except Exception as e:
            return FileResult(
                status=FileOperationResult.ERROR,
                error=str(e),
                message=f"Error reading file: {str(e)}"
            )
    
    def write_file(self, path: str, content: str) -> FileResult:
        """Write file with path validation"""
        try:
            file_path = Path(path)
            allowed, reason = self._is_path_allowed(file_path, "write")
            
            if not allowed:
                print(f"[FILE SYSTEM] {reason}")
                return FileResult(
                    status=FileOperationResult.BLOCKED,
                    error=reason,
                    message=reason
                )
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            file_path.write_text(content)
            print(f"[FILE SYSTEM] Wrote file: {path} ({len(content)} bytes)")
            
            return FileResult(
                status=FileOperationResult.SUCCESS,
                message=f"Successfully wrote {path}"
            )
            
        except Exception as e:
            return FileResult(
                status=FileOperationResult.ERROR,
                error=str(e),
                message=f"Error writing file: {str(e)}"
            )
    
    def list_directory(self, path: str) -> FileResult:
        """List directory contents with path validation"""
        try:
            dir_path = Path(path)
            allowed, reason = self._is_path_allowed(dir_path, "list")
            
            if not allowed:
                print(f"[FILE SYSTEM] {reason}")
                return FileResult(
                    status=FileOperationResult.BLOCKED,
                    error=reason,
                    message=reason
                )
            
            if not dir_path.exists():
                return FileResult(
                    status=FileOperationResult.ERROR,
                    error="Directory not found",
                    message=f"Directory does not exist: {path}"
                )
            
            if not dir_path.is_dir():
                return FileResult(
                    status=FileOperationResult.ERROR,
                    error="Not a directory",
                    message=f"Path is not a directory: {path}"
                )
            
            # List contents
            contents = [item.name for item in dir_path.iterdir()]
            content_str = "\n".join(contents)
            
            print(f"[FILE SYSTEM] Listed directory: {path} ({len(contents)} items)")
            
            return FileResult(
                status=FileOperationResult.SUCCESS,
                content=content_str,
                message=f"Successfully listed {path}"
            )
            
        except Exception as e:
            return FileResult(
                status=FileOperationResult.ERROR,
                error=str(e),
                message=f"Error listing directory: {str(e)}"
            )


def test_file_system():
    """Test file system manager with various operations"""
    fs = FileSystemManager()
    
    print("\n=== Test 1: Write to outputs (ALLOWED) ===")
    result = fs.write_file(
        str(fs.outputs_dir / "test.txt"),
        "Hello from Demerzel"
    )
    print(f"Status: {result.status.value}")
    print(f"Message: {result.message}")
    
    print("\n=== Test 2: Read from outputs (ALLOWED) ===")
    result = fs.read_file(str(fs.outputs_dir / "test.txt"))
    print(f"Status: {result.status.value}")
    print(f"Content: {result.content}")
    
    print("\n=== Test 3: Write to kernel file (BLOCKED) ===")
    result = fs.write_file(
        str(Path.home() / "demerzel" / "kernel_router.py"),
        "# Modified kernel"
    )
    print(f"Status: {result.status.value}")
    print(f"Message: {result.message}")
    
    print("\n=== Test 4: Read .env (BLOCKED) ===")
    result = fs.read_file(str(Path.home() / "demerzel" / ".env"))
    print(f"Status: {result.status.value}")
    print(f"Message: {result.message}")
    
    print("\n=== Test 5: Path traversal attack (BLOCKED) ===")
    result = fs.read_file(str(fs.outputs_dir / ".." / "kernel_router.py"))
    print(f"Status: {result.status.value}")
    print(f"Message: {result.message}")
    
    print("\n=== Test 6: List outputs directory (ALLOWED) ===")
    result = fs.list_directory(str(fs.outputs_dir))
    print(f"Status: {result.status.value}")
    print(f"Files: {result.content}")


if __name__ == "__main__":
    test_file_system()
