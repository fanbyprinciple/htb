https://lazyhackers.com/article/stream-htb-writeups-season-12

Stream — Linux Recon & PrivEsc Cheatsheet
1. Initial Recon
Port & service scan

# Fast full-port sweep, then targeted service/version scan
nmap -p- --min-rate 5000 -oA stream-all 10.10.X.X
nmap -sC -sV -p 22,80,443 -oA stream-svc 10.10.X.X

# UDP quick check (top ports)
sudo nmap -sU --top-ports 50 10.10.X.X

Web enumeration

# Directory + file brute force
feroxbuster -u http://10.10.X.X -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt -x php,txt,html

# Virtual hosts / subdomains
ffuf -u http://10.10.X.X -H "Host: FUZZ.stream.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 0

# Tech fingerprint
whatweb http://10.10.X.X
nikto -h http://10.10.X.X

Add discovered hostnames to /etc/hosts. For a "Stream" box, hunt specifically for: upload endpoints, media players (HLS .m3u8, RTMP), log/event dashboards, and any ffmpeg/gstreamer processing on the back end.
2. Local Enumeration (after foothold)

# Drop and run an automated enumerator
./linpeas.sh | tee linpeas.out
# alt: ./lse.sh -l1   |   ./pspy64   (watch for root-run cron / media jobs)

# Manual quick-wins
id; sudo -l                       # sudo rights
uname -a; cat /etc/os-release     # kernel + distro -> maps to CVEs below
find / -perm -4000 -type f 2>/dev/null   # SUID binaries
getcap -r / 2>/dev/null           # capabilities
cat /etc/crontab; ls -la /etc/cron.*     # scheduled jobs
ss -tulpn                         # internal listening services
ps aux --forest                   # who runs what (look for root ffmpeg)

Key idea: capture uname -a and /etc/os-release first — the kernel version and distro decide which CVE below actually applies.
3. Collective CVE Hit-List (Linux LPE)

Ordered newest first. Match the target's distro/kernel/package version before firing — wrong-version kernel exploits crash the box.
CVE 	Name 	Component 	Affected 	Quick check
CVE-2025-6019 	(chained with 6018) 	libblockdev via udisks daemon 	udisks ships by default on nearly all distros; PoC confirmed on Ubuntu, Debian, Fedora, openSUSE 	udisksctl version
CVE-2025-6018 	PAM "allow_active" 	PAM config 	openSUSE Leap 15 / SLES 15 (gives allow_active, the pre-req for 6019) 	local SSH session treated as console
CVE-2024-1086 	— 	Kernel nf_tables (netfilter) UAF 	Linux kernel 5.14 – 6.6 range 	uname -r
CVE-2023-4911 	Looney Tunables 	glibc dynamic loader (GLIBC_TUNABLES) 	glibc 2.34+; Debian/Ubuntu/Fedora defaults of the era 	ldd --version
CVE-2023-0386 	— 	Kernel OverlayFS 	Kernel < 5.19 (patched in 6.2) 	uname -r
CVE-2023-2640 / 32629 	GameOver(lay) 	OverlayFS (Ubuntu-specific) 	Ubuntu 20.04/22.04 HWE kernels 	cat /etc/os-release
CVE-2022-0847 	Dirty Pipe 	Kernel pipe/splice 	Kernel 5.8 – 5.16.11 / 5.15.25 / 5.10.102 	uname -r
CVE-2021-4034 	PwnKit 	polkit pkexec 	Nearly all distros pre-2022; very reliable 	ls -l $(which pkexec)
CVE-2021-3156 	Baron Samedit 	sudo heap overflow 	sudo 1.8.2 – 1.8.31p2, 1.9.0 – 1.9.5p1 	sudo --version

Note: CVE-2025-6018 + CVE-2025-6019 is a two-stage chain — 6018 grants the allow_active context that 6019 needs to reach root through udisks. Treat them as one path.
4. Privilege Escalation Playbook
Check the cheap wins before dropping a kernel exploit

    sudo -l — any NOPASSWD entry, or a binary with a GTFOBins escape.
    SUID binaries — cross-reference the find -perm -4000 output against GTFOBins.
    Capabilities — cap_setuid on python/perl = instant root.
    Cron / services as root — writable script path, or a job that processes your uploaded file (prime for the "Stream" media-job theory: filename/metadata command injection).
    Writable sensitive files — /etc/passwd, /etc/shadow, /etc/sudoers.d/, service unit files, PATH hijack on a root script.
    Reused / leaked creds — config files, .bash_history, DB dumps, SSH keys from the foothold file-read.
    Kernel/package CVE — only after the above, and only after version-matching the table.

