from unittest.mock import patch, MagicMock
from updater import AppUpdater


class TestUpdates:

    @patch('updater.subprocess.run')
    def test_no_updates(self, mock_run):
        mock_run.return_value = MagicMock(stdout="0\n")
        AppUpdater.check_and_update()
        for call in mock_run.call_args_list:
            assert call[0][0] != ["git", "pull"]

    @patch('updater.subprocess.run')
    @patch('updater.input', return_value='нет')
    def test_update_available_but_user_refused(self, mock_input, mock_run):
        mock_run.return_value = MagicMock(stdout="5\n")
        AppUpdater.check_and_update()
        assert mock_input.called
        for call in mock_run.call_args_list:
            assert call[0][0] != ["git", "pull"]

    @patch('updater.subprocess.run')
    def test_network_error_handling(self, mock_run):
        mock_run.side_effect = Exception("Ошибка сети")
        AppUpdater.check_and_update()