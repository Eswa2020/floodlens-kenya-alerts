# START HERE (Esther's checklist, delete before final submission if you like)

Everything is built and tested. What's left for you: run it on your laptop, push it with branches + PRs,
get Denis's approval on `proposal.md`, and do the peer review.

## 1. Unzip and open
**Tool: File Explorer / Finder.** Unzip `module4-capstone.zip` into your Moringa folder (next to `afyaplus-platform`).
**Tool: VS Code.** File → Open Folder → `module4-capstone`.

## 2. Install and run everything (about 2 minutes)
**Tool: VS Code's integrated terminal** (Terminal → New Terminal)
```bash
python -m venv venv
source venv/bin/activate          # Windows PowerShell: venv\Scripts\activate
pip install -r requirements.txt
python run_all.py
```
Expect `**Overall: PASS**` at the end. This also regenerates `perf_stub.json` and `docs/demo_transcript.md`
on YOUR machine (that file is your Deliverable 3 transcript evidence).
If port 8080 is busy: `python run_all.py --port 8090`.

## 3. Create the GitHub repo
**Tool: browser, github.com → New repository.** Name: `module4-capstone`, Public, **no** README / .gitignore / license.
(If you choose another name, change the CI badge line near the top of `README.md`.)

## 4. First commit on main (small), then everything on a feature branch
**Tool: VS Code's integrated terminal**
```bash
git init -b main
git add .gitignore .gitattributes README.md
git commit -m "chore: initialise FloodLens Kenya capstone repo"
git remote add origin https://github.com/Eswa2020/floodlens-kenya-alerts.git
git push -u origin main

git checkout -b feature/capstone-build
git add .
git status                         # check: no .env, no venv/ in the list
git commit -m "feat: FloodLens Kenya MWP (API, MCP agent, RAG, pins, security smoke, eval, docs)"
git push -u origin feature/capstone-build
```

## 5. Protect main and open PR #1
**Tool: browser (GitHub).**
- Settings → Rules → Rulesets → New branch ruleset → target `main` → require a pull request + require status check `test`.
- Pull requests → New → `feature/capstone-build` → `main`. The PR template fills in automatically.
- Wait for the CI check to go green (Actions tab shows ruff, pytest, smoke, eval gate, checkers).
- Ask your assigned peer to review it on the PR using `docs/peer_review_checklist.md` (Checklist / Block / Nit / Ask).

## 6. After the review: log it, merge
**Tool: VS Code** — edit `review_log.md`: replace the placeholder row with the real date, PR #, reviewer name, outcome.
Tick "peer review completed" and "slides PDF" in the README submission checklist.
**Tool: VS Code's integrated terminal**
```bash
git add review_log.md README.md
git commit -m "docs: log peer review outcome"
git push
```
Then merge PR #1 on GitHub. Optional second PR for any review fixes (`feature/review-fixes`), which adds more branch history.

## 7. Before 4pm with Denis
- Walk him through `proposal.md` (Path, Problem, MWP table, Out of scope) and ask him to approve it.
  Fill in the "Mentor approval" line after he does.
- Ask: is `module4-capstone` the right repo name, or does he want an org name?

## 8. Things worth knowing for questions on Week 12 Monday
- **Why no missed alarms?** If the photo shows water, the score never drops below 0.35, so a person always sees it.
  This came from a real bug the eval caught: "Ngong Road" was read as a road claim (`docs/build_checkpoint.md`).
- **Why is the gold score 1.0?** Gold rows are the known-good subset by definition. The honest number is the full
  fixture: 0.973, with deliberately hard rows the system gets wrong (`evals/last_score.json`).
- **Is the MCP real?** Yes: the agent opens a real MCP client session to the FastMCP server (in-memory transport).
  `python -m agents.mcp_server` serves the same tools over stdio.
- **What's stubbed?** The LLM (template from retrieved sentences) and the image model (fixture tags). Both declared.
- **Slides:** `docs/presentation.pdf` (10 slides). Edit the source at `docs/slides/presentation.html` if needed.
