SHELL := /bin/bash
VENV  := tests/.venv
PIP   := $(VENV)/bin/pip
ANSIBLE := $(VENV)/bin/ansible-playbook
GALAXY  := $(VENV)/bin/ansible-galaxy
PYTHON  := $(VENV)/bin/python3

.DEFAULT_GOAL := help

# ── Help ────────────────────────────────────────────────────────────

.PHONY: help
help:
	@echo ""
	@echo "OCP Virtualization Cookbook - Test Framework"
	@echo "============================================"
	@echo ""
	@echo "Setup:"
	@echo "  make setup                  Create venv and install dependencies"
	@echo "  make clean                  Remove the virtual environment"
	@echo ""
	@echo "Generate tests from tutorials:"
	@echo "  make generate TUTORIAL=path/to/tutorial.adoc"
	@echo "  make generate-dry TUTORIAL=path/to/tutorial.adoc    (preview only)"
	@echo "  make generate TUTORIAL=... FORCE=1                  (overwrite existing)"
	@echo ""
	@echo "Run tests:"
	@echo "  make test MODULE=vm-configuration NAME=internal-dns-for-vms"
	@echo "  make test-no-cleanup MODULE=... NAME=...            (keep resources)"
	@echo ""
	@echo "Examples:"
	@echo "  make generate-dry TUTORIAL=modules/vm-configuration/pages/internal-dns-for-vms.adoc"
	@echo "  make test MODULE=vm-configuration NAME=internal-dns-for-vms"
	@echo ""

# ── Setup ───────────────────────────────────────────────────────────

.PHONY: setup
setup: $(VENV)/bin/activate
	@echo "Setup complete. Run 'source $(VENV)/bin/activate' or use make targets."

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install kubernetes ansible
	$(GALAXY) collection install -r tests/requirements.yaml
	@touch $(VENV)/bin/activate

# ── Generate ────────────────────────────────────────────────────────

.PHONY: generate
generate: setup
ifndef TUTORIAL
	$(error TUTORIAL is required. Example: make generate TUTORIAL=modules/vm-configuration/pages/internal-dns-for-vms.adoc)
endif
	$(PYTHON) tests/generate-test.py $(if $(DRY_RUN),--dry-run) $(if $(FORCE),--force) $(TUTORIAL)

.PHONY: generate-dry
generate-dry: setup
ifndef TUTORIAL
	$(error TUTORIAL is required. Example: make generate-dry TUTORIAL=modules/vm-configuration/pages/internal-dns-for-vms.adoc)
endif
	$(PYTHON) tests/generate-test.py --dry-run $(TUTORIAL)

# ── Auth check ──────────────────────────────────────────────────────

.PHONY: check-auth
check-auth:
	@oc whoami > /dev/null 2>&1 || \
		{ echo ""; \
		  echo "Error: Not logged into an OpenShift cluster."; \
		  echo "Run 'oc login <cluster-url>' first."; \
		  echo ""; \
		  exit 1; }
	@echo "Logged in as $$(oc whoami) on $$(oc whoami --show-server)"

# ── Test ────────────────────────────────────────────────────────────

.PHONY: test
test: setup check-auth
ifndef MODULE
	$(error MODULE is required. Example: make test MODULE=vm-configuration NAME=internal-dns-for-vms)
endif
ifndef NAME
	$(error NAME is required. Example: make test MODULE=vm-configuration NAME=internal-dns-for-vms)
endif
	@$(ANSIBLE) tests/$(MODULE)/$(NAME)/test-$(NAME).yaml $(EXTRA_ARGS) \
		&& echo "" && echo "PASS: $(MODULE)/$(NAME)" \
		|| { echo "" && echo "FAIL: $(MODULE)/$(NAME)"; exit 1; }

.PHONY: test-no-cleanup
test-no-cleanup: setup check-auth
ifndef MODULE
	$(error MODULE is required. Example: make test-no-cleanup MODULE=vm-configuration NAME=internal-dns-for-vms)
endif
ifndef NAME
	$(error NAME is required. Example: make test-no-cleanup MODULE=vm-configuration NAME=internal-dns-for-vms)
endif
	@$(ANSIBLE) tests/$(MODULE)/$(NAME)/test-$(NAME).yaml -e cleanup=false $(EXTRA_ARGS) \
		&& echo "" && echo "PASS: $(MODULE)/$(NAME)" \
		|| { echo "" && echo "FAIL: $(MODULE)/$(NAME)"; exit 1; }

# ── Clean ───────────────────────────────────────────────────────────

.PHONY: clean
clean:
	rm -rf $(VENV)
	@echo "Virtual environment removed."
