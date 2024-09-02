import unittest
from unittest.mock import patch, MagicMock
from src.claude_manager import ClaudeManager
import tenacity

class TestClaudeAPIIntegration(unittest.TestCase):

    def setUp(self):
        self.claude_manager = ClaudeManager()

    @patch('anthropic.Anthropic')
    def test_claude_api_call(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="<response>I do not actually respond to test prompts. I am Claude, an AI assistant created by Anthropic to be helpful, harmless, and honest.</response>")]
        mock_client.messages.create.return_value = mock_response

        response = self.claude_manager.generate_response("Test prompt")
        
        self.assertEqual(response, "I do not actually respond to test prompts. I am Claude, an AI assistant created by Anthropic to be helpful, harmless, and honest.")
        mock_client.messages.create.assert_called_once_with(
            model=self.claude_manager.select_model("Test prompt"),
            max_tokens=1000,
            messages=[
                {"role": "user", "content": "Test prompt"}
            ]
        )

    def test_tiered_model_selection(self):
        # Test fast tier
        self.assertEqual(self.claude_manager.select_model("simple task"), "claude-3-haiku-20240307")
        
        # Test balanced tier
        self.assertEqual(self.claude_manager.select_model("moderate complexity task"), "claude-3-sonnet-20240229")
        
        # Test powerful tier
        self.assertEqual(self.claude_manager.select_model("highly complex task"), "claude-3-opus-20240229")

    def test_error_handling(self):
        with patch.object(self.claude_manager, 'client') as mock_client:
            mock_client.messages.create.side_effect = Exception("API Error")

            with self.assertRaises(Exception):
                self.claude_manager.generate_response("Test prompt")

    def test_input_validation(self):
        # Test empty input
        with self.assertRaises(tenacity.RetryError):
            self.claude_manager.generate_response("")

        # Test very long input
        long_input = "a" * 100001  # Assuming 100,000 is the max allowed length
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
        
        self.assertEqual(response, "Parsed response")

    @patch('anthropic.Anthropic')
    def test_retry_mechanism(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = [
            Exception("Temporary error"),
            MagicMock(content=[MagicMock(text="<response>Successful response</response>")])
        ]

        response = self.claude_manager.generate_response("Test prompt")
        
        self.assertEqual(response, "Successful response")
        self.assertEqual(mock_client.messages.create.call_count, 2)

if __name__ == '__main__':
    unittest.main()
