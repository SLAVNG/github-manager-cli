import pytest
from unittest.mock import patch, MagicMock
from ghrm.cli import run_cli, load_config
import os
import yaml

@pytest.fixture
def mock_config():
    return {
        'repositories': {
            'test-repo': {
                'description': 'Test repository'
            },
            'test-repo-2': {
                'description': 'Another test repository'
            }
        },
        'description': 'Default description'
    }

@pytest.fixture
def mock_config_list():
    return {
        'repositories': ['test-repo', 'test-repo-2'],
        'description': 'Default description'
    }

@pytest.fixture
def mock_env_vars():
    with patch.dict(os.environ, {
        'DISCORD_WEBHOOK_URL': 'https://discord.webhook.url',
        'SLACK_WEBHOOK_URL': 'https://slack.webhook.url'
    }):
        yield

def test_load_config(tmp_path):
    """Test loading configuration from YAML file"""
    config_data = {
        'repositories': {
            'test-repo': {'description': 'Test repository'}
        }
    }
    config_file = tmp_path / "test_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    loaded_config = load_config(str(config_file))
    assert loaded_config == config_data

@pytest.mark.parametrize("config_file", ["nonexistent.yaml"])
def test_load_config_file_not_found(config_file):
    """Test loading configuration from non-existent file"""
    with pytest.raises(FileNotFoundError):
        load_config(config_file)

@patch('ghrm.cli.create_repository')
@patch('ghrm.cli.send_slack_notification')
@patch('ghrm.cli.send_discord_notification')
def test_create_repository_dict(mock_discord, mock_slack, mock_create, mock_config, mock_env_vars, capsys):
    """Test repository creation with dictionary config"""
    mock_create.return_value = "created"

    with patch('sys.argv', ['cli.py', 'create', '--config', 'test_config.yaml']):
        with patch('ghrm.cli.load_config', return_value=mock_config):
            run_cli()

    # Verify repository creation was called
    assert mock_create.call_count == 2
    mock_create.assert_any_call(
        'test-repo',
        description='Test repository',
        repo_config={'description': 'Test repository'}
    )

    # Verify notifications were sent
    assert mock_slack.call_count == 2
    assert mock_discord.call_count == 2

    # Check console output
    captured = capsys.readouterr()
    assert "GitHub repository created: test-repo" in captured.out

@patch('ghrm.cli.create_repository')
@patch('ghrm.cli.send_slack_notification')
@patch('ghrm.cli.send_discord_notification')
def test_create_repository_list(mock_discord, mock_slack, mock_create, mock_config_list, mock_env_vars, capsys):
    """Test repository creation with list config"""
    mock_create.return_value = "created"

    with patch('sys.argv', ['cli.py', 'create', '--config', 'test_config.yaml']):
        with patch('ghrm.cli.load_config', return_value=mock_config_list):
            run_cli()

    assert mock_create.call_count == 2
    mock_create.assert_any_call('test-repo', description='Default description')

@patch('ghrm.cli.delete_repository')
@patch('ghrm.cli.send_slack_notification')
@patch('ghrm.cli.send_discord_notification')
def test_delete_repository_dict(mock_discord, mock_slack, mock_delete, mock_config, mock_env_vars, capsys):
    """Test repository deletion with dictionary config"""
    mock_delete.return_value = True

    with patch('sys.argv', ['cli.py', 'delete', '--config', 'test_config.yaml']):
        with patch('ghrm.cli.load_config', return_value=mock_config):
            run_cli()

    assert mock_delete.call_count == 2
    mock_delete.assert_any_call('test-repo')

@patch('ghrm.cli.create_repository')
def test_create_repository_error(mock_create, mock_config, mock_env_vars, capsys):
    """Test error handling during repository creation"""
    mock_create.side_effect = Exception("Test error")

    with patch('sys.argv', ['cli.py', 'create', '--config', 'test_config.yaml']):
        with patch('ghrm.cli.load_config', return_value=mock_config):
            run_cli()

    captured = capsys.readouterr()
    assert "Error: Test error" in captured.out

def test_invalid_action(capsys):
    """Test CLI with invalid action"""
    with pytest.raises(SystemExit):
        with patch('sys.argv', ['cli.py', 'invalid', '--config', 'test_config.yaml']):
            run_cli()

def test_missing_config_argument(capsys):
    """Test CLI without config argument"""
    with pytest.raises(SystemExit):
        with patch('sys.argv', ['cli.py', 'create']):
            run_cli()

@pytest.mark.parametrize("webhook_url", [None, ""])
def test_notifications_disabled(webhook_url, mock_config):
    """Test behavior when webhook URLs are not configured"""
    env_vars = {}
    if webhook_url is not None:
        env_vars['DISCORD_WEBHOOK_URL'] = webhook_url
        env_vars['SLACK_WEBHOOK_URL'] = webhook_url

    with patch.dict(os.environ, env_vars, clear=True):
        with patch('sys.argv', ['cli.py', 'create', '--config', 'test_config.yaml']):
            with patch('ghrm.cli.load_config', return_value=mock_config):
                with patch('ghrm.cli.create_repository', return_value="created"):
                    run_cli()
