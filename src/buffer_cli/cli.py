import click

from .client import ACCESS_TOKEN_ENV, BufferClient


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--token",
    envvar=ACCESS_TOKEN_ENV,
    help=f"Buffer access token (or set ${ACCESS_TOKEN_ENV}).",
)
@click.pass_context
def main(ctx, token):
    """Buffer CLI - Manage your Buffer account from the command line."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = BufferClient(token)


@main.command()
@click.pass_context
def user(ctx):
    """Show information about the authenticated user."""
    client = ctx.obj["client"]
    try:
        data = client.get_user()
        u = data.get("user", {})
        click.echo(f"Name: {u.get('name')}")
        click.echo(f"Email: {u.get('email')}")
        click.echo(f"ID: {u.get('id')}")
    except Exception as e:
        click.echo(f"Error fetching user info: {e}", err=True)


@main.command()
@click.pass_context
def profiles(ctx):
    """List all connected social profiles."""
    client = ctx.obj["client"]
    try:
        data = client.get_profiles()
        channels = data.get("account", {}).get("channels", [])
        if not channels:
            click.echo("No profiles found.")
            return
        for channel in channels:
            click.echo(f"{channel.get('service').capitalize()} - {channel.get('name')} (ID: {channel.get('id')})")
    except Exception as e:
        click.echo(f"Error fetching profiles: {e}", err=True)


if __name__ == "__main__":
    main()
