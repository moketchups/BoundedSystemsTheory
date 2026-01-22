"""
Tests for DeepSeek API Integration (January 19, 2026)

DeepSeek is added as the 5th LLM option alongside Claude, GPT-4o, Gemini, and Grok.
"""

import pytest
import sys
sys.path.insert(0, '/Users/jamienucho/demerzel')


class TestDeepSeekIntegration:
    """Tests for DeepSeek integration into the cognitive layer"""

    def test_smart_model_selector_includes_deepseek(self):
        """SmartModelSelector.MODELS should include deepseek"""
        from smart_model_selector import SmartModelSelector

        assert "deepseek" in SmartModelSelector.MODELS
        assert len(SmartModelSelector.MODELS) == 6  # claude, gpt-4o, gemini, grok, deepseek, mistral

    def test_smart_model_selector_initializes_deepseek_failures(self):
        """SmartModelSelector should track deepseek failures"""
        from smart_model_selector import SmartModelSelector

        selector = SmartModelSelector()
        assert "deepseek" in selector.recent_failures

    def test_cognitive_has_deepseek_client_attr(self):
        """MultiModelCognitive should have deepseek_client attribute after init"""
        from multi_model_cognitive import MultiModelCognitive

        # Check class has the _call_deepseek method
        assert hasattr(MultiModelCognitive, '_call_deepseek')

    def test_cognitive_has_call_deepseek_method(self):
        """MultiModelCognitive should have _call_deepseek method"""
        from multi_model_cognitive import MultiModelCognitive
        import inspect

        # Check method signature
        sig = inspect.signature(MultiModelCognitive._call_deepseek)
        params = list(sig.parameters.keys())

        assert 'self' in params
        assert 'prompt' in params
        assert 'system' in params

    def test_call_model_handles_deepseek(self):
        """_call_model should handle 'deepseek' model name"""
        from multi_model_cognitive import MultiModelCognitive
        import inspect

        # Check source code includes deepseek dispatch
        source = inspect.getsource(MultiModelCognitive._call_model)

        assert 'deepseek' in source
        assert 'self.deepseek_client' in source
        assert '_call_deepseek' in source

    def test_init_clients_initializes_deepseek(self):
        """_init_clients should attempt to initialize deepseek_client"""
        from multi_model_cognitive import MultiModelCognitive
        import inspect

        source = inspect.getsource(MultiModelCognitive._init_clients)

        assert 'DEEPSEEK_API_KEY' in source
        assert 'deepseek_client' in source
        assert 'api.deepseek.com' in source

    def test_models_list_includes_deepseek_when_client_exists(self):
        """models list should include deepseek when client is initialized"""
        from multi_model_cognitive import MultiModelCognitive
        import inspect

        # Check __init__ source for deepseek model registration
        source = inspect.getsource(MultiModelCognitive.__init__)

        assert 'if self.deepseek_client:' in source
        assert 'self.models.append("deepseek")' in source


class TestDeepSeekModelSelection:
    """Tests for DeepSeek in model selection flow"""

    def test_selector_can_select_deepseek(self):
        """SmartModelSelector should be able to select deepseek"""
        from smart_model_selector import SmartModelSelector

        selector = SmartModelSelector()

        # deepseek should be in available models
        available = selector._get_healthy_models()
        assert "deepseek" in available

    def test_selector_respects_deepseek_exclusion(self):
        """SmartModelSelector should exclude deepseek when requested"""
        from smart_model_selector import SmartModelSelector

        selector = SmartModelSelector()

        # Exclude deepseek
        available = selector._get_healthy_models(exclude=["deepseek"])
        assert "deepseek" not in available

    def test_selector_can_learn_deepseek_outcomes(self):
        """SmartModelSelector should record deepseek outcomes"""
        from smart_model_selector import SmartModelSelector

        selector = SmartModelSelector()

        # Record an outcome
        selector.record_outcome("deepseek", "code_generation", True)

        # Check it was recorded
        assert "code_generation" in selector.task_patterns
        assert "deepseek" in selector.task_patterns["code_generation"]


class TestDeepSeekAPIFormat:
    """Tests for DeepSeek API call format"""

    def test_deepseek_uses_openai_format(self):
        """DeepSeek should use OpenAI-compatible chat format"""
        from multi_model_cognitive import MultiModelCognitive
        import inspect

        source = inspect.getsource(MultiModelCognitive._call_deepseek)

        # Should use chat.completions.create
        assert 'chat.completions.create' in source

        # Should use messages format
        assert '"role": "system"' in source
        assert '"role": "user"' in source

        # Should use deepseek-chat model
        assert 'deepseek-chat' in source

    def test_deepseek_base_url(self):
        """DeepSeek client should use correct base URL"""
        from multi_model_cognitive import MultiModelCognitive
        import inspect

        source = inspect.getsource(MultiModelCognitive._init_clients)

        assert 'base_url="https://api.deepseek.com"' in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
