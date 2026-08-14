# AI silicon field notes

A zero-build, offline-capable knowledge base for NVIDIA Solutions Architect—Ethernet/NVIS certification study, networking job preparation, AI infrastructure, and future personal blog content. It tracks NVIDIA GPUs/CPUs and networking alongside Cisco Silicon One, Broadcom switch ASICs, protocols, operations, and system-design trade-offs.

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
- Mark evolving material as `scratch`, `reviewed`, or `blog-ready`; do not make rough notes sound final.
- An **Open questions / to research** section at the bottom collects loose threads (GFM task lists render as checkboxes).
- GFM tables are used heavily for lineups and comparisons.
- New diagrams and flowcharts should be created in Excalidraw. Keep editable `.excalidraw` sources in `diagrams/` and export SVG copies to `notes/img/` for the reader. Existing generated figures can continue to use `tools/figures.py`.
- Flowcharts, packet/control-path diagrams, decision trees, sequence diagrams, and comparison tables are preferred when they communicate the idea better than prose alone.
- Use `templates/topic-note.md` to start a substantial topic.
- See `AGENTS.md` for the complete study-session and content-development workflow.

## Layout

```
index.html        the reader (nav, routing, rendering, dark mode)
manifest.json     chapter list — the only file to edit when adding notes
notes/*.md        the actual content
diagrams/*.excalidraw  editable Excalidraw diagram sources
templates/        reusable study-note structure
notes/img/*.svg   diagrams rendered for the reader
vendor/marked.umd.js  markdown renderer (vendored, MIT)
```

## Ideas for later

- Client-side search (fetch all chapters, index in memory)
- Per-chapter tags / vendor filter in the sidebar
- A `git log --follow` view per note to see how understanding evolved
