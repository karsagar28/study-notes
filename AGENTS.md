# Working agreement for this knowledge base

## Purpose

Use this repository as Karthik's working knowledge base for:

1. NVIDIA Solutions Architect—Ethernet/NVIS certification study
2. NVIDIA networking and solutions-architect job preparation
3. Technical discussions, practice questions, and knowledge-gap tracking
4. Source material that can later become personal blog posts

Prefer technically precise explanations that connect architecture, packet behavior,
operations, troubleshooting, design trade-offs, and customer outcomes.

## How to capture a study session

- Add useful conclusions to the relevant existing note instead of creating duplicates.
- Create a new topic note when the subject does not fit an existing chapter.
- Preserve uncertainty. Label claims as confirmed, inferred, or still to verify.
- End study notes with open questions and follow-up research tasks.
- Add scenario questions and concise interview-ready answers when appropriate.
- Keep scratch material useful but clearly separate it from polished, publishable prose.
- Record sources and verification dates for facts that may change.

## Visual-first explanations

Use visuals whenever they improve understanding. Favor:

- flowcharts for packet paths, control loops, and troubleshooting decisions
- sequence diagrams for protocol exchanges and convergence behavior
- architecture diagrams for fabrics, rails, planes, and component relationships
- comparison tables for products, protocols, design choices, and failure modes
- small worked examples for calculations, queue behavior, and capacity planning

Create diagram source files in `diagrams/` using Excalidraw's editable
`.excalidraw` format. Export each diagram as SVG into `notes/img/` for use by the
offline reader. Keep the source and export names aligned, for example:

```text
diagrams/rocev2-congestion-loop.excalidraw
notes/img/rocev2-congestion-loop.svg
```

Prefer one teaching idea per diagram. Use clear labels, a restrained color palette,
and a legend when colors or line styles carry meaning. Make diagrams readable in
both light and dark contexts when practical.

Do not create or edit a published SVG directly. Excalidraw is the source of truth;
SVG files are exports only. A diagram change is incomplete unless both the editable
`.excalidraw` file and its matching SVG export are present.

Before completing a diagram or note change, run `python3 tools/check_diagrams.py`.
Completion requires every published SVG to have a same-named editable source and every
local image reference in the notes to resolve.

## Note quality bar

Each substantial topic should cover the relevant parts of this outline:

- why the topic matters to an NVIDIA solutions architect
- mental model and key terminology
- architecture or packet/control flow
- design choices and trade-offs
- configuration and operational considerations
- failure modes and troubleshooting approach
- comparison with credible alternatives
- certification checks and interview questions
- customer-facing explanation
- open questions, sources, and last verification date

Do not invent NVIDIA product behavior or exam requirements. Verify time-sensitive
claims against authoritative sources before treating them as facts.
