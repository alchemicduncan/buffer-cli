---
name: buffer-list-posts
description: List Buffer posts — defaults to sent (published) posts across all channels. Filter by status (sent, draft, scheduled, sending, needs_approval, error), by channel, or limit the count. Use to audit what has been published, find a post ID for follow-up edits, or check what is currently in flight.
---

# List Buffer posts

Use the `buffer` CLI to enumerate posts on the authenticated account, with status and channel filters.

## When to use this skill

- The user wants to see what has been published recently (default behavior — sent posts).
- The user wants to inspect drafts, scheduled posts, or posts that errored.
- A workflow needs a post ID before calling a future `posts edit` or `posts delete`.
- Audit posts on a specific channel.

## Prerequisite

```bash
export BUFFER_ACCESS_TOKEN=...
```

## Default — recently sent posts

```bash
uv run buffer posts list
```

Returns up to 30 sent posts across all channels. Output:

```json
{
  "posts": [
    {
      "id": "...",
      "status": "sent",
      "text": "...",
      "createdAt": "...",
      "dueAt": null,
      "sentAt": "...",
      "channelId": "...",
      "channelService": "bluesky",
      "shareMode": "shareNow",
      "externalLink": "https://bsky.app/..."
    }
  ],
  "pageInfo": { "hasNextPage": false, "endCursor": "..." }
}
```

## Filtering

Status (repeatable; default is `sent`):

```bash
uv run buffer posts list --status draft
uv run buffer posts list --status scheduled --status needs_approval
```

Drop the status filter entirely (return all statuses):

```bash
uv run buffer posts list --status all
```

Status values: `draft`, `needs_approval`, `scheduled`, `sending`, `sent`, `error`.

Channel (repeatable — IDs from `buffer-list-channels`):

```bash
uv run buffer posts list --channel <CHANNEL_ID>
uv run buffer posts list --channel <CHANNEL_ID> --channel <ANOTHER_ID>
```

Limit the result count (default 30):

```bash
uv run buffer posts list --limit 5
```

## Multi-organization accounts

The CLI auto-resolves the organization ID from `account.organizations[0]`. If the account belongs to more than one organization, pass `--org <id>` explicitly:

```bash
uv run buffer posts list --org <ORG_ID>
```

Find org IDs by querying the account directly (not yet exposed as a top-level command).

## jq examples

Just the URLs of recently sent posts:

```bash
uv run buffer posts list | jq -r '.posts[].externalLink // empty'
```

Count by service:

```bash
uv run buffer posts list --limit 100 \
  | jq '.posts | group_by(.channelService) | map({service: .[0].channelService, count: length})'
```

Most recent post text and link as a table:

```bash
uv run buffer posts list --limit 10 \
  | jq -r '.posts[] | "\(.sentAt // .createdAt)\t\(.channelService)\t\(.text)"' \
  | column -t -s $'\t'
```

Errored posts only (good for triage):

```bash
uv run buffer posts list --status error
```

## Notes

- Pagination is one page at a time — bump `--limit` (server-side caps may apply) for more, or follow `pageInfo.endCursor` manually if a second page is needed.
- `externalLink` is only populated for `sent` posts that the social network returned a URL for.
- The CLI does not expose a free-text search — filter the JSON with `jq` after listing.
