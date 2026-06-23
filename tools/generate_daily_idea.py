#!/usr/bin/env python3
"""
generate_daily_idea.py — ask Claude (with web search) for ONE sourced agentic-OS idea,
emit it as JSON for update_daily_signal.py to splice in.

Used by the daily GitHub Action. Requires ANTHROPIC_API_KEY in the environment.

Output: writes the idea to the path given by --out (default new_idea.json) and prints it.
Exit codes: 0 = idea written; 4 = model declined / nothing solid (skip the day, do not commit).

Guardrails are enforced both in the prompt AND here: the result must carry a real http(s)
source URL or we treat it as a skip. update_daily_signal.py re-validates and de-dups.
"""
import argparse, datetime, json, os, re, sys

MODEL = os.environ.get("DAILY_MODEL", "claude-sonnet-4-6")
ALLOWED_TAGS = {"skills", "connectors", "memory", "technique", "orchestration", "governance", "cost", "claude"}

SYSTEM = (
    "You curate a daily 'Daily Signal' for a public teaching page about building a personal "
    "agentic OS. The page carries Dr. Jon Schoenecker's name. You are conservative, accurate, "
    "and strictly source-bound. You never invent benchmarks, quotes, novelty claims, or any "
    "title/role/credential for Dr. Schoenecker. You write for a smart non-expert (a "
    "surgeon-scientist), not an engineer."
)

def build_prompt(recent_titles):
    avoid = "\n".join(f"  - {t}" for t in recent_titles) or "  (none yet)"
    return f"""Use web search to find ONE concrete, genuinely useful, recent idea or feature for
*building* a personal agentic OS — agents, skills, memory, MCP/connectors, context engineering,
orchestration, verification, governance, or cost/latency. Prefer something new or newly clarified.

Good public wells: anthropic.com/news, anthropic.com/engineering, docs.anthropic.com,
docs.claude.com, modelcontextprotocol.io, the AI Daily Brief, aidbagentos.ai.

Do NOT repeat any of these already-published ideas (pick something distinct):
{avoid}

Return ONLY a single JSON object (no prose, no code fence) with EXACTLY these keys:
  "title"      : <= 60 chars, plain language, names the thing.
  "blurb"      : 2-3 sentences (<= 600 chars). What it is + what it means for THEIR OS.
  "source"     : a real public http(s) URL you actually consulted via web search.
  "sourceName" : short label, e.g. "Anthropic Engineering".
  "tag"        : one of: skills, connectors, memory, technique, orchestration, governance, cost, claude.

Hard rules: only claims the source supports; no hype ("first/novel/breakthrough"); no vendor/
medical/legal advice; no secrets/PHI; no invented credentials. If you cannot find something solid,
new, and properly sourced, return exactly: {{"skip": true}}"""

def extract_json(text):
    text = text.strip()
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0)) if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="new_idea.json")
    ap.add_argument("--index", default="index.html")
    a = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr); sys.exit(3)

    # recent titles (so we don't repeat)
    recent = []
    try:
        h = open(a.index, encoding="utf-8").read()
        m = re.search(r'id="daily-signal-data">(.*?)</script>', h, re.S)
        recent = [it["title"] for it in json.loads(m.group(1)).get("items", [])][:15]
    except Exception:
        pass

    try:
        import anthropic
    except ImportError:
        print("ERROR: pip install anthropic", file=sys.stderr); sys.exit(3)

    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=MODEL, max_tokens=1024, system=SYSTEM,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
        messages=[{"role": "user", "content": build_prompt(recent)}],
    )
    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    idea = extract_json(text)

    if not idea or idea.get("skip"):
        print("SKIP: model returned no solid idea today."); sys.exit(4)
    for k in ("title", "blurb", "source", "sourceName", "tag"):
        if not idea.get(k):
            print(f"SKIP: missing field {k} — treating as skip."); sys.exit(4)
    if not str(idea["source"]).startswith(("http://", "https://")):
        print("SKIP: no valid source URL."); sys.exit(4)
    if idea["tag"] not in ALLOWED_TAGS:
        idea["tag"] = "technique"
    idea["date"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    open(a.out, "w", encoding="utf-8").write(json.dumps(idea, ensure_ascii=False, indent=2))
    print("IDEA:", json.dumps(idea, ensure_ascii=False))

if __name__ == "__main__":
    main()
