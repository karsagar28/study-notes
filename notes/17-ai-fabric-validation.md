# Validating and accepting a new AI fabric

> **Interview scenario:** You have designed and built a GPU training and inference fabric. How do you prove that it meets the customer's technical and performance requirements?

![AI fabric validation workflow](notes/img/fig-ai-fabric-validation.svg)

The short answer is: **validate from the requirement backward, in layers, under realistic load, and with explicit pass/fail criteria.** A link-up check proves basic connectivity; it does not prove application performance, congestion behavior, failure recovery, or repeatability.

## Interview-ready answer (about 90 seconds)

I start by converting the design requirements into a signed acceptance-test matrix. For every requirement—topology, bandwidth, latency, collective performance, training throughput, inference tail latency, resilience, and observability—I define the traffic pattern, measurement method, test scale, and numerical pass/fail threshold.

I then validate in layers. First I prove physical and topology integrity: correct cabling and rail mapping, negotiated speed, FEC, BER, optics, MTU, firmware, and absence of degraded links. Next I validate the control plane and hosts: routing and ECMP, QoS, RoCE settings, RDMA reachability, GPU-to-NIC/NUMA affinity, GPUDirect RDMA, and software consistency.

After that I test performance progressively: point-to-point RDMA latency and bandwidth, all-to-all and bisection bandwidth, then NCCL collectives at node, rack, rail, and full-job scale. The final performance proof is the customer's representative workload. For training I measure step time, tokens per second, collective bandwidth, and scaling efficiency. For inference I measure throughput plus p95/p99 time-to-first-token and inter-token latency under realistic concurrency and bursts.

Finally, I repeat those tests during congestion, component failures, and a burn-in period. I verify ECN/PFC behavior, drops and retransmits, path convergence, workload impact, alerting, and recovery. I accept the fabric only when results meet the thresholds, remain consistent across rails and node groups, and are reproducible. The deliverable includes raw evidence, configurations, a golden baseline, exceptions, dashboards, and operating runbooks.

## The governing principle

```text
requirement → measurable KPI → test method → pass/fail threshold → evidence
```

Avoid accepting on averages alone. AI jobs are synchronized, so one slow link, rail, NIC, or GPU host can become a cluster-wide straggler. Validate **uniformity and variance**, not only peak throughput.

## 1. Build the acceptance matrix before testing

Capture the intended topology and the workloads it must carry:

- GPU/node count, link speeds, number of rails, path diversity, oversubscription, and expected bisection bandwidth
- training parallelism: data, tensor, pipeline, expert, and sequence parallel traffic
- inference modes: single-node, distributed prefill/decode, KV-cache transfer, and mixture-of-experts traffic
- tenant concurrency, storage/checkpoint traffic, management traffic, and maintenance conditions
- clean-fabric, congested, degraded, failed-component, and soak-test states

Thresholds must come from the customer requirement, validated design baseline, vendor reference, or agreed engineering budget—not from an arbitrary universal percentage.

| Requirement | KPI | Test condition | Example acceptance form |
|---|---|---|---|
| Topology | expected links, rails, speed/width | all ports and hosts | zero unexpected or degraded links |
| Point-to-point performance | bandwidth, latency, message rate | representative message sizes and paths | at or above agreed baseline; bounded variance |
| Fabric capacity | bisection bandwidth and fairness | concurrent cross-fabric flows | meets modeled capacity without persistent hot spots |
| Training | NCCL bus/algorithm bandwidth, step time, scaling efficiency | representative job sizes | within agreed target and variance band |
| Inference | tokens/s, TTFT, ITL, p95/p99 | expected concurrency and bursts | SLO sustained without queue collapse |
| Congestion | ECN, PFC, drops, retransmits, queue depth | incast, all-to-all, noisy neighbor | bounded congestion; no uncontrolled pause spreading |
| Resilience | convergence and workload impact | link/NIC/switch/path failure while loaded | recovery within agreed SLO; no persistent black hole |
| Stability | errors, thermals, performance drift | repeated 24–72-hour burn-in or agreed duration | no accumulating errors or material regression |

## 2. Physical, topology, and component validation

Verify the installed fabric matches the low-level design:

- cable and transceiver types, serials, port map, and GPU/NIC rail placement
- link speed, lane width, FEC mode, symbol errors, BER, flaps, and optic DOM data
- end-to-end MTU and absence of accidental speed downgrades
- switch, NIC, cable, transceiver, driver, and firmware compatibility
- power, cooling, and temperature behavior under sustained load

For InfiniBand, `ibdiagnet` can validate expected link speed/width and rail-optimized connectivity. For Ethernet, use LLDP/topology data, switch interface/FEC/BER counters, cable validation, and the platform's fabric-health tooling. A topology check should detect a correctly operating cable placed on the **wrong rail**, not merely a disconnected cable.

