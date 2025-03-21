import pytest
from unittest.mock import patch, Mock
from datetime import datetime
import logging
from ghrm.notifications.discord import DiscordNotifier, send_discord_notification

@pytest.fixture
def discord_notifier():
    """Fixture for DiscordNotifier with mock webhook URL"""
    with patch.dict('os.environ', {'DISCORD_WEBHOOK_URL': 'https://discord.webhook.test'}):
        return DiscordNotifier()

@pytest.fixture
def mock_requests():
    """Fixture to mock requests.post"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.raise_for_status = Mock()
        yield mock_post

def test_discord_notifier_initialization():
    """Test DiscordNotifier initialization with and without webhook URL"""
    # Test with webhook URL
    with patch.dict('os.environ', {'DISCORD_WEBHOOK_URL': 'https://discord.webhook.test'}):
        notifier = DiscordNotifier()
        assert notifier.webhook_url == 'https://discord.webhook.test'

    # Test without webhook URL
    with patch.dict('os.environ', {}, clear=True):
        notifier = DiscordNotifier()
        assert notifier.webhook_url is None

def test_send_discord_notification_success(discord_notifier, mock_requests):
    """Test successful Discord notification sending"""
    title = "Test Title"
    description = "Test Description"
    color = 0x00ff00
    fields = [{"name": "Field1", "value": "Value1", "inline": True}]

    discord_notifier.send_discord_notification(title, description, color, fields)

    mock_requests.assert_called_once()
    call_args = mock_requests.call_args

    # Verify the URL
    assert call_args[0][0] == 'https://discord.webhook.test'

    # Verify the payload
    payload = call_args[1]['json']
    embed = payload['embeds'][0]
    assert embed['title'] == title
    assert embed['description'] == description
    assert embed['color'] == color
    assert embed['fields'] == fields
    assert 'timestamp' in embed

def test_send_discord_notification_no_webhook(capsys):
    """Test notification behavior when webhook URL is not set"""
    with patch.dict('os.environ', {}, clear=True):
        notifier = DiscordNotifier()
        notifier.send_discord_notification("Test", "Test Description")

    captured = capsys.readouterr()
    assert "Warning: DISCORD_WEBHOOK_URL not set" in captured.out

def test_send_discord_notification_request_error(discord_notifier, mock_requests, caplog):
    """Test handling of request errors"""
    mock_requests.side_effect = Exception("Network Error")

    with caplog.at_level(logging.ERROR):
        try:
            discord_notifier.send_discord_notification("Test", "Test Description")
        except Exception as e:
            assert str(e) == "Network Error"
            assert "Failed to send Discord notification" in caplog.text

@pytest.mark.parametrize("status,color", [
    ("success", 0x00ff00),
    ("warning", 0xffff00),
    ("error", 0xff0000),
    ("info", 0x0000ff),
    ("invalid_status", 0x00ff00),  # Should default to success color
])
def test_send_discord_notification_helper(mock_requests, status, color):
    """Test the helper function with different statuses"""
    with patch.dict('os.environ', {'DISCORD_WEBHOOK_URL': 'https://discord.webhook.test'}):
        action = "Test Action"
        details = {"key": "value"}

        send_discord_notification(action, details, status)

        mock_requests.assert_called_once()
        payload = mock_requests.call_args[1]['json']
        embed = payload['embeds'][0]

        assert embed['title'] == f"GitHub Manager: {action}"
        assert embed['color'] == color
        assert len(embed['fields']) == 1
        assert embed['fields'][0]['name'] == "key"
        assert embed['fields'][0]['value'] == "value"

def test_send_discord_notification_with_string_details(mock_requests):
    """Test sending notification with string details instead of dict"""
    with patch.dict('os.environ', {'DISCORD_WEBHOOK_URL': 'https://discord.webhook.test'}):
        action = "Test Action"
        details = "Test Details"

        send_discord_notification(action, details)

        mock_requests.assert_called_once()
        payload = mock_requests.call_args[1]['json']
        embed = payload['embeds'][0]

        assert embed['title'] == f"GitHub Manager: {action}"
        assert embed['description'] == "Test Details"
        assert 'fields' in embed
        assert not embed['fields']  # Should be empty list

@pytest.mark.parametrize("fields", [
    None,
    [],
    [{"name": "Field1", "value": "Value1", "inline": True}],
    [
        {"name": "Field1", "value": "Value1", "inline": True},
        {"name": "Field2", "value": "Value2", "inline": False}
    ]
])
def test_send_discord_notification_fields(discord_notifier, mock_requests, fields):
    """Test notification sending with different field configurations"""
    discord_notifier.send_discord_notification("Test", "Test Description", fields=fields)

    payload = mock_requests.call_args[1]['json']
    embed = payload['embeds'][0]

    if fields is None:
        assert embed['fields'] == []
    else:
        assert embed['fields'] == fields
