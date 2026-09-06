This is a comprehensive Substack-style writeup detailing the exploitation of the machine **Cap** (10.129.12.165). This walkthrough covers the journey from initial packet analysis to exploiting misconfigured Linux capabilities for full root access.

---

# Cracking "Cap": A Deep Dive into PCAP Leaks and Python Capabilities

Welcome back to the lab. Today, we’re tackling **Cap**, a machine that reminds us why cleartext protocols and "convenient" security dashboards are a dangerous combination.

### 1. Initial Reconnaissance: The Open Gates

We started with a standard Nmap scan to see what we were up against. The results showed a fairly standard attack surface:

```bash
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 8.2p1
80/tcp open  http    Gunicorn (Security Dashboard)

```

We have **FTP**, **SSH**, and a **Web Server**. Initial checks for anonymous FTP login returned nothing, and the SSH version didn't have any immediate "low-hanging fruit" exploits. Our focus shifted to the web server running on port 80.

### 2. Web Enumeration: The "Security Dashboard"

The website presents itself as a "Security Dashboard." Navigating the site, we noticed it provides various network diagnostic tools like `netstat` and `ip` information.

Using `gobuster`, we identified several interesting directories:

* `/data`: Redirects to packet capture summaries.
* `/capture`: Appears to trigger a fresh packet capture.

The `/data` endpoint used an incremental ID system (e.g., `/data/0`, `/data/1`). This is a classic indicator of an **Insecure Direct Object Reference (IDOR)** vulnerability. While `/data/1` and `/data/2` showed relatively empty traffic, navigating back to `/data/0` revealed a goldmine.

### 3. The Foothold: Analyzing the PCAP

On the `/data/0` page, the dashboard allowed us to download a `.pcap` file of past network traffic.

Opening this file in Wireshark (or simply using `tcpdump`), we followed the TCP streams. Because FTP is a cleartext protocol, the credentials used by a user named **nathan** were sitting right there in the packets:

* **User:** `nathan`
* **Password:** `Buck3tH4TF0RM3!`

### 4. Entry: FTP & SSH Access

Armed with these credentials, we pivoted back to the open services. We successfully logged into FTP and retrieved the `user.txt` flag. Knowing that users often reuse passwords, we tried the same credentials for **SSH**:

```bash
ssh nathan@10.129.12.165
# Success!

```

### 5. Privilege Escalation: The Power of Capabilities

Once inside as `nathan`, we performed local enumeration. A check of `sudo -l` yielded nothing useful, and standard SUID binaries like `pkexec` were correctly patched.

However, we hit the jackpot when checking for **Linux Capabilities**. Linux uses capabilities to grant specific privileges to binaries without making them full SUID root. We ran the following command:
`getcap -r / 2>/dev/null`

The output was startling:

```text
/usr/bin/python3.8 = cap_setuid,cap_net_bind_service+eip

```

This means the Python 3.8 binary has the `cap_setuid` capability. This "superpower" allows Python to manipulate process UIDs. Since Python is an interpreter, we can write a one-liner to tell it to change our User ID to 0 (root) and spawn a shell.

**The Exploit:**

```bash
python3.8 -c 'import os; os.setuid(0); os.system("/bin/bash")'

```

Immediately, the prompt changed. A quick `whoami` confirmed we were now **root**.

### 6. Lessons Learned

**Cap** is a perfect example of two major security failures:

1. **Exposing Sensitive Data:** Always protect diagnostic data. The PCAP files contained cleartext credentials because the system was using FTP—a protocol that should be replaced with SFTP in any modern environment.
2. **Over-Privileging Binaries:** Granting `cap_setuid` to a powerful tool like Python is equivalent to giving every user a root key. Capabilities should be applied sparingly and never to interpreters that can execute arbitrary code.

**Status:** *Machine Pwned.*

---

*If you enjoyed this writeup, consider subscribing to our newsletter for weekly deep dives into CTF challenges and real-world penetration testing techniques.*