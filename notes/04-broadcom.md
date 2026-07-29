# Broadcom switch and routing ASICs

*Last updated: July 2026*

Two distinct silicon lines, split by one question: **where does the packet buffer live?**

- **StrataXGS** (Tomahawk, Trident): shallow on-chip shared buffer → speed, radix, low cost per bit.
- **StrataDNX** (Jericho, Qumran, Ramon): deep HBM buffer + VOQ scheduling → scale, lossless routing.

## The families

| Family | Line | Role | Current parts |
|---|---|---|---|
| Tomahawk | XGS | Scale-out AI/cloud fabric | TH5 (51.2T, 5nm), TH6 (102.4T, 3nm, BCM78910/78914) |
| Tomahawk Ultra | XGS | Scale-up + HPC, low latency | InfiniBand replacement; GPU/XPU memory linking via Scale-Up Ethernet (SUE) |
| Trident | XGS | Feature-rich ToR / enterprise | Trident 4 (12.8T, BCM56880; 8T MACsec variant BCM56780), Trident 5 |
| Jericho | DNX | Deep-buffer AI routing | Jericho3-AI + Ramon3 (scheduled DDC fabric); Jericho4 + Ramon4 (scale-across) |
| Qumran | DNX | SP edge routing | Qumran 2C, Qumran 3 class |

## Tomahawk 6

- First single-chip **102.4 Tbps** switch. TSMC 3nm. Two SKUs, plus co-packaged optics variant (TH6-Davisson, BCM78919) with integrated silicon photonics.
- Cognitive Routing 2.0 — adaptive traffic management for AI training fabrics.
- Serves both scale-out and (with SUE) scale-up.

## Jericho4

- 51.2T deep-buffer fabric router, shipping since 2025. Built to interconnect **1M+ XPUs across multiple data centers**.
- 3.2 Tbps HyperPorts (up to 36,000 per system), HBM buffering (~160× more than on-chip), line-rate MACsec, lossless RoCE over 100 km+.
- The scale-across play: distribute AI clusters across facilities when a single site runs out of power.

## The three-roles frame (Broadcom's own)

1. **Scale-up** (XPU↔XPU in a rack): Tomahawk Ultra, TH6 + SUE. Competes with NVLink.
2. **Scale-out** (leaf/spine in a DC): TH5/TH6, or Jericho3-AI + Ramon3 as a scheduled DDC.
3. **Scale-across** (between DCs): Jericho4 + Ramon4. Competes with Cisco P200.

## vs Cisco Silicon One

Same territory, opposite structure: Broadcom ships specialized silicon lines with different programming models; Cisco ships one architecture in different configurations. Broadcom wins on raw top-end today (102.4T, CPO shipping); Cisco's pitch is operational uniformity.

## Open questions / to research

- [ ] Tomahawk 6 real-world deployments and which NOS stacks (SONiC support status)
- [ ] SUE vs UALink vs NVLink Fusion — how the scale-up standards fight shakes out
- [ ] Trident 5 full specs
