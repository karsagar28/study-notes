# Cisco Silicon One

*Last updated: July 2026*

One unified architecture and SDK spanning switching and routing, from campus access to web-scale AI fabrics. The pitch: same P4-programmable pipeline, same tooling, different die configurations per role. This is the structural opposite of Broadcom's two-silicon-lines approach (StrataXGS vs StrataDNX).

![Cisco Silicon One families by role](notes/img/fig-silicon-one.svg)

> Cisco's other DC silicon, CloudScale (Nexus 9000 / ACI), is covered in **C-07** — different generation of thinking, now converging toward Silicon One.

## Families by role

| Family | Role | Key parts | Notes |
|---|---|---|---|
| G-series | Web-scale switching, AI/ML fabric | G100, G200 (51.2T), G202 (25.6T), G300 | Shallow buffer, high radix. The AI story lives here. |
| P-series | Deep-buffer routing, DCI | P100 (19.2T), P200 (51.2T) | P200: first-to-market 51.2T deep-buffer router processor. |
| Q-series | Core and leaf routing/switching | Q100, Q200/L, Q201, Q202, Q211 | Q100 launched the Silicon One brand (2019). |
| K-series | SP access, edge, metro | K100 (6.4T), K200 | Feature richness and scale: subscriber queues, big tables, NetFlow. |
| E-series | Enterprise / feature-rich routing | E100, E200 | |
| A-series | Campus access | A100, A200 | |

## G200 highlights

- 5 nm, 51.2 Tbps, 512 × 112G PAM4 SerDes — industry-highest radix at launch (512 × 100GE on one die, 512 MACs at 1:1).
- Claimed cluster math: 32K × 400G GPU cluster in a **2-layer** network → ~50% fewer optics, ~40% fewer switches, ~33% fewer network layers vs lower-radix designs.
- Supports fully scheduled fabric with packet spraying (vs plain ECMP) for AI traffic.

## P200 highlights

- 51.2 Tbps full-duplex deep-buffer router; positioned for AI-era DCI / scale-across.
- Deep buffers + line-rate MACsec → lossless RoCE over long-haul distances. Direct counter to Broadcom Jericho4.

## Strategic notes

- NVIDIA alliance: Silicon One integrated into **Spectrum-X Ethernet** platforms — Cisco silicon inside NVIDIA's reference AI networking stack. Odd-couple arrangement given they compete elsewhere.
- Deployment flexibility: same device can run shallow-buffer switch mode or scheduled-fabric mode; P100/Q200-class as TOR with Q200L/G100 leaf-spine for fully scheduled designs.
- No public answer yet at 102.4T (vs Tomahawk 6) — watch for the next G-series part.

## Open questions / to research

- [ ] G300 specs and positioning
- [ ] Silicon One roadmap response to Tomahawk 6 / 102.4T class
- [ ] Where Silicon One lands in Nexus/8000-series platforms I touch at work
