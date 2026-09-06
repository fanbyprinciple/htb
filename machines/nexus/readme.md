https://medium.com/@indigoshadowwashere/hackthebox-walkthrough-nexus-f48a53ea87d5

─$ nmap -F 10.129.75.201
Starting Nmap 7.95 ( https://nmap.org ) at 2026-08-04 14:12 EDT
Nmap scan report for 10.129.75.201
Host is up (0.27s latency).
Not shown: 98 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 2.66 seconds

flag in guiding path

j.matthew@nexus.htb


```
└─$ ffuf -u http://nexus.htb -H "HOST:FUZZ.nexus.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -ac 

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://nexus.htb
 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
 :: Header           : Host: FUZZ.nexus.htb
 :: Follow redirects : false
 :: Calibration      : true
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

git                     [Status: 200, Size: 14474, Words: 1195, Lines: 242, Duration: 408ms]
billing                 [Status: 302, Size: 390, Words: 60, Lines: 12, Duration: 2537ms]
:: Progress: [4989/4989] :: Job [1/1] :: 124 req/sec :: Duration: [0:00:44] :: Errors: 0 ::
```

we got git and billing

adding into our host file

exploring gitea account

```
APP_NAME='Krayin CRM'
APP_ENV=local
APP_KEY=
APP_DEBUG=true
APP_URL=http://billing.nexus.htb
APP_TIMEZONE=Asia/Kolkata
APP_LOCALE=en
APP_CURRENCY=USD
VITE_HOST=
VITE_PORT=
LOG_CHANNEL=stack
LOG_LEVEL=debug
DB_CONNECTION=mysql
DB_HOST=krayin-mysql
DB_PORT=3306
DB_DATABASE=krayin
DB_USERNAME=krayin
DB_PASSWORD=
DB_PREFIX=
BROADCAST_DRIVER=log
CACHE_DRIVER=file
QUEUE_CONNECTION=sync
SESSION_DRIVER=file
SESSION_LIFETIME=120
MEMCACHED_HOST=127.0.0.1
REDIS_HOST=127.0.0.1
REDIS_PASSWORD=null
REDIS_PORT=6379
MAIL_MAILER=smtp
MAIL_HOST=mailhog
MAIL_PORT=1025
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_ENCRYPTION=null
MAIL_FROM_ADDRESS=laravel@krayincrm.com
MAIL_FROM_NAME="${APP_NAME}"
MAIL_DOMAIN=webkul.com
MAIL_RECEIVER_DRIVER=sendgrid
IMAP_HOST=imap.nexus.htb
IMAP_PORT=993
IMAP_ENCRYPTION=ssl
IMAP_VALIDATE_CERT=true
IMAP_USERNAME=username1
IMAP_PASSWORD=password1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1
AWS_BUCKET=
PUSHER_APP_ID=
PUSHER_APP_KEY=
PUSHER_APP_SECRET=
PUSHER_APP_CLUSTER=mt1
MIX_PUSHER_APP_KEY="${PUSHER_APP_KEY}"
MIX_PUSHER_APP_CLUSTER="${PUSHER_APP_CLUSTER}"

```

you get password from recent commit section

DB_PASSWORD=N27xh!!2ucY04

trying it with j.matthew@nexus.htb on billing we have

Version: 2.2.0 


```
    array:2 [▼
      "XSRF-TOKEN" => "YXnXByeYMTaLm4TWtftwCvxmayvGRSyH51CeGSU1"
      "krayin_crm_session" => "64ZFjwbEc3hAEHCG59BUohsxOiyv7DCwrO3hHNUN"
    ]

```
