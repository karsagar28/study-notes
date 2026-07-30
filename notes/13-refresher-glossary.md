# Refresher glossary (5 minutes before the interview)

*Last updated: July 2026*

Quick-scan definitions, 2–3 sentences each, cross-referenced to the deep chapters.

**Rail-optimized design / rail size.** Each GPU's NIC *k* connects to its own leaf plane ("rail") *k*, so the GPU-to-GPU traffic NCCL generates most (rank *i* ↔ rank *i* across nodes) stays inside one rail and one switch hop. Rail size = how many GPUs one rail switch reaches (NICs/server × servers per leaf); collectives are arranged so most traffic never crosses spines. Kills incast and spine congestion at the source.

**Elephant vs mice flows.** Elephants: few, long-lived, bandwidth-hungry flows (training collectives, storage sync). Mice: many short, latency-sensitive flows. ECMP struggles with elephants (two hashed onto one link saturate it while others idle); CloudScale's AFD/DPP treats the two classes differently on purpose (C-07).

**Non-blocking.** A fabric where every input/output pairing can run at full line rate simultaneously — 1:1 oversubscription in a Clos. AI training demands it because barrier-synchronized collectives drive all ports at once; enterprise-style 3:1 oversubscription assumes statistical quiet that AI traffic doesn't have.

**VOQ (virtual output queue).** Ingress queues keyed per egress port × traffic class, drained by an egress credit scheduler. Prevents HOL blocking because congestion on one output never traps packets bound elsewhere. Physically shared buffer pools, logically per-queue accounting (X-08).

**HOL (head-of-line) blocking.** The packet at a queue's head can't transmit (its output is busy or paused), so every packet behind it — including ones bound for idle outputs — waits too. The problem VOQs exist to solve; also what PFC pauses cause at fabric scale.

**Synchronized flows.** Collectives are barrier-synchronized: every rank bursts on the same clock edge, so the fabric sees microbursts/incast even at low *average* utilization. This is why average-load capacity planning fails for AI and why incast is the defining stress test (X-10).

**Load balancing — ECMP, DLB, DSF/scheduled Ethernet.** ECMP: hash a flow onto one path — cheap, stateless, but elephants collide. DLB/flowlet/adaptive (Cognitive Routing class): reroute flowlets or packets based on live link load — better, still reactive. DSF/scheduled Ethernet (DDC): VOQ + cell spray + credits — perfect balancing by construction, at the price of a closed single-vendor fabric (X-08). UEC moves spraying into the standard endpoints (X-11).

**RDMA / RoCEv2 — do they compete with NFS?** No — different layers. RDMA is a transport capability (NIC writes directly into remote memory, bypassing CPUs); RoCEv2 is RDMA over UDP/IP Ethernet (X-10). NFS is a *file* protocol that can ride on top (NFS over RDMA is standard for AI storage); in practice both GPU collectives and storage traffic often share the RoCE fabric on different priorities.

**ECN / PFC.** ECN: switch marks packets instead of dropping as queues build; receiver NIC sends CNPs; sender rate-limits that flow (DCQCN). PFC: per-priority pause when ingress buffers cross XOFF — the last-resort airbag. Tuning rule: ECN must engage well before PFC; PFC needs a watchdog because pause cycles can deadlock (X-10).

**NVIDIA Reference Architecture — Scalable Units.** NVIDIA's validated cluster blueprint (DGX SuperPOD): an SU is a fixed building block (e.g., 32 nodes / 256 GPUs) with its own rail-optimized leaves; clusters grow by replicating SUs under shared spines. You're buying pre-validated cabling, switch counts, and NCCL behavior — predictability, not novelty.

**SLURM.** The dominant open-source HPC scheduler: queues jobs, allocates GPUs/nodes, enforces priorities and preemption. Network-relevant because *placement* is destiny: a job fragmented across SUs pushes collective traffic over spines and inflates JCT — topology-aware scheduling is a fabric optimization.

**Network tuning — how to approach it.** Order of operations: topology and placement first (rails, 1:1, job packing), then buffers (headroom sized from cable lengths, alpha thresholds), then the ECN curve (Kmin/Kmax/Pmax comfortably below XOFF), then NIC DCQCN parameters. Validate with collective benchmarks (nccl-tests bus bandwidth), watch PFC pause counters, watchdog hits, and tail latency — and change one knob at a time.

**Trade-off: buffers vs latency.** Buffer absorbs bursts; buffer *occupancy* is queuing delay (bufferbloat). Goal: enough headroom for microbursts, aggressive early ECN so standing depth stays near zero. Deep buffers belong where they're needed (ingress VOQ, DCI) — not on every hop (05, X-08).

**JCT (job completion time).** Wall-clock time for the training job or iteration — the only metric that ultimately matters, not link utilization. Collectives finish at the pace of the *last* rank, so the network's contribution to JCT comes through its worst path, not its average.

**Tail latency.** p99/p999 completion times. Because collectives are barrier-synchronized, one slow flow stalls every rank — tail latency converts directly into JCT. This is why bimodal latency (PFC pause events) is poison even when the median looks great.

**Credit-based flow control.** Receiver advertises buffer credits; sender transmits only against them — overflow is impossible by construction rather than prevented reactively. InfiniBand link FC, scheduled-fabric egress grants, and NVLink all work this way; contrast with Ethernet's transmit-then-pause (X-12).

**Data vs tensor vs pipeline parallelism.** Data: replicate the model, split the batch, all-reduce gradients — bandwidth-heavy, overlappable, rides scale-out. Tensor: split individual layers' matrices across GPUs — chatty per-layer all-reduces, needs NVLink-class scale-up. Pipeline: split layers into sequential stages with micro-batches — point-to-point traffic, pays a "bubble" (idle time) cost. The mix determines which fabric tier each byte rides.

**Bisection bandwidth.** Cut the network into two halves the worst way possible; bisection bandwidth is what crosses the cut. Full bisection = either half can talk to the other at line rate — the bound that all-to-all and large all-reduce phases push against; equivalent to 1:1 non-blocking in a Clos.

**Switch radix.** Ports per chip at a given speed (e.g., 512×100G on G200/Tomahawk 5). High radix is a *topology* feature: flatter networks, fewer tiers and hops, and critically fewer optics — which dominate cost and failure rate at cluster scale (05).

**Scale-up vs scale-out vs scale-across.** Up: GPU↔GPU memory domain inside the rack — NVLink/SUE, ~100s of ns. Out: racks within one DC — the Ethernet/IB Clos back-end, µs. Across: between DCs — deep-buffer, MACsec'd DCI routers (Jericho4, P200), ms and speed-of-light constraints (06).
