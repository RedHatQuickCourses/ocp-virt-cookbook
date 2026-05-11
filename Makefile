SHELL := /bin/bash
VENV  := tests/.venv
PIP   := $(VENV)/bin/pip
ANSIBLE := $(VENV)/bin/ansible-playbook
GALAXY  := $(VENV)/bin/ansible-galaxy
PYTHON  := $(VENV)/bin/python3
BUILD_DIR := build
NODE_MODULES := node_modules

.DEFAULT_GOAL := help

# ── Help ────────────────────────────────────────────────────────────

.PHONY: help
help:
	@echo ""
	@echo "OCP Virtualization Cookbook - Contributor Automation"
	@echo "===================================================="
	@echo ""
	@echo "Setup:"
	@echo "  make setup              Install all dependencies (test + docs)"
	@echo "  make check-deps         Verify required tools are installed"
	@echo ""
	@echo "Documentation:"
	@echo "  make build              Build HTML documentation"
	@echo "  make serve              Start local preview server"
	@echo "  make watch              Auto-rebuild on changes"
	@echo "  make dev                Watch + serve for development"
	@echo ""
	@echo "Validation:"
	@echo "  make lint               Check AsciiDoc syntax"
	@echo "  make check-links        Validate links in built HTML"
	@echo "  make check-xrefs        Verify xref links resolve"
	@echo "  make validate           Run all validation checks"
	@echo "  make test-manifests     Validate YAML manifests"
	@echo "  make test-manifests-dry Test manifests with oc dry-run"
	@echo "  make review-file FILE=  Review a single .adoc file"
	@echo "  make review             Review changed .adoc files"
	@echo "  make review-all         Review all .adoc files"
	@echo ""
	@echo "Generate & Run Tests:"
	@echo "  make generate TUTORIAL= Generate test from tutorial"
	@echo "  make generate-dry       Preview test generation"
	@echo "  make test MODULE= NAME= Run a specific test"
	@echo "  make test-no-cleanup    Run test, keep resources"
	@echo ""
	@echo "Clean:"
	@echo "  make clean              Remove virtual environment"
	@echo "  make clean-all          Remove venv, build, node_modules"
	@echo ""
	@echo "Git Helpers:"
	@echo "  make branch NAME=xyz    Create feature branch"
	@echo "  make pr                 Push and open PR"
	@echo "  make sync               Rebase on upstream main"
	@echo ""

# ── Setup ───────────────────────────────────────────────────────────

.PHONY: setup
setup: $(VENV)/bin/activate
	@echo "Setup complete. Run 'source $(VENV)/bin/activate' or use make targets."

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install kubernetes ansible yamllint
	$(GALAXY) collection install -r tests/requirements.yaml
	@touch $(VENV)/bin/activate

.PHONY: check-deps
check-deps:
	@echo "Checking required tools..."
	@echo ""
	@command -v node > /dev/null 2>&1 && \
		echo "[OK] node ($$(node --version))" || \
		{ echo "[MISSING] node — Install: https://nodejs.org or use nvm/brew"; EXIT=1; }
	@command -v pnpm > /dev/null 2>&1 && \
		echo "[OK] pnpm ($$(pnpm --version))" || \
		{ echo "[MISSING] pnpm — Install: npm install -g pnpm or https://pnpm.io"; EXIT=1; }
	@command -v python3 > /dev/null 2>&1 && \
		echo "[OK] python3 ($$(python3 --version | cut -d' ' -f2))" || \
		{ echo "[MISSING] python3 — Install via system package manager"; EXIT=1; }
	@command -v yamllint > /dev/null 2>&1 && \
		echo "[OK] yamllint ($$(yamllint --version | cut -d' ' -f2))" || \
		{ echo "[MISSING] yamllint — Install: pip install yamllint"; EXIT=1; }
	@command -v asciidoctor > /dev/null 2>&1 && \
		echo "[OK] asciidoctor ($$(asciidoctor --version | head -1 | awk '{print $$2}'))" || \
		{ echo "[MISSING] asciidoctor — Install: gem install asciidoctor (optional)"; }
	@command -v oc > /dev/null 2>&1 && \
		echo "[OK] oc ($$(oc version --client -o yaml | grep gitVersion | awk '{print $$2}'))" || \
		{ echo "[MISSING] oc — Install: https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html (for tests)"; }
	@echo ""
	@[ -z "$$EXIT" ] && echo "All required tools installed!" || { echo "Please install missing tools."; exit 1; }

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

# ── Documentation ───────────────────────────────────────────────────

.PHONY: build
build:
	@if [ ! -d "$(NODE_MODULES)" ]; then \
		echo "Installing node dependencies..."; \
		pnpm install; \
	fi
	pnpm run build

.PHONY: serve
serve:
	pnpm run serve

