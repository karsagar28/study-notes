# Training fabrics versus inference fabrics

*Status: reviewed study note*  
*Last updated: August 2026*  
*Last verified: August 2026*

## Why this matters

“AI fabric” is not a complete requirement. Training and inference can use the same
Ethernet technology, but their traffic patterns, success metrics, and acceptable
trade-offs differ. A solutions architect must first identify the model's parallelism,
deployment mode, communication pattern, and service-level objectives (SLOs).

## Thirty-second explanation

Large distributed training normally needs a high-bandwidth, low-variance,
low-oversubscription fabric because GPUs repeatedly enter synchronized collectives.
A congested path or slow rank can delay the whole job. Rail optimization is therefore
a strong default for large training clusters.

Inference is conditional. Independent replicas serving models that fit inside one
server or one NVLink scale-up domain do not need a rail-optimized east-west fabric.
Multi-node tensor, pipeline, or expert-parallel inference can benefit greatly from rail
optimization because it also generates tightly coupled GPU traffic. Disaggregated
prefill/decode adds large KV-cache transfers, but cache-aware routing, topology-aware
placement, load balancing, and SLO control may matter as much as strict rail alignment.

**Interview answer:** inference does not automatically require rail optimization;
distributed inference with substantial, stable cross-node GPU communication usually
benefits from it.

## Decision diagram

![Training and inference fabric rail-optimization decision](notes/img/fig-training-vs-inference-fabric.svg)

Editable source: `diagrams/fig-training-vs-inference-fabric.excalidraw`  
Editable Excalidraw+ scene: https://app.excalidraw.com/s/7Zy4MTUQ2T3/6dMdrRfE0Gx

## The mental model

Start by separating four networks or traffic roles:

1. **Scale-up:** GPU-to-GPU communication inside a server or NVLink domain.
2. **Scale-out / east-west:** GPU communication across compute nodes using RDMA.
3. **North-south / client:** requests, responses, gateways, APIs, and service traffic.
4. **Storage and management:** datasets, checkpoints, model loading, KV-cache tiers,
   provisioning, telemetry, and out-of-band management.

Training is dominated by a coordinated scale-out problem when a job spans nodes.
Inference may be dominated by north-south serving, scale-out collectives, point-to-point
KV transfers, or some mixture of all three.

## Traffic signatures

| Dimension | Distributed training | Production inference |
|---|---|---|
| Primary objective | Minimize time to train; maximize scaling efficiency and GPU utilization | Meet throughput and latency SLOs at an acceptable cost per token/request |
| Common communication | All-reduce, reduce-scatter, all-gather; all-to-all for MoE | Request/response, tensor/pipeline/expert parallel traffic, KV-cache transfer, model and cache access |
| Timing | Repeated, synchronized, often predictable bursts | Bursty and demand-driven; can be continuous, asymmetric, and heterogeneous |
| Failure scope | One slow rank or path can delay a large synchronized job | Usually affects a request or replica, but shared bottlenecks can raise fleet-wide tail latency |
| Network KPI | Effective collective bandwidth, job completion time, rail balance, low jitter | p50/p95/p99 TTFT, inter-token latency, tokens/s, queue time, KV-transfer time |
| Capacity posture | Usually close to nonblocking or deliberately low oversubscription | Right-sized by deployment mode and measured traffic matrix; oversubscription may be acceptable for replica serving |
| Placement | Gang and topology-aware placement of all job ranks | Cache-, SLO-, and topology-aware routing; independent scaling of serving roles |
| Availability | Checkpoint/restart, job resilience, drain unhealthy nodes | Continuous service, redundancy, admission control, load shedding, graceful degradation |

NCCL defines collectives such as all-reduce, all-gather, reduce-scatter, and
all-to-all across GPU ranks. Rank-to-device mapping affects several operations, which
is why placement, NIC affinity, and topology cannot be treated independently.

## Training-fabric design considerations

### 1. Derive the traffic matrix from parallelism

