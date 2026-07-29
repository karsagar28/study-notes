# Cisco CloudScale (vs Silicon One)

*Last updated: July 2026*

CloudScale and Silicon One coexist inside the Nexus 9000 line but are different generations of thinking. **CloudScale is a product-family ASIC; Silicon One is a silicon platform.**

## Head to head

| | CloudScale | Silicon One |
|---|---|---|
| Born | 2016, for Nexus 9000 / ACI | 2019, clean sheet (Q100) |
| Sold as | Cisco systems only (NX-OS / ACI) | Chips, whitebox, and systems |
| Scope | DC switching only | Switching + routing, access to web-scale |
| Pipeline | Fixed high-perf + smart buffers | P4-programmable, run-to-completion |
| Die budget bias | Tables, telemetry, ACI features | Radix, power/bit, mode flexibility |
| NOS | NX-OS / ACI | NX-OS, IOS XR, SONiC, FBOSS |
| AI-era flagship | H2R (400G class) | G200 in Nexus 9364E-SG2 (800G) |

Key contrasts:

- **Business model**: CloudScale never ships as a bare chip — it competes with Trident by being *more integrated than merchant silicon*. Silicon One competes with Broadcom by *being* merchant silicon.
- **Tables**: CloudScale-era claims of up to 512K MAC / 896K LPM — 2–3× the merchant silicon of its day. Classic feature-rich spend.
- **Direction of travel**: the raw-bandwidth frontier (800G, AI back-end) is going to Silicon One (9364E-SG2 = G200; Nexus 9800 modular = Silicon One). CloudScale continues where ACI integration and its feature set matter (H2R/H1: MACsec, SyncE, PTP, PFC/ECN/DCQCN). No public CloudScale part at 51.2T.
- Historically Cisco ran **three** custom silicon lines: CloudScale (Nexus DC), UADP (Catalyst campus), Silicon One. Silicon One is the declared convergence point.

## Intelligent buffering: AFD + DPP

CloudScale's answer to "shallow buffers, spent wisely." Premise: DC traffic is bimodal — a few **elephants** (long-lived, bandwidth-hungry) and many **mice** (short, latency-sensitive). A dumb shared buffer lets elephants fill the queue and every mouse waits behind them (bufferbloat where it hurts most).

![CloudScale intelligent buffering: DPP express lane for new flows, AFD-managed queue for elephants](notes/img/fig-afd-dpp.svg)

- **DPP (Dynamic Packet Prioritization)**: first N packets of every new flow go to a strict-priority express queue — mice usually finish inside that window and never queue behind elephants. Past the threshold, the flow is demoted to the normal queue.
- **AFD (Approximate Fair Dropping)**: the ETRAP (elephant trap) flow table tracks per-flow arrival rates in hardware, computes a fair share of the link, and probabilistically drops/ECN-marks flows exceeding it, proportional to the excess. Elephants get an early, *fair* congestion signal, so TCP/DCQCN backs off before the queue fills — low standing queue depth without losing throughput.

Philosophy: don't absorb congestion (deep buffers), **discipline** it. Cost: per-flow state and rate estimation in silicon — die area that Tomahawk-class chips don't spend.

## Open questions / to research

- [ ] CloudScale roadmap beyond H2R — is there another generation, or is Silicon One the end state for Nexus?
- [ ] AFD/DPP defaults and tuning on the platforms I run (which Nexus models, NX-OS knobs)
- [ ] How AFD interacts with DCQCN/PFC in a RoCE fabric — complementary or fighting?
