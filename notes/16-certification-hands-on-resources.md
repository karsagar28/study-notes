# Certification hands-on resources: NCP-AIN, NCP-AII, and NCP-AIO

*Status: reviewed resource guide*  
*Last updated: September 2026*
*Last verified: August 2026*

## Purpose

This is a practical, cost-conscious route through NVIDIA's professional AI networking,
infrastructure, and operations certifications. The goal is real operating experience
without buying a DGX system.

## Certification names

NVIDIA's current certification catalog separates the tracks as follows:

| Certification | Level | Focus |
|---|---|---|
| NCA-AIIO | Associate | Foundational AI infrastructure and operations concepts |
| NCP-AIN | Professional | AI networking |
| NCP-AII | Professional | Deploying, configuring, and validating AI infrastructure |
| NCP-AIO | Professional | Monitoring, operating, troubleshooting, and optimizing AI infrastructure |

There is no current professional certification named `NCP-AIIO`. The professional
progression covered here is:

```text
NCP-AIN -> NCP-AII -> NCP-AIO
network -> deploy and validate -> operate and troubleshoot
```

For an Ethernet/NVIS solutions-architect path, start with NCP-AIN. NCP-AII adds
deployment and validation depth, while NCP-AIO covers day-two operations and live
troubleshooting.

## Exam overview

| Certification | Current format | Price | Practical emphasis |
|---|---|---:|---|
| NCP-AIN | 70-75 questions, 120 minutes | $400 | Spectrum-X, InfiniBand, RoCE, UFM, NetQ, DSX Air, Kubernetes and automation |
| NCP-AII | 70-75 questions, 120 minutes | $400 | Physical bring-up, BCM, drivers, containers, HPL/NCCL and cluster validation |
| NCP-AIO | 30 questions plus 3 hands-on labs, 120 minutes | $500 | Linux CLI on BCM, Slurm and Kubernetes clusters; workload and fault management |

NVIDIA recommends two to three years of relevant data-center operational experience
for each professional certification. These labs build skill and close access gaps, but
they do not replace production experience.

## Blueprint summary

### NCP-AIN

| Domain | Weight |
|---|---:|
| AI data-center design and optimization | 5% |
| NVIDIA Spectrum networking | 30% |
| NVIDIA InfiniBand networking | 30% |
| Kubernetes integration | 5% |
| Troubleshooting tools | 20% |
| Automation and configuration | 10% |

### NCP-AII

| Domain | Weight |
|---|---:|
| System and server bring-up | 31% |
| Physical-layer management | 5% |
| Control-plane installation and configuration | 19% |
| Cluster testing and verification | 33% |
| Troubleshooting and optimization | 12% |

### NCP-AIO

| Domain | Weight |
|---|---:|
| Installation and deployment | 31% |
| Administration | 23% |
| Workload management | 23% |
| Troubleshooting and optimization | 23% |

## Recommended lab portfolio

No affordable service reproduces a complete NVIDIA AI factory. A better approach is
to combine a few focused environments and reuse them across certifications.

| Environment | Approximate cost | NCP-AIN | NCP-AII | NCP-AIO |
|---|---:|---|---|---|
| NVIDIA DSX Air free trial | $0 | Primary Ethernet lab | Topology/OOB context | Limited |
| Three-node Linux VM cluster | $20-60 | Network Operator basics | BCM, OS, Slurm and containers | Primary Slurm/Kubernetes lab |
| Single GPU cloud VM | $20-75 | Host/RDMA concepts | Drivers, DCGM, NGC, containers and MIG | GPU operations and troubleshooting |
| Short multi-GPU rental | $75-250 | NCCL traffic observation | HPL, NCCL and burn-in | Distributed workload diagnosis |
| NVIDIA self-paced networking courses | $0-400 | InfiniBand, UFM, Cumulus and BlueField | Physical/network gaps | Supporting knowledge |
| Official instructor-led lab | Usually $1,500+ | Spectrum-X/InfiniBand hardware | Physical HGX and BCM gaps | BCM, Run:ai and DPU gaps |

## Lab 1: NVIDIA DSX Air

Use DSX Air as the main NCP-AIN practice environment. The current individual free trial
provides up to 60 concurrent vCPUs, 60 GiB of memory, 10,000 compute-hour credits, and
one year of access. It requires an NGC organization and a business email.

