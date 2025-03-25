import os
from typing import Optional
import requests
from rich.console import Console

console = Console()

def get_discord_webhook_url() -> Optional[str]:
    """Get Discord webhook URL from environment variable."""
    return os.getenv('DISCORD_WEBHOOK_URL')

def validate_webhook_url() -> bool:
    """Validate if Discord webhook URL is set."""
    webhook_url = get_discord_webhook_url()
    if not webhook_url:
        console.print("[bold red]Warning: DISCORD_WEBHOOK_URL not set. Notifications will be disabled.[/bold red]")
        return False
    return True

def send_discord_notification(title: str, message: str, color: int = 0x7289DA) -> bool:
    if not validate_webhook_url():
        return False

    webhook_url = get_discord_webhook_url()

    embed = {
        "title": title,
        "description": message,
        "color": color
    }

    payload = {
        "embeds": [embed],
        "content": None
    }

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error sending Discord notification: {str(e)}[/bold red]")
        return False


def send_success_notification(title: str, message: str) -> bool:
    """Send a success notification with green color."""
    return send_discord_notification(title, message, color=0x2ECC71)

def send_error_notification(title: str, message: str) -> bool:
    """Send an error notification with red color."""
    return send_discord_notification(title, message, color=0xFF0000)

def send_warning_notification(title: str, message: str) -> bool:
    """Send a warning notification with yellow color."""
    return send_discord_notification(title, message, color=0xFFA500)