- **Data parallelism:** gradient synchronization, commonly reduce-scatter/all-gather
  or all-reduce.
- **Tensor parallelism:** frequent communication on the execution critical path;
  latency and small-message efficiency become important.
- **Pipeline parallelism:** mainly point-to-point activation transfers between stages;
  stage imbalance can create bubbles.
- **Expert parallelism / MoE:** all-to-all traffic, incast, and uneven expert popularity;
  load balancing and congestion control become critical.

### 2. Protect synchronized progress

Collectives couple the participants. The fabric should minimize variation, not merely
offer a high theoretical line rate. Evaluate effective collective bandwidth, congestion,
packet loss, retransmission/recovery behavior, and tail latency under simultaneous jobs.

### 3. Preserve bandwidth across the topology

Use sufficient bisection bandwidth, low oversubscription, appropriate radix, and as few
tiers as practical. Validate the design at the intended job size—not only with isolated
link tests.

### 4. Match GPUs, NICs, and rails

In a rail-optimized design, corresponding GPU-facing NICs across servers attach to the
same leaf or rail. Communication that follows the rail can remain on a short,
predictable path. NVIDIA's DGX H100 reference architecture describes rail-aligned node
groups in which same-rail traffic is one hop away within a scalable unit; traffic
between rails traverses the spine.

### 5. Engineer congestion behavior

Use ECN/RDMA congestion control, sound PFC boundaries where PFC is required, adaptive
routing or flow-aware load balancing, adequate buffering, and telemetry. Test correlated
incast and all-to-all patterns, not just uniform random traffic.

### 6. Treat storage as a separate performance path

Dataset reads and checkpoint bursts must not unexpectedly contend with collectives.
Capacity-plan the storage fabric, staging/cache tier, and recovery time alongside the
compute fabric.

## Inference-fabric design considerations

### 1. Classify the serving architecture first

| Inference mode | Cross-node GPU traffic | Rail-optimization position |
|---|---:|---|
| Model fits one server or one NVLink domain; independent replicas | Low or none on the scale-out fabric | Usually unnecessary |
| Data-parallel replicas with no cross-replica synchronization on the request path | Low | Usually unnecessary; prioritize north-south capacity and load balancing |
| Multi-node tensor or pipeline parallelism | High and latency-sensitive | Usually beneficial; often recommended |
| Expert-parallel / MoE inference | High, often all-to-all and skewed | Strongly beneficial, plus adaptive routing and congestion control |
| Disaggregated prefill/decode | Potentially large point-to-point KV transfers | Beneficial when endpoints and paths align, but cache-aware routing and topology-aware placement are equally important |
| Mixed multi-tenant inference fleet | Variable and changing | Build rail-aligned performance pods, then schedule suitable workloads into them rather than assuming every request follows one rail |

### 2. Design to the SLO

Training asks, “How fast does the job finish?” Inference asks, “Did each request meet
its latency target?” Track at least:

- **TTFT:** time to first token; affected by queueing, prefill, and request routing.
- **ITL:** inter-token latency; sensitive to decode scheduling and communication on the
  token-generation critical path.
- **Throughput:** tokens/s or requests/s at the required latency percentile.
- **Tail behavior:** p95/p99 latency during bursts, failures, and noisy-neighbor events.

### 3. Preserve data locality

KV-cache location changes the best destination for a request. Routing only to the
least-loaded GPU can cause expensive cache recomputation or transfer. Distributed
inference needs routing that considers queue depth, cache affinity, topology, and SLO.

### 4. Account for disaggregated prefill and decode

Prefill is compute-heavy; decode is commonly memory-bandwidth-sensitive. Separating
them enables independent scaling but creates a KV-cache transfer path. Capacity-plan
that path and the prefill:decode ratio. Otherwise one tier waits while the other queues.

### 5. Separate performance classes

