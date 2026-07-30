# Lossless Ethernet: PFC, ECN, and the watchdog

*Last updated: July 2026*

RDMA (RoCEv2) assumes lossless transport — drops are catastrophic because go-back-N retransmission (on pre-adaptive-retransmit NICs) tanks throughput. So the fabric needs two mechanisms: one to **prevent drops** (PFC) and one to **prevent PFC from ever firing** (ECN). That framing is the whole tuning philosophy: **ECN is the first line of defense, PFC is the airbag.**

## PFC (802.1Qbb)

Per-priority pause. Unlike legacy 802.3x pause (stops the whole link), PFC pauses a single traffic class — typically priority 3 for RoCE data, 7 for CNPs. When a switch's ingress buffer for that priority crosses **XOFF**, it sends a pause frame upstream; traffic resumes at **XON**.

**Headroom**: after XOFF is sent, in-flight bytes keep arriving — pause-frame propagation, sender response time, one MTU serializing in each direction, plus 2× cable propagation delay. Headroom must absorb all of it. Rule of thumb: ~50 KB per port per lossless PG at 100G/100 m; longer links and 400G need meaningfully more. **Undersized headroom = drops on a "lossless" class — the worst failure mode because it's silent.** Buffer profiles are a strong candidate for generated config driven from a cable-length source of truth.

## ECN / DCQCN

The end-to-end mechanism. The switch marks CE bits in the IP header (WRED-style probabilistic marking on egress queue depth) instead of dropping; the receiving NIC fires CNPs (Congestion Notification Packets) back to the sender, whose NIC rate-limits *that flow*. Marking + CNP + sender rate algorithm = DCQCN.

![The DCQCN control loop: switch marks CE, receiver sends CNP, sender rate-limits the flow](notes/img/fig-dcqcn-loop.svg)

Three switch-side knobs per queue: **Kmin** (marking starts), **Kmax** (100% marking probability), **Pmax** (probability at Kmax). Plus NIC-side DCQCN parameters: rate decrease factor, recovery timers, CNP interval.

## The tuning relationship

![Threshold ladder on one queue: healthy, ECN ramp from Kmin to Kmax, 100% marking, then XOFF and PFC headroom](notes/img/fig-pfc-ecn-thresholds.svg)

The single most important relationship: **ECN must engage well before PFC.** Kmax sits comfortably below the XOFF threshold. If PFC fires before ECN has throttled senders, you get pause-driven head-of-line blocking instead of graceful per-flow rate reduction, and latency goes bimodal. Kmin: low enough to react early, high enough to ride out microbursts without marking — too low and you cap throughput on healthy links.

## Why PFC is dangerous

- **Incast**: many senders → one egress simultaneously. Fan-in is the killer: 16 hosts bursting at line rate toward one 100G port = 16× drain rate for a few µs, regardless of average load. AI collectives are barrier-synchronized, so every flow bursts on the same clock edge — the defining stress test, and why shallow-buffer silicon needs aggressive early ECN.
- **Congestion spreading**: PFC is hop-by-hop backpressure — congestion propagates upstream into HOL blocking and congestion trees. A malfunctioning NIC that stops draining can pause an entire fabric (**PFC storm**).
- **Cyclic buffer dependency → deadlock**: PFC means "I won't drop; I pause my upstream." So A's ability to drain depends on B accepting, which depends on C… If that dependency chain forms a **loop**, every buffer in the cycle is full, everyone has sent XOFF, and nobody can drain — permanent standstill; PFC has no timeout. In a clean Clos with strict up/down (valley-free) routing the dependency graph is a DAG — there's always someone who depends on nobody, so it always unwinds. Cycles sneak in through exceptions: reroutes after link failure that bounce traffic back up a tier, ECMP anomalies, leaf-to-leaf east-west paths. Incast is what fills the buffers fast enough to arm the deadlock.

![Three switches pausing each other in a cycle — deadlock — broken by the PFC watchdog](notes/img/fig-pfc-deadlock.svg)

## PFC watchdog

The blunt instrument. Detects a queue paused beyond a threshold (storm or deadlock), then stops honoring pause / drops on that queue — deliberately sacrificing losslessness to break the cycle, then restores after a recovery interval. Complementary mitigations: limit PFC to one or two classes, keep the lossless domain as small as possible, enforce valley-free routing so the lossless priority never rides a path that can re-ascend.

## Aside: why RoCEv2 rides UDP, not TCP

Everything TCP would provide, RoCEv2 already has — in NIC hardware. RoCEv2 = the InfiniBand transport layer wrapped in UDP/IP; that IB transport carries QPs, sequence numbers, ACK/NAK, and retransmission in silicon. TCP on top would mean a redundant state machine and two congestion controllers fighting over one flow. UDP is chosen because it adds *nothing* — the thinnest routable shim over IP.

- **Byte streams break zero-copy.** RDMA's value is direct data placement — each packet self-describes where its payload lands (straight into app/GPU memory). TCP's ordered byte stream forces buffer→reassemble→copy, reintroducing exactly the overhead RDMA eliminates.
- **Hardware implementability.** IB transport was designed for silicon. Full TCP state machines in NICs (TOE) are complex, per-connection stateful, and scale poorly to millions of QPs. The counterexample existed: **iWARP = RDMA over TCP**, and it lost largely for this reason.
- **UDP contributes the one needed thing: ECMP entropy.** Dest port fixed (4791); *source* port varied per flow/QP — the entropy field switches hash on. The fabric load-balances RDMA without parsing IB headers. (Also the knob for multipath tricks: vary source port mid-flow → ECMP re-paths.)
- **Congestion philosophy.** TCP's loss-based CC treats drops as the signal — the opposite of a lossless fabric. RoCEv2 delegates to DCQCN (above). TCP would also drag in handshakes and slow-start — poison for µs-scale barrier-synchronized bursts.

Pattern to remember: UDP appears wherever a protocol has its own transport brain and just needs IP routability — VXLAN, QUIC, and UET all made the same call.

## SONiC side (CONFIG_DB)

The knobs live in: `BUFFER_POOL` (shared pool + shared headroom pool), `BUFFER_PROFILE` (XOFF/XON/headroom, dynamic threshold **alpha**), `BUFFER_PG` (profile → port/PG binding), `WRED_PROFILE` (Kmin/Kmax/Pmax, ECN mode), `QUEUE` (WRED profile → egress queue), `PORT_QOS_MAP` (DSCP/PFC priority mapping), `PFC_WD` (watchdog detect/restore times, action).

## Open questions / to research

- [ ] Headroom values actually deployed per cable class in our fabric vs the calculated minimums
- [ ] PFC watchdog detect/restore timers — vendor defaults vs what storms actually look like
- [ ] How AFD interacts with DCQCN when CloudScale fronts a RoCE fabric (cross-ref C-07)
- [ ] UEC's answer: does spray + smarter retransmit remove the need for PFC entirely?
