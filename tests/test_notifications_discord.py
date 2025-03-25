import pytest
from unittest.mock import patch, Mock
from ghrm.notifications.discord import (
    send_discord_notification,
    send_success_notification,
    send_error_notification,
    send_warning_notification,
    get_discord_webhook_url,
    validate_webhook_url
)

@patch("os.getenv")
def test_get_discord_webhook_url(mock_getenv):
    """Test retrieving the Discord webhook URL from the environment."""
    mock_getenv.return_value = "https://discord.com/api/webhooks/test-webhook"
    webhook_url = get_discord_webhook_url()
    assert webhook_url == "https://discord.com/api/webhooks/test-webhook"

@patch("os.getenv")
def test_validate_webhook_url_valid(mock_getenv):
    """Test validate_webhook_url when the webhook URL is set."""
    mock_getenv.return_value = "https://discord.com/api/webhooks/test-webhook"
    assert validate_webhook_url() is True


@patch("os.getenv")
def test_validate_webhook_url_invalid(mock_getenv):
    """Test validate_webhook_url when the webhook URL is not set."""
    mock_getenv.return_value = None
    assert validate_webhook_url() is False

@patch("requests.post")
@patch("os.getenv")
def test_send_discord_notification_success(mock_getenv, mock_post):
    """Test sending a Discord notification successfully."""
    mock_getenv.return_value = "https://discord.com/api/webhooks/test-webhook"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    result = send_discord_notification("Test Title", "Test Message", color=0x2ECC71)
    assert result is True
    mock_post.assert_called_once_with(
        "https://discord.com/api/webhooks/test-webhook",
        json={
            "embeds": [
                {
                    "title": "Test Title",
                    "description": "Test Message",
                    "color": 0x2ECC71
                }
            ],
            "content": None
        },
        headers={"Content-Type": "application/json"}
    )

@patch("requests.post")
@patch("os.getenv")
def test_send_discord_notification_failure(mock_getenv, mock_post):
    """Test sending a Discord notification with a failure."""
    mock_getenv.return_value = "https://discord.com/api/webhooks/test-webhook"
    mock_response = Mock()
    mock_response.status_code = 400
    mock_post.return_value = mock_response

    result = send_discord_notification("Test Title", "Test Message", color=0xFF0000)
    assert result is False
    mock_post.assert_called_once_with(
        "https://discord.com/api/webhooks/test-webhook",
        json={
            "embeds": [
                {
                    "title": "Test Title",
                    "description": "Test Message",
                    "color": 0xFF0000
                }
            ],
            "content": None
        },
        headers={"Content-Type": "application/json"}
    )

@patch("ghrm.notifications.discord.send_discord_notification")
def test_send_success_notification(mock_send_discord_notification):
    """Test sending a success notification."""
    mock_send_discord_notification.return_value = True
    result = send_success_notification("Success Title", "Success Message")
    assert result is True
    mock_send_discord_notification.assert_called_once_with(
        "Success Title", "Success Message", color=0x2ECC71
    )

@patch("ghrm.notifications.discord.send_discord_notification")
def test_send_error_notification(mock_send_discord_notification):
    """Test sending an error notification."""
    mock_send_discord_notification.return_value = True
    result = send_error_notification("Error Title", "Error Message")
    assert result is True
    mock_send_discord_notification.assert_called_once_with(
        "Error Title", "Error Message", color=0xFF0000
    )

@patch("ghrm.notifications.discord.send_discord_notification")
def test_send_warning_notification(mock_send_discord_notification):
    """Test sending a warning notification."""
    mock_send_discord_notification.return_value = True
    result = send_warning_notification("Warning Title", "Warning Message")
    assert result is True
    mock_send_discord_notification.assert_called_once_with(
        "Warning Title", "Warning Message", color=0xFFA500
    )
