$ nmap -sV -p- <ip>
...
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.38 ((Debian))

$ gobuster dir -u <ip>:80 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
...
/images               (Status: 301) [Size: 317] [--> http://10.129.146.191/images/]
/css                  (Status: 301) [Size: 314] [--> http://10.129.146.191/css/]
/js                   (Status: 301) [Size: 313] [--> http://10.129.146.191/js/]
/vendor               (Status: 301) [Size: 317] [--> http://10.129.146.191/vendor/]
/fonts                (Status: 301) [Size: 316] [--> http://10.129.146.191/fonts/]
/server-status        (Status: 403) [Size: 279]
...

$ firefox <ip>:80 &

e3d0796d002a446c0e622226f42e9672
