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


@main.group()
def posts():
    """Manage Buffer posts."""


@posts.command("create")
@click.option("--channel", "channel_id", required=True, help="Channel ID to post to (use `buffer channels list`).")
@click.option("--text", required=True, help="Post text content.")
@click.option("--share-now", "share_now", is_flag=True, default=False, help="Publish immediately.")
@click.option("--add-to-queue", "add_to_queue", is_flag=True, default=False, help="Add to the channel queue.")
@click.option("--at", "scheduled_at", default=None, help="Schedule for a specific ISO datetime (e.g. 2026-06-01T14:00:00Z).")
@click.option("--notification", "use_notification", is_flag=True, default=False, help="Use notification publishing (you post manually) instead of automatic.")
@click.option("--tag", "tags", multiple=True, help="Tag ID (repeatable).")
@click.pass_context
def posts_create(ctx, channel_id, text, share_now, add_to_queue, scheduled_at, use_notification, tags):
    """Create a post on a channel. Defaults to saving as a draft (safe)."""
    chosen = sum([bool(share_now), bool(add_to_queue), bool(scheduled_at)])
    if chosen > 1:
        raise click.UsageError("Pass at most one of --share-now, --add-to-queue, --at")

    if share_now:
        mode, save_to_draft, due_at = "shareNow", False, None
    elif add_to_queue:
        mode, save_to_draft, due_at = "addToQueue", False, None
    elif scheduled_at:
        mode, save_to_draft, due_at = "customScheduled", False, scheduled_at
    else:
        mode, save_to_draft, due_at = "addToQueue", True, None

    scheduling_type = "notification" if use_notification else "automatic"

    _run(ctx, lambda c: c.create_post(
        channel_id=channel_id,
        text=text,
        mode=mode,
        scheduling_type=scheduling_type,
        save_to_draft=save_to_draft,
        due_at=due_at,
        tag_ids=list(tags) if tags else None,
    ))


if __name__ == "__main__":
    main()
