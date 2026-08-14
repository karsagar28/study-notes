# SONiC & Linux Networking — Interview Field Notes

Revision notes, not a tutorial. Assumes you already know BGP, EVPN/VXLAN, and Clos design — this covers what's *specific* to SONiC and to Linux as a forwarding host.

---

## Part 1 — SONiC

### 1.1 The mental model (say this first in any interview)

> Traditional NOS: Linux **is** the network OS. SONiC: Linux **hosts** the network OS.

SONiC is a Debian base image running a set of Docker containers that talk to each other through a Redis instance. Redis — not a config file, not the kernel — is the source of truth. Every piece of configuration and operational state is a key in a database, and every component is a publisher or subscriber on those keys.

Three consequences that interviewers probe for:

- **No config file to edit.** You write to a database. `config_db.json` is only a boot-time seed and a manual snapshot target.
- **The kernel is not the forwarding source of truth.** Kernel netdevs exist for control-plane punt (BGP peering, LLDP, ARP), but the ASIC is programmed through SAI, not through the kernel FIB.
- **Failure is per-container.** `bgp` can crash and restart without touching `syncd`. This is the whole reason for the microservice split.

### 1.2 The Redis databases

| ID | Database | Contains | Written by |
|---|---|---|---|
| 0 | `APPL_DB` | Application-level intent (ROUTE_TABLE, PORT_TABLE, NEIGH_TABLE) | `*mgrd` daemons, `fpmsyncd` |
| 1 | `ASIC_DB` | SAI object representation of the above | `orchagent` |
| 2 | `COUNTERS_DB` | Port / queue / PG statistics | `syncd` flex counters |
| 3 | `LOGLEVEL_DB` | Per-component log verbosity | CLI |
| 4 | `CONFIG_DB` | User-facing configuration (the running config) | CLI, GCU, gNMI |
| 5 | `FLEX_COUNTER_DB` / `PFC_WD_DB` | Counter polling groups, PFC watchdog | `syncd`, `pfcwd` |
| 6 | `STATE_DB` | Actual operational state ("is the port *really* up") | `*mgrd`, `syncd`, `pmon` |
| 7 | `SNMP_OVERLAY_DB` | SNMP-specific derived data | `snmp` container |

!!! tip "The distinction they're testing"
    `CONFIG_DB` = what you asked for. `APPL_DB` = what the subsystem decided to do about it. `STATE_DB` = what actually happened in hardware. If a port is admin-up in CONFIG_DB but down in STATE_DB, the problem is below the software.

### 1.3 The path a config takes

This is the single most-asked SONiC architecture question. Learn it as a chain:

```
CLI / GCU / gNMI
      ↓
  CONFIG_DB  ─── subscribe ──→  portmgrd / intfmgrd / vlanmgrd / buffermgrd  (in swss)
                                            ↓
                                        APPL_DB
                                            ↓  subscribe
                                      orchagent  (portorch, routeorch, neighorch,
                                            ↓     vxlanorch, bufferorch, aclorch …)
                                        ASIC_DB
                                            ↓  subscribe
                                        syncd
                                            ↓
                                      SAI API  (sai_create_route_entry, …)
                                            ↓
                                    vendor SDK  →  ASIC
```

State returns up the other side into `STATE_DB` and `COUNTERS_DB`.

**Routing is the interesting special case.** FRR (in the `bgp` container) computes routes and would normally program the kernel via netlink. Instead, FRR's **FPM** (Forwarding Plane Manager) interface streams route updates to **`fpmsyncd`**, which writes them into `APPL_DB:ROUTE_TABLE`. From there `routeorch` picks them up and the chain continues. The kernel FIB still gets programmed too, but only so the CPU can originate and receive traffic.

If you remember one sentence: **`fpmsyncd` is the bridge between FRR and the SONiC data plane.**

### 1.4 Container inventory

| Container | Job |
|---|---|
| `database` | The Redis instance. Everything else dies without it. |
| `swss` | Switch State Service — `orchagent` plus the `*mgrd` daemons. The brain. |
| `syncd` | Owns the SAI/SDK connection to the ASIC. The only thing that touches hardware. |
| `bgp` | FRR — `zebra`, `bgpd`, `staticd` — plus `fpmsyncd` and `bgpcfgd` |
| `teamd` | LAG via `libteam` (not the kernel bonding driver) |
| `pmon` | Platform monitor — `xcvrd` (optics), `psud`, `thermalctld`, `ledd`, `fancontrol` |
| `lldp` | `lldpd` + `lldp_syncd` |
| `snmp`, `telemetry`/`gnmi`, `mgmt-framework` | Northbound interfaces |
| `dhcp_relay`, `radv`, `nat`, `sflow`, `macsec` | Feature containers, enabled per-platform |

