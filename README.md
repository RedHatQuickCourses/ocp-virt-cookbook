# OpenShift Virtualization Cookbook

This cookbook provides bite-sized, practical tutorials for deploying and managing virtualization workloads on Red Hat OpenShift Virtualization. It serves as a complement to official OpenShift Virtualization training and documentation, offering hands-on guides with tested workflows, YAML manifests, and troubleshooting tips specifically designed for partner and customer engineers getting started with OpenShift Virtualization.

## Quick Start (Contributors)

Get started contributing in minutes:

```bash
make setup         # Install all dependencies
make dev           # Start local preview
```

Make your changes, then:

```bash
make validate      # Run all checks
make pr            # Push and create PR
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor guide.

## Creating Course Content

We use a system called Antora (https://antora.org) to publish courses. Antora expects the files and folders in a source repository to be arranged in a certain opinionated way to simplify the process of writing course content using asciidoc, and then converting the asciidoc source to HTML.

Refer to the quick courses contributor guide for a detailed guide on how to work with Antora tooling and publish courses.

## TL;DR Quickstart

This section is intended as a quick start guide for technically experienced members. The contributor guide remains the canonical reference for the course content creation process with detailed explanations, commands, video demonstrations, and screenshots.

### Pre-requisites

- You have a macOS or Linux workstation. Windows has not been tested, or supported. You can try using a WSL2 based environment to run these steps - YMMV!
- You have a somewhat recent version of the Git client installed on your workstation
- You have a somewhat new Node.js LTS release (Node.js 16+) installed locally.
- You have [pnpm](https://pnpm.io/installation); npm will work but not recommended
- Install a recent version of Visual Studio Code. Other editors with asciidoc editing support may work - YMMV, and you are on your own...

### Antora Files and Folder Structure

The _antora.yml_ file lists the chapters/modules/units that make up the course.

Each chapter entry points to a _nav.adoc_ file that lists the sections in that chapter. The home page of the course is rendered from _modules/ROOT/pages/index.adoc_.

Each chapter lives in a separate folder under the _modules_ directory. All asciidoc source files live under the _modules/CHAPTER/pages_ folder.

To create a new chapter in the course, create a new folder under _modules_.

To add a new section under a chapter create an entry in the _modules/CHAPTER/nav.adoc_ file and then create the asciidoc file in the _modules/CHAPTER/pages_ folder.

### Steps

1. Clone or fork the course repository.

```
$ git clone git@github.com:RedHatQuickCourses/ocp-virt-cookbook.git
```

2. Install the pnpm dependencies for the course tooling.

```
$ cd ocp-virt-cookbook
$ pnpm install
```

3. Start the asciidoc to HTML compiler in the background. This command watches for changes to the asciidoc source content in the **modules** folder and automatically re-generates the HTML content.

```
$ pnpm run watch:adoc
```

4. Start a local web server to serve the generated HTML files. Navigate to the URL printed by this command to preview the generated HTML content in a web browser.

```
$ pnpm run serve
```

5. Before you make any content changes, create a local Git branch based on the **main** branch. As a good practice, prefix the branch name with your GitHub ID. Use a suitable branch naming scheme that reflects the content you are creating or changing.

```
$ git checkout -b username/add-tutorial-xyz
```

6. Make your changes to the asciidoc files. Preview the generated HTML and verify that there are no rendering errors. Commit your changes to the local Git branch and push the branch to GitHub.

```
$ git add .
$ git commit -m "Add tutorial for XYZ feature"
$ git push -u origin username/add-tutorial-xyz
```

7. Create a GitHub pull request (PR) for your changes using the GitHub web UI. For forks, create a PR that merges your forked changes into the `main` branch of this repository.
8. Request a review of the PR from your technical peers and/or a member of the PTL team.
9. Make any changes requested by the reviewer in the **same** branch as the PR, and then commit and push your changes to GitHub. If other team members have made changes to the PR, then do not forget to do a **git pull** before committing your changes.
10. Once reviewer(s) approve your PR, you should merge it into the **main** branch.
11. Wait for a few minutes while the automated GitHub action publishes your changes to the production GitHub pages website.
12. Verify that your changes have been published to the production GitHub pages website at https://redhatquickcourses.github.io/ocp-virt-cookbook

## Current Roadmap

The project roadmap covers 105 open issues organized across four quarters, prioritized by dependency order, module cohesion, and effort level. Contributions are welcome -- feel free to open new issues for topics you'd like to see covered, or comment on any existing open issue to request that it be prioritized.

| Quarter | Theme | Issues | Effort Profile |
|---|---|---|---|
| **Q2 2026** | Foundation, Quick Wins, Tech Debt | 17 | Small items, fast turnaround |
| **Q3 2026** | Core Networking and Storage | 27 | Mix of improvements and standard tutorials |
| **Q4 2026** | VM Ops, Migration, Monitoring | 28 | Intermediate tutorials and operations |
| **Q1 2027** | Deep Dives and Advanced | 33 | Large, reference-grade content |

**Q2 2026** clears the oldest backlog items, adds CI infrastructure, polishes the Getting Started module with diagrams and quick-start tutorials, and resolves long-standing housekeeping issues.

**Q3 2026** fills out the two most critical technical modules -- networking and storage -- with 15 topology diagram improvements for existing pages plus 14 new tutorials covering network policies, dual-stack, MetalLB, ODF/Ceph, NFS, CDI operations, and more.

**Q4 2026** delivers the operational layer: VMware migration with MTV, live migration, monitoring and metrics, GPU configuration, Ansible automation, RBAC and multi-tenancy, plus diagram improvements across the VM configuration, lifecycle, and performance modules.

**Q1 2027** caps the roadmap with 33 deep dives and advanced tutorials -- comprehensive reference guides on topics like virtctl CLI, cloud-init, UDN architecture, storage class selection, HCP, CIS benchmarks, and managed cloud services (ROSA/ARO).

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full detailed roadmap with every issue mapped to its quarter.

## Problems and Feedback

If you run into any issues, report bugs/suggestions/improvements about this course here - https://github.com/RedHatQuickCourses/ocp-virt-cookbook/issues

## License

This project is licensed under the MIT License - see the LICENSE file for details.