## 3. Control plane, QoS, and endpoint readiness

Validate the forwarding system and the GPU hosts together:

- BGP/EVPN or InfiniBand subnet-manager health, routes, ECMP, path diversity, and symmetry
- VLAN/VRF/PKey correctness and tenant isolation
- QoS classification, trust boundary, queue mapping, ETS, ECN, PFC, watchdog, and DCBX consistency
- RDMA connectivity and correct GID/interface selection
- BIOS, PCIe, NUMA, GPU/NIC topology, CPU affinity, and GPUDirect RDMA
- consistent NIC firmware, driver/OFED or DOCA, CUDA, container, and NCCL versions
- Kubernetes Network Operator, SR-IOV, device plug-ins, and IP pools when used

This stage prevents blaming the switches for a host placement, affinity, software-version, or container configuration defect.

## 4. Synthetic network tests

Test progressively so failures remain diagnosable:

1. one link and one node pair
2. each rail and representative same-rack/cross-rack paths
3. many concurrent pairs
4. cross-section or bisection load
5. expected oversubscription boundaries
6. all-to-all, incast, elephant/mice mixes, and storage coexistence

Use TCP tools only as a TCP baseline. For the AI data path, use RDMA-aware tests such as the perftest bandwidth/latency family and GPU-memory-aware tests where available. Sweep small and large messages because a fabric can have acceptable bulk bandwidth but poor small-message latency or message rate.

Measure:

- throughput, latency distribution, message rate, and CPU utilization
- path and rail balance, fairness, and variance between node groups
- queue occupancy, ECN marks, PFC pause duration, drops, retransmissions, and error counters
- achieved bisection bandwidth versus the design model

## 5. GPU collective tests

Run `nccl-tests` across increasing failure domains and job sizes:

- `all_reduce_perf` for the common synchronized training pattern
- all-gather and reduce-scatter for sharded/tensor-parallel behavior
- all-to-all for expert-parallel and MoE traffic
- broadcast or point-to-point patterns where the workload needs them

Sweep message sizes, channels, ranks, GPU counts, node placements, and rails. Record algorithm bandwidth, bus bandwidth, latency, error-free completion, and run-to-run variance. Compare multiple hardware groups: repeatable underperformance in one rail, rack, switch path, or host group is an actionable signal.

NVIDIA's ClusterKit also exposes latency/bandwidth, effective and bisection bandwidth, ring/random-ring, collective, NCCL, and stress tests. NCCL proves that the full GPU-to-GPU path works; it does not replace the customer workload.

### Where GDRCopy, HPL, and LLM tests fit

These tests are complementary: each exercises a different part of the system and none replaces NCCL or network-level testing.

| Test | What it proves | What it does **not** prove | Best use in acceptance |
|---|---|---|---|
| **GDRCopy** | low-overhead, CPU-driven reads/writes to mapped GPU memory; small-copy latency; BAR1/PCIe/NUMA behavior | fabric bandwidth, RDMA NIC-to-GPU performance, or general bulk CUDA-copy performance | compare every GPU/CPU/NUMA placement; detect asymmetric or mis-affined host-to-GPU paths |
| **nvbandwidth / DCGM PCIe test** | bulk CPU↔GPU and GPU↔GPU copy bandwidth, latency, PCIe/NVLink path health, and peer-to-peer correctness | application collectives or end-to-end network performance | establish the node-local data-movement baseline before blaming the fabric |
| **HPL** | sustained GPU compute, memory, power/thermal stability, MPI/NCCL/NVSHMEM communication, and multi-node consistency | LLM traffic shape, collective-specific limits, or inference tail latency | burn-in and system-level straggler detection; compare identical node groups |
| **HPL-MxP / HPL-AI-style test** | mixed-precision compute and refinement at high sustained utilization | a real transformer workload or its communication schedule | additional AI-era compute/system stress, especially for newer GPU platforms |
| **LLM training workload** | real framework, model parallelism, optimizer, memory pressure, communication overlap, and checkpoint behavior | standardized comparison unless the workload/configuration is controlled | final training acceptance using the customer's model or a representative NeMo/Megatron workload |
| **LLM inference load test** | serving throughput and TTFT/ITL/e2e tail latency under concurrency, request rate, and sequence-length distributions | training scaling or raw fabric isolation | final inference SLO validation using NVIDIA AIPerf and the intended serving stack |
| **MLPerf** | reproducible, standardized system comparison under published rules | the customer's exact topology, model, traffic distribution, or SLO | external reference point; supplement rather than replace workload acceptance |

#### GDRCopy nuance

