# OpenShift Virtualization Cookbook -- Current Roadmap

> Covers 105 open, unassigned issues spread across four quarters from Q2 2026 through Q1 2027.

Contributions are welcome -- feel free to open new issues for topics you'd like to see covered, or comment on any existing open issue to request that it be prioritized.

## Design Principles

1. **Oldest first** -- Issues open since January-March 2026 get priority in the earliest quarter that matches their topic area.
2. **Dependencies flow downhill** -- Getting Started content must exist before Deep Dives can reference it as a prerequisite. Networking and storage tutorials must exist before migration and operations tutorials can link to them.
3. **Quick wins build momentum** -- The 32 "good first issue" improvements are spread across Q2-Q4, making each quarter productive from day one.
4. **Deep dives are last by design** -- They are the most expensive to write (5000+ words, extensive testing), benefit from all standard tutorials existing first, and by then CI and style conventions will be fully battle-tested.
5. **Module cohesion** -- Issues in the same module are grouped in the same quarter so contributors can batch-produce similar work efficiently.

## Summary

| Quarter | Theme | Issues | Effort Profile |
|---|---|---|---|
| **Q2 2026** | Foundation, Quick Wins, Tech Debt | 17 | Small items, fast turnaround |
| **Q3 2026** | Core Networking and Storage | 27 | Mix of improvements and standard tutorials |
| **Q4 2026** | VM Ops, Migration, Monitoring | 28 | Intermediate tutorials and operations |
| **Q1 2027** | Deep Dives and Advanced | 33 | Large, reference-grade content |

---

## Q2 2026 (Current Quarter: May -- June)

**Theme: Foundation, Quick Wins, and Technical Debt**

Clear the backlog of oldest issues, do the housekeeping that unblocks everything else, and knock out the "good first issue" improvements that polish existing content quickly. These improvements also serve as templates for future contributors.

### Housekeeping and Infrastructure (5 issues)

| # | Title | Rationale |
|---|---|---|
| 75 | Update README and add standard project files | Oldest good-first-issue; makes the project welcoming |
| 83 | Add CI pipeline with GitHub Actions for tutorial tests | Enables automated quality gates for all future work |
| 146 | Project-wide formatting and style cleanup from CI review linter | Clean slate before adding 90+ new pages |
| 141 | Real-Time VMs tutorial: add guest RT kernel image variant | Fix to existing content, quick patch |
| 20 | [Feature]: How to connect to Windows VM via SSH | Old issue, small scope, complements existing Windows tutorial |

### Getting Started Improvements (5 issues)

| # | Title |
|---|---|
| 210 | Add learning path diagram to Getting Started index |
| 209 | Add state machine diagram to VM Lifecycle States tutorial |
| 208 | Add resource flow diagram to Create VM from Web Console tutorial |
| 207 | Add architecture diagram to Install OpenShift Virtualization tutorial |
| 206 | Tutorial: OpenShift Virtualization Architecture Overview |

### Getting Started Tutorials (4 issues)

| # | Title |
|---|---|
| 202 | Quick Start: Your First VM in 5 Minutes |
| 203 | Creating a VM from CLI Using YAML Manifests |
| 204 | Installing and Configuring the QEMU Guest Agent |
| 205 | Cloud-init Fundamentals for OpenShift Virtualization VMs |

### Oldest Pending Tutorials (3 issues)

| # | Title |
|---|---|
| 11 | Storage Profiles for OpenShift Virtualization |
| 46 | Deploying Windows VMs with VirtIO Drivers |
| 86 | Transferring files to and from VMs |

**Q2 Total: 17 issues**

---

## Q3 2026 (July -- September)

**Theme: Core Networking and Storage Content**

With the foundation polished in Q2, the project fills out its two most critical technical modules: networking and storage. These are the topics users ask about most when adopting OpenShift Virtualization. The improvement issues add diagrams to existing pages (low effort), while the new tutorials fill major content gaps.

### Networking Improvements (8 issues)

