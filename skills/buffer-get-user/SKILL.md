---
name: buffer-get-user
description: Fetch the authenticated Buffer account (id, email, name) using the `buffer` CLI. Use to confirm which account a token belongs to, surface the account name/email before taking action, or sanity-check that BUFFER_ACCESS_TOKEN is valid before running other commands.
---

# Fetch the authenticated Buffer account

Use the `buffer` CLI (provided by the `buffer-cli` Python package) to read the authenticated account.

## When to use this skill

- The user wants to confirm which Buffer account a token is authenticating as.
- A workflow needs the account's email or display name (e.g. to address them in a confirmation prompt before scheduling posts).
- Sanity-check that `BUFFER_ACCESS_TOKEN` is valid before running other Buffer commands.

## Prerequisite

```bash
export BUFFER_ACCESS_TOKEN=...   # from Buffer account settings
```

If the user hasn't set this, ask them to before running — don't try to invent or guess a token.

## Command

```bash
uv run buffer user
```

Output is JSON on stdout, with `account` as the top-level key (matches Buffer's GraphQL schema — there is no `user` type):

```json
{
  "account": {
    "id": "...",
    "email": "...",
    "name": "..."
  }
}
```

## Working with the output

Pipe to `jq`:

```bash
uv run buffer user | jq -r '.account.email'
uv run buffer user | jq -r '.account | "\(.name) <\(.email)>"'
```

## Notes

- The endpoint requires a valid token. A 401 means the token is missing or invalid — surface the error and ask the user to fix it; do not retry blindly.
- The CLI also accepts `--token <value>`, but prefer the env var so secrets stay out of process listings and shell history.
- If `uv run buffer` is not on PATH, the CLI is not installed in this project — fall back to telling the user to clone the buffer-cli repo and run `uv sync`.
