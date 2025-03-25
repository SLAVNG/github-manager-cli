# cli.py - Command Line Interface module for GitHub Manager CLI

import argparse
import os
import yaml
from rich.text import Text
from dotenv import load_dotenv
from github import Github, GithubException, Auth
from .repository import (
    create_repository,
    delete_repository
)

from .display import (
    display_result,
    display_list,
    display_empty
)

from .notifications.slack import send_slack_notification
from .notifications.discord import send_discord_notification
from .__version__ import VERSION

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def run_cli():
    parser = argparse.ArgumentParser(description="GitHub Repository Manager CLI")

    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show program's version number and exit"
    )

    parser.add_argument(
        "action",
        choices=["create", "delete"],
        help="Action to perform",
        nargs="?"
    )

    parser.add_argument(
        "--config",
        help="Path to YAML config file",
        required=False
    )

    args = parser.parse_args()

    if args.version:
        print(f"GitHub Manager CLI Version: {VERSION}")
        return

    if not args.action:
        parser.error("action is required when not using --version")

    if not args.config:
        parser.error("--config is required when performing an action")

    config = load_config(args.config)
    repos = config.get('repositories', {})
    description = config.get('description')

    def send_notification(action, details, status="success"):
        if SLACK_WEBHOOK_URL:
            send_slack_notification(action, details, status)
        if DISCORD_WEBHOOK_URL:
            send_discord_notification(action, details, status)

    try:
        # Handle repository creation based on YAML config
        if args.action == "create":
            if isinstance(repos, dict):
                for repo_name, repo_config in repos.items():
                    result = create_repository(repo_name, description=repo_config.get('description'), repo_config=repo_config)
                    if result == "created":
                        send_notification(
                            "Repository Created",
                            {
                                "Repository": repo_name,
                                "Description": repo_config.get('description')
                            },
                            "success"
                        )
                        display_result(
                            Text.assemble(
                                "GitHub repository created: ",
                                (repo_name, "bold green")
                            ),
                            "success"
                        )
                    elif result == "updated":
                        send_notification(
                            "Repository Updated",
                            {
                                "Repository": repo_name,
                                "Description": repo_config.get('description')
                            },
                            "success"
                        )
                        display_result(
                            Text.assemble(
                                "GitHub repository updated: ",
                                (repo_name, "bold blue")
                            ),
                            "success"
                        )
            elif isinstance(repos, list):
                for repo_name in repos:
                    result = create_repository(repo_name, description=description)
                    if result == "created":
                        send_notification(
                            "Repository Created",
                            {
                                "Repository": repo_name,
                                "Description": description
                            },
                            "success"
                        )
                        display_result(
                            Text.assemble(
                                "GitHub repository created: ",
                                (repo_name, "bold green")
                            ),
                            "success"
                        )
                    elif result == "updated":
                        send_notification(
                            "Repository Updated",
                            {
                                "Repository": repo_name,
                                "Description": description
                            },
                            "success"
                        )
                        display_result(
                            Text.assemble(
                                "GitHub repository updated: ",
                                (repo_name, "bold blue")
                            ),
                            "success"
                        )

        # Handle repository deletion based on YAML config
        elif args.action == "delete":
            if isinstance(repos, dict):
                for repo_name in repos.keys():
                    if delete_repository(repo_name):
                        send_notification(
                            "Repository Deleted",
                            {
                                "Repository": repo_name
                            },
                            "warning"
                        )
                        display_result(
                            Text.assemble(
                                "GitHub repository deleted: ",
                                (repo_name, "bold red")
                            ),
                            "warning"
                        )
            elif isinstance(repos, list):
                for repo_name in repos:
                    if delete_repository(repo_name):
                        send_notification(
                            "Repository Deleted",
                            {
                                "Repository": repo_name
                            },
                            "warning"
                        )
                        display_result(
                            Text.assemble(
                                "GitHub repository deleted: ",
                                (repo_name, "bold red")
                            ),
                            "warning"
                        )

    except Exception as e:
        error_message = str(e)
        send_notification(
            "Error Occurred",
            {
                "Action": args.action,
                "Error": error_message
            },
            "error"
        )
        display_result(
            Text.assemble(
                "Error: ",
                (error_message, "bold red")
            ),
            "error"
        )

if __name__ == "__main__":
    run_cli()
