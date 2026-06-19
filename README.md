# Build Your Own Agentic OS — teaching build console

An evergreen, self-contained teaching page that walks anyone through building their own
**agentic OS** — from a first Project to a full skill-library + vault + connectors setup.
Part of the **TŌGE** family. By Dr. Jon Schoenecker.

**Live:** https://emory-agentic-os.vercel.app (existing alias, preserved for residents who already have the link)

## What this repo is

A single, dependency-free `index.html` (~144 KB). No build step, no framework, no external
requests — it opens offline and renders identically anywhere. The page is an 11-tab build
console: Why · Square One · OS Core · Connectors · ★ Zotero + Papers · Cowork · Claude Code ·
The Graph · Skills · At Scale · Reference.

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
