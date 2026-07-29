# AI silicon field notes

A zero-build, offline-capable notes site for tracking AI silicon: NVIDIA GPUs/CPUs, Cisco Silicon One, Broadcom switch ASICs, and the design trade-offs behind them.

Markdown in, website out. No build step, no node_modules, no framework. `marked.js` is vendored in `vendor/` so it works with no network.

## Run it

```bash
cd ai-silicon-notes
python3 -m http.server 8080
# open http://localhost:8080
```

Any static server works (`npx serve`, `caddy file-server`, nginx). It can't run from `file://` because the app fetches markdown at runtime.

## Add a note

1. Create `notes/07-my-topic.md` (start it with a single `# Title`).
2. Add one line to `manifest.json`:

```json
{ "id": "07-my-topic", "part": "X-07", "title": "My topic" }
```

3. Commit.

The `part` field is the silkscreen-style label shown in the sidebar and page eyebrow — the loose convention here is a vendor letter + sequence (`N-` NVIDIA, `C-` Cisco, `B-` Broadcom, `X-` cross-cutting), but it's freeform.

## Conventions used in the notes

- Each note opens with `*Last updated: <month year>*` — bump it when you touch the file.
- An **Open questions / to research** section at the bottom collects loose threads (GFM task lists render as checkboxes).
- GFM tables are used heavily for lineups and comparisons.

## Layout

```
index.html        the reader (nav, routing, rendering, dark mode)
manifest.json     chapter list — the only file to edit when adding notes
notes/*.md        the actual content
vendor/marked.umd.js  markdown renderer (vendored, MIT)
```

## Ideas for later

- Client-side search (fetch all chapters, index in memory)
- Per-chapter tags / vendor filter in the sidebar
- A `git log --follow` view per note to see how understanding evolved
