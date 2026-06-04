# OpenShift Virtualization Cookbook

[![Build](https://github.com/RedHatQuickCourses/ocp-virt-cookbook/actions/workflows/build.yml/badge.svg)](https://github.com/RedHatQuickCourses/ocp-virt-cookbook/actions/workflows/build.yml)
[![OpenShift 4.18+](https://img.shields.io/badge/OpenShift-4.18%2B-ee0000)](https://docs.redhat.com/en/documentation/openshift_container_platform/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Bite-sized, practical tutorials for deploying and managing virtualization workloads on Red Hat OpenShift Virtualization. This cookbook complements official training and documentation with hands-on guides, tested YAML manifests, and troubleshooting tips for partner and customer engineers.

**[Browse the live documentation](https://redhatquickcourses.github.io/ocp-virt-cookbook)**

## Content Overview

| Module | Topics |
|--------|--------|
| [Getting Started](https://redhatquickcourses.github.io/ocp-virt-cookbook/ocp-virt-cookbook/1/getting-started/index.html) | Prerequisites, operator installation, creating VMs, virtctl CLI, VM lifecycle states, default storage class |
| [Storage](https://redhatquickcourses.github.io/ocp-virt-cookbook/ocp-virt-cookbook/1/storage/index.html) | LVM Operator, storage classes, HostPath provisioner, multi-disk configuration, troubleshooting |
| [Networking](https://redhatquickcourses.github.io/ocp-virt-cookbook/ocp-virt-cookbook/1/networking/index.html) | UDN primary networks, localnet, VLAN, Linux bridges, SR-IOV, static IPs, ingress routes, troubleshooting |
| [VM Configuration](https://redhatquickcourses.github.io/ocp-virt-cookbook/ocp-virt-cookbook/1/vm-configuration/index.html) | Templates, node placement, hotplug volumes/interfaces, remote access (Linux/Windows), internal DNS, VirtIO drivers |
| [Performance](https://redhatquickcourses.github.io/ocp-virt-cookbook/ocp-virt-cookbook/1/performance/index.html) | CPU pinning, NUMA/hugepages, real-time VMs, resource limits and QoS |
| [VM Lifecycle](https://redhatquickcourses.github.io/ocp-virt-cookbook/ocp-virt-cookbook/1/vm-lifecycle/index.html) | Golden images, boot order/sources, snapshots, cloning, qcow2 import |
| [API](https://redhatquickcourses.github.io/ocp-virt-cookbook/ocp-virt-cookbook/1/api/index.html) | Component overview |
| [Appendix](https://redhatquickcourses.github.io/ocp-virt-cookbook/ocp-virt-cookbook/1/appendix/glossary.html) | Glossary and reference material |

## Prerequisites for Tutorial Users

To follow the tutorials you need:

- An OpenShift 4.18+ cluster with the OpenShift Virtualization operator installed
- The `oc` CLI authenticated to the cluster
- The `virtctl` CLI ([installation guide](https://redhatquickcourses.github.io/ocp-virt-cookbook/ocp-virt-cookbook/1/getting-started/virtctl-basics.html))
- Basic familiarity with Kubernetes concepts (pods, namespaces, services)

Some tutorials have additional requirements (specific storage backends, network configurations, or multiple nodes). Each tutorial lists its own prerequisites at the top.

## Compatibility

| Component | Version |
|-----------|---------|
| OpenShift Container Platform | 4.18+ |
| OpenShift Virtualization Operator | 4.18+ |
| KubeVirt | Bundled with OCP Virt operator |
| `oc` CLI | Matching cluster version |
| `virtctl` CLI | Matching operator version |

## Quick Start for Contributors

```bash
make setup         # Install all dependencies
make dev           # Start local preview at http://localhost:8080
```

Make your changes, then validate and submit:

```bash
make validate      # Run all checks (lint, build, links, review)
make pr            # Push and create PR
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor guide, including AsciiDoc conventions, testing, and the PR process.

## Related Resources

- [OpenShift Virtualization Documentation](https://docs.redhat.com/en/documentation/openshift_container_platform/latest/html/virtualization/index)
- [KubeVirt User Guide](https://kubevirt.io/user-guide/)
- [Antora Documentation](https://docs.antora.org/)
- [AsciiDoc Language Reference](https://docs.asciidoctor.org/asciidoc/latest/)

## Roadmap

Contributions are welcome -- open new issues for topics you'd like to see, or comment on existing issues to request prioritization. See [docs/ROADMAP.md](docs/ROADMAP.md) for quarterly themes, design principles, and how to view the live project board.

## Problems and Feedback

Report bugs, suggestions, or improvements at https://github.com/RedHatQuickCourses/ocp-virt-cookbook/issues

## Security

See [SECURITY.md](SECURITY.md) for reporting security vulnerabilities.

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
