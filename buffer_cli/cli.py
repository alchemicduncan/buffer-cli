import click
import json
from .config import set_access_token, get_access_token
from .api import BufferClient

@click.group()
def main():
    """Buffer CLI - Manage your Buffer account from the command line."""
    pass

@main.command()
@click.option("--token", prompt="Your Buffer Access Token", help="Your Personal Access Token from Buffer.")
def login(token):
    """Authenticate with Buffer using a Personal Access Token."""
    set_access_token(token)
    click.echo("Access token saved successfully!")

@main.command()
def user():
    """Show information about the authenticated user."""
    token = get_access_token()
    if not token:
        click.echo("Error: Not authenticated. Run 'buffer login' first.", err=True)
        return

    client = BufferClient(token)
    try:
        user_info = client.get_user()
        click.echo(json.dumps(user_info, indent=2))
    except Exception as e:
        click.echo(f"Error fetching user info: {e}", err=True)

@main.command()
def profiles():
    """List all connected social profiles."""
    token = get_access_token()
    if not token:
        click.echo("Error: Not authenticated. Run 'buffer login' first.", err=True)
        return

    client = BufferClient(token)
    try:
        profiles = client.get_profiles()
        for profile in profiles:
            click.echo(f"{profile.get('service').capitalize()} - {profile.get('formatted_username')} (ID: {profile.get('id')})")
    except Exception as e:
        click.echo(f"Error fetching profiles: {e}", err=True)

if __name__ == "__main__":
    main()
