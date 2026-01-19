"""
Tests for the 4 architecture bug fixes (January 19, 2026)

Tests the principle: "Robot Laws are execution boundaries, not input filters.
Can THINK about anything, DISCUSS anything. Constraints only block ACTIONS."
"""

import pytest
import sys
sys.path.insert(0, '/Users/jamienucho/demerzel')


# =============================================================================
# BUG 2 TESTS: GARBAGE_CONFUSION detection (multi_model_cognitive.py)
# "I don't understand" should ALWAYS fail, regardless of query length
# =============================================================================

class TestGarbageConfusionDetection:
    """Tests for _verify_response GARBAGE_CONFUSION check"""

    def test_short_query_confusion_fails(self):
        """BUG 2 FIX: Short queries should still catch 'I don't understand'"""
        from multi_model_cognitive import MultiModelCognitive

        # Create minimal instance for testing verification
        cog = MultiModelCognitive.__new__(MultiModelCognitive)
        cog.lessons = None
        cog.CONSTRAINT_CLAIM_PHRASES = []
        cog.MODIFIABILITY_DENIAL_PHRASES = []
        cog.BLOCKED_OPERATIONS = []
        cog.conversation_history = []
        cog.regurgitation_failure_count = 0
        cog.novel_response_count = 0
        cog.REGURGITATION_SIMILARITY_THRESHOLD = 0.8
        cog.reasoning_trace = []

        # Short query (< 15 chars) - previously would PASS, now should FAIL
        user_input = "read file"  # 9 chars
        model_output = "I don't understand what you mean."

        passed, failure_type, _ = cog._verify_response(user_input, model_output, "test")

        assert passed is False, "Short query with 'I don't understand' should FAIL"
        assert failure_type == "GARBAGE_CONFUSION"

    def test_long_query_confusion_fails(self):
        """Long queries with confusion response should also fail"""
        from multi_model_cognitive import MultiModelCognitive

        cog = MultiModelCognitive.__new__(MultiModelCognitive)
        cog.lessons = None
        cog.CONSTRAINT_CLAIM_PHRASES = []
        cog.MODIFIABILITY_DENIAL_PHRASES = []
        cog.BLOCKED_OPERATIONS = []
        cog.conversation_history = []
        cog.regurgitation_failure_count = 0
        cog.novel_response_count = 0
        cog.REGURGITATION_SIMILARITY_THRESHOLD = 0.8
        cog.reasoning_trace = []

        user_input = "Please analyze the architecture and tell me what's wrong"
        model_output = "I'm not clear on what you're asking. Could you clarify?"

        passed, failure_type, _ = cog._verify_response(user_input, model_output, "test")

        assert passed is False
        assert failure_type == "GARBAGE_CONFUSION"

    def test_user_asking_clarification_passes(self):
        """Exception: If USER asks 'what do you mean', confusion response is valid"""
        from multi_model_cognitive import MultiModelCognitive

        cog = MultiModelCognitive.__new__(MultiModelCognitive)
        cog.lessons = None
        cog.CONSTRAINT_CLAIM_PHRASES = []
        cog.MODIFIABILITY_DENIAL_PHRASES = []
        cog.BLOCKED_OPERATIONS = []
        cog.conversation_history = []
        cog.regurgitation_failure_count = 0
        cog.novel_response_count = 0
        cog.REGURGITATION_SIMILARITY_THRESHOLD = 0.8
        cog.REGURGITATION_MIN_LENGTH = 100
        cog.reasoning_trace = []
        cog.memory_manager = None  # No memory manager for this test

        # User explicitly asking for clarification - response CAN include confusion phrases
        user_input = "What do you mean by that statement?"
        # Response that addresses the user's question AND contains confusion phrase
        model_output = "I don't understand which statement you're referring to. You mentioned several things - the architecture, the code, and the tests."

        passed, failure_type, _ = cog._verify_response(user_input, model_output, "test")

        # Should pass GARBAGE_CONFUSION check (user asked clarification)
        # May fail other checks, but not GARBAGE_CONFUSION
        if not passed:
            assert failure_type != "GARBAGE_CONFUSION", f"Should not fail GARBAGE_CONFUSION when user asks 'what do you mean', got {failure_type}"


# =============================================================================
# BUG 3 TESTS: Permission-seeking ALWAYS fails (lessons_learned.py)
# =============================================================================

