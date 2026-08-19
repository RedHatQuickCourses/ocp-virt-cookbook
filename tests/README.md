# Tutorial Test Framework

Validates tutorial YAML manifests by extracting them from `.adoc` files and
running `oc apply --dry-run=client` against an OpenShift cluster.

## Quick start

```bash
make setup               # create venv, install deps
oc login <cluster>       # authenticate to the cluster

make test                # generate attachments, yamllint, dry-run test
```

## How it works

1. **`make generate-all`** — the parser reads each tutorial `.adoc` file, extracts
   Kubernetes manifests (heredoc blocks, attachment-referenced YAML, namespace
   creation commands), and writes them as individual files under
   `modules/<module>/attachments/<tutorial>/`.

2. **`make test-manifests`** — runs `yamllint` on all YAML files under `modules/`.

3. **`make test-manifests-dry`** — runs `oc apply --dry-run=client -f` on every
   YAML file to validate against the cluster's API server.

`make test` runs all three steps in sequence.

## Architecture

```
tests/
  parser.py              # AsciiDoc parser — extracts Kubernetes manifests
  generate-attachments.py # CLI — generates attachment YAML files
  requirements.txt       # Python dependencies (pyyaml, yamllint)
  README.md              # This file
```

## Individual targets

```bash
make generate TUTORIAL=modules/vm-configuration/pages/internal-dns-for-vms.adoc
make generate-all       # all tutorials
make generate-dry TUTORIAL=...  # preview without writing

make test-manifests     # yamllint validation
make test-manifests-dry # oc apply --dry-run=client
make test               # all of the above
```