### Build and break these topologies

1. Two-leaf/two-spine CLOS fabric with BGP unnumbered.
2. EVPN/VXLAN with at least two tenants.
3. MLAG and VRR.
4. Separate in-band and out-of-band management paths.
5. Zero-touch provisioning from the OOB management server.
6. RoCE QoS classification and queue mapping.
7. PFC and ECN configuration.
8. NetQ monitoring and validation.
9. NVUE templates and Ansible automation.
10. Intentional BGP, MTU, interface, MLAG and policy failures.

Maintain two saved versions of every lab:

- a known-good baseline
- a deliberately broken troubleshooting scenario

### Limitations

DSX Air covers NOS configuration, architecture, automation, telemetry, and failure
diagnosis well. It cannot reproduce real Spectrum ASIC buffering, physical congestion,
optics, BlueField hardware, or a production InfiniBand subnet.

## Lab 2: three-node Linux cluster

Use inexpensive x86 Ubuntu VMs. Shut them down or delete them between study sessions.

```text
control01    2-4 vCPU    4-8 GB RAM
worker01     2 vCPU      4 GB RAM
worker02     2 vCPU      4 GB RAM
storage01    optional NFS and test storage
```

### Slurm exercises

- Configure MUNGE, `slurmctld`, and `slurmd`.
- Create nodes, partitions, reservations, limits, and fair-share policies.
- Use `srun`, `sbatch`, `squeue`, `sinfo`, `scontrol`, and `sacct` fluently.
- Add SlurmDBD and accounting storage.
- Drain, resume, and remove nodes.
- Diagnose pending, failed, cancelled, and stuck jobs.
- Configure generic resources and understand GPU GRES definitions.
- Add shared NFS storage.
- Install Enroot and Pyxis where practical.
- Run multi-node jobs and introduce DNS, permission, storage, and network failures.

### Kubernetes exercises

- Install a three-node cluster with `kubeadm` or K3s.
- Practice deployments, jobs, services, namespaces, quotas, and RBAC.
- Use labels, taints, affinity, anti-affinity, and topology constraints.
- Install Prometheus and Grafana.
- Deploy containers from NGC.
- Inspect failed pods, image-pull failures, scheduling shortages, and networking errors.
- Read and apply NVIDIA GPU Operator and Network Operator manifests.
- Understand the Network Operator's RDMA and secondary-network resources even when
  the test VMs do not contain RDMA hardware.

## Lab 3: Base Command Manager

BCM is central to NCP-AII and NCP-AIO. NVIDIA currently offers a free BCM license for
environments with up to eight accelerators per system, without support.

```text
bcm-head       4 vCPU    12-16 GB RAM    100 GB disk
compute01      2-4 vCPU  8 GB RAM
compute02      2-4 vCPU  8 GB RAM
private management/provisioning network
```

Prefer a local virtualization platform when possible. BCM node provisioning uses PXE,
DHCP, images, and Layer-2 management behavior that public-cloud VPCs may restrict.

### NCP-AII focus

- Install and activate BCM.
- Define devices, categories, interfaces, and software images.
- Provision nodes and synchronize images.
- Install Slurm and integrate Enroot/Pyxis.
- Configure users, networks, storage, and health checks.
- Understand head-node HA and backup design.

### NCP-AIO focus

- Use Base View and `cmsh` without step-by-step instructions.
- Monitor node health and utilization.
- Patch and update managed images.
- Drain and recover unhealthy nodes.
- Diagnose failed jobs and resource bottlenecks.
- Generate usage and performance reports.
- Practice role, permission, and account administration.

## Lab 4: temporary single-GPU VM

Prepare the commands and expected results before starting the billing clock. A less
expensive L4, A40, A6000, or similar GPU is enough for most host-operations work.
Use an A100 or H100 only when practicing supported MIG workflows.

### Exercises

- Inspect PCI devices, NUMA layout, drivers, and GPU state.
- Use `nvidia-smi` for inventory, processes, clocks, topology, and errors.
- Install or validate NVIDIA Container Toolkit.
- Authenticate to NGC and run a CUDA or PyTorch container.
- Run CUDA samples and framework device validation.
- Install DCGM and run diagnostics.
- Export DCGM metrics to Prometheus.
- Perform GPU stress, memory, temperature, and utilization tests.
- Create deliberate driver/container compatibility failures.
- Configure MIG when the provider exposes a complete supported GPU and grants the
  necessary administrative control.

