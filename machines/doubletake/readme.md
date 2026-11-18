PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http


sudo tee -a /etc/hosts <<'EOF'
10.129.248.123 doubletake.htb
EOF

python3 ./machines/doubletake/ 10.129.248.123 10.10.14.214 9001

