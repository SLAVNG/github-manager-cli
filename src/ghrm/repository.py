# repository.py - Repository module for GitHub Manager CLI

import os
import sys
import yaml
from github import Github, GithubException, Auth

_github_instance = None
_org_instance = None

def initialize_github():
    """
    Initialize GitHub connection.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    github_org = os.getenv("GITHUB_ORG")

    if not github_token:
        raise EnvironmentError("GITHUB_TOKEN environment variable is not set")
    if not github_org:
        raise EnvironmentError("GITHUB_ORG environment variable is not set")

    auth = Auth.Token(github_token)
    g = Github(auth=auth)

    try:
        # Test the authentication
        g.get_user().login
    except GithubException as e:
        if e.status == 401:
            raise EnvironmentError(
                "Invalid GitHub token. Please check your GITHUB_TOKEN environment variable."
            ) from e
        raise

    try:
        org = g.get_organization(github_org)
        # Test organization access
        org.login
        return g, org
    except GithubException as e:
        if e.status == 404:
            raise EnvironmentError(
                f"Organization '{github_org}' not found. Please check your GITHUB_ORG environment variable."
            ) from e
        if e.status == 403:
            raise EnvironmentError(
                f"No access to organization '{github_org}'. Please check your permissions."
            ) from e
        raise


def get_github_and_org():
    """
    Lazily initialize and return the GitHub and organization instances.
    """
    global _github_instance, _org_instance
    if _github_instance is None or _org_instance is None:
        _github_instance, _org_instance = initialize_github()
    return _github_instance, _org_instance


def get_repo(repo_name):
    """
    Fetches a repo from GitHub organization.
    """
    if not repo_name:
        raise ValueError("Repository name cannot be empty")

    g, org = get_github_and_org()
    try:
        repo = org.get_repo(repo_name)
        if repo.name:
            print(f"Repository `{repo_name}` exists within GitHub {org.login}")
            return repo
    except GithubException as e:
        if e.status == 404:
            print(f"Repository `{repo_name}` does not exist within GitHub {org.login}")
            return None
        elif e.status == 401:
            print("Authentication failed. Please check your GitHub token.", file=sys.stderr)
            sys.exit(1)
        elif e.status == 403:
            print("Access denied. Please check your permissions.", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"Error fetching repository from GitHub {org.login} - {str(e)}", file=sys.stderr)
            raise


def load_repo_configs(config_file):
    """
    Loads repository configurations from a YAML file.
    """
    if not config_file:
        raise ValueError("Configuration file path cannot be empty")

    try:
        with open(config_file, 'r') as f:
            try:
                repos = yaml.safe_load(f)
                if not repos:
                    print("Warning: Empty configuration file", file=sys.stderr)
                    return {}
                return repos.get("repositories", {})
            except yaml.YAMLError as e:
                print(f"Invalid YAML format: {str(e)}", file=sys.stderr)
                sys.exit(1)
    except FileNotFoundError:
        print(f"Configuration file not found: {config_file}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Permission denied accessing file: {config_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error reading configuration: {str(e)}", file=sys.stderr)
        sys.exit(1)


def create_repository(repo_name, description=None, repo_config=None):
    """
    Creates a single GitHub repository.
    """
    if not repo_name:
        raise ValueError("Repository name cannot be empty")

    g, org = get_github_and_org()
    try:
        repo = get_repo(repo_name)
        default_config = {
            "name": repo_name,
            "description": description,
            "private": True
        }

        if repo_config is None:
            repo_config = default_config
        else:
            repo_config = {**default_config, **repo_config}

        if repo is None:
            try:
                print(f"Creating GitHub repository `{repo_name}`")
                org.create_repo(**repo_config)
                return "created"
            except GithubException as e:
                if e.status == 422:
                    print(f"Repository `{repo_name}` already exists.")
                else:
                    print(f"Error creating repository `{repo_name}`: {str(e)}", file=sys.stderr)
                    raise
        else:
            print(f"Repository `{repo_name}` already exists. Updating repository.")
            # Remove unsupported arguments for the edit method
            unsupported_args = ["auto_init", "gitignore_template", "license_template"]
            for arg in unsupported_args:
                repo_config.pop(arg, None)
            try:
                repo.edit(**repo_config)
                return "updated"
            except GithubException as e:
                print(f"Error updating repository `{repo_name}`: {str(e)}", file=sys.stderr)
                raise

    except Exception as e:
        print(f"Error in repository creation/update: {str(e)}", file=sys.stderr)
        raise


def delete_repository(repo_name):
    """
    Deletes GitHub repository.
    """
    if not repo_name:
        raise ValueError("Repository name cannot be empty")

    try:
        repo = get_repo(repo_name)
        if repo:
            try:
                print(f"Deleting GitHub repository `{repo_name}`")
                repo.delete()
                return True
            except GithubException as e:
                if e.status == 403:
                    print(f"Permission denied to delete repository `{repo_name}`", file=sys.stderr)
                else:
                    print(f"Error deleting repository `{repo_name}`: {str(e)}", file=sys.stderr)
                raise
        else:
            print(f"Repository `{repo_name}` does not exist. Skipping deletion.")
            return False

    except Exception as e:
        print(f"Error in repository deletion: {str(e)}", file=sys.stderr)
        raise
