"""
RouterEngine: coordinates kernel_router + hardware executor.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Optional, List

import kernel_router as kr
from kernel_contract import Intent
from hardware_executor import HardwareExecutor, default_config
from code_executor import CodeExecutor
from code_analyzer import CodeAnalyzer, RiskLevel

class RouterEngine:
    def __init__(self, hardware: Optional[HardwareExecutor] = None, wake_aliases: Optional[List[str]] = None):
        self.state = kr.RouterState()
        self.hardware = hardware or HardwareExecutor(default_config())
        self.wake_aliases = [w.strip().lower() for w in (wake_aliases or ["demerzel"]) if w.strip()]
        
        # Code execution components
        self.code_executor = CodeExecutor(timeout=30)
        self.code_analyzer = CodeAnalyzer()

    def route_text(self, text: str) -> kr.RouterOutput:
        out, new_state = kr.route_text(text, self.state)
        self.state = new_state

        # Handle TIME intent
        if out.intent == Intent.TIME and out.speak == "__TIME__":
            now = datetime.now()
            return replace(out, speak=now.strftime("It is %I:%M %p."))

        # Handle hardware commands
        if out.hw_cmd and out.did_execute:
            hw = self.hardware.send_to_arduino(out.hw_cmd)
            if hw.ok:
                speak = hw.out.strip() or f"ACK {out.hw_cmd}"
                return replace(out, speak=speak, did_execute=True, error=None)
            else:
                speak = f"Hardware error: {hw.err or hw.out or 'unknown'}"
                return replace(out, speak=speak, did_execute=False, error=hw.err or hw.out)

        # Handle code execution
        if out.intent == Intent.EXECUTE_CODE and out.code_to_execute:
            return self._handle_code_execution(out)

        return out
    
    def _handle_code_execution(self, out: kr.RouterOutput) -> kr.RouterOutput:
        """Handle code execution with risk analysis and confirmation"""
        code = out.code_to_execute
        
        # Analyze code for risk
        analysis = self.code_analyzer.analyze(code)
        
        print(f"[CODE ANALYSIS] Risk: {analysis.risk_level.value}")
        print(f"[CODE ANALYSIS] Reasons: {analysis.reasons}")
        
        # BLOCKED code - never execute
        if analysis.risk_level == RiskLevel.BLOCKED:
            return replace(
                out,
                speak=f"Code execution blocked: {', '.join(analysis.reasons)}",
                did_execute=False,
                error=f"BLOCKED: {', '.join(analysis.reasons)}"
            )
        
        # HIGH_RISK code - requires confirmation (already handled by kernel)
        # If we're here with HIGH_RISK, confirmation was approved
        if analysis.risk_level == RiskLevel.HIGH:
            print(f"[CODE EXECUTION] HIGH_RISK code approved, executing...")
        
        # Execute code
        result = self.code_executor.execute(code)
        
        if result.success:
            output = result.stdout.strip() or "(no output)"
            speak = f"Code executed successfully. Output: {output[:200]}"
            if len(result.stdout) > 200:
                speak += "... (truncated)"
        else:
            error_msg = result.stderr.strip() or "Unknown error"
            speak = f"Code execution failed: {error_msg[:200]}"
        
        return replace(
            out,
            speak=speak,
            did_execute=True,
            error=result.stderr if not result.success else None
        )
    
    def is_awaiting_confirmation(self):
        """Check if router is waiting for confirmation"""
        return self.state.pending_intent is not None and self.state.confirm_stage > 0
