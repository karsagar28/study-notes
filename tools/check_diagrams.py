#!/usr/bin/env python3
"""Verify that Excalidraw is the source of truth for every published diagram."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    source_dir = root / "diagrams"
    export_dir = root / "notes" / "img"
    errors: list[str] = []

    sources = {path.stem: path for path in source_dir.glob("*.excalidraw")}
    exports = {path.stem: path for path in export_dir.glob("*.svg")}

    for name in sorted(exports.keys() - sources.keys()):
        errors.append(f"SVG has no editable Excalidraw source: notes/img/{name}.svg")
    for name in sorted(sources.keys() - exports.keys()):
        errors.append(f"Excalidraw source has no website export: diagrams/{name}.excalidraw")

    image_pattern = re.compile(r"!\[[^]]*\]\(([^)]+)\)")
    for note in sorted((root / "notes").glob("*.md")):
        for reference in image_pattern.findall(note.read_text(encoding="utf-8")):
            if "://" in reference:
                continue
            if not (root / reference).is_file():
                errors.append(f"Missing image referenced by {note.relative_to(root)}: {reference}")

    for path in sorted(sources.values()):
        try:
            scene = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"Invalid Excalidraw JSON in {path.relative_to(root)}: {exc}")
            continue
        if scene.get("type") != "excalidraw" or not isinstance(scene.get("elements"), list):
            errors.append(f"Invalid Excalidraw scene structure: {path.relative_to(root)}")
        non_nunito = [
            element.get("id", "unknown")
            for element in scene.get("elements", [])
            if element.get("type") == "text" and element.get("fontFamily") != 6
        ]
        if non_nunito:
            errors.append(
                f"Non-Nunito text in {path.relative_to(root)}: {', '.join(non_nunito)}"
            )

    if errors:
        print("Diagram validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Diagram validation passed: {len(sources)} editable sources, "
        f"{len(exports)} matching SVG exports."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