Do not force every inference service onto the most expensive nonblocking fabric.
Create tiers or pods for latency-critical distributed models, throughput-oriented batch
inference, and independent replicas. Apply QoS, admission control, and tenant isolation
so bursty serving traffic does not damage critical GPU communication.

### 6. Engineer for continuous service

Inference usually needs redundant gateways, health-aware routing, rolling upgrades,
rapid failover, capacity headroom, and load shedding. A fabric can have excellent
collective bandwidth and still fail the product requirement if p99 latency collapses
during a node drain or traffic spike.

## Does inference need rail optimization?

**Not by definition.** NVIDIA's NVL72 AI Factory reference architecture marks the GPU
compute east-west network as recommended for training but optional for pure inference.
That is a useful starting point, not permission to ignore the workload.

Use the following test:

1. Does the model and its active KV state fit within one server or scale-up domain?
2. Does one request require GPUs across multiple nodes?
3. Which parallelism dimensions cross the network?
4. Are communicating ranks and NICs stable enough to exploit rails?
5. How much KV-cache traffic moves between prefill, decode, memory, and storage tiers?
6. What bandwidth and latency are required at p99, under burst and failure?

If cross-node communication is sustained, coordinated, and mapped predictably to
GPU/NIC pairs, rail optimization is valuable. If inference is primarily independent
replicas with north-south requests, it adds cost and cabling without solving the main
bottleneck.

## Common design mistakes

| Mistake | Consequence | Better approach |
|---|---|---|
| Reusing the training BOM for every inference service | Excess cost and stranded fabric capacity | Classify serving modes and create performance tiers |
| Assuming “inference is light on networking” | Distributed models miss TTFT/ITL targets | Measure model-parallel and KV-transfer traffic |
| Designing only for average bandwidth | Bursts and incast cause p99 latency spikes | Test burst, skew, failure, and multi-tenant scenarios |
| Rail-aligning hardware but ignoring placement | Traffic crosses rails and spines anyway | Make the scheduler topology- and NIC-aware |
| Least-loaded routing without cache awareness | KV cache is recomputed or moved repeatedly | Combine load, cache locality, and SLO in routing |
| Mixing storage/checkpoint/cache traffic blindly with collectives | Contention creates GPU stalls | Separate fabrics or enforce capacity and QoS boundaries |

## Validation plan

1. Reproduce the intended tensor, pipeline, data, and expert parallel dimensions.
2. Measure NCCL collectives and application-level TTFT/ITL—not only link throughput.
3. Test all-to-all, incast, KV-cache transfer, and simultaneous tenant workloads.
4. Verify each GPU uses the expected NIC and rail; inspect per-port utilization.
5. Introduce a failed link, congested spine, slow node, and rolling node drain.
6. Confirm congestion control, adaptive routing, telemetry, and alerting operate as
   designed.
7. Compare performance per dollar against a less expensive oversubscribed design.

## Interview practice

### Scenario

A customer wants one Ethernet fabric for LLM training and inference and asks whether
all inference nodes must be rail optimized.

### Strong answer

I would not decide from the word “inference.” I would classify the serving modes and
map their traffic. Large training jobs use synchronized collectives, so I would make
rail optimization, low oversubscription, predictable latency, and congestion control
the default for the training performance domain. For inference models contained within
a server or NVLink domain and scaled as independent replicas, the east-west GPU fabric
can be smaller or oversubscribed because north-south capacity, load balancing, and p99
SLOs dominate. For multi-node tensor, pipeline, or expert-parallel inference, I would
use the rail-optimized performance domain. For disaggregated prefill/decode, I would
also model KV-cache transfers and make routing and placement cache- and topology-aware.
I would validate the recommendation with NCCL tests plus real TTFT, ITL, throughput,
burst, and failure measurements.

## Certification checks

1. **Why does rail optimization help distributed training?**
   - It aligns GPU/NIC communication with short, predictable fabric paths and reduces
     unnecessary cross-rail traffic. This improves collective bandwidth consistency.