Host-level (not containerised): `hostcfgd` (applies host config from CONFIG_DB), `caclmgrd` (control-plane ACLs), `procdockerstatsd`.

!!! note "Multi-ASIC platforms"
    On modular chassis (e.g. Cisco 8800), each ASIC gets its **own Linux network namespace** (`asic0`, `asic1`, …) with its own `swss`/`syncd`/`bgp` set and its own Redis DB instance. Internal BGP sessions stitch the namespaces together over the fabric. Commands take `-n asic0`. This is where SONiC knowledge and Linux namespace knowledge intersect — a very common senior-level question.

### 1.5 Configuration management

- **`/etc/sonic/config_db.json`** — boot-time seed. Loaded into `CONFIG_DB` at startup. **Not** updated automatically; `sudo config save` writes the running DB back to it.
- **`config reload`** — reloads from the JSON file, disruptive.
- **`config load_minigraph`** — regenerates config from `minigraph.xml` (the older XML topology description). Blows away manual config. Legacy but still present.
- **GCU — Generic Config Updater** — `sudo config apply-patch patch.json`. Applies an **RFC 6902 JSON patch** to `CONFIG_DB` incrementally, validated against the SONiC YANG models. This is what makes declarative, idempotent, diff-based automation viable without a full reload.
- **YANG models** — `sonic-yang-models` package. Underpins GCU validation and the gNMI/REST northbound.
- **`sonic-cfggen`** — Jinja2 template renderer that reads from the DB or minigraph. The tool underneath most config generation.

!!! warning "The GCU talking point"
    GCU is the strongest thing you can bring to a SONiC automation interview. The framing: *pre-GCU, changing one BGP neighbour meant regenerating and reloading the whole config_db, which is a service-affecting event. GCU turns configuration into a diffable, reviewable, revertible patch — which is what lets you put a fabric config in git and run it through CI.*

### 1.6 Reboot modes

| Mode | Data-plane impact | Mechanism |
|---|---|---|
| **Cold** | Full outage (minutes) | Normal reboot |
| **Fast** | ~25–30s | Control plane restarts, ASIC reprogrammed from scratch, but boot path is shortcut |
| **Warm** | Sub-second, ideally zero | ASIC state preserved; `syncd` restores from `ASIC_DB`, BGP uses **graceful restart**, LACP/LLDP state preserved |

Warm reboot is the marquee hyperscaler feature and a favourite question. The key point: it works because forwarding state lives in the ASIC and in Redis, both of which survive the control-plane restart. Graceful restart on the BGP side stops neighbours from withdrawing routes during the window.

Related: `config warm_restart enable <container>` for per-container warm restart without a full reboot.

### 1.7 Troubleshooting command set

```bash
# State and inventory
show interfaces status
show interfaces transceiver eeprom          # optics
show ip route bgp
show bgp summary
show platform summary
show version
show runningconfiguration all

# The databases directly — knowing these signals real experience
sonic-db-cli CONFIG_DB keys "PORT|*"
sonic-db-cli APPL_DB hgetall "ROUTE_TABLE:10.0.0.0/24"
sonic-db-cli STATE_DB hgetall "PORT_TABLE|Ethernet0"
sonic-db-cli COUNTERS_DB keys "COUNTERS:*"

# Containers
docker ps
docker exec -it bgp vtysh                    # drop into FRR
docker logs swss

# Counters
portstat -i Ethernet0
show queue counters
show priority-group drop counters            # PFC / lossless debugging
show pfc counters

# The big hammer
show techsupport
```

**Debug methodology to articulate:** walk the chain. Config present in `CONFIG_DB`? Did it reach `APPL_DB`? Did `orchagent` translate it into `ASIC_DB`? Did `syncd` log a SAI failure? Each gap points at a different component. That layered-bisection answer is what separates someone who has operated SONiC from someone who has read about it.

### 1.8 Honest weaknesses (have these ready — they're a maturity signal)

