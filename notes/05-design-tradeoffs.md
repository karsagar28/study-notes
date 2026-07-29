# What each chip optimizes for

*Last updated: July 2026*

Every ASIC has a fixed die-area and power budget. Every "feature" is a decision about where to spend transistors. Two 51.2T chips with identical datasheet throughput can be completely different products depending on what the silicon was spent on.

![Where die area goes, by use case](notes/img/fig-die-budget.svg)

**The one-sentence version**: throughput is what the datasheet leads with, but the use case is defined by what the chip does when things go wrong — congestion, table exhaustion, protocol weirdness — and each family pre-pays for exactly one flavor of trouble.

## The axes

### 1. Buffer depth
The biggest fork. **Shallow** (on-chip SRAM, tens of MB): nanosecond access, low power — but sustained incast or long-RTT flows overflow it → drops. Tomahawk, G-series. **Deep** (HBM, gigabytes): absorbs seconds of congestion, enables lossless RoCE over 100 km DCI. Jericho, P-series. The tax: HBM cost, power, and latency when packets spill off-chip. Never build a leaf-spine out of deep-buffer silicon — you pay the tax on every hop that doesn't need it.

### 2. Radix
Ports per chip. A topology feature, not a speed feature: 512 × 100G on one die = flatter network = fewer tiers, fewer switches, fewer **optics** (which dominate cost and failure rate in AI clusters). Fabric chips spend most of their beachfront on SerDes and starve everything else.

### 3. Latency
The scale-up specialty. Tomahawk Ultra strips the pipeline to the hundreds-of-ns class to compete with InfiniBand/NVLink for GPU↔GPU memory traffic. Bought by deleting features: no big tables, no fancy parsing, minimal buffering.

### 4. Table scale
FIB routes, MAC entries, ACLs. AI fabric spine: a few thousand routes. SP edge: millions of routes, per-subscriber queues, huge ACL/NetFlow tables. Tables = TCAM + SRAM = area hogs. This is why K100 and Trident exist as separate products rather than being "a slower G200."

### 5. Queueing and scheduling
How the chip **fights** congestion rather than absorbing it. VOQs kill head-of-line blocking. Fully scheduled cell-based fabrics (Jericho+Ramon DDC, Silicon One scheduled mode) spray packets across all paths and reassemble — sidesteps the elephant-flow problem that wrecks ECMP hashing under AI training traffic. Shallow-buffer chips counter with adaptive load balancing (Cognitive Routing) — cheaper in silicon, less deterministic.

### 6. Programmable pipeline
Flexible parsers for VXLAN, SRv6, MPLS, GTP, whatever comes next. Insurance against protocol churn. Mandatory at the edge, dead weight in a uniform fabric. Costs pipeline stages → latency.

### 7. Line-rate security
MACsec/IPsec engines at full throughput. Nearly free to omit inside a secured DC; non-negotiable when traffic crosses a fence. Hence DCI (Jericho4, P200) and edge silicon, not fabric chips.

### 8. Telemetry
NetFlow/IPFIX, INT, per-flow state. Enterprise and SP edge care; fabrics get by with coarse counters + streaming telemetry.

## Die budget cheat sheet

| Block | Fabric chip (TH6, G200) | Deep-buffer router (Jericho4, P200) | Edge chip (Trident, K100) |
|---|---|---|---|
| SerDes / I/O | Dominant | Large | Moderate |
| Buffering | Small SRAM | HBM controllers + VOQ | Moderate |
| Tables / TCAM | Minimal | Large FIB | Dominant |
| Pipeline | Fast, fixed | Scheduler-heavy | Flexible, programmable |
| Security | — | Line-rate MACsec | MACsec/IPsec variants |