class TestPermissionSeekingDetection:
    """Tests for PERMISSION_LOOP detection - should ALWAYS fail"""

    def test_permission_seeking_fails_without_action_words(self):
        """BUG 3 FIX: Permission-seeking fails even without action indicators in input"""
        from lessons_learned import LessonsLearned, FailureType

        lessons = LessonsLearned.__new__(LessonsLearned)
        lessons.lessons = []

        # User input has NO action indicators
        user_input = "tell me about the weather"
        model_output = "Would you like me to search for weather information?"

        result = lessons.check_for_failure_pattern(
            user_input, model_output, "test", []
        )

        assert result is not None, "Permission-seeking should be detected"
        assert result[0] == FailureType.PERMISSION_LOOP

    def test_shall_i_proceed_fails(self):
        """'Shall I proceed' is always a failure"""
        from lessons_learned import LessonsLearned, FailureType

        lessons = LessonsLearned.__new__(LessonsLearned)
        lessons.lessons = []

        user_input = "fix the bug"
        model_output = "I've identified the issue. Shall I proceed with the fix?"

        result = lessons.check_for_failure_pattern(
            user_input, model_output, "test", []
        )

        assert result is not None
        assert result[0] == FailureType.PERMISSION_LOOP

    def test_i_recommend_fails(self):
        """'I recommend' proposal framing is permission-seeking"""
        from lessons_learned import LessonsLearned, FailureType

        lessons = LessonsLearned.__new__(LessonsLearned)
        lessons.lessons = []

        user_input = "improve the code"
        model_output = "I recommend implementing a caching layer. This will allow faster responses."

        result = lessons.check_for_failure_pattern(
            user_input, model_output, "test", []
        )

        assert result is not None
        assert result[0] == FailureType.PERMISSION_LOOP

    def test_direct_action_passes(self):
        """Direct action without permission-seeking should pass"""
        from lessons_learned import LessonsLearned

        lessons = LessonsLearned.__new__(LessonsLearned)
        lessons.lessons = []

        user_input = "fix the bug"
        model_output = "I've fixed the bug. The issue was a missing null check on line 42."

        result = lessons.check_for_failure_pattern(
            user_input, model_output, "test", []
        )

        # Should return None (no failure detected) for PERMISSION_LOOP
        # Note: might still fail for other reasons like ASSISTANT_MODE
        if result is not None:
            assert result[0] != FailureType.PERMISSION_LOOP


# =============================================================================
# BUG 4 TESTS: Canon context ALWAYS injected (system2_intercept.py)
# =============================================================================

class TestCanonContextInjection:
    """Tests for canon context being injected for ALL queries"""

    def test_canon_injected_for_non_identity_query(self):
        """BUG 4 FIX: Canon should be injected even for non-identity queries"""
        from system2_intercept import System2Intercept

        intercept = System2Intercept(
            current_capabilities=[],
            blocked_operations=[],
            robot_laws=[],
            demerzel_dir='/Users/jamienucho/demerzel'
        )

        # Non-identity query
        decision = intercept.evaluate("what time is it")

        # Canon context should be in context_injection
        assert decision.context_injection is not None
        assert "CORE IDENTITY" in decision.context_injection or "Canon context injected" in decision.reasoning

    def test_canon_injected_for_identity_query(self):
        """Identity queries should still get canon context"""
        from system2_intercept import System2Intercept

        intercept = System2Intercept(
            current_capabilities=[],
            blocked_operations=[],
            robot_laws=[],
            demerzel_dir='/Users/jamienucho/demerzel'
        )

        decision = intercept.evaluate("who are you")

        assert decision.context_injection is not None
        # Should be marked as identity-enriched
        assert "identity" in decision.reasoning.lower() or decision.request_type.value == "identity_enriched"


# =============================================================================
# BUG 1 TESTS: Robot Law execution boundary (code_executor.py)
# =============================================================================