GDRCopy should not be described simply as a generic “CPU-to-GPU bandwidth test.” It maps GPU memory into CPU user space using GPUDirect RDMA mechanisms, allowing the CPU to drive very low-overhead copies. Its included tests measure copy bandwidth, copy latency, API latency, and CPU/GPU ping-pong latency.

The path is naturally asymmetric: CPU writes into GPU memory can benefit from write combining, while CPU reads from GPU memory are typically much slower. Therefore:

- sweep small buffer sizes where launch/copy overhead dominates
- test host-to-device and device-to-host directions separately
- pin the process to the CPU/NUMA node local to each GPU and compare against remote placement
- treat abnormal variance as evidence of PCIe topology, BAR1, NUMA affinity, BIOS, driver, or platform configuration issues
- use `nvbandwidth` or the DCGM PCIe plugin for broader bulk-copy and peer-to-peer path validation

GDRCopy validates an **endpoint data path**, not the scale-out network. GPUDirect RDMA must still be tested with NIC-to-GPU RDMA/perftest, NCCL, and the real workload.

#### HPL nuance

HPL is valuable because it sustains compute, memory, power, cooling, and multi-node communication together. NVIDIA explicitly lists HPL as a math-intensive application with network communication in its SuperPOD health guidance. Run single-node first, then multiple node groups and the intended scale; compare achieved performance, runtime variance, thermals, corrected errors, and node/rail counters.

Do not use HPL as the sole network acceptance benchmark. A strong HPL result can hide collective, incast, all-to-all, or small-message weaknesses that affect AI workloads. Pair it with NCCL, bisection tests, congestion tests, and an LLM job.

#### LLM training and inference tests

For **training**, run a controlled NeMo/Megatron or customer framework job with the intended data/tensor/pipeline/expert parallelism. Fix the model, precision, sequence length, global batch, optimizer, checkpoint interval, dataset path, and GPU count. Record:

- tokens per second and per-GPU throughput
- step-time median, p95, and variance
- model FLOP utilization when available
- time spent in collectives and communication overlap
- scaling efficiency across node counts
- checkpoint interference, loss behavior, retries, and hardware/software errors

For **inference**, NVIDIA's current NIM benchmarking guidance uses **AIPerf**; current Triton documentation marks GenAI-Perf as deprecated in favor of AIPerf. Sweep concurrency, request rate, input length, output length, and realistic prompt distributions. Measure TTFT, ITL, end-to-end latency, tokens/s, requests/s, and p95/p99 while also collecting GPU utilization, KV-cache pressure, queue time, network telemetry, and errors.

Run LLM tests in at least four states: isolated baseline, expected production load, burst/overload, and degraded fabric. This connects fabric behavior to the customer-visible outcome.

## 6. Prove the customer's workload

### Training fabric

Use a representative model, framework, precision, batch size, dataset path, checkpoint behavior, and parallelism strategy. Measure:

- step time and its variance
- samples or tokens per second
- scaling efficiency from a smaller known-good baseline
- collective time and computation/communication overlap
- checkpoint and storage interference
- time-to-train or time-to-target-quality when practical

### Inference fabric

Test steady load and bursts, not just maximum throughput. Measure:

- requests and tokens per second
- time to first token (TTFT)
- inter-token latency (ITL)
- p50, p95, and p99 latency
- queueing and admission behavior at increasing concurrency
- distributed prefill/decode, KV-cache transfer, expert routing, and cache locality when applicable

The distinction matters: training acceptance is usually dominated by collective bandwidth, scaling, and straggler behavior; inference acceptance is often dominated by tail latency and SLO stability under concurrency.

## 7. Congestion and multi-tenant validation

Run the workload while deliberately introducing:

- incast and all-to-all traffic
- a noisy tenant or background elephant flows
- simultaneous checkpoint/storage traffic
- bursty inference arrivals
- asymmetric or reduced path capacity

Validate ECN thresholds, congestion-control response, PFC pause scope/duration, watchdog behavior, adaptive routing where used, and QoS fairness. Look for head-of-line blocking, pause spreading, unfair flows, persistent hot spots, or starvation of non-lossless classes.

On NVIDIA Ethernet, NetQ's What Just Happened telemetry can provide contextual reasons for hardware drops, including congestion, routing, ACL, and layer-1 causes. On InfiniBand, UFM fabric-health and validation capabilities can correlate topology, port health, errors, and failures.

## 8. Failure and recovery testing

Inject faults **while the fabric is carrying a representative load**:

- server link, rail, NIC port, leaf uplink, and spine path loss
- route withdrawal or control-plane restart
- switch or subnet-manager failover where the design promises it
- degraded optic, rising BER, or link flap
- node/process loss and maintenance drain
- configuration drift such as MTU or QoS mismatch in a controlled test