| # | Title |
|---|---|
| 177 | Add master topology decision diagram to networking index |
| 178 | Add topology diagram to UDN Primary Networks tutorial |
| 179 | Add topology diagram to Localnet Secondary (CUDN) tutorial |
| 180 | Add topology diagram to Localnet VLAN (NAD) tutorial |
| 181 | Add topology diagram to Localnet VLAN (CUDN) tutorial |
| 182 | Add topology diagram to Layer 2 Secondary Networks tutorial |
| 183 | Add topology diagram to Linux Bridges tutorial |
| 184 | Add topology diagram to VM Ingress Routes tutorial |

### New Networking Tutorials (7 issues)

| # | Title |
|---|---|
| 171 | Network Policies for Virtual Machines |
| 172 | Dual-Stack IPv4/IPv6 Networking for VMs |
| 173 | Network Interface Hotplugging for Running VMs |
| 174 | VM-to-VM and VM-to-Pod Communication Patterns |
| 175 | Network Mapping for VMware-to-OpenShift Migration |
| 176 | MetalLB and Load Balancer Services for VM Workloads |
| 215 | Network Performance Tuning for Virtual Machines |

### Storage Improvements (5 issues)

| # | Title |
|---|---|
| 196 | Add storage decision diagram to storage index page |
| 197 | Add architecture diagram to LVM Operator tutorial |
| 198 | Add architecture diagram to HostPath Provisioner tutorial |
| 199 | Add storage tiering diagram to Multi-Disk VM Configuration tutorial |
| 200 | Add provisioning flow diagram to Storage Classes tutorial |

### New Storage Tutorials (7 issues)

| # | Title |
|---|---|
| 190 | ODF/Ceph Storage for Virtual Machines |
| 191 | NFS Storage for Virtual Machine Workloads |
| 192 | Expanding VM Disk Size (PVC Volume Expansion) |
| 193 | VM Disk I/O Performance Tuning |
| 194 | CDI Operations: DataVolumes, Imports, and Upload |
| 195 | Storage Requirements for VM Live Migration |
| 201 | Thin vs Thick Provisioning for VM Disks |

**Q3 Total: 27 issues**

---

## Q4 2026 (October -- December)

**Theme: VM Configuration, Lifecycle, Migration, and Operations**

With networking and storage complete, the focus shifts to operational topics that production users need: VM lifecycle management, scheduling, migration, monitoring, and the remaining intermediate-level tutorials from the original backlog. This quarter also delivers the VMware migration path -- a high-demand topic.

### VM Configuration and Lifecycle Improvements (9 issues)

| # | Title |
|---|---|
| 216 | Add topology diagram to Internal DNS for VMs tutorial |
| 217 | Add access method decision diagram to Remote Access Linux VMs tutorial |
| 218 | Add network topology diagram to Remote Access Windows VMs tutorial |
| 219 | Add cluster topology diagram to Node Placement and Affinity tutorial |
| 220 | Add before/after diagram to Hotplug Volumes and Interfaces tutorial |
| 224 | Add import method flow diagram to Import qcow2 tutorial |
| 225 | Add pipeline diagram to Custom Golden Images tutorial |
| 226 | Add cloning method comparison diagram to Cloning VMs tutorial |
| 227 | Add snapshot timeline diagram to VM Snapshots tutorial |

### Performance Improvements (5 issues)

| # | Title |
|---|---|
| 232 | Add QoS tier diagram to Resource Limits and QoS tutorial |
| 233 | Add core assignment diagram to CPU Pinning tutorial |
| 234 | Add NUMA topology diagram to NUMA and Hugepages tutorial |
| 235 | Add latency stack diagram to Real-Time VMs tutorial |
| 236 | Add progression diagram to Performance module index |

### Intermediate Tutorials from Original Backlog (5 issues)

| # | Title |
|---|---|
| 50 | Live Migration of VMs Between Cluster Nodes |
| 51 | Migrating VMs from VMware vSphere Using MTV |
| 56 | VM Monitoring and Metrics |
| 58 | VM Scheduling with Tolerations and Taints |
| 14 | GPU Configuration for Virtual Machines |

