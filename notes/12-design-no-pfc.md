# Design exercise: a fabric without PFC/ECN

*Last updated: July 2026*

Interview framing: PFC/ECN aren't features — they're **compensations** for Ethernet's default physics (transmit first, discover congestion later, loss-intolerant transport). Remove them and you must change the physics one of two ways: a fabric that **cannot congest internally**, or a transport that **doesn't care about loss**.

![Decision tree: never congest (credits) vs tolerate loss (smart endpoints)](notes/img/fig-no-pfc-tree.svg)

## Path 1 — never congest (credit-based admission)

Nothing enters the fabric without a guaranteed landing slot; the interior physically cannot overflow.

- **InfiniBand** (Quantum-class): the textbook answer if Ethernet isn't mandated. Link-level credit flow control is native — senders transmit only against advertised buffer credits; losslessness needs no pause protocol. Adaptive routing for load balancing; SHARP in-network reduction shrinks incast fan-in at the source.
- **Scheduled fabric / DDC** (Jericho3-AI/J4 + Ramon, or Silicon One scheduled mode): ingress VOQs with HBM absorb incast, cell spraying gives perfect load balancing by construction, egress credit grants keep the interior contention-free. No PFC (nothing overflows mid-fabric), no DCQCN tuning (rate control *is* the credit loop). Costs: single-vendor scheduling domain, HBM power/cost, scale bounded by fabric state. See X-08.
- **Tomahawk Ultra / SUE** for the scale-up tier: Ethernet framing with link-level credits and link-layer retry — Ethernet re-learning InfiniBand's link discipline.

## Path 2 — tolerate loss (UEC/UET endpoints)

Make drops cheap instead of impossible. Standard shallow-buffer 1:1 Clos (Tomahawk 6 / G200 class), UEC NICs doing native packet spraying + **selective retransmission** (a drop costs one packet, not a go-back-N window), plus packet trimming so the receiver learns of loss in one one-way delay. No PFC because loss is acceptable; no DCQCN because UET's CC is its own telemetry loop. See X-11.

**Interviewer asterisk:** some UET CC modes still consume ECN-style signals. If the constraint is literally "no ECN bits anywhere," the credit path is the strictly correct answer; if it means "no PFC and no DCQCN tuning hell," UET qualifies.

## The layer people forget: prevent congestion topologically

Applies to either path — a strong answer leads with these:

- **Rail-optimized topology**: each GPU's NIC on its own rail plane → NCCL's dominant traffic is one hop, never converging on shared spines.
- **Strict 1:1 non-blocking** Clos.
- **Topology-aware scheduling**: NCCL rings/trees aligned to physical fabric; job placement that avoids fragmenting a job across the cluster.
- **In-network collectives** where available (SHARP class) — reduces incast fan-in at the source.

A large fraction of real-world "PFC/ECN tuning" is compensating for incast that better topology and placement would have prevented.

## What I'd actually build

- Pure training, vendor lock acceptable → **scheduled DDC** (or InfiniBand if allowed). Deterministic; "no congestion control to tune" is operationally priceless at scale.
- Multivendor procurement, future-proofing → **UEC fabric**, accepting early-adopter status on 1.0-generation NICs.
- Either way: **rail-optimized 1:1 topology first** — the best congestion mechanism is the one that never triggers.

## Open questions / to research

- [ ] Real deployments running DDC for training back-end (who, at what scale)
- [ ] UET CC without any ECN signaling — which modes, which NICs
- [ ] SHARP-equivalents outside InfiniBand: state of in-network collectives on Ethernet
