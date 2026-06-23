# Build Your Own Agentic OS — teaching build console

An evergreen, self-contained teaching page that walks anyone through building their own
**agentic OS** — from a first Project to a full skill-library + vault + connectors setup.
Part of the **TŌGE** family. By Dr. Jon Schoenecker.

**Live:** https://emory-agentic-os.vercel.app (existing alias, preserved for residents who already have the link)

## What this repo is

A single, dependency-free `index.html` (~150 KB). No build step, no framework, no external
requests — it opens offline and renders identically anywhere. The page is a build console with
a pinned **★ Today** tab plus 11 build tabs: Why · Square One · OS Core · Connectors ·
★ Zotero + Papers · Cowork · Claude Code · The Graph · Skills · At Scale · Reference.

## Stickiness features

- **Daily Signal (★ Today).** A banner + archive of fresh, sourced agentic-OS ideas, updated
  automatically most days (see *Daily auto-update* below). The reason to come back.
- **Build-progress tracker.** Each build tab has a "mark complete" toggle persisted in
  `localStorage` (`agos.progress.v1`); the top progress rail and tab ✓ badges reflect how many
  of the 11 stages the reader has finished. Pulls people back to finish their build.
- **Per-tab share / deep links.** Every tab has a "copy link to this tab" button on top of the
  existing `#tab=<id>` deep-linking, so a specific stage (or the day's idea) is shareable.

## Daily auto-update (the Daily Signal pipeline)

The day's ideas live in ONE inline JSON block in `index.html`, between the markers
`<!-- DAILY_SIGNAL_START -->` … `<!-- DAILY_SIGNAL_END -->`.

The updater runs **in GitHub's cloud** via the `.github/workflows/daily-signal.yml` Action —
so it fires every day **whether or not any of Jon's machines are on**. Each run:

1. `tools/generate_daily_idea.py` asks Claude (with web search) for ONE publicly-sourced new
   idea and writes it to `new_idea.json`. If nothing solid is found it **skips the day** (exit 4).
2. `tools/update_daily_signal.py --from-file new_idea.json --stamp` splices it in
   (deterministic — the LLM never hand-edits the HTML; de-dups by title, caps the archive at 40,
   refuses any item without an http(s) source URL).
3. the Action commits + pushes to `main` → Vercel auto-deploys.

`tools/DAILY_BUILD_PROMPT.md` is the equivalent instruction set if you'd rather run the job from
a claude.ai routine or a Claude Code session instead of the Action.

### One-time setup (required for the Action to run)

Add an **`ANTHROPIC_API_KEY`** repository secret:
GitHub repo → Settings → Secrets and variables → Actions → New repository secret.
(That's the only manual step; the Action already has `contents: write` to push.)
Schedule: `12 11 * * *` UTC ≈ 6:12 AM America/Chicago — edit the cron in the workflow to taste.
You can also trigger a run any time from the repo's **Actions** tab → *Daily Signal* → *Run workflow*.

### Run it by hand (local)

    python tools/update_daily_signal.py --title "..." --blurb "..." \
      --source "https://..." --source-name "..." --tag skills --stamp

Exit codes: `0` added · `2` duplicate (nothing to do) · `3` validation/structure error.

## Autodeploy (the point of this repo)

This repo is connected to a **Vercel project via Git integration**. Every push to `main`
triggers an automatic production deploy — no manual `vercel deploy` needed.

    edit index.html  ->  git commit  ->  git push  ->  Vercel auto-builds & goes live

- **Framework preset:** Other / static (no build command). See `vercel.json`.
- **Production branch:** `main`.
- **Domains on the Vercel project:** `emory-agentic-os.vercel.app` (legacy, kept live) plus the
  evergreen alias added at setup. Both serve this same deployment.

## Source of truth

The canonical authored copy lives in the ShenOS vault at
`ShenLab/06-Presentations-and-Events/Visiting-Professorships/2026-06_Emory/03_Agentic-OS-Workshop/AgenticOS_Ultimate_Guide.html`.
This repo holds the **evergreen, de-Emory-ized** publication copy. When you change content,
edit `index.html` here (the repo is the deploy source of truth for the live page) and, if you
want the vault and repo to stay in lockstep, mirror the change back to the vault file.

## Editing rules (carried from the original build)

- **Curated-public only.** No real Zotero IDs/keys, no grant numbers, no theory names, no PHI.
  Every key/ID on the page is a placeholder (`<your-key>`, `<your-userID>`).
- **Keep it dependency-free.** No external `<script src>`, `<link>`, or `<img>` — it must keep
  working offline.
- **Honesty rule.** Projects + Memory are free; Cowork / Claude Code need a paid plan. Keep the
  free-vs-paid framing intact.
- **Pricing / model line-up** stay under "as of <month year>" disclaimers with a
  `claude.com/pricing` source link.

## Deploy discipline (WebOS)

Publishing follows the WebOS **Andes-prep / Olympic-publish** pattern: author anywhere, push to
`main` only from Olympic (the deploy host). The Git->Vercel integration handles the publish.
