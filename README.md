# 👋 Welcome Mentors — TARDIS Approach-4 Prototype

Thank you for reviewing this proposal prototype.

You have collaborator access so you can directly try the pipeline with small config edits and see the generated notebook/gallery update automatically.

**This prototype's code is written with assist of AI/LLMs and due to time constraint I haven't reviewed the codebase thoroughly apart from the major functionalities but as its just a protoype its main purpose is just to show you what I designed, what my plans are, and a preview of what my understanding reflect from the projects description. I will be submitting my proposal very shortly too describing why I chose this approach, more depth about this approach, my research and other related details. And as discussed with [Andrew](https://github.com/andrewfullard) as we will run the notebooks in a server so to mimick that I am executing the notebooks in my Azure based VM.**

## ✅ What this prototype does

This repository automates end-to-end notebook generation:
- detects changed setup configs in CI
- does quick sanity validation
- runs full notebook generation on the Azure server
- syncs generated outputs back into this repo
- publishes a browsable GitHub Pages gallery

## 🚀 Quick Try

### 1) Make a small test change

Edit a basic config such as:
- `setups/tardis_example.yml`
Any harmless, visible change is fine (for example a comment line).
or create a similar minimal config

### 2) Commit and push

```bash
git add setups/tardis_example.yml
git commit -m "mentor test: trigger notebook pipeline"
git push
```

### 3) Watch the workflow

In GitHub Actions, open:
- `approach-4-incremental-config-pipeline`

This pipeline will detect your changed config, dispatch server execution, pull outputs back, and publish updated artifacts.

### 4) Check results

- Notebook execution status: Actions logs
- Manifest details: `out/notebook-manifest.json`
- Generated notebook(s): `out/`
- Rendered web gallery: GitHub Pages site for this repository

## ⏱️ Expected turnaround time

For a basic `tardis_example.yml` change, **expect around 10 minutes** from `git push` to seeing changes reflected on GitHub Pages.

Timing can vary slightly depending on queue/load, but ~10 minutes is the normal prototype target.

Meanwhile, you can directly browse the 2–3 notebooks already generated here:
- https://aaryan-dadu.github.io/tardis-proposal-demo/

## 📚 If you want deeper technical details

- Main design: [docs/DESIGN.md](docs/DESIGN.md)
- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- User workflow details: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- Server setup: [docs/SERVER_SETUP.md](docs/SERVER_SETUP.md)

---
