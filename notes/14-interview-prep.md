# Interview prep: RDMA depth for an NVIDIA SA (Ethernet) role

*Last updated: July 2026*

Calibration: be a **fluent consumer** of RDMA, not a verbs programmer. Nobody asks an SA to write `ibv_post_send()`. They probe whether you understand the transport well enough to explain *why the fabric behaves the way it does* — the SA job is translating between the customer's network team and their ML engineers.

## Tier 1 — know cold

- **QP model, concept level.** Queue pair = send queue + receive queue, the NIC-level connection abstraction; completion queues signal done-ness. **RC (Reliable Connected)** is what RoCE training traffic uses. Scaling implication: RC is per-peer state → full-mesh QPs is O(n²) NIC memory, which is why QP scaling appears in fabric sizing and why NCCL manages channels/QPs the way it does.
- **Reliability semantics.** RC guarantees in-order exactly-once delivery in NIC hardware; classic recovery is **go-back-N** — *the* reason drops are catastrophic and the lossless edifice exists (X-10). Newer NICs' selective/adaptive retransmit is what relaxes losslessness — the through-line to Spectrum-X and UEC (X-11).
- **Verbs as vocabulary.** SEND/RECV (two-sided) vs READ/WRITE (one-sided). Network consequence of one-sided: receiver CPU is uninvolved, so incast victims can't "slow down" at the app layer — the fabric must handle it.
- **Memory registration + GPUDirect RDMA.** Pinned memory regions, lkey/rkey at handwave level; data lands NIC→GPU HBM directly. Explains **DDP — Direct Data Placement**: the NIC writes each packet's payload to its final memory location from addressing in the packet itself, so out-of-order arrival (spraying/adaptive routing) needs no reassembly buffer. ⚠ Acronym collision: in ML software, DDP = PyTorch DistributedDataParallel — confirm which is meant.
- **The stack.** PyTorch → NCCL → verbs → RoCEv2 → fabric. CNPs generated/consumed at the NIC; DCQCN rate limiting at the NIC; NCCL above (rings/trees, channels, chunking). "Training is slow" arrives at the fabric, often resolves in this stack.

## Tier 2 — conversational depth

UD transport (connection mgmt, some collectives), SRQs, atomics, connection establishment (CM), iWARP-vs-RoCE history (see the "why UDP" aside in X-10), and baseline tooling: `perftest` (`ib_write_bw`, `ib_send_lat`) and `nccl-tests` bus bandwidth — plus a feel for healthy 400G numbers. "How would you validate a new fabric?" is a near-certain question.

## Tier 3 — skip

Verbs API mechanics, WQE formats, doorbell registers, kernel-bypass internals, MPI details. Zero SA interview value.

## Where to spend the marginal hour instead

NVIDIA weights *their* stack: Spectrum-X (adaptive routing + DDP + telemetry CC), BlueField SuperNIC roles, NCCL on rail-optimized topologies, SuperPOD/SU reference architecture (X-13), and comparative positioning vs Broadcom/UEC — the "three answers to elephant flows" framing (X-11) is exactly the synthesis that lands.

One-line calibration: an SA who can whiteboard *why go-back-N forced lossless Ethernet and what selective retransmit changes* beats one who memorized twenty verbs.

## Mock question bank (answers live in the referenced chapters)

1. Why does RoCEv2 run over UDP and not TCP? What does the UDP source port do? (X-10)
2. Walk me through what happens in the fabric when 512 ranks hit an all-reduce barrier simultaneously. (X-10, X-13)
3. ECN vs PFC — which fires first and why? What happens if you get the thresholds backwards? (X-10)
4. Why does PFC need a watchdog? Describe the deadlock without one. (X-10)
5. A customer refuses PFC and ECN outright. Design their training fabric. (X-12)
6. Deep-buffer switches: per-port or shared buffers? Where does the HBM sit in the data path? (X-08)
7. Scheduled fabric vs standalone VOQ switch — both use credits, so what's different? (X-08)
8. Compare DDC, Spectrum-X, and UEC as answers to ECMP elephant collisions. Who carries the reorder burden in each? (X-11)
9. What does Spectrum-X adaptive routing do that ECMP and flowlet-based DLB don't? Why does it need BlueField at the far end? (ch. 06, X-13)
10. Customer says all-reduce stalls at 8k GPUs. Give three hypotheses spanning NCCL, NIC, and fabric. (this chapter, X-10)
11. Why is rail-optimized topology the first congestion tool, before any QoS knob? What's a rail? (X-12, X-13)
12. What's the trade between buffer depth and latency? Why not deep buffers everywhere? (05, X-13)
13. Tomahawk 6 vs Silicon One G200 — how would you position against Broadcom in a bake-off? (03, 04)
14. Why is JCT the metric and not utilization? How does tail latency couple to it? (X-13)
15. What changes about fabric design if the NICs do selective retransmission instead of go-back-N? (X-11, X-12)
16. NFS and RoCE on one fabric — do they conflict? How would you class/queue them? (X-13, X-10)
17. Scale-up vs scale-out vs scale-across — which NVIDIA product answers each, and where does Ethernet compete? (06)
18. What is DDP in this context, and what's the acronym trap? (this chapter)

## Open questions / to research

- [ ] Healthy `ib_write_bw` / nccl-tests busbw baselines for 400G/800G — collect real numbers
- [ ] NCCL channel/QP counts at scale — current defaults and tuning guidance
- [ ] Spectrum-X + BlueField failure modes an SA should know (link flap behavior, telemetry CC edge cases)
