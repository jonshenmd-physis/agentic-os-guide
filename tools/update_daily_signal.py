#!/usr/bin/env python3
"""
update_daily_signal.py — deterministically splice a new "Daily Signal" idea into index.html.

The page is a single self-contained HTML file (offline-safe, zero deps). The daily ideas
live in ONE inline JSON block between these exact markers:

    <!-- DAILY_SIGNAL_START ... -->
    <script type="application/json" id="daily-signal-data"> {...} </script>
    <!-- DAILY_SIGNAL_END -->

This script rewrites ONLY that block — nothing else in the file is touched. The LLM that runs
the daily job supplies the *content* of one idea (title / blurb / source); this script does the
file surgery, so there is no risk of an LLM mangling the rest of the page.

Usage (one new idea):
    python tools/update_daily_signal.py \
        --title "Agent Skills: teach your OS a job once" \
        --blurb "A Skill is a small folder of instructions the model loads on demand..." \
        --source "https://www.anthropic.com/news/agent-skills" \
        --source-name "Anthropic — Agent Skills" \
        --tag skills

Or from a JSON file holding {"title","blurb","source","sourceName","tag","date"}:
    python tools/update_daily_signal.py --from-file new_idea.json

Flags:
    --date YYYY-MM-DD   date for the item + the "updated" stamp (default: today, UTC)
    --max N             cap the archive at N items (default 40)
    --stamp             also bump the top-of-file <!-- build ... --> marker (traceability)
    --dry-run           print what would change; do not write
Exit codes: 0 ok, 2 nothing-to-do (duplicate), 3 validation/structure error.
"""
import argparse, datetime, json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

START = "<!-- DAILY_SIGNAL_START"
END = "<!-- DAILY_SIGNAL_END -->"
DATA_RE = re.compile(
    r'(<script type="application/json" id="daily-signal-data">)(.*?)(</script>)',
    re.S,
)
BUILD_RE = re.compile(r"<!-- build [0-9]+ -->")


def fail(msg, code=3):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title")
    ap.add_argument("--blurb")
    ap.add_argument("--source")
    ap.add_argument("--source-name", dest="source_name")
    ap.add_argument("--tag", default="technique")
    ap.add_argument("--date")
    ap.add_argument("--from-file")
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--stamp", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    today = a.date or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", today):
        fail(f"--date must be YYYY-MM-DD, got {today!r}")

    if a.from_file:
        item = json.loads(pathlib.Path(a.from_file).read_text(encoding="utf-8"))
    else:
        item = {
            "title": a.title, "blurb": a.blurb, "source": a.source,
            "sourceName": a.source_name, "tag": a.tag,
        }
    item.setdefault("date", today)
    item.setdefault("tag", a.tag or "technique")
    item.setdefault("sourceName", item.get("source"))

    # ---- validate the idea ----
    for k in ("title", "blurb", "source"):
        if not item.get(k) or not str(item[k]).strip():
            fail(f"missing required field: {k}  (source URL is mandatory — no source, no publish)")
    if not str(item["source"]).startswith(("http://", "https://")):
        fail("source must be an http(s) URL")
    if len(item["blurb"]) > 600:
        fail("blurb too long (>600 chars) — keep it tight")

    if not INDEX.exists():
        fail(f"index.html not found at {INDEX}")
    html = INDEX.read_text(encoding="utf-8")
    if START not in html or END not in html:
        fail("DAILY_SIGNAL markers not found — page structure changed; refusing to write")

    m = DATA_RE.search(html)
    if not m:
        fail("daily-signal-data <script> block not found")
    try:
        data = json.loads(m.group(2))
    except json.JSONDecodeError as e:
        fail(f"existing daily-signal JSON is invalid: {e}")

    items = data.get("items", [])
    # de-dup by normalized title
    norm = lambda s: re.sub(r"\s+", " ", str(s)).strip().lower()
    if any(norm(it.get("title")) == norm(item["title"]) for it in items):
        print(f"DUPLICATE: '{item['title']}' already present — nothing to do.")
        sys.exit(2)

    items.insert(0, {
        "date": item["date"], "tag": item["tag"], "title": item["title"].strip(),
        "blurb": item["blurb"].strip(), "source": item["source"].strip(),
        "sourceName": str(item["sourceName"]).strip(),
    })
    data["items"] = items[: a.max]
    data["updated"] = today

    new_json = json.dumps(data, indent=2, ensure_ascii=False)
    # sanity: it must re-parse
    json.loads(new_json)
    new_block = m.group(1) + "\n" + new_json + "\n" + m.group(3)
    new_html = html[: m.start()] + new_block + html[m.end():]

    if a.stamp:
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
        new_html = BUILD_RE.sub(f"<!-- build {stamp} -->", new_html, count=1)

    # final guards: markers + build marker survive
    if START not in new_html or END not in new_html:
        fail("post-write markers missing — aborting")
    if not BUILD_RE.search(new_html):
        fail("build marker lost — aborting")

    if a.dry_run:
        print(f"[dry-run] would add: {item['date']} [{item['tag']}] {item['title']}")
        print(f"[dry-run] archive size would be {len(data['items'])}")
        return
    INDEX.write_text(new_html, encoding="utf-8")
    print(f"OK added: {item['date']} [{item['tag']}] {item['title']}")
    print(f"archive size: {len(data['items'])}  updated: {today}")


if __name__ == "__main__":
    main()