### Operations and Automation Tutorials (6 issues)

| # | Title |
|---|---|
| 157 | Day-0 IaC: Provisioning OpenShift Virtualization with Ansible |
| 158 | Automating Post-Migration Validation with Ansible |
| 159 | Zero-Downtime Cluster Upgrades Using Live Migration |
| 162 | Multi-Tenancy and RBAC for VM Workloads |
| 165 | Building a VM Self-Service Portal with Templates |
| 166 | Resource Quotas and Chargeback for VM Workloads |

### Additional Operations Content (3 issues)

| # | Title |
|---|---|
| 10 | SR-IOV Secondary Network Configuration for VMs |
| 163 | Comparative Benchmarking vs Legacy Hypervisors |
| 170 | Rolling Hardware Refresh Strategy |

**Q4 Total: 28 issues**

---

## Q1 2027 (January -- March)

**Theme: Deep Dives, Advanced Topics, and Strategic Content**

Deep dives are the most complex content (3000-5000+ words, reference-grade). They require the standard tutorials to exist first so readers have prerequisites, and many of these topics are Advanced-labeled or target niche enterprise audiences. By this point the project's style, structure, and CI pipeline are fully mature.

### Deep Dives -- Getting Started and Configuration (5 issues)

| # | Title |
|---|---|
| 211 | Comprehensive virtctl CLI Reference |
| 212 | OpenShift Virtualization Installation, Configuration, and Day-2 Ops |
| 213 | VM Lifecycle Management and Automation |
| 214 | Cloud-init for OpenShift Virtualization |
| 221 | Secure VM Access Architecture |

### Deep Dives -- VM Lifecycle and Scheduling (6 issues)

| # | Title |
|---|---|
| 222 | Advanced VM Scheduling and Placement |
| 223 | VM Template Governance and Self-Service Catalog |
| 228 | Automated Golden Image Pipeline |
| 229 | VM Snapshot Strategies and Backup Architecture |
| 230 | Advanced Boot Configuration and PXE Automation |
| 231 | VM Export, Import, and Cross-Cluster Mobility |

### Deep Dives -- Networking (5 issues)

| # | Title |
|---|---|
| 185 | User Defined Networks (UDN) for OpenShift Virtualization |
| 186 | Localnet Networking Architecture |
| 187 | Linux Bridge Networking |
| 188 | Exposing VM Services Externally |
| 189 | IP Address Management for VM Fleets at Scale |

### Deep Dives -- Storage and Performance (5 issues)

| # | Title |
|---|---|
| 153 | Choosing the Right Storage Class for VM Disks |
| 154 | Vendor-Specific Storage Optimization (NetApp, Dell, Pure) |
| 155 | Windows VM Performance Optimization |
| 164 | Memory Overcommit for VM Density |
| 151 | Bare Metal Deployment for Maximum VM Performance |

### Deep Dives -- Platform and Advanced (5 issues)

| # | Title |
|---|---|
| 152 | OpenShift Virtualization with Hosted Control Planes (HCP) |
| 237 | Advanced CPU Topology and Pinning Strategies |
| 238 | Production Real-Time VM Deployment and Validation |
| 239 | NUMA Architecture and Memory Performance |
| 160 | Advanced VM Observability with Prometheus and Grafana |

### Advanced Tutorials (7 issues)

| # | Title |
|---|---|
| 64 | Custom HyperConverged Configuration Options |
| 65 | Enabling Nested Virtualization for Development and Testing |
| 156 | Enabling Virtualization-Based Security (VBS) for Windows VMs |
| 161 | Applying CIS Benchmarks to the OpenShift Virtualization Stack |
| 167 | vGPU Sharing for High-Density Graphics Workloads |
| 168 | Running OpenShift Virtualization on Managed Cloud Services (ROSA/ARO) |
| 169 | Multicloud VM Management |

**Q1 2027 Total: 33 issues**

