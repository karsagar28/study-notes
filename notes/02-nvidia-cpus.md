# NVIDIA CPUs (Grace line)

*Last updated: July 2026*

One CPU architecture at a time, sold standalone or fused into superchips. The CPU exists to feed the GPU: huge memory bandwidth, coherent NVLink-C2C to the accelerator, low power.

## The line

| Product | What it is | Notes |
|---|---|---|
| Grace | Standalone Arm CPU | 72 Neoverse V2 cores, LPDDR5X for energy efficiency. Also sold as Grace CPU Superchip (2× Grace, 144 cores). Confirmed as a multi-billion-dollar standalone business line. |
| GH200 | Grace + Hopper superchip | CPU and GPU on one module, NVLink-C2C coherent link (900 GB/s). |
| GB200 / GB300 | Grace + Blackwell / Blackwell Ultra | 1 Grace + 2 GPUs per superchip; the building block of the NVL72 racks. |
| Vera | Next-gen Arm CPU | Custom NVIDIA-designed Arm cores (dropping off-the-shelf Neoverse). Pairs with Rubin — the "Vera" in Vera Rubin NVL72. |

## Why it matters

- **LPDDR5X instead of DDR5**: trades some capacity ceiling for dramatically better energy per bit — matters when the rack budget is 120 kW+.
- **NVLink-C2C coherence**: GPU can address CPU memory directly; the CPU's LPDDR becomes cheap(er) extension memory for KV caches and optimizer states.
- **Vera = vertical integration**: moving from licensed Neoverse cores to custom cores mirrors what Apple/Amazon did — control the whole memory subsystem and the NVLink integration points.

## Open questions / to research

- [ ] Vera core count and confirmed specs (custom "Olympus" cores — verify final numbers vs the GTC 2025 announcement)
- [ ] Grace roadmap independent of superchips — will standalone Vera be sold?
