# Tutorial Tests

Ansible playbooks to test cookbook tutorials against a live OpenShift cluster.

## Prerequisites

- OpenShift cluster with Virtualization operator installed
- `oc` CLI authenticated to the cluster
- Ansible with kubernetes.core collection

## Setup

```bash
# Install required collections
ansible-galaxy collection install -r requirements.yaml
```

## Running Tests

```bash
# Run a specific tutorial test
cd tests/networking/cudn-localnet-vlan
ansible-playbook test-cudn-localnet-vlan.yaml

# Override variables
ansible-playbook test-cudn-localnet-vlan.yaml -e physical_interface=eth1

# Skip cleanup to inspect resources
ansible-playbook test-cudn-localnet-vlan.yaml -e cleanup=false
```

## Test Structure

Each tutorial test follows this structure:

```
tests/
└── <module>/
    └── <tutorial-name>/
        ├── test-<tutorial-name>.yaml   # Main playbook
        ├── vars.yaml                    # Default variables
        └── manifests/                   # YAML manifests
            ├── resource1.yaml
            └── resource2.yaml
```

## Writing Tests

1. Create folder matching tutorial name
2. Extract manifests from tutorial to `manifests/`
3. Create playbook that:
   - Applies manifests in order
   - Verifies resources are created correctly
   - Cleans up in `always` block
