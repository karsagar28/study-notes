# Excalidraw sources

Store editable Excalidraw source files here and export their SVG counterparts to
`notes/img/`. Give both files the same base name so a published figure can always
be traced back to its editable source.

Example:

```text
diagrams/rocev2-congestion-loop.excalidraw
notes/img/rocev2-congestion-loop.svg
```

When updating a diagram, commit the `.excalidraw` source and refreshed SVG export
together.

Do not author or update SVG diagrams directly. Always make the change in Excalidraw,
save the editable source here, and then export the matching SVG.
