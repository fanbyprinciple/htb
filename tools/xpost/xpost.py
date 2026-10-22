#!/usr/bin/env python3
"""
xpost - post templated "Day N. @hackthebox_eu <box> <kind> ..." updates to X.
Default: free, opens prefilled compose windows (threads included). --api: posts via the paid X API.
--polish: tidies your notes with a free LLM API (Groq by default; any OpenAI-compatible endpoint).
See README.md for setup and usage.
"""
import argparse
import json
import os
import re
import stat
import subprocess
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlencode

API = "https://api.x.com/2"
INTENT_URL = "https://x.com/intent/post"
CRED_VARS = ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET")
CONFIG_DIR = Path.home() / ".config" / "xpost"
DEFAULT_ENV = CONFIG_DIR / "credentials.env"
STATE_FILE = CONFIG_DIR / "state.json"
DEFAULT_TEMPLATE = Path(__file__).resolve().parent / "template.txt"
FIRST_DAY = 16  # used when there is no state file yet
MAX_LEN = 280
URL_RE = re.compile(r"https?://|www\.", re.I)

LLM_BASE_URL = "https://api.groq.com/openai/v1"
LLM_MODEL = "openai/gpt-oss-120b"
POLISH_PROMPT = """You tidy rough study notes into a post for X (Twitter).
The post will start with this fixed prefix, which you must NOT repeat:
"{prefix}"
Write only the text that comes right after that prefix. The prefix ends mid-sentence, so your
output MUST start with one of: "was about", "wanted me to", "taught me", "walked me through",
"had me investigate" - so "<box> sherlock <your text>" reads as a correct English sentence.
Never start with "This", "The", a past participle like "observed", or a capital letter.
Rewrite references that make no sense out of context (e.g. "this command" with no command shown)
so they name the actual thing.

Rules:
- Keep every technical fact, name, tool, command, event ID and number exactly as given. Do not invent anything.
- Remove copy-paste junk such as "Google Cloud Blog +1", citation markers, stray headings and footers.
- Plain, clear English, first person, concise. No hashtags, no emojis, no markdown, no quotes around the output.
- Stay under {budget} characters (hard limit; count carefully, be brief). If the notes genuinely need more, use short paragraphs
  separated by a blank line (it will become a thread).
- Output only the post text."""


# ---------- credentials ----------

def load_env_file(path: Path) -> None:
    """Load KEY=VALUE lines into os.environ without overriding existing vars."""
    if not path.exists():
        return
    if path.stat().st_mode & (stat.S_IRWXG | stat.S_IRWXO):
        sys.exit(f"[!] {path} is readable by group/others. Run: chmod 600 {path}")
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip().strip("'\""))


def get_session():
    missing = [v for v in CRED_VARS if not os.environ.get(v)]
    if missing:
        sys.exit(f"[!] Missing credentials: {', '.join(missing)}\n"
                 f"    Put them in {DEFAULT_ENV} (chmod 600) or export them.")
    try:
        from requests_oauthlib import OAuth1Session
    except ImportError:
        sys.exit("[!] pip install -r requirements.txt")
    return OAuth1Session(
        os.environ["X_API_KEY"],
        client_secret=os.environ["X_API_SECRET"],
        resource_owner_key=os.environ["X_ACCESS_TOKEN"],
        resource_owner_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )


# ---------- AI polish ----------

def polish(content: str, prefix: str) -> str:
    """Rewrite notes with an OpenAI-compatible chat API (free Groq tier by default)."""
    key = os.environ.get("XPOST_LLM_API_KEY")
    base = os.environ.get("XPOST_LLM_BASE_URL", LLM_BASE_URL).rstrip("/")
    if not key and "localhost" not in base and "127.0.0.1" not in base:
        sys.exit(f"[!] --polish needs XPOST_LLM_API_KEY in {DEFAULT_ENV} (see README)")
    try:
        import requests
    except ImportError:
        sys.exit("[!] pip install -r requirements.txt")
    budget = MAX_LEN - len(prefix) - 20  # margin: models undercount
    resp = requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {key}"} if key else {},
        json={
            "model": os.environ.get("XPOST_LLM_MODEL", LLM_MODEL),
            "messages": [
                {"role": "system", "content": POLISH_PROMPT.format(prefix=prefix, budget=budget)},
                {"role": "user", "content": content},
            ],
            "temperature": 0.3,
        },
        timeout=60,
    )
    if resp.status_code >= 400:
        sys.exit(f"[!] Polish failed ({resp.status_code}): {resp.text[:500]}")
    text = (resp.json()["choices"][0]["message"]["content"] or "").strip()
    text = text.strip('"\u201c\u201d').strip()
    if text.lower().startswith(prefix.lower()):  # model repeated the prefix anyway
        text = text[len(prefix):].strip()
    if not text:
        sys.exit("[!] Polish returned nothing; post without --polish")
    return clean_content(text)


