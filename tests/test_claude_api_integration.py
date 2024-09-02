import unittest
from unittest.mock import patch, MagicMock
from src.claude_manager import ClaudeManager
import tenacity
import anthropic
import re
from src.llm_evaluator import LLMEvaluator

class TestClaudeAPIIntegration(unittest.TestCase):

    def setUp(self):
        self.claude_manager = ClaudeManager()
        self.llm_evaluator = LLMEvaluator()

    @patch('anthropic.Anthropic')
    def test_claude_api_call(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="I am Claude, an AI assistant created by Anthropic to be helpful, harmless, and honest.")]
        mock_client.messages.create.return_value = mock_response

        response = self.claude_manager.generate_response("Introduce yourself")
        
        self.assertTrue("Claude" in response and "Anthropic" in response)
        self.assertTrue(self.llm_evaluator.evaluate_response(response, "The response should mention Claude and Anthropic"))

    def test_tiered_model_selection(self):
        self.assertEqual(self.claude_manager.select_model("simple task"), "claude-3-haiku-20240307")
        self.assertEqual(self.claude_manager.select_model("moderate complexity task"), "claude-3-sonnet-20240229")
        self.assertEqual(self.claude_manager.select_model("highly complex task"), "claude-3-opus-20240229")

    def test_error_handling(self):
        with patch.object(self.claude_manager, 'client') as mock_client:
            mock_client.messages.create.side_effect = Exception("API Error")

            with self.assertRaises(Exception):
                self.claude_manager.generate_response("Test prompt")

    def test_input_validation(self):
        with self.assertRaises(tenacity.RetryError):
            self.claude_manager.generate_response("")

        long_input = "a" * 100001
        with self.assertRaises(tenacity.RetryError):
            self.claude_manager.generate_response(long_input)

    @patch('anthropic.Anthropic')
    def test_response_parsing(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="<response>Parsed response</response>")]
        mock_client.messages.create.return_value = mock_response

        response = self.claude_manager.generate_response("Test prompt")
        
        self.assertTrue(re.match(r"<response>.*</response>", response))
        self.assertTrue(self.llm_evaluator.evaluate_response(response, "The response should be wrapped in <response> tags"))

    @patch('anthropic.Anthropic')
    def test_retry_mechanism(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = [
            Exception("Temporary error"),
            MagicMock(content=[MagicMock(text="<response>Successful response</response>")])
        ]

        response = self.claude_manager.generate_response("Test prompt")
        
        self.assertTrue("Successful" in response)
        self.assertEqual(mock_client.messages.create.call_count, 2)

    @patch('anthropic.Anthropic')
    def test_consistency(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_responses = [
            MagicMock(content=[MagicMock(text="The capital of France is Paris.")]),
            MagicMock(content=[MagicMock(text="Paris is the capital city of France.")])
        ]
        mock_client.messages.create.side_effect = mock_responses

        response1 = self.claude_manager.generate_response("What is the capital of France?")
        response2 = self.claude_manager.generate_response("Tell me the capital of France.")

        self.assertTrue("Paris" in response1 and "Paris" in response2)
        self.assertTrue(self.llm_evaluator.evaluate_response(response1, "The answer should mention Paris as the capital of France"))
        self.assertTrue(self.llm_evaluator.evaluate_response(response2, "The answer should mention Paris as the capital of France"))

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()
