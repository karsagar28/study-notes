# Vocabulary: P4, pipelines, and recurring terms

*Last updated: July 2026*

Terms that keep recurring in ASIC datasheets and white papers. All three of the big ones are answers to the same problem: **silicon is frozen at tape-out, but traffic and protocols aren't.**

## P4-programmable

About *what the pipeline understands*. Fixed-function chips hardwire the parser and stages to a protocol list frozen at design time — new encapsulation (SRv6 micro-SID, GTP, INT headers) means waiting for the next chip. P4 (Programming Protocol-independent Packet Processors) is a DSL where you declare header formats and match-action logic; a compiler maps the program onto generic parser + match-action resources. The silicon ships protocol-agnostic; protocol knowledge arrives as software.

- This is partly how Silicon One's one architecture covers campus switch → SP edge router: same engines, different loaded programs.
- Caveat: programmable ≠ unlimited. Stage counts, table memory, and header-depth budgets are fixed physical resources, and vendors vary in how much P4 surface they expose.
- The purist extreme — Intel Tofino, fully user-programmable — was discontinued in 2023. The market mostly buys vendor P4 programs rather than writing its own.

## Pipeline vs run-to-completion

About *how the hardware executes* the forwarding logic.

![Pipeline model: fixed stage sequence. Run-to-completion: a processor array runs the whole program per packet](notes/img/fig-pipeline-vs-rtc.svg)

**Pipeline** = assembly line. Every packet visits every stage in order; each stage takes fixed cycles. Great throughput, deterministic latency. But program length is capped by stage count, and an L2-only packet still marches through the ACL stage. Deep feature stacks (multi-level tunnels, multiple FIB lookups) may simply not fit.

**Run-to-completion (RTC)** = room full of craftsmen. An array of identical packet processors; each picks up a packet and executes the *entire* program — however many lookups it takes — against shared tables, then releases it. Simple packets finish fast, gnarly ones take longer; array parallelism keeps aggregate throughput up. Natural fit for routing feature depth (Juniper Trio lineage). Trade: variable per-packet latency, and packet order must be restored.

Silicon One = P4-programmable RTC engines → the program stretches, not the silicon. CloudScale = pipeline with smart buffers → a rich but fixed feature set, cleverness spent on queue management. Neither is "better": one optimizes for a known job done extremely well, the other for not knowing the job five years out.

## Quick glossary

| Term | Meaning |
|---|---|
| VOQ | Virtual output queue — ingress queue per (egress port × traffic class); kills head-of-line blocking. See X-08. |
| DDC | Distributed disaggregated chassis — Jericho line cards + Ramon fabric elements behaving as one huge scheduled router. |
| OCB | On-chip buffer — the SRAM tier in front of HBM in deep-buffer designs. |
| ETRAP / AFD / DPP | CloudScale elephant-flow detection, fair early dropping, and new-flow prioritization. See C-07. |
| ECN / PFC / DCQCN | Congestion signaling stack for RoCE: mark instead of drop, pause per priority, rate-control end hosts. |
| Incast | Many senders → one receiver simultaneously; the traffic pattern that defines buffer requirements. |
| SUE | Broadcom Scale-Up Ethernet — Ethernet as an NVLink alternative inside the rack. |
| HyperPort | Jericho4's bonded 3.2 Tbps logical port for scale-across links. |
| CPO / LPO | Co-packaged / linear pluggable optics — moving or simplifying the optical conversion to cut power. |

## Open questions / to research

- [ ] What P4 surface Silicon One actually exposes to customers vs Cisco-internal
- [ ] How RTC architectures restore packet order at 51.2T without adding latency
