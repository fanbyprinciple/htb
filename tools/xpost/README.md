# xpost

Post daily HTB learning updates to X in a fixed format:

```
Day 16. @hackthebox_eu Malicious_AutoIT sherlock wanted me to analyse an AutoIT file. ...
```

You give the box name and your notes. xpost fills the template, adds the day
number (it goes up by itself each run, starting at **16**), and turns anything
over 280 characters into a thread with ` 1/n` markers. It never adds images.

## Two ways to post

| Mode | Cost | Setup | How it posts |
|------|------|-------|--------------|
| **Browser (default)** | Free | None | Opens X's compose window with the text filled in. You click **Post**. |
| `--api` | Paid (X pay-per-use, about $0.015 per post, much more if it has a link) | API keys | Posts by itself, whole threads included. |

Browser mode uses X's official share link (`x.com/intent/post`), so it is
within X's rules and needs no credentials. Make sure you're logged in to X in
your default browser.

## Usage

Write your content as the words that follow `<box> sherlock`:

```sh
# Day N. @hackthebox_eu Malicious_AutoIT sherlock wanted me to analyse ...
xpost Malicious_AutoIT "wanted me to analyse an AutoIT file. AutoIt is ..."

# machines / challenges: change the word after the box name
xpost Lame -k machine "taught me ..."
xpost SomeBox -k ""   "..."          # no word at all

# easiest: copy your notes (Ctrl-C in the browser), then
xpost UFO-1 -p -c

# content from a notes file
xpost Campfire -f ../../sherlocks/Campfire/notes.md

# or paste right into the terminal, then press Enter and Ctrl-D
xpost Brutus

# preview without posting (day counter is not changed)
xpost Brutus "notes..." -n

# set the day yourself (fixes the count; later runs carry on from it)
xpost Brutus "notes..." --day 20

# let a free AI tidy your notes first (you approve before anything posts)
xpost UFO-1 -p "pasted notes..."

# post through the API instead (see "API setup" below)
xpost Brutus "notes..." --api
```

| Option | Meaning |
|--------|---------|
| `box` | Box, sherlock or challenge name (required) |
| `content` | Your notes. Leave it out or pass `-` to read stdin |
| `-k, --kind W` | Word after the box name (default `sherlock`) |
| `-c, --clip` | Read notes from the clipboard (needs `xclip`) |
| `-f, --file` | Read notes from a file |
| `-d, --day N` | Use day N (the default is last day + 1) |
| `-t, --template F` | Use a different template file |
| `-n, --dry-run` | Preview only |
| `-p, --polish` | Tidy notes with a free AI API first (see "AI polish") |
| `--api` | Post via the paid X API |

### Threads

If the post is over 280 characters, xpost splits it, preferring paragraph,
then line, then sentence, then word breaks. It adds ` 1/3`, ` 2/3`, ...
to the end of each part.

In free browser mode the thread is built with you:

1. A compose window opens for part 1. Click **Post**.
2. Copy that post's link (or just its number) and paste it into the terminal.
3. The next compose window opens as a **reply** to it. Repeat until done.

Press Enter at the prompt with nothing typed to stop. The remaining parts stay
printed in the terminal. With `--api` the whole thread is posted
automatically.

### Content formatting

- Surrounding whitespace is trimmed, and 3 or more blank lines become one.
- `*`, `+` and `•` bullets are converted to `- `.
- Character counts are approximate: X counts links as 23 characters and some
  emoji as 2.

### Day counter

Stored in `~/.config/xpost/state.json` along with a history of each post. It
starts at Day 16 and goes up by one after each post (in browser mode, once the
compose windows have been opened). If you didn't actually post, re-run with
`--day N`. To change where the count starts, edit `last_day` in that file.

## AI polish (`-p`, free)

`-p` sends your notes to an AI model, which rewrites them to follow
`Day N. @hackthebox_eu <box> sherlock` naturally. It removes copy-paste junk
like `Google Cloud Blog +1` and keeps facts, tools and IDs unchanged. You
always see the result first:

```
----- AI version -----
Day 16. @hackthebox_eu UFO-1 sherlock covered how Sandworm abused scilc.exe ...
Use it? [Y]es / [r]etry / [o]riginal / [q]uit:
```

`r` asks for another version, and `o` posts your original text instead.
Without `-p`, no AI is involved: your text is only formatted, never reworded.

### Setup (one time, free)

1. Get a free key at https://console.groq.com/keys (no card needed). The
   free tier allows roughly 1,000 requests a day on this model.
2. Add it to `~/.config/xpost/credentials.env` (the same file the X API keys
   use; create it with `chmod 600`):
   ```
   XPOST_LLM_API_KEY=gsk_...
   ```

`requests` is the only dependency; Kali already has it.

### Using a different provider

Any OpenAI-compatible API works. Set these in the same file:

| Provider | `XPOST_LLM_BASE_URL` | `XPOST_LLM_MODEL` (example) |
|----------|----------------------|-----------------------------|
| Groq (default) | `https://api.groq.com/openai/v1` | `openai/gpt-oss-120b` |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta/openai` | `gemini-2.5-flash` |
| OpenRouter | `https://openrouter.ai/api/v1` | any model ending in `:free` |
| Ollama (local, offline, no key) | `http://localhost:11434/v1` | `llama3.2` |

Free tiers and model names change often. If you get an error about the model,
check the provider's model list and update `XPOST_LLM_MODEL`. Also, free
tiers (Gemini especially) may use your prompts for training. That's fine for
public writeup notes, but don't send anything sensitive.

## Customising the template

Edit `template.txt`. It supports `{day}`, `{box}`, `{kind}` and `{content}`:

```
Day {day}. @hackthebox_eu {box} {kind} {content}
```

For a one-off format, use `-t other.txt`.

## API setup (only for `--api`)

1. Go to https://developer.x.com and create an app on the account you want
   to post from. Add credits; new accounts usually get starter credits.
2. Set **User authentication settings -> App permissions = Read and Write**,
   *then* generate the API Key/Secret and the Access Token/Secret. Tokens
   generated before that change are read-only and will fail with a 403.
3. Store the keys **outside this repo** (it is pushed to GitHub):
   ```sh
   mkdir -p ~/.config/xpost
   cp credentials.env.example ~/.config/xpost/credentials.env
   chmod 600 ~/.config/xpost/credentials.env   # xpost won't read the file otherwise
   nano ~/.config/xpost/credentials.env
   ```
   Exported `X_API_KEY` / `X_API_SECRET` / `X_ACCESS_TOKEN` /
   `X_ACCESS_TOKEN_SECRET` override the file, so you can inject them from
   `pass` or another secret manager instead. Use `XPOST_ENV=/path` to point at
   a different file.
4. Install the dependencies (browser mode doesn't need them):
   ```sh
   python3 -m venv ~/.venvs/xpost
   ~/.venvs/xpost/bin/pip install -r requirements.txt
   ~/.venvs/xpost/bin/python xpost.py Campfire "notes" --api
   ```

## Running it from anywhere

`xpost` is a symlink to this script in `~/.local/bin` (which is on PATH):

```sh
ln -sf "$PWD/xpost.py" ~/.local/bin/xpost   # (re)create
rm ~/.local/bin/xpost                       # remove
```

Without it, run `python3 tools/xpost/xpost.py ...` from the repo root.
