# Scripts

## Diagram generation (Mermaid)

Diagrams are authored as Mermaid (`.mmd`) files in `scripts/diagrams/` and rendered to PNG in module `images/` folders.

### Setup

Install the Mermaid CLI globally (one time):

```bash
npm install -g @mermaid-js/mermaid-cli
```

### Render diagrams

```bash
./scripts/render-diagrams.sh
```

### Adding a new diagram

1. Add a `.mmd` file under `scripts/diagrams/`.
2. Run `./scripts/render-diagrams.sh`.
3. Reference the image in the `.adoc` page with `image::filename.png[Alt text]`.

---

## Screenshot capture (Playwright)

Captures OpenShift web console screenshots using Python and Playwright.

### Setup

```bash
python3 -m venv scripts/screenshots/.venv
source scripts/screenshots/.venv/bin/activate
pip install -r scripts/screenshots/requirements.txt
playwright install chromium
```

### Usage

Activate the venv first:

```bash
source scripts/screenshots/.venv/bin/activate
```

Set environment variables (do not commit these):

```bash
export CONSOLE_URL=https://console-openshift-console.apps.example.com
export CONSOLE_USER=kubeadmin
export CONSOLE_PASS=<kubeadmin-password>
export PLAYWRIGHT_BROWSERS_PATH=0
```

Capture all screenshots defined in `captures.yaml`:

```bash
python scripts/screenshots/capture.py
```

Capture a single screenshot by name:

```bash
python scripts/screenshots/capture.py --name vm-snapshots-tab
```

Run with a visible browser (for debugging):

```bash
python scripts/screenshots/capture.py --headed
```

### Configuration

Edit `scripts/screenshots/captures.yaml` to add or change screenshots. Each entry supports:

- `path` -- console URL path
- `output_dir` -- module images directory (relative to repo root)
- `filename` -- output PNG filename
- `wait_for` -- CSS selector to wait for before capturing
- `highlight` -- CSS selector to outline in red before capturing
- `clip` -- CSS selector to capture only that element (instead of full page)