def review_polish(original: str, prefix: str) -> str:
    """Show the AI version and let the user accept, retry, or keep the original."""
    while True:
        text = polish(original, prefix)
        print(f"----- AI version -----\n{prefix} {text}\n")
        while True:
            choice = ask_tty("Use it? [Y]es / [r]etry / [o]riginal / [q]uit: ").lower()[:1]
            if choice in ("", "y", "r", "o", "q"):
                break
            print("    Please answer y, r, o or q.")
        if choice in ("", "y"):
            return text
        if choice == "o":
            return original
        if choice == "q":
            sys.exit("[~] Cancelled, nothing posted.")


# ---------- day counter ----------

def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"last_day": FIRST_DAY - 1}


def record_post(state: dict, day: int, box: str, via: str, post_id=None) -> None:
    state["last_day"] = max(day, state["last_day"])
    entry = {"day": day, "box": box, "via": via}
    if post_id:
        entry["id"] = post_id
    state.setdefault("history", []).append(entry)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")
    print(f"[+] Day {day} recorded. Next run will be Day {state['last_day'] + 1}.")


# ---------- formatting ----------

def clean_content(text: str) -> str:
    """Tidy free-form notes: trim, collapse blank runs, turn '* '/'+ ' bullets into '- '."""
    lines = [re.sub(r"^\s*[*+•]\s+", "- ", ln.rstrip()) for ln in text.strip().splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines))


