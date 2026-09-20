

 |  |              |      |    |             |               
 __ |   _` |   _|  | /     _|    \    -_)     _ \   _ \ \ \ /
_| _| \__,_| \__| _\_\   \__| _| _| \___|   _.__/ \___/  _\_\


Things to do to a box

1. do the nmap scan
`nmap -F 10.129.75.201`

`nmap -A -T4 -p- -v 10.129.58.231`

2. put the hostname on /etc/hosts

`sudo nano /etc/hosts` even subdomains.

3. enumerate subdomains

`ffuf -u http://silentium.htb/ -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt -H "Host: FUZZ.silentium.htb" -fs 154 -fc 301,302 -ac`

`ffuf -w /usr/share/wordlists/dirb/common.txt -u http://silentium.htb/FUZZ -fc 404 -ac`

in case it returns wildcard response then fuzz based on the size

first determine the size

`curl -s -o /dev/null -w '%{http_code} %{size_download}\n' http://silentium.htb/thisdefinitelydoesnotexist123`

find the size and filter

`ffuf -w /usr/share/wordlists/dirb/common.txt -u http://silentium.htb/FUZZ -fs 154`

we can also autocalibrate

`ffuf -w /usr/share/wordlists/dirb/common.txt -u http://silentium.htb/FUZZ -ac`

4. Always keep a file for all username/ emails and password. During brute force attempts try everything with everything

5. If there is a git repo, there are commit based flags.

6. Always look for version number of the software, if they are exploitable.

7. if we see a wildcard in the tls its a give away then there could be sub domain.

8. if port 111, 2049 then nfs mount might be there.

9. in webmail try same password with all users.

10. look at the cronjob.

11. Webpages can reveal user name

for email we can try user@domain_name to try and brute force.