Container-only GPU services may not provide `systemd`, kernel access, driver control,
or MIG administration. Verify those capabilities before paying.

## Lab 5: multi-GPU and two-node validation bursts

Prepare scripts offline. Rent the systems for a short session, capture the results, and
terminate the resources as soon as the tests finish.

### Single multi-GPU node

- Inspect GPU, PCIe, NUMA, and NVLink topology.
- Run peer-to-peer bandwidth tests.
- Run single-node NCCL collectives.
- Run HPL and GPU burn-in.
- Validate DCGM health and fabric-manager state.
- Measure local and shared-storage throughput.
- Compare native and containerized results.

### Two GPU nodes

- Configure SSH, users, file paths, and shared storage consistently.
- Select intended NCCL network interfaces.
- Run distributed NCCL tests and record E/W bandwidth.
- Compare TCP with RDMA when exposed by the provider.
- Introduce an MTU mismatch, incorrect interface selection, blocked port, slow storage
  path, and failed rank.

Do not assume a managed GPU cluster exposes its InfiniBand subnet manager, UFM, switch
CLI, or physical diagnostic commands. Confirm access before purchasing time.

## Product-specific gaps and best substitutes

| Technology or skill | Cheapest credible practice path |
|---|---|
| Cumulus Linux, NVUE, BGP/EVPN | DSX Air plus Cumulus self-paced courses |
| Spectrum-X QoS, PFC and ECN | DSX Air configuration plus official architecture and congestion-control material |
| NetQ and WJH | DSX Air demos and NetQ course |
| InfiniBand configuration and diagnostics | InfiniBand Essentials, then InfiniBand Network Administration lab/course |
| UFM | NVIDIA UFM self-paced course or Academy lab |
| BlueField and DOCA | BlueField DPU Administration course; LaunchPad/Academy hardware lab when available |
| Kubernetes Network Operator | Three-node Kubernetes lab; real RDMA behavior requires suitable hardware |
| BCM | Free license on a VM lab; official workshop for production-like workflows |
| Slurm | Three-node CPU VM cluster; later add a temporary GPU worker |
| MIG | Full A100/H100 VM with administrative GPU control |
| DCGM and NGC | Short-lived single-GPU VM |
| HPL, NCCL and burn-in | Prepared multi-GPU rental session |
| Run:ai | Official documentation and requested product trial; NVIDIA AI Enterprise's standard trial does not include Run:ai |
| NVSwitch and fabric-manager failures | Multi-GPU HGX rental or official hardware lab |
| Physical FRU replacement, optics and signal quality | Service manuals, CVT/MLXlink courses, employer/partner or Academy hardware lab |

## Targeted NVIDIA learning resources

NVIDIA's current AI Networking learning path lists:

| Resource | Listed price |
|---|---:|
| AI Infrastructure and Operations Fundamentals | $50 |
| Introduction to Networking | Free |
| NVIDIA Cable Validation Tool Fundamentals | Free |
| InfiniBand Essentials | Free |
| InfiniBand Network Administration | $200 |
| Cumulus Linux Essentials | Free |
| Cumulus Linux Administration | $100 |
| Fundamentals of RDMA Programming | Free |
| SONiC Essentials by NVIDIA | Free |
| Data Center Management Made Easy with UFM | $50 |
| NetQ Deployment and Installation | Free |
| BlueField DPU Administration | $50 |

The $1,500 Spectrum-X instructor-led workshop provides official hands-on access. It
makes more sense with employer reimbursement or when it closes a final hardware gap.

## Suggested preparation order

### Phase 1: NCP-AIN

1. Complete the free networking, Cumulus, InfiniBand, RDMA, SONiC, and NetQ courses.
2. Build the DSX Air CLOS, EVPN, QoS, telemetry, and automation labs.
3. Add the paid InfiniBand, UFM, Cumulus Administration, and BlueField courses as
   needed.
4. Practice troubleshooting from symptoms without looking at the solution.

### Phase 2: NCP-AII

