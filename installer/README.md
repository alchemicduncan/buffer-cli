# buffer-cli-skills

Installer that copies the [buffer-cli](https://github.com/alchemicduncan/buffer-cli) agent skills into your project so Claude Code (and other compatible agents) can discover them.

## Usage

In your project root:

```bash
npx buffer-cli-skills install
```

This copies the bundled `SKILL.md` files into `.claude/skills/`:

- `buffer-get-user` — fetch the authenticated Buffer account (id, email, name)
- `buffer-list-channels` — list connected social channels and their IDs

### Options

```bash
npx buffer-cli-skills install --target .cursor/skills   # custom target dir
npx buffer-cli-skills install --force                   # overwrite existing
npx buffer-cli-skills list                              # list bundled skills
```

## Prerequisite

The skills shell out to the `buffer` Python CLI. Install it from the parent repo:

```bash
git clone https://github.com/alchemicduncan/buffer-cli && cd buffer-cli && uv sync
```

Set `BUFFER_ACCESS_TOKEN` in your environment before running any commands.
