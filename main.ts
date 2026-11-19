// The World Gazette — entry program for make.fun news-image-20261119.
//
// The sandbox has no network, so the edition is drawn ahead of time: render.py
// reads stories.json (the day's curated wire reports) and draws entry.png with
// PIL primitives — masthead, date banner, lead illustration, 12-card grid and a
// world ticker. This program validates that PNG and copies it byte for byte to
// /output/entry.png. Two runs, identical bytes: it reads one fixed file and
// writes it unchanged, with no clock, no randomness, no network.
//
// Run locally:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const buf = readFileSync(join(here, "entry.png"));

// Whole-image checks against the contest caps: PNG signature, a 13-byte IHDR
// first, dimensions within 1024x1024, size within 1 MiB, and an IEND trailer.
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!buf.subarray(0, 8).equals(PNG_SIG)) throw new Error("entry.png: not a PNG");
if (buf.length > 1_048_576) throw new Error("entry.png: over the 1 MiB cap");
if (buf.readUInt32BE(8) !== 13 || buf.toString("ascii", 12, 16) !== "IHDR") {
  throw new Error("entry.png: first chunk is not a 13-byte IHDR");
}
const width = buf.readUInt32BE(16);
const height = buf.readUInt32BE(20);
if (width < 1 || height < 1 || width > 1024 || height > 1024) {
  throw new Error(`entry.png: ${width}x${height} outside the 1024x1024 cap`);
}
if (buf.toString("ascii", buf.length - 8, buf.length - 4) !== "IEND") {
  throw new Error("entry.png: no IEND trailer");
}
// The IEND chunk is always 0 bytes long and its CRC over the type name is fixed.
if (buf.readUInt32BE(buf.length - 12) !== 0 || buf.readUInt32BE(buf.length - 4) !== 0xae426082) {
  throw new Error("entry.png: malformed IEND chunk");
}

mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, "entry.png"), buf);
const sha = createHash("sha256").update(buf).digest("hex");
console.log(`The World Gazette · ${width}x${height} · ${buf.length} bytes · sha256 ${sha} -> ${join(outDir, "entry.png")}`);