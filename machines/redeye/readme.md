Starting Nmap 7.99 ( https://nmap.org ) at 2026-11-21 14:35 -0500
Nmap scan report for 10.129.3.118
Host is up (0.16s latency).
Not shown: 65532 filtered tcp ports (no-response)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
3000/tcp open  ppp

sudo tee -a /etc/hosts <<'EOF'
10.129.3.118 redeye.htb    
EOF
