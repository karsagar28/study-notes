# NVIDIA data center GPUs

*Last updated: July 2026*

NVIDIA moved from a two-year to an **annual architecture cadence** for data center silicon. The confirmed roadmap: Blackwell (2024) → Blackwell Ultra (2025) → Rubin (H2 2026) → Rubin Ultra (H2 2027) → Feynman (2028).

## Generations

| Generation | Chips | Memory | Process | Status (mid-2026) |
|---|---|---|---|---|
| Hopper | H100, H200 | HBM3 / HBM3e | TSMC 4N | Still in production for installed-base customers |
| Blackwell | B200, GB200 NVL72 | 192 GB HBM3e | TSMC 4NP | Shipping in volume; was sold out through mid-2026 |
| Blackwell Ultra | B300, GB300 NVL72 | 288 GB HBM3e, 8 TB/s | TSMC 4NP | Current production flagship, ~15 PFLOPS dense FP4, 1400 W |
| Rubin | R100, Vera Rubin NVL72 | 288 GB HBM4, ~13 TB/s | TSMC 3nm (N3/N3P) | Entered full production June 2026; volume H2 2026 → 2027 |

## Rubin notes

- Full node shrink from Blackwell (4NP → 3nm). ~336B transistors.
- HBM4 + NVLink 6 (~3.6 TB/s per GPU; ~260 TB/s aggregate per NVL72 rack).
- Rack-scale SKUs: Vera Rubin NVL72 (successor to GB200/GB300 NVL72), HGX Rubin NVL8, and NVL144 CPX for massive-context inference (~8 EF, ~100 TB fast memory per rack).
- Positioned for agentic AI / reasoning workloads; pitched as an efficiency play as much as a performance one.
- DGX Rubin rack pricing reported around $3.5–4M.

## Rack-scale framing

The unit of sale is increasingly the **rack, not the card**: GB200 NVL72 → GB300 NVL72 → Vera Rubin NVL72. 72 GPUs in one NVLink coherency domain, liquid-cooled, with the CPU (Grace, then Vera) integrated on the superchip. Think of the NVL72 as the "chip" and the data center as the motherboard.

## Open questions / to research

- [ ] Rubin Ultra dual-die details and claimed 3.5× inference perf/W vs B300
- [ ] Feynman (2028) — anything concrete beyond the name
- [ ] China-specific SKUs (B40 etc.) current status
