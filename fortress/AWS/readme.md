https://github.com/momenbasel/htb-writeups/blob/main/fortresses/README.md

└─$ nmap -F 10.13.37.15                
Starting Nmap 7.95 ( https://nmap.org ) at 2026-08-02 13:10 EDT
Nmap scan report for 10.13.37.15
Host is up (0.40s latency).
Not shown: 93 closed tcp ports (reset)
PORT    STATE SERVICE
53/tcp  open  domain
80/tcp  open  http
88/tcp  open  kerberos-sec
135/tcp open  msrpc
139/tcp open  netbios-ssn
389/tcp open  ldap
445/tcp open  microsoft-ds

Nmap done: 1 IP address (1 host up) scanned in 2.08 seconds

┌──(ajp㉿kali)-[~/codeplay/exploitdev-notes/htb/fortress]
└─$ curl 10.13.37.15
<html><meta http-equiv="refresh" content="0; url=http://jobs.amzcorp.local/" /></html>                                                         


Sudo nmap -sS -Pn -T5 -p- 10.13.37.15