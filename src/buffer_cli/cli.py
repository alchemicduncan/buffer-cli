from __future__ import annotations

import json
import sys

import click

from .client import ACCESS_TOKEN_ENV, BufferClient, BufferError


def _emit(payload):
    click.echo(json.dumps(payload, indent=2, sort_keys=False))


def _run(ctx, fn):
    try:
        result = fn(ctx.obj["client"])
    except BufferError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    _emit(result)


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
    ctx.call_on_close(ctx.obj["client"].close)


@main.command()
@click.pass_context
def user(ctx):
    """Show information about the authenticated user."""
    _run(ctx, lambda c: c.get_user())


@main.group()
def channels():
    """Manage connected social channels."""


@channels.command("list")
@click.pass_context
def channels_list(ctx):
    """List all connected social channels."""
    _run(ctx, lambda c: c.get_channels())


if __name__ == "__main__":
    main()