Useful one-liners

# SUID -> check GTFOBins for each hit
find / -perm -4000 -type f 2>/dev/null

# Capabilities granting setuid
getcap -r / 2>/dev/null | grep -i cap_setuid

# Watch cron / root processes live (no root needed)
./pspy64

# Writable files owned by root
find / -writable -type f 2>/dev/null | grep -v -e '^/proc' -e '^/sys'

# Stabilize a shell
python3 -c 'import pty;pty.spawn("/bin/bash")'; export TERM=xterm; # then Ctrl-Z, stty raw -echo; fg

5. Predicted Path (our call)

Web app → server-side ffmpeg/media file-read or RCE → leaked service creds → root via a privileged media job (filename/metadata command injection) or a version-matched CVE from the table. Confidence that media processing is the gimmick: ~70%.

Stream Machine Summary

Stream is a medium-difficulty Linux machine on Hack The Box that focuses on web application enumeration, sensitive information disclosure, XML External Entity (XXE) injection, credential reuse, lateral movement, backup analysis, and privilege escalation through a misconfigured ClickHouse database and a root-executed systemd service.

The exploitation process begins with Nmap enumeration, which reveals SSH, an Nginx web server, and a Uvicorn-based AIDX ingestion service running on port 8081. After configuring the local /etc/hosts file, I enumerate the web applications, API directories, and Swagger documentation to identify available endpoints and understand the application's functionality. Testing the AIDX XML endpoint confirms that it accepts flight-leg data, while virtual host enumeration reveals additional API and ClickHouse database subdomains. I update my hosts file accordingly and investigate the ClickHouse interface, authentication requirements, database endpoints, and accessible directories.

Further API directory enumeration exposes a Spring Boot Actuator heapdump endpoint, allowing me to download and analyze a Java heap memory dump. By examining the heapdump, I recover database credentials, identify JDBC configuration details, and enumerate database user information. I then reuse the extracted credentials to authenticate to ClickHouse, enumerate its databases and tables, and investigate the stored flight-leg records.

The next stage involves exploiting an XML External Entity (XXE) vulnerability in the AIDX ingestion service. I prepare and submit a malicious XML payload that references /etc/passwd, then retrieve the disclosed file contents through ClickHouse. After confirming arbitrary local file disclosure, I modify the payload to target the Kafka server configuration file. Submitting this payload exposes Kafka authentication credentials, which I successfully reuse to establish an SSH session as svc-infra.

With an initial foothold established, I enumerate the local system, user accounts, home directories, and sudo privileges. After identifying the martin_cole account, I perform an SU password brute-force attack and recover its password. I then switch to martin_cole, enumerate the user's environment, and retrieve the user flag.

During further enumeration, I discover a Kopia backup repository in the user's home directory. I authenticate to the repository using the recovered password, enumerate its available snapshots, and restore a backup containing ClickHouse server logs. Analyzing these logs reveals a plaintext password associated with the ClickHouse default account. I subsequently verify that the disclosed credentials provide database access.

For privilege escalation, I investigate a scheduled systemd service responsible for processing AIDX dead-letter queue messages. The service executes /opt/ops/dlq_drainer.py as root and references a Python formatter located inside ClickHouse's user_files directory. Although direct filesystem access to this location is restricted, my authenticated ClickHouse session provides an alternative attack surface.

I configure a Netcat reverse shell listener and abuse the ClickHouse file() table function to write a malicious Python reverse shell payload into the formatter script. After submitting another AIDX XML request and waiting for the scheduled drainer to execute, I receive a reverse shell running as root. Finally, I verify administrative privileges using whoami and id, then retrieve the root flag from /root/root.txt, completing the machine.

Overall, Stream demonstrates how multiple weaknesses can be chained together to achieve a complete system compromise. The attack path combines exposed diagnostic endpoints, credential leakage, XXE-based file disclosure, password reuse, insecure backup contents, database file-write capabilities, and privileged scheduled execution, progressing from unauthenticated reconnaissance to full root access.
HackTheBox Stream Walkthrough - Season 12 HTB Writeup Aero Machines


THe ip is 10.129.4.57

