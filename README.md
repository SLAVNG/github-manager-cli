# GitHub Manager CLI (ghrm)

[![PyPI](https://img.shields.io/pypi/v/github-manager-cli.svg)](https://pypi.python.org/pypi/github-manager-cli)
![CI](https://github.com/SLAVNG/github-manager-cli/workflows/CI/badge.svg)
[![readthedocs](https://img.shields.io/badge/docs-stable-brightgreen.svg?style=flat)](https://pygithub.readthedocs.io/en/stable/?badge=stable)
[![License](https://img.shields.io/badge/license-LGPL-blue.svg)](https://en.wikipedia.org/wiki/GNU_Lesser_General_Public_License)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview
GitHub Manager CLI is a Python application designed to help users manage their GitHub repositories via YAML file definition.

## Features
- Create or delete repositories
- Update repositories based on updated YAML config
- Notifications via Slack and Discord

## Installation
To install the required dependencies, run the following command:

```sh
pip install -r requirements/main.txt
```

To install the `ghrm` CLI tool, run the following command:

```sh
pip install uv
uv build
uv pip install -e .
```

## Configuration
Create a `.env` file in the root directory of the project and add the following environment variables:

```env
GITHUB_TOKEN=your_github_token
GITHUB_ORG=your_github_org
DISCORD_WEBHOOK_URL=your_discord_webhook
SLACK_WEBHOOK_URL=your_slack_webhook
```

## Development
To run tool with environmental variable defined in `src/.env` file

```sh
cd src
dotenv run -- python -m ghrm --help
```

## Usage
To use the GitHub Repository Manager, you can run the `grm` command.

```sh
ghrm create --config repositories.yaml
ghrm delete --config delete_repositories.yaml
```

## Vision
For more details on the vision and goals of this project, please refer to the [VISION.md](VISION.md) file.

## Contributions

Long-term discussion and bug reports are maintained via GitHub Issues.
Code review is done via GitHub Pull Requests.

For more information read [CONTRIBUTING.md].

[CONTRIBUTING.md]: https://github.com/SLAVNG/github-manager-cli/blob/main/CONTRIBUTING.md

## Code of Conduct

We are committed to fostering a welcoming and inclusive environment. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) to understand our expectations for respectful participation.

By contributing to this project, you agree to abide by its terms.

## Sponsors

Please [contact me](https://github.com/sosadtsia) if you want to become a sponsor.
