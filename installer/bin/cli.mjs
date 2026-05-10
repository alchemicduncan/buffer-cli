#!/usr/bin/env node
import { cp, mkdir, readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SKILLS_SRC = resolve(HERE, "..", "skills");

const HELP = `buffer-cli-skills — install Buffer agent skills into a project

Usage:
  npx buffer-cli-skills install [--target <dir>] [--force]
  npx buffer-cli-skills list
  npx buffer-cli-skills --help

Options:
  --target <dir>   Destination directory (default: .claude/skills)
  --force          Overwrite existing skill directories
  -h, --help       Show this help
`;

function parseArgs(argv) {
  const args = { command: argv[0], target: ".claude/skills", force: false, help: false };
  for (let i = 1; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--target") args.target = argv[++i];
    else if (a === "--force") args.force = true;
    else if (a === "-h" || a === "--help") args.help = true;
    else {
      console.error(`Unknown argument: ${a}`);
      process.exit(2);
    }
  }
  return args;
}

async function listSkills() {
  const entries = await readdir(SKILLS_SRC, { withFileTypes: true });
  return entries.filter((e) => e.isDirectory()).map((e) => e.name);
}

async function install(target, force) {
  if (!existsSync(SKILLS_SRC)) {
    console.error(`No bundled skills found at ${SKILLS_SRC}`);
    process.exit(1);
  }
  const targetAbs = resolve(process.cwd(), target);
  await mkdir(targetAbs, { recursive: true });

  const skills = await listSkills();
  let written = 0;
  let skipped = 0;
  for (const name of skills) {
    const src = join(SKILLS_SRC, name);
    const dest = join(targetAbs, name);
    if (existsSync(dest) && !force) {
      console.log(`skip  ${name}  (exists; pass --force to overwrite)`);
      skipped++;
      continue;
    }
    await cp(src, dest, { recursive: true, force: true });
    console.log(`wrote ${dest}`);
    written++;
  }
  console.log(`\nDone — ${written} written, ${skipped} skipped, target: ${targetAbs}`);
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv.length === 0 || argv[0] === "-h" || argv[0] === "--help") {
    process.stdout.write(HELP);
    return;
  }
  const args = parseArgs(argv);
  if (args.help) {
    process.stdout.write(HELP);
    return;
  }
  switch (args.command) {
    case "install":
      await install(args.target, args.force);
      break;
    case "list": {
      const skills = await listSkills();
      for (const s of skills) console.log(s);
      break;
    }
    default:
      console.error(`Unknown command: ${args.command}\n`);
      process.stdout.write(HELP);
      process.exit(2);
  }
}

main().catch((err) => {
  console.error(err.stack || err.message || err);
  process.exit(1);
});
