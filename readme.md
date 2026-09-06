

 |  |              |      |    |             |               
 __ |   _` |   _|  | /     _|    \    -_)     _ \   _ \ \ \ /
_| _| \__,_| \__| _\_\   \__| _| _| \___|   _.__/ \___/  _\_\


Things to do to a box

1. do the nmap scan
`nmap -F 10.129.75.201`

2. put the hostname on /etc/hosts

`sudo nano /etc/hosts`

3. enumerate subdomains

`ffuf -u http://nexus.htb -H "HOST:FUZZ.nexus.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -ac`

4. Always keep a file for all username/ emails and password. During brute force attempts try everything with everything

5. If there is a git repo, there are commit based flags.

6. Always look for version number of the software, if they are exploitable.

7. 


