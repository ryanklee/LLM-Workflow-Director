import unittest
from unittest.mock import patch, MagicMock
from src.claude_manager import ClaudeManager

class TestClaudeAPIIntegration(unittest.TestCase):

    def setUp(self):
        self.claude_manager = ClaudeManager()

    @patch('anthropic.Anthropic')
    def test_claude_api_call(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.completion.return_value = MagicMock(completion="Test response")

        response = self.claude_manager.generate_response("Test prompt")
        
        self.assertEqual(response, "Test response")
        mock_client.completion.assert_called_once_with(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            prompt="\n\nHuman: Test prompt\n\nAssistant:",
        )

    def test_tiered_model_selection(self):
        # Test fast tier
        self.assertEqual(self.claude_manager.select_model("simple task"), "claude-3-haiku-20240307")
        
        # Test balanced tier
        self.assertEqual(self.claude_manager.select_model("moderate complexity task"), "claude-3-sonnet-20240229")
        
        # Test powerful tier
        self.assertEqual(self.claude_manager.select_model("highly complex task"), "claude-3-opus-20240229")

    def test_error_handling(self):
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.side_effect = Exception("API Error")

            with self.assertRaises(Exception):
                self.claude_manager.generate_response("Test prompt")

if __name__ == '__main__':
    unittest.main()