- **No transactional config.** There is no `commit`/`rollback` equivalent to IOS-XR or Junos. GCU narrows the gap but doesn't close it.
- **MCLAG is weaker than vendor NOS equivalents.** Community MCLAG lags behind; many designs sidestep it with EVPN multihoming (ESI-LAG) instead.
- **Fragmentation.** Community SONiC vs Broadcom Enterprise SONiC vs Dell vs Cisco vs NVIDIA "pure SONiC" — feature sets and CLI surfaces diverge, and vendor branches don't always upstream.
- **Upgrade discipline is on you.** Release branches (e.g. `202411`, `202505`) move fast; there's no vendor holding your hand on the community track.
- **Troubleshooting requires Linux fluency.** No `show tech` narrative walking you through it — you need to reason about containers, Redis, and netlink.

---

## Part 2 — Linux Networking

Everything here is fair game because SONiC is Debian and because interviewers use it to check whether you actually understand the substrate.

### 2.1 Interfaces and the iproute2 surface

`ifconfig`/`route`/`netstat` are deprecated (net-tools). Use `iproute2`:

```bash
ip link show                      # L2 / device state
ip addr show                      # L3 addressing
ip route show                     # main routing table
ip -br -c link show               # brief + colour, fastest scan
ip neigh show                     # ARP / ND cache
ss -tulpn                         # sockets (replaces netstat)
ethtool -S eth0                   # driver-level counters
ethtool -m eth0                   # transceiver info
```

### 2.2 Network namespaces

A namespace is an isolated copy of the entire network stack — its own interfaces, routing tables, ARP cache, iptables rules.

```bash
ip netns add red
ip link add veth0 type veth peer name veth1
ip link set veth1 netns red
ip netns exec red ip addr add 10.0.0.2/24 dev veth1
ip netns exec red ip link set veth1 up
```

**Why it matters here:** containers are namespaces; multi-ASIC SONiC uses namespaces per ASIC; VRF and namespaces are frequently confused in interviews (see below).

### 2.3 VRF vs namespace — a classic trap

| | Namespace | VRF (`l3mdev`) |
|---|---|---|
| Isolates | The whole network stack | L3 routing only |
| Shares | Nothing | Kernel, sockets, netfilter, L2 |
| Use case | Multi-tenant process isolation, multi-ASIC | Multi-tenant routing on one control plane |

```bash
ip link add vrf-red type vrf table 100
ip link set vrf-red up
ip link set eth1 master vrf-red
ip route show vrf vrf-red
```

SONiC uses VRFs for tenant separation and a namespace (`mgmt`) for the management interface — a neat example of both, and a good answer to give.

### 2.4 Bridging and VLANs

```bash
ip link add br0 type bridge vlan_filtering 1     # VLAN-aware bridge
ip link set eth1 master br0
bridge vlan add vid 100 dev eth1
bridge fdb show
bridge link show
```

The **VLAN-aware bridge** (one bridge, `vlan_filtering 1`, per-port VLAN membership) replaced the old model of one bridge per VLAN. Cumulus made this mainstream; it's the Linux-native equivalent of a trunk port.

### 2.5 VXLAN in the kernel

```bash
ip link add vxlan100 type vxlan id 100 dstport 4789 local 10.1.1.1 nolearning
ip link set vxlan100 master br0
bridge fdb append 00:00:00:00:00:00 dev vxlan100 dst 10.1.1.2
```

`nolearning` + FRR programming the FDB is how EVPN control-plane learning replaces flood-and-learn. In SONiC this is handled by `vxlanorch` writing to the ASIC rather than by the kernel VXLAN driver, but the model is the same.

### 2.6 Policy routing

```bash
ip rule add from 192.168.1.0/24 table 100 priority 100
ip rule show
ip route add default via 10.0.0.1 table 100
```

Rules are evaluated by priority; each points at a routing table. This is the mechanism VRF is built on top of.

### 2.7 Netlink, and why it matters

Netlink is the kernel↔userspace socket API for network configuration. `iproute2`, FRR's `zebra`, and `systemd-networkd` are all netlink clients. When someone asks "how does FRR program routes," the answer is netlink — and then in SONiC the interesting part is that it *also* streams them out via FPM to `fpmsyncd`.

### 2.8 switchdev vs SAI — the disaggregation fork

Two philosophies for getting kernel state into an ASIC:

- **switchdev** — kernel-native. Front-panel ports are real netdevs; the kernel FIB, FDB, and bridge state are offloaded to hardware by the driver. Cumulus and mlxsw take this path.
- **SAI** — vendor-neutral C API below a userspace agent. The kernel is bypassed for forwarding. SONiC takes this path.