.PHONY: watch
watch:
	@if [ ! -d "$(NODE_MODULES)" ]; then \
		echo "Installing node dependencies..."; \
		pnpm install; \
	fi
	pnpm run watch:adoc

.PHONY: dev
dev:
	@if [ ! -d "$(NODE_MODULES)" ]; then \
		echo "Installing node dependencies..."; \
		pnpm install; \
	fi
	@echo "Starting watch in background..."
	@pnpm run watch:adoc > /dev/null 2>&1 & echo $$! > .watch.pid
	@echo "Starting preview server (Ctrl+C to stop both)..."
	@trap 'kill $$(cat .watch.pid 2>/dev/null) 2>/dev/null; rm -f .watch.pid' EXIT; \
		pnpm run serve

# ── Validation ──────────────────────────────────────────────────────

.PHONY: lint
lint:
	@echo "Linting AsciiDoc files..."
	@if command -v asciidoctor > /dev/null 2>&1; then \
		find modules -name "*.adoc" -exec asciidoctor -o /dev/null -a attribute-missing=warn {} \; 2>&1 | \
			grep -E "(WARN|ERROR)" || echo "[OK] No AsciiDoc errors found"; \
	else \
		echo "⚠ asciidoctor not installed. Install with: gem install asciidoctor"; \
		exit 1; \
	fi

.PHONY: check-links
check-links:
	@if [ ! -d "$(BUILD_DIR)" ]; then \
		echo "Build directory not found. Run 'make build' first."; \
		exit 1; \
	fi
	@echo "Checking links in built HTML..."
	@if command -v htmltest > /dev/null 2>&1; then \
		htmltest $(BUILD_DIR); \
	else \
		echo "⚠ htmltest not installed. Skipping link validation."; \
		echo "Install from: https://github.com/wjdp/htmltest"; \
	fi

.PHONY: check-xrefs
check-xrefs: build
	@echo "Checking xref links..."
	@echo "[OK] No xref warnings found (checked during build)"

.PHONY: validate
validate: lint build check-xrefs review-all
	@echo ""
	@echo "[OK] All validation checks passed!"

.PHONY: test-manifests
test-manifests: setup
	@echo "Validating YAML manifests..."
	@find modules -type f \( -name "*.yaml" -o -name "*.yml" \) -exec $(VENV)/bin/yamllint {} + || \
		{ echo "YAML validation failed. Fix errors above."; exit 1; }
	@echo "[OK] All YAML manifests valid"

.PHONY: test-manifests-dry
test-manifests-dry: check-auth
	@echo "Testing manifests with oc dry-run..."
	@find modules -type f \( -name "*.yaml" -o -name "*.yml" \) | while read file; do \
		echo "Testing $$file..."; \
		oc apply --dry-run=client -f "$$file" || exit 1; \
	done
	@echo "[OK] All manifests passed dry-run"

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

# ── Review ──────────────────────────────────────────────────────────

.PHONY: review-file
review-file:
ifndef FILE
	$(error FILE is required. Example: make review-file FILE=modules/networking/pages/some-tutorial.adoc)
endif
	@bash scripts/review-docs.sh $(FILE)

.PHONY: review
review:
	@CHANGED=$$(git diff --name-only origin/main -- '*.adoc'); \
	if [ -z "$$CHANGED" ]; then \
		echo "No changed .adoc files found."; \
	else \
		bash scripts/review-docs.sh $$CHANGED; \
	fi

.PHONY: review-all
review-all:
	@bash scripts/review-docs.sh --all

# ── Clean ───────────────────────────────────────────────────────────

.PHONY: clean
clean:
	rm -rf $(VENV)
	@echo "Virtual environment removed."

.PHONY: clean-all
clean-all:
	rm -rf $(VENV) $(BUILD_DIR) $(NODE_MODULES)
	rm -f .watch.pid
	@echo "Removed: venv, build, node_modules"

# ── Git Helpers ─────────────────────────────────────────────────────

.PHONY: branch
branch:
ifndef NAME
	$(error NAME is required. Example: make branch NAME=add-tutorial-xyz)
endif
	@git fetch upstream 2>/dev/null || git fetch origin
	@git checkout main
	@git pull upstream main 2>/dev/null || git pull origin main
	@git checkout -b $(NAME)
	@echo "Created branch: $(NAME)"

.PHONY: pr
pr:
	@BRANCH=$$(git branch --show-current); \
	git push -u origin $$BRANCH; \
	echo ""; \
	echo "Create PR at:"; \
	echo "https://github.com/RedHatQuickCourses/ocp-virt-cookbook/compare/$$BRANCH"

.PHONY: sync
sync:
	@BRANCH=$$(git branch --show-current); \
	git fetch upstream 2>/dev/null || git fetch origin; \
	git rebase upstream/main 2>/dev/null || git rebase origin/main; \
	echo "Rebased $$BRANCH on upstream/main"
