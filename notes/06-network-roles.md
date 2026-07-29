# Scale-up, scale-out, scale-across

*Last updated: July 2026*

The AI cluster network splits into three tiers with different physics, and the competitive map is different in each.

## The three tiers

| Tier | What it connects | Distance | Latency budget | Buffer need |
|---|---|---|---|---|
| Scale-up | GPU↔GPU memory, one rack | < 3 m | ~100s of ns | Minimal |
| Scale-out | Racks within one DC (back-end fabric) | ≤ ~500 m | µs | Shallow OK with good load balancing |
| Scale-across | Between data centers | 10–100+ km | ms (speed of light) | Deep — must absorb long-RTT congestion |

## Who plays where

**Scale-up**: NVIDIA NVLink 5/6 (incumbent, proprietary) vs Broadcom Tomahawk Ultra + Scale-Up Ethernet (SUE) vs the UALink consortium. Cisco doesn't play here.

**Scale-out**: NVIDIA Spectrum-X (with Cisco Silicon One inside some platforms — the odd-couple alliance), Broadcom TH5/TH6, Cisco G200, Broadcom Jericho3-AI+Ramon3 as a scheduled-fabric alternative. This is the most crowded tier.

**Scale-across**: Broadcom Jericho4+Ramon4 vs Cisco P200. The newest battleground — driven by single sites running out of power, forcing training jobs to span facilities. Deep buffers + line-rate MACsec are the entry ticket.

## Why scale-across is suddenly hot

Model sizes outgrew single-building power envelopes (each facility = tens to hundreds of MW). Distributing XPUs across sites requires lossless, secure, very-high-bandwidth transport over regional distances — a new router class, not a bigger switch.

## Vendor strategy summary

- **NVIDIA**: owns scale-up (NVLink), fights in scale-out (Spectrum-X), sells the whole rack as the product.
- **Broadcom**: complete merchant portfolio across all three tiers, three specialized silicon lines; the arms dealer to everyone building non-NVIDIA clusters (and plenty of NVIDIA ones).
- **Cisco**: one architecture (Silicon One) across scale-out and scale-across, plus systems business; partnership with NVIDIA rather than head-on collision in scale-up.

## Open questions / to research

- [ ] Ultra Ethernet Consortium (UEC) spec adoption status across these chips
- [ ] How SONiC support maps across TH6 / G200 / Jericho4 (relevant to my SONiC fabric work)
- [ ] Optics: LPO vs CPO adoption per platform