Being able to contrast these cleanly is a strong senior-level answer, especially if you've been asked about Cumulus vs SONiC.

### 2.9 Packet path and tooling

```bash
tcpdump -i Ethernet0 -nn -e            # capture (CPU-punted traffic only, on a switch)
tc qdisc show dev eth0                 # queueing discipline
nft list ruleset                       # nftables (iptables successor)
conntrack -L                           # connection tracking table
```

!!! warning "Capture caveat on a switch"
    `tcpdump` on a SONiC front-panel port only sees traffic punted to the CPU. Hardware-forwarded traffic never reaches the kernel. If you claim otherwise in an interview it's an immediate tell. For data-plane visibility you need ACL mirroring (ERSPAN/SPAN), sFlow, or `show` counters.

---

## Part 3 — Likely questions, condensed answers

1. **What is SONiC and how does it differ from a traditional NOS?**
   Containerised, DB-driven, SAI-abstracted, multi-vendor, community-governed. Redis is the source of truth; the ASIC is programmed via SAI, not via the kernel.

2. **Walk me through what happens when I configure an IP on an interface.**
   The chain in §1.3. Name `intfmgrd`, `APPL_DB`, `orchagent`, `ASIC_DB`, `syncd`, SAI.

3. **What is SAI and why does it exist?**
   A standard C API for switch ASIC functions. It decouples the NOS from the silicon, so one SONiC image supports Broadcom, Silicon One, Marvell, and Spectrum with only a vendor SAI library and SDK swapped underneath.

4. **How does routing work in SONiC?**
   FRR computes; FPM → `fpmsyncd` → `APPL_DB` → `routeorch` → `ASIC_DB` → `syncd` → SAI.

5. **How is configuration persisted?**
   It isn't, automatically. Running config lives in Redis; `config save` writes `config_db.json`.

6. **What's the difference between fast and warm reboot?**
   §1.6. Warm preserves ASIC state and uses BGP graceful restart.

7. **How would you automate SONiC config at fabric scale?**
   Templates rendered from a source-of-truth inventory, diffed into RFC 6902 patches, validated against YANG, applied with `config apply-patch`, verified by pre/post state comparison in CI.

8. **A port is down. Walk me through the debug.**
   `show interfaces status` → `STATE_DB` vs `CONFIG_DB` → `xcvrd`/optics via `show interfaces transceiver` → `syncd` logs for SAI errors → physical.

9. **How do you do lossless Ethernet for RDMA on SONiC?**
   PFC on the priority carrying RoCEv2, ECN marking with WRED thresholds on the queue, PFC watchdog to catch stuck queues, buffer profiles sized per port speed. `show pfc counters`, `show priority-group drop counters`.

10. **What don't you like about SONiC?**
    §1.8. Answer it honestly — the trap is claiming there are no downsides.

11. **Namespace vs VRF?** §2.3.

12. **How does a Linux bridge differ from a hardware switch?**
    The bridge is a software FDB in the kernel, CPU-forwarded. A hardware switch does it in the ASIC at line rate; the kernel bridge is only a model of it unless switchdev offload is in play.

---

## Part 4 — Framing your own experience

If you've built pipeline or fabric automation, lead with the *problem*, not the tooling:

- **The problem:** applying config to a leaf-spine fabric without a service-affecting full reload, and without hand-editing JSON on 12 devices.
- **The approach:** a base + overlay rendering model — common fabric config as a base layer, per-device role and identity as an overlay — producing a target `config_db` state per device.
- **The delivery:** diff target against running, emit an RFC 6902 patch, validate, apply via GCU, verify post-state.
- **The value:** configuration becomes reviewable in a pull request, and a change is revertible as a patch rather than as a reload.

That narrative answers architecture, automation, and operational-risk questions at once — which is usually three interview objectives in one story.

---

## Further reading

- `github.com/sonic-net/SONiC` — `doc/` holds the High Level Design documents (GCU, EVPN, warm reboot each have one)
- `github.com/r12f/sonic-book` — "Getting Started with SONiC," free, the most readable overview available
- `sonic-net.github.io` — CLI and configuration command reference
- `developer.cisco.com/docs/sonic/` — Cisco 8000 SONiC setup and config
- SONiC Foundation YouTube — workshop recordings and weekly community meetings
