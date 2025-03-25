import pytest
from unittest.mock import Mock, patch, mock_open
from ghrm.repository import (
    initialize_github,
    get_repo,
    load_repo_configs,
    configure_repository,
    create_repository,
    delete_repository,
    decommission_repository,
)

@patch("os.getenv")
@patch("github.Github")
def test_initialize_github(mock_github, mock_getenv):
    """Test GitHub initialization."""
    mock_getenv.side_effect = lambda key: "test_token" if key == "GITHUB_TOKEN" else "test_org"
    mock_github_instance = Mock()
    mock_github.return_value = mock_github_instance
    mock_github_instance.get_user.return_value.login = "test_user"
    mock_github_instance.get_organization.return_value.login = "test_org"

    g, org = initialize_github()

    assert g == mock_github_instance
    assert org.login == "test_org"
    mock_github_instance.get_user.assert_called_once()
    mock_github_instance.get_organization.assert_called_once_with("test_org")

@patch("ghrm.repository.org")
def test_get_repo_success(mock_org):
    """Test fetching an existing repository."""
    mock_repo = Mock()
    mock_repo.name = "test_repo"
    mock_org.get_repo.return_value = mock_repo

    repo = get_repo("test_repo")

    assert repo == mock_repo
    mock_org.get_repo.assert_called_once_with("test_repo")

@patch("ghrm.repository.org")
def test_get_repo_not_found(mock_org):
    """Test fetching a non-existent repository."""
    mock_org.get_repo.side_effect = Mock(status=404)

    repo = get_repo("non_existent_repo")

    assert repo is None
    mock_org.get_repo.assert_called_once_with("non_existent_repo")

@patch("builtins.open", new_callable=mock_open, read_data="repositories:\n  test_repo: {}")
def test_load_repo_configs(mock_open_file):
    """Test loading repository configurations from a YAML file."""
    configs = load_repo_configs("test_config.yaml")

    assert configs == {"test_repo": {}}
    mock_open_file.assert_called_once_with("test_config.yaml", "r")

@patch("builtins.open", new_callable=mock_open, read_data="repositories:\n  - test_repo")
@patch("ghrm.repository.delete_repository")
def test_decommission_repository(mock_delete_repository, mock_open_file):
    """Test decommissioning repositories."""
    decommission_repository("test_decom_list.yaml")

    mock_delete_repository.assert_called_once_with("test_repo")
    mock_open_file.assert_called_once_with("test_decom_list.yaml", "r")

@patch("ghrm.repository.get_repo")
@patch("ghrm.repository.org")
def test_create_repository(mock_org, mock_get_repo):
    """Test creating a new repository."""
    mock_get_repo.return_value = None
    mock_org.create_repo.return_value = Mock(name="test_repo")

    result = create_repository("test_repo", description="Test description")

    assert result == "created"
    mock_org.create_repo.assert_called_once_with(
        name="test_repo", description="Test description", private=True
    )

@patch("ghrm.repository.get_repo")
@patch("ghrm.repository.org")
def test_create_repository_already_exists(mock_org, mock_get_repo):
    """Test creating a repository that already exists."""
    mock_repo = Mock()
    mock_get_repo.return_value = mock_repo

    result = create_repository("test_repo", description="Test description")

    assert result == "updated"
    mock_repo.edit.assert_called_once_with(
        name="test_repo", description="Test description", private=True
    )

@patch("ghrm.repository.get_repo")
def test_delete_repository_success(mock_get_repo):
    """Test deleting an existing repository."""
    mock_repo = Mock()
    mock_get_repo.return_value = mock_repo

    result = delete_repository("test_repo")

    assert result is True
    mock_repo.delete.assert_called_once()

@patch("ghrm.repository.get_repo")
def test_delete_repository_not_found(mock_get_repo):
    """Test deleting a non-existent repository."""
    mock_get_repo.return_value = None

    result = delete_repository("non_existent_repo")

    assert result is False
