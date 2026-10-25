# DanglingTree (HTB, Hard, Windows AD) — 10.129.7.198

## Enumeration → Initial Breach (completed)

### Recon
- `ping` TTL 127 → Windows. Full nmap: AD Domain Controller.
- Open: 53(DNS) 80/443(HTTP/S) 88(Kerb) 135/139/445(SMB/RPC) 389/636/3268/3269(LDAP)
  464(kpasswd) 593 3389(RDP) 6600(**Windows Admin Center**) 9389(ADWS) + high RPC.
- No 5985 WinRM → no evil-winrm; interactive shell comes via **RDP (3389)**.
- `nxc smb` → domain `danglingtree.htb`, host `DC`, Build 26100 (Srv 2025), signing required, **Null Auth: True**.
- Clock skew ~7h → `ntpdate`/`faketime` needed for Kerberos later.
- hosts: `10.129.7.198 danglingtree.htb dc.danglingtree.htb DC` (needs sudo; set it for certipy/kerberos).

### SMB shares (guest/null)
- Non-default share **IT** readable as `guest`.
- `IT\Security\DanglingTree_RoE_Assessment.pdf` → pentest RoE doc.

### PDF loot (the breach)
- Provided creds leaked in doc: **anderson.w : R3dT3am@Acc3ss#01** (low-priv domain user).
- Naming convention: firstname.lastinitial.

### Authenticated enum as anderson.w
- Creds valid (SMB + LDAP + RDP).
- RID brute users: Administrator, alex.o, anderson.w, jake.h, noah.b, svc_mail, krbtgt, Guest.
- AS-REP roast: none. Kerberoast: none. No extra shares.
- certipy: CA `danglingtree-DC-CA`, web enrollment for Authenticated Users, but **no pre-built vulnerable template** (ESC1 requires crafting a rogue "ghost" template post-foothold).
- **RDP as anderson.w works → initial foothold shell.**

## Next (exploitation — needs interactive RDP session)
1. RDP in as anderson.w (`xfreerdp /v:10.129.7.198 /u:anderson.w /p:'R3dT3am@Acc3ss#01' /cert:ignore`).
2. Exfil DPAPI: masterkeys `%APPDATA%\Microsoft\Protect\<SID>\`, creds `%APPDATA%\Microsoft\Credentials\` → nc/PS one-liner off box.
3. `impacket-dpapi masterkey` (w/ anderson.w pass + SID) → decrypt masterkey → decrypt cred blob → **alex.o : SunsetMountainPeak@2025**.
4. BloodHound as alex.o → SUPPORT-IT group has **ForceChangePassword** over jake.h → `bloodyAD` reset jake.h.
5. ADCS ESC1: inject rogue ghost template (EmployeeAuthTemplate) + OID → `certipy req` Administrator SAN → PKINIT → NT hash → `impacket-psexec` PtH → SYSTEM.
6. Flags: root.txt (Admin desktop), user.txt (noah.b profile).
