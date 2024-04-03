import unittest
from unittest.mock import patch, MagicMock
import main

class TestMarketAnalysis(unittest.TestCase):

    @patch('main.input')
    def test_agent_report_search(self, mock_input):
        mock_input.return_value = "1"
        ragreportagent = MagicMock()
        main.agent_report_search(ragreportagent)
        ragreportagent.reset.assert_called_once()

    @patch('main.input')
    def test_agent_google_search(self, mock_input):
        mock_input.return_value = "2"
        internetagent = MagicMock()
        main.agent_google_search(internetagent, "test query")
        internetagent.reset.assert_called_once()

    @patch('main.input')
    def test_main_valid_input(self, mock_input):
        mock_input.return_value = "1"
        assistant = MagicMock()
        ragreportagent = MagicMock()
        ragreportagent.reset = MagicMock()
        ragreportagent.initiate_chat = MagicMock()
        main.internetagent = MagicMock()
        main.main()
        ragreportagent.reset.assert_called_once()
        ragreportagent.initiate_chat.assert_called_once_with(assistant, message=ragreportagent.message_generator, problem=mock_input.return_value)

    @patch('main.input')
    def test_main_invalid_input(self, mock_input):
        mock_input.return_value = "invalid"
        assistant = MagicMock()
        ragreportagent = MagicMock()
        ragreportagent.reset = MagicMock()
        ragreportagent.initiate_chat = MagicMock()
        main.main()
        ragreportagent.reset.assert_not_called()
        ragreportagent.initiate_chat.assert_not_called()

if __name__ == '__main__':
    unittest.main()