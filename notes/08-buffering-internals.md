# Buffer internals: per-port, shared, or both?

*Last updated: July 2026*

Q: do deep-buffer devices (Jericho, P-series) have per-port buffers or shared?

A: **physically shared, logically per-queue.** Nobody does static per-port carving anymore — it strands capacity.

![Two-tier deep buffer: packets land in shared on-chip SRAM; only congested VOQs spill to shared external HBM](notes/img/fig-voq-two-tier.svg)

## Three layers to the answer

**Logically: per-queue, finer than per-port.** These are VOQ (virtual output queue) architectures: every packet is classified on ingress into a queue keyed on *egress port × traffic class*. A 512-port × 8-TC device tracks thousands of VOQs; in a multi-chip DDC (Jericho + Ramon) it's VOQs for every egress port in the whole fabric — can reach six figures. Per-queue granularity is what kills head-of-line blocking.

**Physically: shared pools, two tiers.** VOQs draw from a shared on-chip SRAM pool (tens of MB) backed by a shared external HBM pool (GBs). HBM is **not in the default data path**: packets land in SRAM; only queues that build depth get *evicted* to HBM and read back when the scheduler grants bandwidth. Consequences:

- Latency stays SRAM-class for uncongested traffic — a deep-buffer chip is not slow when the network is healthy.
- It *must* work this way: HBM bandwidth is a fraction of switching capacity — you physically cannot push 51.2T through the HBM. Only a minority of queues can be deep at once, which matches what real congestion looks like.

**Accounting: dynamic thresholds.** Each VOQ has admission thresholds (adaptive, plus WRED-style profiles) that shrink as the shared pool fills. One incast victim can grab a huge slice of idle HBM but can't starve everyone else. Per-queue guarantees layered on shared physics.

## The shallow side is shared too

Tomahawk/Trident use a shared MMU buffer with dynamic thresholds across all ports. Tomahawk 5 moved to a fully unified shared buffer after earlier generations partitioned it into per-pipe slices (→ stranded capacity). So shallow-vs-deep is **not** shared-vs-dedicated; it's *how much* shared memory, and whether there's an HBM overflow tier with a VOQ scheduler in front.

## Scheduled fabric vs standalone VOQ

Q: both use credits/grants from egress — so what's different?

A: **same loop, different distance.** The credit mechanism is identical; what changes is the scope of the scheduling domain, plus one genuinely new behavior: cells.

![Unscheduled Ethernet Clos vs scheduled fabric with cell spraying and credit grants](notes/img/fig-scheduled-fabric.svg)

- **Scope.** Single-device VOQ: ingress and egress are two ends of one die (or line cards over a chassis backplane); the credit round-trip is nanoseconds over copper. Scheduled fabric (DDC): the same discipline runs over optics between separate boxes — Jericho devices as "line cards," Ramon as the "backplane." A DDC literally is a modular router with the sheet metal removed. The crediting is inherited, not reinvented.
- **Cells, not packets.** The real new behavior. Normal Clos: packets traverse whole, ECMP pins each flow to one spine path → elephant collisions while other links idle. Scheduled fabric: ingress chops packets into fixed cells and sprays them across *all* fabric links; egress reassembles and reorders. Near-perfect load balancing by construction — no path selection to get wrong. Cost: cell overhead on fabric links, reassembly state at egress.
- **Where contention resolves.** Unscheduled: discovered en route — spine queue fills, ECN/PFC propagate back, DCQCN throttles. Reactive; where PFC storms and deadlocks live. Scheduled: resolved *before* transmission — egress grants credits at drain rate, so cells enter the fabric already guaranteed a landing slot. Fabric core is contention-free by construction; congestion manifests as VOQ depth at ingress (where the HBM is), not queue buildup mid-fabric.
- **Terminology check.** A plain shared-buffer switch (Tomahawk/Trident) is *output-queued* and uses **no credits at all** — packets buffer at the egress MMU. Credits are a VOQ thing. The spectrum: output-queued shared buffer (no credits) → single-device VOQ (credits across one chip/chassis) → scheduled fabric (credits + cell spray across the network).
- **The trade-off keeping both alive.** Scheduled fabric is a closed system: same proprietary cell/credit protocol end to end → single-vendor by construction (all DNX, or all Silicon One in scheduled mode), scale bounded by fabric reachability state. Open Ethernet Clos mixes vendors but must approximate the outcome reactively (adaptive/cognitive routing, NIC packet spraying, DCQCN tuning). UEC's goal is exactly this gap: spray-and-reorder semantics on interoperable Ethernet.

## Caveat

Exact eviction policies and threshold mechanics are datasheet/NDA territory per vendor. The above is the industry-standard shape (Jericho, Silicon One P-series both follow it), not a register-level description of any one part.

## Open questions / to research

- [ ] P200 white paper: published details on OCB size, eviction, HBM bandwidth ratio
- [ ] Jericho3-AI vs Jericho4 buffer sizing deltas
- [ ] How SONiC exposes VOQ counters/thresholds on DNX platforms
