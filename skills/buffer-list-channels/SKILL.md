---
name: buffer-list-channels
description: List the social channels (Twitter/X, LinkedIn, Bluesky, Instagram, Threads, etc.) connected to the authenticated Buffer account. Use to discover channel IDs before posting, find the ID for a specific service, or audit which accounts are connected.
---

# List connected Buffer channels

Use the `buffer` CLI to enumerate the social channels connected to the authenticated Buffer account.

## When to use this skill

- The user wants to see which social accounts are connected to Buffer.
- A workflow needs a channel ID for a specific service before scheduling a post (when post commands are added in a future stage).
- Audit which services are connected (Twitter/X, LinkedIn, Bluesky, Instagram, Threads, etc.).

## Prerequisite

```bash
export BUFFER_ACCESS_TOKEN=...
```

## Command

```bash
uv run buffer channels list
```

Output is JSON on stdout:

```json
{
  "account": {
    "channels": [
      { "id": "...", "name": "alchemicduncan", "service": "twitter" },
      { "id": "...", "name": "Duncan Campbell", "service": "bluesky" }
    ]
  }
}
```

## Working with the output

Get the ID for a specific service:

```bash
uv run buffer channels list \
  | jq -r '.account.channels[] | select(.service == "twitter") | .id'
```

Group by service:

```bash
uv run buffer channels list \
  | jq '.account.channels | group_by(.service) | map({service: .[0].service, count: length})'
```

Just the names and services, as a table:

```bash
uv run buffer channels list \
  | jq -r '.account.channels[] | "\(.service)\t\(.name)\t\(.id)"' \
  | column -t -s $'\t'
```

## Notes

- The list reflects what is connected in Buffer right now — disconnections in the Buffer web UI take effect immediately.
- The `service` field uses Buffer's lowercase identifiers: `twitter`, `linkedin`, `bluesky`, `instagram`, `threads`, etc.
- The CLI also accepts `--token <value>`, but prefer the env var so secrets stay out of process listings and shell history.
- If `uv run buffer` is not on PATH, install via `uv sync` in the buffer-cli repo.