Measure detection time, convergence, packet/workload impact, retry behavior, checkpoint/restart behavior, inference SLO impact, alarm generation, and return to normal. Confirm there is no persistent black hole or silent capacity loss.

## 9. Soak, evidence, and operational handoff

Repeat NCCL, system stress, and representative application tests for the customer-agreed burn-in period. Trend thermals, BER, FEC corrections, link flaps, queue counters, errors, throughput, latency, and variance. A one-time peak result is not a production baseline.

The acceptance package should contain:

- requirement-to-test traceability matrix and signed results
- as-built topology, cabling/rail map, configurations, and firmware/software versions
- commands, raw outputs, workload parameters, dashboards, and timestamps
- deviations, root causes, remediations, and accepted exceptions
- a **golden baseline** for future regression comparisons
- monitoring thresholds, alert tests, rollback procedures, and runbooks

## Common interview traps

| Weak answer | What is missing |
|---|---|
| “Ping every host and run iperf.” | RDMA/GPU path, collective scale, congestion, workload, and resilience |
| “Run NCCL once at full scale.” | Layered isolation, repeatability, variance, and root-cause evidence |
| “The average bandwidth met the target.” | stragglers, rail imbalance, hot spots, and tail latency |
| “Pull a cable to test redundancy.” | failure under load, convergence timing, workload/SLO impact, and alerting |
| “Use vendor benchmarks.” | the customer's real traffic matrix and application success criteria |

## Follow-up questions an interviewer may ask

1. How would you calculate expected bisection bandwidth and define an acceptable result?
2. Which NCCL collectives best approximate data, tensor, pipeline, and expert parallelism?
3. How would you distinguish a network bottleneck from GPU, PCIe, NUMA, storage, or application issues?
4. Which counters would prove that ECN is controlling congestion before PFC dominates?
5. How would the test plan change for a latency-sensitive inference fabric?
6. How would you validate rail optimization and GPU-to-NIC affinity?
7. What evidence would you require before signing customer acceptance?

## Sources

- NVIDIA, [DGX SuperPOD: System Health](https://docs.nvidia.com/dgx-superpod/administration-guide-dgx-superpod/latest/system-health.html) — recommends consistent nodes, single- and multi-node tests, NCCL/HPL, repetition across hardware groups, and customer applications.
- NVIDIA, [DGX Explained: Network Operator Validation](https://docs.nvidia.com/dgx-superpod/dgx-explained/network-operator/latest/validation.html) — validates policy/SR-IOV readiness and multi-node NCCL connectivity.
- NVIDIA, [HPC-X ClusterKit](https://docs.nvidia.com/networking/display/hpcxv2221/clusterkit) — latency, bandwidth, bisection, collectives, NCCL, and stress capabilities.
- NVIDIA, [ibdiagnet Fabric Links Validation](https://docs.nvidia.com/networking/display/ibdiagnetutilityv2240/fabric-links-validation) — expected speed/width and degraded-link validation.
- NVIDIA, [UFM Fabric Validation Tests API](https://docs.nvidia.com/networking/display/ufmenterpriserestapiv6241/fabric-validation-tests-rest-api) — topology, routing, link, partition, temperature, and fabric checks.
- NVIDIA, [NetQ What Just Happened](https://docs.nvidia.com/networking-ethernet-software/cumulus-netq-49/Manage-Events-and-Notifications/Monitor-WJH-Events/) — contextual telemetry for hardware packet drops.
- NVIDIA, [GDRCopy](https://github.com/NVIDIA/gdrcopy) — CPU mappings of GPU memory and small-copy bandwidth/latency test utilities.
- NVIDIA, [nvbandwidth](https://github.com/NVIDIA/nvbandwidth) — CPU/GPU and GPU/GPU copy-path bandwidth measurements.
- NVIDIA, [HPL Benchmark](https://docs.nvidia.com/nvidia-hpc-benchmarks/HPL_benchmark.html) — GPU affinity, communication backends, and multi-node execution.
- NVIDIA, [NIM LLM Benchmarking Guide](https://docs.nvidia.com/nim/benchmarking/llm/latest/) — AIPerf methodology and LLM latency/throughput metrics.
- NVIDIA, [DCGM Diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html) — PCIe/NVLink, memory, compute, and stress diagnostics.
- MLCommons, [MLPerf Inference](https://docs.mlcommons.org/inference/) — standardized inference workloads and measurement rules.

**Last verified:** 2026-08-14

## Open study tasks

- Build a worked acceptance matrix for a specific 400/800 GbE rail-optimized design.
- Add sample `nccl-tests`, RDMA perftest, NetQ, and switch-counter command sequences.
- Practice calculating theoretical payload bandwidth after encoding/protocol overhead.
- Create separate troubleshooting trees for low NCCL bandwidth and inference p99 regression.