def split_text(text: str, limit: int) -> list[str]:
    """Cut text into chunks <= limit, preferring paragraph, line, sentence, then word breaks."""
    chunks = []
    text = text.strip()
    while len(text) > limit:
        window = text[:limit + 1]
        cut = limit
        for pat in (r"\n\n", r"\n", r"[.!?:;]\s", r"\s"):
            ends = [m.end() for m in re.finditer(pat, window) if m.end() >= limit // 2]
            if ends:
                cut = ends[-1]
                break
        chunks.append(text[:cut].rstrip())
        text = text[cut:].lstrip()
    if text:
        chunks.append(text)
    return chunks


def build_posts(template: str, day: int, box: str, kind: str, content: str) -> list[str]:
    """Render the template; if it's over the limit, split into a thread marked ' 1/n'."""
    full = template.format(day=day, box=box, kind=kind, content=content).strip()
    full = re.sub(r"[ \t]{2,}", " ", full)  # e.g. empty {kind}
    if len(full) <= MAX_LEN:
        return [full]
    parts = split_text(full, MAX_LEN - len(" 99/99"))
    n = len(parts)
    return [f"{p} {i}/{n}" for i, p in enumerate(parts, 1)]


# ---------- posting ----------

def ask_tty(prompt: str) -> str:
    """Prompt on the terminal even when content came in on stdin."""
    try:
        with open("/dev/tty") as tty:
            print(prompt, end="", flush=True)
            return tty.readline().strip()
    except OSError:
        return ""


def post_via_browser(posts: list[str]) -> bool:
    """Free mode: open X's prefilled compose page for each part, chaining replies."""
    reply_to = None
    for i, text in enumerate(posts, 1):
        params = {"text": text}
        if reply_to:
            params["in_reply_to"] = reply_to
        webbrowser.open(f"{INTENT_URL}?{urlencode(params)}")
        print(f"[+] Opened compose window for post {i}/{len(posts)} - click Post.")
        if i == len(posts):
            break
        while True:
            link = ask_tty(f"    Paste the link of post {i} to chain the next part (empty = stop): ")
            if not link:
                print("[~] Stopped. Remaining parts are printed above to post by hand.")
                return False
            m = re.search(r"(?:status/)?(\d{5,})", link)
            if m:
                reply_to = m.group(1)
                break
            print("    That doesn't look like a post link, try again.")
    return True


def post_via_api(posts: list[str]) -> str:
    if any(URL_RE.search(p) for p in posts):
        print("[~] Contains a link: X API bills link posts at a much higher rate.", file=sys.stderr)
    session = get_session()
    reply_to = None
    for text in posts:
        body = {"text": text}
        if reply_to:
            body["reply"] = {"in_reply_to_tweet_id": reply_to}
        resp = session.post(f"{API}/tweets", json=body)
        if resp.status_code >= 400:
            sys.exit(f"[!] Post failed ({resp.status_code}): {resp.text}")
        reply_to = resp.json()["data"]["id"]
        print(f"[+] https://x.com/i/status/{reply_to}")
    return reply_to


# ---------- CLI ----------

def main():
    ap = argparse.ArgumentParser(
        description="Post 'Day N. @hackthebox_eu <box> <kind> ...' updates to X")
    ap.add_argument("box", help="HTB box / sherlock / challenge name, e.g. Malicious_AutoIT")
    ap.add_argument("content", nargs="?",
                    help="what you learned; '-' or omit to read stdin")
    ap.add_argument("-k", "--kind", default="sherlock",
                    help="word after the box name: sherlock, machine, challenge... ('' for none)")
    ap.add_argument("-c", "--clip", action="store_true",
                    help="read content from the clipboard (copy your notes, then run)")
    ap.add_argument("-f", "--file", help="read content from a file (e.g. notes.md)")
    ap.add_argument("-d", "--day", type=int, help="override day number (default: last + 1)")
    ap.add_argument("-t", "--template", default=DEFAULT_TEMPLATE,
                    help="template file with {day} {box} {kind} {content}")
    ap.add_argument("-n", "--dry-run", action="store_true", help="preview only, don't post")
    ap.add_argument("-p", "--polish", action="store_true",
                    help="tidy the content with a free AI API first (you approve it)")
    ap.add_argument("--api", action="store_true",
                    help="post via the paid X API instead of free browser compose windows")
    args = ap.parse_args()

    if args.clip:
        try:
            raw = subprocess.run(["xclip", "-selection", "clipboard", "-o"],
                                 capture_output=True, text=True, check=True).stdout
        except (FileNotFoundError, subprocess.CalledProcessError):
            sys.exit("[!] Couldn't read the clipboard (needs xclip: sudo apt install xclip)")
        print(f"[+] Read {len(raw)} chars from clipboard")
    elif args.file:
        raw = Path(args.file).read_text()
    elif args.content and args.content != "-":
        raw = args.content
    else:
        if sys.stdin.isatty():
            print("Paste your notes, then press Enter and Ctrl-D:", file=sys.stderr)
        raw = sys.stdin.read()
    content = clean_content(raw)
    if not content:
        sys.exit("[!] No content given")
    load_env_file(Path(os.environ.get("XPOST_ENV", DEFAULT_ENV)).expanduser())

    state = load_state()
    day = args.day if args.day is not None else state["last_day"] + 1
    template = Path(args.template).read_text()
    if args.polish:
        prefix = template.split("{content}")[0].format(day=day, box=args.box, kind=args.kind)
        content = review_polish(content, re.sub(r"[ \t]{2,}", " ", prefix).strip())
    posts = build_posts(template, day, args.box, args.kind, content)

    for i, p in enumerate(posts, 1):
        print(f"----- post {i}/{len(posts)} ({len(p)} chars) -----\n{p}\n")
    if args.dry_run:
        print(f"[dry-run] nothing posted, counter unchanged (would be Day {day})")
        return

    if args.api:
        record_post(state, day, args.box, "api", post_via_api(posts))
    else:
        post_via_browser(posts)
        record_post(state, day, args.box, "browser")
        print(f"    Didn't actually post it? Re-run with --day {day}.")


if __name__ == "__main__":
    main()
