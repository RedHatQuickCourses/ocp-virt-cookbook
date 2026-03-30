# Contributing to OpenShift Virtualization Cookbook

Thank you for contributing to the OpenShift Virtualization Cookbook! This guide will help you get started with contributing tutorials and documentation.

## Prerequisites

Before you begin, ensure you have the following tools installed:

- **Node.js** 16+ (for Antora builds)
- **pnpm** (package manager)
- **Python** 3.9+ (for test framework)
- **yamllint** (YAML validation)
- **asciidoctor** (optional, for AsciiDoc linting)
- **oc CLI** (optional, for running tests)

### Quick Check

Run `make check-deps` to verify all required tools are installed:

```bash
make check-deps
```

## Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/RedHatQuickCourses/ocp-virt-cookbook.git
   cd ocp-virt-cookbook
   ```

2. **Install dependencies:**

   ```bash
   make setup
   ```

3. **Start development environment:**

   ```bash
   make dev
   ```

   This starts the documentation build watcher and preview server. Navigate to the URL shown (usually http://localhost:8080) to preview your changes live.

## Development Workflow

### Creating a New Tutorial

1. **Create a feature branch:**

   ```bash
   make branch NAME=add-tutorial-xyz
   ```

   Or manually:

   ```bash
   git checkout -b yourusername/add-tutorial-xyz
   ```

2. **Add your tutorial:**

   - Create a new `.adoc` file in the appropriate module under `modules/<module>/pages/`
   - Add an entry to `modules/<module>/nav.adoc`
   - Follow the [AsciiDoc conventions](#asciidoc-conventions)

3. **Preview your changes:**

   ```bash
   make dev
   ```

   Open http://localhost:8080 in your browser.

4. **Validate your changes:**

   ```bash
   make validate
   ```

   This runs all checks: linting, building, link validation, and documentation review.

5. **Commit and push:**

   ```bash
   git add modules/
   git commit -m "Add tutorial for XYZ feature"
   git push -u origin yourusername/add-tutorial-xyz
   ```

6. **Create a pull request:**

   ```bash
   make pr
   ```

   Or use the GitHub web UI.

## Make Targets Reference

### Setup & Dependencies

| Target | Description |
|--------|-------------|
| `make setup` | Install all dependencies (test framework + docs) |
| `make check-deps` | Verify required tools are installed |

### Documentation

| Target | Description |
|--------|-------------|
| `make build` | Build HTML documentation |
| `make serve` | Start local preview server |
| `make watch` | Auto-rebuild on changes |
| `make dev` | Watch + serve for development |

### Validation

| Target | Description |
|--------|-------------|
| `make lint` | Check AsciiDoc syntax |
| `make check-links` | Validate links in built HTML |
| `make check-xrefs` | Verify xref links resolve |
| `make validate` | Run all validation checks |
| `make test-manifests` | Validate YAML manifests |
| `make test-manifests-dry` | Test manifests with `oc dry-run` |
| `make review-file FILE=path/to/file.adoc` | Review a single file |
| `make review` | Review changed .adoc files |
| `make review-all` | Review all .adoc files |

### Testing

| Target | Description |
|--------|-------------|
| `make generate TUTORIAL=path/to/tutorial.adoc` | Generate test from tutorial |
| `make test MODULE=<module> NAME=<name>` | Run a specific test |
| `make test-no-cleanup MODULE=<module> NAME=<name>` | Run test, keep resources |

### Clean

| Target | Description |
|--------|-------------|
| `make clean` | Remove virtual environment |
| `make clean-all` | Remove venv, build, node_modules |

### Git Helpers

| Target | Description |
|--------|-------------|
| `make branch NAME=xyz` | Create feature branch |
| `make pr` | Push and open PR |
| `make sync` | Rebase on upstream main |

## AsciiDoc Conventions

Follow these conventions when writing tutorials (see [USAGEGUIDE.adoc](USAGEGUIDE.adoc) for full details):

### Headings

- Use `= Title` for H1 (one per file)
- Use `== Section` for H2, `=== Subsection` for H3, etc.
- Do not skip heading levels

### Code Blocks

```asciidoc
[source,bash,role=execute]
----
oc get pods
----
```

### Images

```asciidoc
image::screenshot.png[Screenshot description]
```

Always include alt text.

### Links

- External links: `link:https://example.com[Link text, window=_blank]`
- Cross-references: `xref:other-page.adoc[Other Page]`

### Formatting

- **Bold**: `*text*` or `**text**` (both work)
- *Italic*: `_text_`
- Code: `` `code` ``

### YAML Manifests

- Remove `creationTimestamp: null`
- Avoid inline `{}` or `[]` in YAML
- Use proper indentation (2 spaces)

### Admonitions

```asciidoc
NOTE: This is a note.

WARNING: This is a warning.

IMPORTANT: This is important.
```

Capitalize the first word after the admonition keyword.

## Testing Your Tutorials

The test framework can automatically generate and run tests from your tutorials:

1. **Generate a test:**

   ```bash
   make generate TUTORIAL=modules/vm-configuration/pages/my-tutorial.adoc
   ```

2. **Preview without generating:**

   ```bash
   make generate-dry TUTORIAL=modules/vm-configuration/pages/my-tutorial.adoc
   ```

3. **Run the test** (requires `oc login`):

   ```bash
   make test MODULE=vm-configuration NAME=my-tutorial
   ```

## Documentation Review

Before submitting a PR, run the documentation review script:

```bash
make review
```

This checks for common issues:
- Missing alt text on images
- Incorrect heading levels
- YAML formatting issues
- Link formatting
- And more...

## Pull Request Process

1. **Ensure all checks pass:**

   ```bash
   make validate
   ```

2. **Create a PR** with:
   - Clear title describing the change
   - Description of what the tutorial covers
   - Link to any related issues

3. **CI checks will run automatically**, including:
   - Documentation review
   - Build verification
   - Link validation

4. **Request a review** from a team member or maintainer.

5. **Address feedback** by pushing additional commits to the same branch.

6. **Merge** once approved by reviewers.

## Getting Help

- **Issues**: Report bugs or request features at https://github.com/RedHatQuickCourses/ocp-virt-cookbook/issues
- **Questions**: Open a discussion or ask in your PR
- **Slack/Mailing List**: [Add if applicable]

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