1. Write a server bring-up and validation runbook.
2. Build the BCM/Slurm VM cluster.
3. Practice driver, container-toolkit, and NGC deployment.
4. Rent a single GPU for DCGM and host-validation work.
5. Run one prepared multi-GPU validation session for HPL, NCCL, topology, and burn-in.
6. Study the physical tasks that cloud cannot reproduce: BMC, firmware, FRUs, optics,
   cable validation, power, and cooling.

### Phase 3: NCP-AIO

1. Administer Slurm and Kubernetes daily from the CLI.
2. Reuse the BCM environment for monitoring, updates, users, reports, and failures.
3. Add NGC training and inference workloads.
4. Practice GPU, Docker, storage, Magnum IO, and fabric-manager troubleshooting.
5. Request a Run:ai trial or use an official workshop for the proprietary gap.
6. Run timed labs because the exam combines questions and three live exercises in 120
   minutes.

## Expected budget

The following excludes certification exam fees:

| Item | Approximate cost |
|---|---:|
| DSX Air | $0 |
| CPU VM cluster | $20-60 |
| Basic GPU practice | $20-75 |
| Multi-GPU validation sessions | $75-250 |
| Targeted NCP-AIN courses | $200-450 |
| BCM and related learning | $50-150 |
| Total | Approximately $365-985 |

Exam fees currently add $400 for NCP-AIN, $400 for NCP-AII, and $500 for NCP-AIO.

## Cost-control checklist

- [ ] Prepare commands, containers, datasets, and expected outputs before starting a
  paid GPU instance.
- [ ] Use spending alerts and quotas.
- [ ] Terminate compute rather than merely disconnecting from it.
- [ ] Delete chargeable disks, snapshots, public IPs, and managed filesystems when done.
- [ ] Capture command output and screenshots before destroying the lab.
- [ ] Keep reusable Terraform, Ansible, Kubernetes, and Slurm configuration in a
  private lab repository.
- [ ] Confirm root, driver, RDMA, MIG, and multi-node privileges before renting.
- [ ] Prefer official course labs over expensive cloud hardware when management-plane
  access is hidden by the provider.

## Sources

- [NVIDIA NCP-AIN certification and blueprint](https://www.nvidia.com/en-us/learn/certification/ai-networking-professional/) — accessed 2026-08-14.
- [NVIDIA NCP-AII certification and blueprint](https://www.nvidia.com/en-us/learn/certification/ai-infrastructure-professional/) — accessed 2026-08-14.
- [NVIDIA NCP-AIO certification and blueprint](https://www.nvidia.com/en-us/learn/certification/ai-operations-professional/) — accessed 2026-08-14.
- [NVIDIA NCA-AIIO certification and blueprint](https://www.nvidia.com/en-gb/learn/certification/ai-infrastructure-operations-associate/) — accessed 2026-08-14.
- [NVIDIA AI Networking learning path](https://www.nvidia.com/en-us/learn/learning-paths/ai-networking/) — accessed 2026-08-14.
- [NVIDIA DSX Air account setup and free trial](https://docs.nvidia.com/networking-ethernet-software/nvidia-air-v2/Account-Setup/) — accessed 2026-08-14.
- [NVIDIA DSX Air prebuilt demos](https://docs.nvidia.com/networking-ethernet-software/nvidia-air/Pre-Built-Demos/) — accessed 2026-08-14.
- [NVIDIA Base Command Manager resources and free license](https://docs.nvidia.com/dgx-resources/index.html) — accessed 2026-08-14.
- [NVIDIA AI Enterprise trial and Run:ai note](https://www.nvidia.com/en-us/data-center/products/ai-enterprise/) — accessed 2026-08-14.
- [RunPod GPU pricing](https://www.runpod.io/pricing) — accessed 2026-08-14 — example short-term GPU pricing; verify at purchase time.
- [Lambda GPU instances](https://lambda.ai/instances) — accessed 2026-08-14 — alternative full-VM GPU access; verify capabilities and price at purchase time.

## Open questions / to verify before spending

- [ ] Does the selected GPU provider expose a full VM or only a container?
- [ ] Can the selected A100/H100 instance change MIG mode?
- [ ] Does a multi-node offering expose RDMA devices and standard InfiniBand tools?
- [ ] Does the NVIDIA self-paced course currently include a persistent or temporary
  hands-on environment?
- [ ] Is an employer, NVIDIA partner, conference, or Academy promotion offering lab or
  exam vouchers?