2. **Is a rail-optimized fabric mandatory for all inference?**
   - No. It depends on whether requests cause significant cross-node GPU traffic.
3. **Which inference modes are most likely to need it?**
   - Multi-node tensor, pipeline, and expert-parallel inference; some disaggregated
     prefill/decode designs also benefit.
4. **What can be more important than rails in disaggregated inference?**
   - KV-cache locality, topology-aware placement, queue-aware routing, correct
     prefill/decode capacity ratios, and TTFT/ITL control.
5. **Why is oversubscription riskier for training?**
   - Large synchronized flows can demand bandwidth concurrently, and a constrained
     path can stall many ranks rather than only one request.

## Customer-facing explanation

Training resembles a synchronized production line: every station must finish before
the next cycle can proceed, so one congested network path slows the whole job.
Inference can resemble either independent checkout lanes or another synchronized
production line. If each request stays in one server, expensive rail optimization adds
little. If one request spans many servers, predictable GPU-to-GPU paths become valuable
again. The right design follows the traffic and the latency promise made to users.

## Confirmed versus inferred

- **Confirmed:** NVIDIA documents rail-optimized RDMA east-west fabrics for efficient
  multi-GPU communication and marks that fabric recommended for training but optional
  for pure inference.
- **Confirmed:** NVIDIA Dynamo documents multi-node inference using model parallelism,
  GPUDirect RDMA, and rapid KV-cache transfer between prefill and decode workers.
- **Inferred design guidance:** strict rail optimization is most valuable when inference
  has stable, heavy cross-node rank communication. Dynamic disaggregated systems may
  gain more from topology/cache-aware scheduling combined with rail-aligned pods than
  from treating the entire inference fleet as one fixed rail topology.

## Sources

- [NVIDIA NVL72 AI Factory — Network Logical Architecture](https://docs.nvidia.com/enterprise-reference-architectures/nvl72-ai-factory/latest/network-logical-architecture.html) — accessed 2026-08-14 — fabric roles; rail-optimized RDMA east-west network; training versus pure-inference guidance.
- [NVIDIA DGX SuperPOD H100 Reference Architecture](https://docs.nvidia.com/dgx-superpod/reference-architecture-scalable-infrastructure-h100/latest/_downloads/613ff7a85a665da4c3ff710b46eeec91/TEMD055-RA11333001-DSPH100-ReferenceArch.pdf) — accessed 2026-08-14 — balanced fat tree, rail alignment, hop behavior, and separate compute/storage fabrics.
- [NVIDIA NCCL Collective Operations](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/collectives.html) — accessed 2026-08-14 — collective semantics and rank mapping.
- [NVIDIA Dynamo architecture](https://developer.nvidia.com/blog/introducing-nvidia-dynamo-a-low-latency-distributed-inference-framework-for-scaling-reasoning-ai-models/) — accessed 2026-08-14 — distributed inference, model parallelism, GPUDirect RDMA, KV-cache transfer, and cache-aware routing.
- [Deploying disaggregated LLM inference on Kubernetes](https://developer.nvidia.com/blog/deploying-disaggregated-llm-inference-workloads-on-kubernetes/) — accessed 2026-08-14 — separate TTFT/ITL scaling loops and prefill/decode capacity balance.
- [NVIDIA AI Factory networking infrastructure](https://docs.nvidia.com/ai-enterprise/planning-resource/ai-factory-reference-design-for-government-white-paper/latest/networking-infra.html) — accessed 2026-08-14 — adaptive routing, congestion control, and tail-latency considerations for training and inference.

## Open questions / follow-up labs

- [ ] Build representative NCCL traffic matrices for DP, TP, PP, and EP combinations.
- [ ] Compare p99 TTFT/ITL on rail-aligned and non-rail-aligned placement.
- [ ] Quantify KV-cache transfer bandwidth for several context and output lengths.
- [ ] Define acceptable oversubscription ratios for independent, batch, and distributed inference tiers.
