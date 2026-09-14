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

ffuf -u http://jobs.amzcorp.local -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt -H "Host: FUZZ.enigma.htb" -fs 154

ffuf -w /usr/share/wordlists/dirb/common.txt -u http://jobs.amzcorp.local

ffuf -w /usr/share/wordlists/dirb/common.txt -u http://jobs.amzcorp.local/FUZZ -fc 404

└─$ ffuf -w /usr/share/wordlists/dirb/common.txt -u http://jobs.amzcorp.local/FUZZ -fc 404

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://jobs.amzcorp.local/FUZZ
 :: Wordlist         : FUZZ: /usr/share/wordlists/dirb/common.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response status: 404
________________________________________________

                        [Status: 302, Size: 218, Words: 21, Lines: 4, Duration: 573ms]
forgot-password         [Status: 200, Size: 5659, Words: 1, Lines: 1, Duration: 2218ms]
logout                  [Status: 302, Size: 218, Words: 21, Lines: 4, Duration: 1511ms]
login                   [Status: 200, Size: 7951, Words: 1, Lines: 1, Duration: 3076ms]
register                [Status: 200, Size: 8441, Words: 2841, Lines: 148, Duration: 1491ms]
settings                [Status: 403, Size: 4334, Words: 606, Lines: 90, Duration: 918ms]
:: Progress: [4614/4614] :: Job [1/1] :: 57 req/sec :: Duration: [0:01:17] :: Errors: 0 ::

Host is up (0.34s latency).
Not shown: 65408 closed tcp ports (reset), 101 filtered tcp ports (no-response)
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Apache httpd 2.4.52 ((Win64))
|_http-server-header: Apache/2.4.52 (Win64)
| http-methods: 
|   Supported Methods: GET POST OPTIONS HEAD TRACE
|_  Potentially risky methods: TRACE
|_http-title: Site doesn't have a title (text/html).
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-09-14 15:13:49Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
2179/tcp  open  vmrdp?
3268/tcp  open  ldap
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49672/tcp open  msrpc         Microsoft Windows RPC
49676/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49677/tcp open  msrpc         Microsoft Windows RPC
49688/tcp open  msrpc         Microsoft Windows RPC
49704/tcp open  msrpc         Microsoft Windows RPC
50158/tcp open  msrpc         Microsoft Windows RPC
Device type: general purpose
Running: Microsoft Windows 2019
OS CPE: cpe:/o:microsoft:windows_server_2019
OS details: Microsoft Windows Server 2019
Network Distance: 2 hops
TCP Sequence Prediction: Difficulty=262 (Good luck!)
IP ID Sequence Generation: Busy server or unknown class
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-09-14T15:14:53
|_  start_date: N/A

TRACEROUTE (using port 80/tcp)
HOP RTT       ADDRESS
1   440.34 ms 10.10.14.1
2   440.42 ms jobs.amzcorp.local (10.13.37.15)

NSE: Script Post-scanning.
Initiating NSE at 11:15
Completed NSE at 11:15, 0.00s elapsed
Initiating NSE at 11:15
Completed NSE at 11:15, 0.00s elapsed
Initiating NSE at 11:15
Completed NSE at 11:15, 0.00s elapsed
Read data files from: /usr/share/nmap
OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 5075.00 seconds
           Raw packets sent: 80109 (3.525MB) | Rcvd: 212039 (34.013MB)

________________________________________________

                        [Status: 302, Size: 218, Words: 21, Lines: 4, Duration: 573ms]
forgot-password         [Status: 200, Size: 5659, Words: 1, Lines: 1, Duration: 2218ms]
logout                  [Status: 302, Size: 218, Words: 21, Lines: 4, Duration: 1511ms]
login                   [Status: 200, Size: 7951, Words: 1, Lines: 1, Duration: 3076ms]
register                [Status: 200, Size: 8441, Words: 2841, Lines: 148, Duration: 1491ms]
settings                [Status: 403, Size: 4334, Words: 606, Lines: 90, Duration: 918ms]
:: Progress: [4614/4614] :: Job [1/1] :: 57 req/sec :: Duration: [0:01:17] :: Errors: 0 ::
