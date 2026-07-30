# UEC: Ultra Ethernet

*Last updated: July 2026*

UEC = Ultra Ethernet Consortium — Linux Foundation body (founded 2023: Broadcom, Cisco, Arista, AMD, Intel, Meta, Microsoft, HPE; NVIDIA joined later). Spec 1.0 landed June 2025. Mission: make *standard, multivendor* Ethernet good enough for AI/HPC that you don't need InfiniBand, a proprietary pairing (Spectrum-X), or a closed DDC.

## What it brings: UET

The deliverable is a replacement transport — **UET (Ultra Ethernet Transport)** — fixing the assumptions RoCE inherited from InfiniBand:

- **Native packet spraying**: flows multipathed per-packet, delivered out of order, completed in order at the endpoint. No flow-to-path pinning → the ECMP elephant-collision problem disappears without proprietary cells or a co-designed switch/NIC pair.
- **Selective retransmission** (not go-back-N): a drop costs only the lost packet. Philosophically the big one — **drops stop being catastrophic, so losslessness stops being mandatory.** PFC becomes optional; directly answers the open question in X-10.
- **Modern congestion control**: sender- and receiver-driven, telemetry-informed.
- **Packet trimming**: under congestion the switch truncates a packet to its header and forwards *that* instead of silently dropping — receiver learns of the loss in one one-way delay instead of a timeout.
- Also in 1.0: link-layer retry, security at scale, in-network collectives, separate AI and HPC profiles.

## The three answers, side by side

![DDC, Spectrum-X, and UEC compared: where the intelligence lives](notes/img/fig-three-answers.svg)

| | DDC (Jericho + Ramon) | Spectrum-X | UEC / UET |
|---|---|---|---|
| Spray mechanism | Proprietary cells inside fabric | Switch sprays, NIC reorders | Native per-packet, endpoint completes |
| Reorder burden | Egress fabric device | BlueField SuperNIC (DDP into GPU memory) | UEC-capable NIC |
| Loss handling | Lossless by construction (credits) | RoCE + telemetry-based CC | Selective retransmit; loss tolerable |
| PFC needed? | N/A (scheduled interior) | Still RoCE-based | Optional |
| Vendor coupling | Single-vendor scheduling domain | Open wire, NVIDIA both ends for full value | Multivendor by design |
| Switch role | Scheduler + fabric | Co-designed, telemetry in-band | Mostly stateless (+ trimming assist) |
| Cross-ref | X-08 | ch. 06 | X-10 |

## Status (mid-2026)

1.0-generation silicon only now arriving in volume. Tomahawk 6, current Cisco/Arista AI platforms all advertise UEC-readiness — the thing to scrutinize on datasheets: which UET features are actually implemented vs "ready."

## Open questions / to research

- [ ] Which NICs ship full UET in hardware (AMD Pensando, Broadcom Thor line, Intel) and what falls back to firmware
- [ ] Does packet trimming appear in Silicon One / Tomahawk 6 feature lists, and is it enabled by default
- [ ] UEC profiles vs DCQCN coexistence during migration — can both run on one fabric
- [ ] SONiC support timeline for UET-relevant switch features
