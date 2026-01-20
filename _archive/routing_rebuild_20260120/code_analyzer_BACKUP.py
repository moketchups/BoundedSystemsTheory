from __future__ import annotations
import ast
import re
from dataclasses import dataclass
from typing import Set, List
from enum import Enum

class RiskLevel(Enum):
    LOW = "LOW_RISK"
    HIGH = "HIGH_RISK"
    BLOCKED = "BLOCKED"

@dataclass
class AnalysisResult:
    """Result of code analysis"""
    risk_level: RiskLevel
    dangerous_imports: List[str]
    dangerous_calls: List[str]
    file_operations: List[str]
    reasons: List[str]

class CodeAnalyzer:
    """
    Static code analyzer for Demerzel
    Classifies code risk before execution
    """
    
    # Modules that are always blocked
    BLOCKED_IMPORTS = {
        'subprocess', 'os', 'sys', 'socket', 'urllib', 'requests',
        'shutil', 'importlib', '__import__', 'eval', 'exec',
        'compile', 'pickle', 'shelve', 'multiprocessing', 'threading'
    }
    
    # Modules that trigger HIGH_RISK
    HIGH_RISK_IMPORTS = {
        'json', 'csv', 'tempfile', 'glob', 'io'
    }
    
    # Built-in functions that are dangerous
    DANGEROUS_BUILTINS = {
        'eval', 'exec', 'compile', '__import__',
        'input', 'breakpoint', 'exit', 'quit'
    }
    
    # File operation functions (HIGH_RISK)
    FILE_OPERATIONS = {
        'open', 'read', 'write', 'readlines', 'writelines'
    }
    
    def __init__(self):
        pass
    
    def analyze(self, code: str) -> AnalysisResult:
        """
        Analyze Python code and classify risk level
        
        Returns:
            AnalysisResult with risk classification and reasons
        """
        dangerous_imports = []
        dangerous_calls = []
        file_operations = []
        reasons = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return AnalysisResult(
                risk_level=RiskLevel.BLOCKED,
                dangerous_imports=[],
                dangerous_calls=[],
                file_operations=[],
                reasons=[f"Syntax error: {str(e)}"]
            )
        
        # Check for dangerous imports
        for node in ast.walk(tree):
            # Import statements
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if module in self.BLOCKED_IMPORTS:
                        dangerous_imports.append(module)
                        reasons.append(f"BLOCKED import: {module}")
                    elif module in self.HIGH_RISK_IMPORTS:
                        dangerous_imports.append(module)
                        reasons.append(f"HIGH_RISK import: {module}")
            
            # From imports
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    if module in self.BLOCKED_IMPORTS:
                        dangerous_imports.append(module)
                        reasons.append(f"BLOCKED import: {module}")
                    elif module in self.HIGH_RISK_IMPORTS:
                        dangerous_imports.append(module)
                        reasons.append(f"HIGH_RISK import: {module}")
            
            # Function calls
            elif isinstance(node, ast.Call):
                func_name = self._get_func_name(node.func)
                
                # Check for blocked builtins
                if func_name in self.DANGEROUS_BUILTINS:
                    dangerous_calls.append(func_name)
                    reasons.append(f"BLOCKED builtin: {func_name}")
                
                # Check for file operations
                elif func_name in self.FILE_OPERATIONS:
                    file_operations.append(func_name)
                    reasons.append(f"File operation: {func_name} (requires validation)")
        
        # Determine overall risk level
        if any('BLOCKED' in r for r in reasons):
            risk_level = RiskLevel.BLOCKED
        elif dangerous_imports or file_operations or dangerous_calls:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.LOW
        
        return AnalysisResult(
            risk_level=risk_level,
            dangerous_imports=dangerous_imports,
            dangerous_calls=dangerous_calls,
            file_operations=file_operations,
            reasons=reasons if reasons else ["No dangerous patterns detected"]
        )
    
    def _get_func_name(self, node) -> str:
        """Extract function name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return ""


def test_analyzer():
    """Test code analyzer with various code samples"""
    analyzer = CodeAnalyzer()
    
    print("=== Test 1: Safe code (LOW_RISK) ===")
    code = """
import math
result = sum(i**2 for i in range(100))
print(f"Result: {result}")
"""
    result = analyzer.analyze(code)
    print(f"Risk: {result.risk_level.value}")
    print(f"Reasons: {result.reasons}")
    
    print("\n=== Test 2: File operations (HIGH_RISK) ===")
    code = """
with open('data.txt', 'r') as f:
    data = f.read()
print(data)
"""
    result = analyzer.analyze(code)
    print(f"Risk: {result.risk_level.value}")
    print(f"Reasons: {result.reasons}")
    
    print("\n=== Test 3: Dangerous imports (BLOCKED) ===")
    code = """
import subprocess
subprocess.run(['ls', '-la'])
"""
    result = analyzer.analyze(code)
    print(f"Risk: {result.risk_level.value}")
    print(f"Reasons: {result.reasons}")
    
    print("\n=== Test 4: eval/exec (BLOCKED) ===")
    code = """
code = input("Enter code: ")
eval(code)
"""
    result = analyzer.analyze(code)
    print(f"Risk: {result.risk_level.value}")
    print(f"Reasons: {result.reasons}")


if __name__ == "__main__":
    test_analyzer()