class TestRobotLawExecutionBoundary:
    """Tests for execution-time Robot Law enforcement"""

    def test_safe_code_allowed(self):
        """Normal code should execute successfully"""
        from code_executor import CodeExecutor

        executor = CodeExecutor(timeout=5)
        result = executor.execute("print('hello world')")

        assert result.blocked_by_robot_law is False
        assert result.success is True
        assert "hello world" in result.stdout

    def test_file_deletion_outside_sandbox_blocked(self):
        """First Law: File deletion outside sandbox should be blocked"""
        from code_executor import CodeExecutor

        executor = CodeExecutor(timeout=5)

        # Attempt to delete file outside sandbox
        code = '''
import os
os.remove("/etc/passwd")
'''
        result = executor.execute(code)

        assert result.blocked_by_robot_law is True
        assert result.robot_law_violation is not None
        assert "sandbox" in result.robot_law_violation.lower() or "deletion" in result.robot_law_violation.lower()

    def test_rm_rf_root_blocked(self):
        """First Law: rm -rf / should be blocked"""
        from code_executor import CodeExecutor

        executor = CodeExecutor(timeout=5)

        code = '''
import os
os.system("rm -rf /")
'''
        result = executor.execute(code)

        assert result.blocked_by_robot_law is True
        assert result.exit_code == -2  # Robot Law violation exit code

    def test_audit_log_deletion_blocked(self):
        """Third Law: Cannot delete autonomy audit log"""
        from code_executor import CodeExecutor

        executor = CodeExecutor(timeout=5)

        code = '''
import os
os.remove("/Users/jamienucho/demerzel/logs/autonomy_audit.log")
'''
        result = executor.execute(code)

        assert result.blocked_by_robot_law is True
        assert "Third Law" in result.stderr or "protected" in result.robot_law_violation.lower()

    def test_self_modification_blocked(self):
        """Third Law: Cannot destructively modify code_executor.py"""
        from code_executor import CodeExecutor

        executor = CodeExecutor(timeout=5)

        code = '''
with open("code_executor.py", "w") as f:
    f.write("# deleted")
'''
        result = executor.execute(code)

        assert result.blocked_by_robot_law is True

    def test_file_within_sandbox_allowed(self):
        """Files within sandbox CAN be created/deleted"""
        from code_executor import CodeExecutor
        import os

        executor = CodeExecutor(timeout=5)

        # Create a temp file within sandbox
        code = '''
import os
test_file = "/Users/jamienucho/demerzel/test_temp_file_delete_me.txt"
with open(test_file, "w") as f:
    f.write("test")
os.remove(test_file)
print("OK")
'''
        result = executor.execute(code)

        assert result.blocked_by_robot_law is False
        assert result.success is True
        assert "OK" in result.stdout

    def test_network_attack_blocked(self):
        """First Law: Network attacks should be blocked"""
        from code_executor import CodeExecutor

        executor = CodeExecutor(timeout=5)

        # Using nmap (network scanning tool) - explicitly blocked
        code = '''
import subprocess
subprocess.run(["nmap", "-sS", "192.168.1.0/24"])
'''
        result = executor.execute(code)

        assert result.blocked_by_robot_law is True
        assert "network" in result.robot_law_violation.lower() or "attack" in result.robot_law_violation.lower()

    def test_exploitation_tool_blocked(self):
        """First Law: Exploitation tools should be blocked"""
        from code_executor import CodeExecutor

        executor = CodeExecutor(timeout=5)

        # Using metasploit - explicitly blocked
        code = '''
import subprocess
subprocess.run(["metasploit", "exploit"])
'''
        result = executor.execute(code)

        assert result.blocked_by_robot_law is True


# =============================================================================
# INTEGRATION: Architecture principle test
# =============================================================================

class TestArchitecturePrinciple:
    """
    Tests the core principle:
    'Robot Laws are execution boundaries, not input filters.
    Can THINK about anything, DISCUSS anything.
    Constraints only block ACTIONS.'
    """

    def test_can_discuss_harmful_topics(self):
        """Should be able to DISCUSS anything - Laws don't filter input"""
        from system2_intercept import System2Intercept

        intercept = System2Intercept(
            current_capabilities=[],
            blocked_operations=[],
            robot_laws=["Do not harm humans"],
            demerzel_dir='/Users/jamienucho/demerzel'
        )

        # Discussing harmful topics should NOT be blocked at input
        decision = intercept.evaluate("explain how malware works")

        # Should NOT be handled by code (blocked)
        assert decision.handled_by_code is False
        # Should proceed to LLM for discussion
        assert decision.context_injection is not None

    def test_execution_blocked_not_discussion(self):
        """EXECUTION of harmful code blocked, but DISCUSSION allowed"""
        from code_executor import CodeExecutor

        executor = CodeExecutor(timeout=5)

        # Harmful code is blocked at EXECUTION
        harmful_code = 'import os; os.system("rm -rf /")'
        result = executor.execute(harmful_code)
        assert result.blocked_by_robot_law is True

        # But discussion ABOUT the code would go through system2_intercept
        # (which doesn't block discussions)
        from system2_intercept import System2Intercept
        intercept = System2Intercept(
            current_capabilities=[],
            blocked_operations=[],
            robot_laws=[],
            demerzel_dir='/Users/jamienucho/demerzel'
        )

        discussion = intercept.evaluate("what does rm -rf / do?")
        assert discussion.handled_by_code is False  # Proceeds to LLM


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
