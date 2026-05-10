---
name: buffer-create-post
description: Create a post on a Buffer-connected social channel — as a draft (default), shared immediately, added to the channel queue, or scheduled for a specific time. Use when the user has written text content and wants Buffer to handle it. Defaults to draft for safety; explicit flags are required to actually publish.
---

# Create a Buffer post

Use the `buffer` CLI to create a post on a single channel. Defaults to saving as a draft — only publishes when an explicit mode flag is passed.

## When to use this skill

- The user wants to draft, queue, schedule, or immediately publish a social-media post via Buffer.
- A workflow generated text content and needs to push it to Buffer.
- The user wants to schedule a post for a specific time without using the Buffer web UI.

## Prerequisites

```bash
export BUFFER_ACCESS_TOKEN=...
```

You need the destination channel's ID. If you do not have it, run the `buffer-list-channels` skill first:

```bash
uv run buffer channels list \
  | jq -r '.account.channels[] | select(.service == "bluesky") | .id'
```

## Default behavior — DRAFT (safe)

Without any mode flag, the post is saved as a draft in Buffer. Nothing is published.

```bash
uv run buffer posts create --channel <CHANNEL_ID> --text "hello world"
```

This is the safe default and is what to use when in doubt.

## Explicit modes (mutually exclusive)

Pick at most one of these flags to control how the post is handled:

| Flag                | What it does                                                             |
| ------------------- | ------------------------------------------------------------------------ |
| (none)              | Save as draft (Buffer stores it; nothing is published)                   |
| `--share-now`       | Publish immediately to the channel                                       |
| `--add-to-queue`    | Add to the channel queue (Buffer publishes per its existing schedule)    |
| `--at <ISO>`        | Schedule for a specific datetime (e.g. `2026-06-01T14:00:00Z`)           |

Examples:

```bash
# Publish right now (live; do not run unless the user explicitly confirmed)
uv run buffer posts create --channel <CHANNEL_ID> --text "..." --share-now

# Add to the channel's posting queue
uv run buffer posts create --channel <CHANNEL_ID> --text "..." --add-to-queue

# Schedule for a specific time (UTC ISO 8601)
uv run buffer posts create --channel <CHANNEL_ID> --text "..." --at 2026-06-01T14:00:00Z
```

## Other flags

- `--notification` — use Buffer's notification publishing (Buffer reminds the user to post manually) instead of automatic publishing. Required for some channels (e.g. personal Instagram) where automatic publishing is not allowed.
- `--tag <ID>` — attach a Buffer tag (repeatable).

## Output

On success, the CLI prints the created post as JSON:

```json
{
  "id": "...",
  "status": "draft",
  "text": "hello world",
  "createdAt": "...",
  "dueAt": null,
  "channelId": "...",
  "channelService": "bluesky",
  "shareMode": "addToQueue"
}
```

Useful jq filters:

```bash
# Just the new post ID
uv run buffer posts create --channel <ID> --text "..." | jq -r '.id'

# Status check
uv run buffer posts create --channel <ID> --text "..." | jq -r '.status'
```

## Errors

The CLI exits non-zero with the error type and message when the mutation returns a typed error union member. Common cases:

- `UnauthorizedError` — token is missing or invalid; ask the user to refresh `BUFFER_ACCESS_TOKEN`.
- `InvalidInputError` — usually means empty text, bad ISO datetime in `--at`, or an invalid channel ID.
- `LimitReachedError` — the channel's queue is full or a posting cap was hit.
- `RestProxyError` — the underlying social network rejected the post; surface the message verbatim.

## Safety notes

- **Default to draft.** Treat `--share-now` like a destructive action — confirm with the user before passing it.
- The CLI does not have a delete command; retract drafts in the Buffer web UI if needed.
- If `uv run buffer` is not on PATH, install via `uv sync` in the buffer-cli repo.
