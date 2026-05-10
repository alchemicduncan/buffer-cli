#!/usr/bin/env node
import { cp, readdir, rm } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = resolve(HERE, "..", "..", "skills");
const DEST = resolve(HERE, "..", "skills");

if (!existsSync(SRC)) {
  console.error(`Canonical skills dir not found at ${SRC}`);
  process.exit(1);
}

await rm(DEST, { recursive: true, force: true });
await cp(SRC, DEST, { recursive: true });
const names = (await readdir(DEST, { withFileTypes: true }))
  .filter((e) => e.isDirectory())
  .map((e) => e.name);
console.log(`synced ${names.length} skill(s) into installer/skills: ${names.join(", ")}`);
