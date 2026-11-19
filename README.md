# VGC World Laboratory

A local simulator for exploring business-jet market entry using system dynamics, sampled futures and candidate adaptive pathways. The browser dashboard runs against a Python server on your own computer.

**Research prototype:** inputs are illustrative and uncalibrated. Outputs are model experiments, not Saab forecasts or validated investment advice. Keep this repository private under the team's university/sponsor arrangements; no public open-source license has been assigned.

## Requirements

- Python **3.10 or newer** (3.12 or newer recommended).
- A modern browser: Edge, Chrome, Firefox or Safari.
- Git if cloning/pulling updates. Downloading the repository ZIP also works.

**No pip packages, Node.js, commercial solvers or external accounts are required to run it.** The application uses Python's standard library and local HTML/JavaScript. Internet is needed only to obtain the repository/Python or pull updates.

## Quick start

Clone the team repository using its actual GitHub URL, or download and extract its ZIP. Open a terminal in the extracted/cloned project folder (the folder containing this README).

### Windows / PowerShell

```powershell
python --version
python run.py --open
```

If Windows does not recognize `python`, try `py -3 run.py --open`. You can also double-click `start-lab.cmd` after Python is installed and on PATH.

### macOS / Linux

```bash
python3 --version
python3 run.py --open
```

The browser should open at **http://127.0.0.1:8765**. Leave the terminal running. Press **Ctrl+C** there to stop the server. `--open` is optional: you can open the URL yourself. Do not open `vgc_sd/app.html` directly or use GitHub Pages; the interactive simulator requires its Python backend.

### Optional isolated environment

There are no dependencies to install, but you may prefer a virtual environment:

```powershell
# Windows
python -m venv .venv
.\.venv\Scripts\python.exe run.py --open
```

```bash
# macOS / Linux
python3 -m venv .venv
.venv/bin/python run.py --open
```

No activation or `pip install` step is necessary. The Windows launch scripts prefer `.venv` when present.

## First experiment (about two minutes)

1. Open **Inputs**. For a reproducible team example, load `examples/team-demo.json` with **Load saved inputs or experiment JSON**.
2. This example uses 20 years, eight sampled futures, seed 42 and an exit trigger of **2,800 USD million**. All values are demonstration assumptions.
3. Click **Generate worlds and run policies**. Start with eight futures before trying the maximum of 40.
4. In **Outputs**, choose a future and move the year slider. The adaptive trajectory changes color when the implemented action changes. Hover/focus decision markers for stock values and thresholds. Shaded shock periods appear on plots for their main model channels; hover the bands or labeled tracks for details. Hover never changes the selected year.
5. Open **Robustness dashboard**. Set your minimum NPV and latest acceptable entry-into-service (EIS) year. Inspect **Overview**, **Staffing** and **Finances**. Select a future to see its exposure crossing, exit review and implementation sequence.
6. Click **Evaluate limits** to compare identical sampled futures at different exposure triggers. Teal meets all criteria, coral exits, amber continues but misses a criterion. These counts are coverage of the experiment design, not probabilities.
7. Expand **Audit a single decision** only when you need the detailed same-state comparison. It holds the previous action versus the changed action under identical future shocks, without later adaptive decisions.
8. Return to Inputs and use **Download inputs** to share a configuration, or **Download experiment JSON** to retain full trajectories and decision branches. Browser runs are otherwise held in memory; refreshing discards them.

The robustness sweep is displayed separately; the experiment JSON export does not currently include that sweep. Save its limits and success criteria with your experiment notes and rerun it when needed.

## Editing inputs correctly

- Fixed program values apply unless overridden by an active DOE range. Clear **both** range endpoints to hold that parameter fixed.
- DOE uses independent Latin hypercube sampling. Each shock also samples its start, duration and magnitude. Equal min/max endpoints fix a value.
- All listed shocks occur once per future. Remove events to exclude them. Counts, occurrence probabilities and correlations are not sampled.
- Every policy and decision branch within a future uses the same realized shocks. Different futures can have different parameter values and shocks.
- Changing an input or policy exit trigger requires **Generate worlds and run policies** again. Changing dashboard success criteria only reclassifies existing results.
- The UI starts with an editable example shock. The complete team example has several shocks; load it explicitly.

## Updates and troubleshooting

After pulling changes, **stop the old Python server**, then restart and refresh the browser with Ctrl+F5 (Cmd+Shift+R on macOS):

