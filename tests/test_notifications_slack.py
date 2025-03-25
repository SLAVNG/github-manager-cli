import pytest
from unittest.mock import Mock, patch
from ghrm.notifications.slack import send_slack_notification


@patch("os.getenv")
@patch("rich.console.Console.print")
def test_send_slack_notification_without_webhook_url(mock_console_print, mock_getenv):
    """Test send_slack_notification when SLACK_WEBHOOK_URL is not configured."""
    mock_getenv.return_value = None

    response = send_slack_notification("Test Title", "Test Details", "info")

    assert response is None
    mock_console_print.assert_called_once_with("[bold red]Error: SLACK_WEBHOOK_URL is not configured.[/bold red]")


@patch("os.getenv")
@patch("requests.post")
@patch("rich.console.Console.print")
def test_send_slack_notification_success(mock_console_print, mock_requests_post, mock_getenv):
    """Test send_slack_notification with a successful response."""
    mock_getenv.return_value = "https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_requests_post.return_value = mock_response

    response = send_slack_notification("Test Title", {"key": "value"}, "success")

    assert response.status_code == 200
    mock_requests_post.assert_called_once_with(
        "https://hooks.slack.com/services/XXXX/YYYY/ZZZZ",
        json={
            "attachments": [
                {
                    "color": "#36a64f",
                    "text": "*Test Title*\n*key*: value"
                }
            ]
        }
    )
    mock_console_print.assert_called_once_with("[bold green]Notification sent successfully.[/bold green]")


@patch("os.getenv")
@patch("requests.post")
@patch("rich.console.Console.print")
def test_send_slack_notification_failure(mock_console_print, mock_requests_post, mock_getenv):
    """Test send_slack_notification with a failed response."""
    mock_getenv.return_value = "https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"
    mock_response = Mock()
    mock_response.status_code = 404
    mock_requests_post.return_value = mock_response

    response = send_slack_notification("Test Title", "Test Details", "error")

    assert response.status_code == 404
    mock_requests_post.assert_called_once_with(
        "https://hooks.slack.com/services/XXXX/YYYY/ZZZZ",
        json={
            "attachments": [
                {
                    "color": "#ff0000",
                    "text": "*Test Title*\nTest Details"
                }
            ]
        }
    )
    mock_console_print.assert_called_once_with("[bold red]Failed to send notification. Status code: 404[/bold red]")


@patch("os.getenv")
@patch("requests.post")
@patch("rich.console.Console.print")
def test_send_slack_notification_with_default_status(mock_console_print, mock_requests_post, mock_getenv):
    """Test send_slack_notification with default status."""
    mock_getenv.return_value = "https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_requests_post.return_value = mock_response

    response = send_slack_notification("Test Title", "Test Details")

    assert response.status_code == 200
    mock_requests_post.assert_called_once_with(
        "https://hooks.slack.com/services/XXXX/YYYY/ZZZZ",
        json={
            "attachments": [
                {
                    "color": "#0000ff",
                    "text": "*Test Title*\nTest Details"
                }
            ]
        }
    )
    mock_console_print.assert_called_once_with("[bold green]Notification sent successfully.[/bold green]")
