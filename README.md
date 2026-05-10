# buffer-cli

A Python CLI for the [Buffer](https://buffer.com) GraphQL API. Inspired by [devto-cli](https://github.com/alchemicduncan/devto-cli) — same shape, same conventions: env-var auth, JSON output for `jq` piping, agent skills for Claude Code.

## Install

```bash
git clone https://github.com/alchemicduncan/buffer-cli && cd buffer-cli
uv sync
```

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

## Authenticate

Generate a Personal Access Token from your Buffer account settings, then export it:

```bash
export BUFFER_ACCESS_TOKEN=...
```

Or pass per-invocation: `buffer --token <value> ...`. The env var is preferred so secrets stay out of process listings and shell history.

## Commands

### `buffer user`

Show the authenticated Buffer account.

```bash
uv run buffer user
uv run buffer user | jq -r '.account.email'
```

### `buffer channels list`

List connected social channels (Twitter/X, LinkedIn, Bluesky, Instagram, Threads, etc.).

```bash
uv run buffer channels list

# Get the ID of a specific service
uv run buffer channels list \
  | jq -r '.account.channels[] | select(.service == "bluesky") | .id'
```

### `buffer posts list`

List posts. Defaults to `--status sent` across all channels, 30 max.

```bash
uv run buffer posts list
uv run buffer posts list --status draft
uv run buffer posts list --status scheduled --status needs_approval
uv run buffer posts list --status all                    # drop the status filter
uv run buffer posts list --channel <CHANNEL_ID> --limit 5
uv run buffer posts list --org <ORG_ID>                  # multi-org accounts
```

Status values: `draft`, `needs_approval`, `scheduled`, `sending`, `sent`, `error`.

The organization ID is auto-resolved from the account; pass `--org` only if you have more than one organization.

### `buffer posts create`

Create a post on a single channel. **Defaults to saving as a draft** — explicit flags are required to publish.

```bash
# Save as draft (safe default)
uv run buffer posts create --channel <CHANNEL_ID> --text "hello world"

# Publish immediately
uv run buffer posts create --channel <CHANNEL_ID> --text "..." --share-now

# Add to the channel queue (Buffer publishes per its schedule)
uv run buffer posts create --channel <CHANNEL_ID> --text "..." --add-to-queue

# Schedule for a specific UTC datetime
uv run buffer posts create --channel <CHANNEL_ID> --text "..." --at 2026-06-01T14:00:00Z
```

The three mode flags (`--share-now`, `--add-to-queue`, `--at`) are mutually exclusive.

Other flags:

- `--notification` — use Buffer's notification publishing (you post manually via a reminder) instead of automatic publishing. Required for some channels (e.g. personal Instagram).
- `--tag <ID>` — attach a Buffer tag (repeatable).

## Output

Every command prints JSON to stdout. Errors go to stderr with a non-zero exit code.

```bash
uv run buffer posts list --limit 5 \
  | jq -r '.posts[] | "\(.sentAt // .createdAt)\t\(.channelService)\t\(.text)"' \
  | column -t -s $'\t'
```

## Agent skills

The repo ships [Claude Code](https://docs.claude.com/en/docs/claude-code)-compatible skills that teach agents how to use this CLI. Install into a project:

```bash
cd your-project
npx buffer-cli-skills install
```

This drops `SKILL.md` files into `.claude/skills/`:

- `buffer-get-user`
- `buffer-list-channels`
- `buffer-list-posts`
- `buffer-create-post`

Options: `--target <dir>` (e.g. `.cursor/skills`), `--force` to overwrite, `npx buffer-cli-skills list` to see what is bundled.

## Development

```bash
uv run pytest
```

Tests mock the HTTP layer via [respx](https://lundberg.github.io/respx/); no network calls. The CLI is tested end-to-end with `click.testing.CliRunner`.

## License

MIT.