```bash
git pull
python run.py --open
```

Use `python3` instead on macOS/Linux if needed. A browser refresh reloads HTML but does not reload Python code.

| Problem | Fix |
| --- | --- |
| `No module named vgc_sd` or tests directory missing | Run `python run.py` from the repository, or pass the full path to `run.py`. Module commands below must run from the repository root. |
| `/robustness` returns 404 or `Unexpected token '<'` | Stop the old server with Ctrl+C, restart from this checkout, refresh, then rerun the experiment. Check [server health](http://127.0.0.1:8765/health): it should list `/run` and `/robustness`. |
| Port 8765 already in use | Stop the previous server or run `python run.py --port 8766 --open`. Use the matching browser port. |
| PowerShell blocks `.ps1` scripts | Use `python run.py --open` or `start-lab.cmd`; no execution-policy change is required. |
| Python command opens the Microsoft Store | Install Python and enable its PATH option, or use `py -3`. |
| Invalid shock start after shortening the horizon | Adjust shock start ranges to fit the new horizon. |
| No decision audit for a future | It may have no implemented decisions. Select another future; pending decisions have no audit. |
| Evaluation feels slow | Reduce futures; the simulator also runs same-state decision continuations. Sweeps repeat policy simulations at each limit. |

The server binds only to `127.0.0.1`. Each teammate should run a local copy. This development server is not configured for public hosting or multi-user access.

## Tests

From the repository root:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the Python checks on Windows and Linux. Local UI script smoke checks were also used during development, but a real browser interaction suite is not yet included. Python tests do not establish calibration or empirical validity.

## Optional CSV / offline report mode

This is a separate, simpler fixed-policy experiment; it does not include the full interactive DOE/adaptive dashboard:

```bash
python -m vgc_sd --config config/baseline.json --years 20 --out results
```

Open `results/report.html` in a browser. This standalone report needs no running server. It compares three fixed policies at three staffing levels, writes CSVs and an input manifest, and retains its own report interactions. Generated results are ignored by Git.

## Repository layout

```text
run.py                    Portable launcher
start-lab.cmd / .ps1       Windows convenience launchers
examples/team-demo.json   Shareable interactive experiment inputs
config/baseline.json      Simpler CSV/report-mode parameters
vgc_sd/model.py           Stocks, flows, equations and world state
vgc_sd/experiment.py      DOE, shocks, policies, decision forks and robustness sweep
vgc_sd/server.py          Local HTTP server and API
vgc_sd/app.html           Interactive browser interface
vgc_sd/report.py / .html  Standalone report generator/template
vgc_sd/__main__.py        CSV/report command
tests/                   Numerical, sampling and policy checks
docs/MODEL.md            Model assumptions and interpretation
LICENSE_REVIEW.md        Dependency and licensing review
```

## Team development and first push

Create a **private, empty** GitHub repository for this project. From this folder, initialize Git if needed, review staged files and commit. Replace the remote URL with the repository you created:

```bash
git init
git branch -M main
git add .
git status
git commit -m "Initial VGC simulation laboratory"
git remote add origin https://github.com/YOUR-TEAM/YOUR-REPOSITORY.git
git push -u origin main
```

The commands above are instructions; no GitHub repository, commit or push was created automatically. Invite teammates through GitHub, then they can clone the actual URL and follow Quick start. Prefer branches and pull requests for equations, policies and input changes. Run tests before merging. Include the input JSON, seed, success criteria and relevant findings with research comparisons. Reproducibility depends on both the input and the source revision.

`.gitignore` excludes environments, caches, generated results, local credentials and exports. Do not commit sponsor decks, confidential datasets or client outputs without authorization. The supplied package contains no source slide decks and incorporates no BusinessSimulation/system-flow code. See [LICENSE_REVIEW.md](LICENSE_REVIEW.md) for the dependency assessment. Do not add an MIT/GPL/public license without agreement on project ownership and sponsor terms.

## Scope and limitations

The current DAPP layer evaluates hand-designed stock-threshold pathways; it does not discover or optimize strategies. Inputs are synthetic, market capture is fixed, hiring uses a first-order adjustment, and finance excludes taxes, financing, terminal value and currency changes. Exit freezes operations with **no closure costs or recoveries**, which can overstate its benefit. All money is constant USD million; time is years from launch. See [model notes](docs/MODEL.md) before interpreting results.
