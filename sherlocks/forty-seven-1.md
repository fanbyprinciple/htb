Below is a story version of the Sherlock scenario. Instead of simply memorizing flags, think of yourself as a cyber threat intelligence analyst reconstructing an investigation. Each question becomes another clue that reveals the identity and methods of the attacker.

---

# Sherlock: The Mystery of the Hajj Phishing Campaign

Government agencies begin reporting something unusual.

Several diplomats receive emails discussing **Hajj pilgrimage arrangements**. At first glance, everything appears legitimate—official documents, religious travel information, and WhatsApp instructions.

But opening one of these files starts an invisible chain of events.

Your job is to identify **who** is behind the attacks.

---

# 🕵️ Clue 1 – Who is the attacker?

The first reports from Kaspersky and Knownsec describe a previously unidentified South Asian threat actor using Hajj-themed phishing campaigns.

After comparing infrastructure, malware, and attack techniques, researchers finally give the actor a name.

### Flag

> **Mysterious Elephant**

Think of this as learning the criminal's alias.

---

# 🕵️ Clue 2 – How long have they been operating?

Many APT groups appear suddenly, but intelligence teams always ask:

> *"Is this actually a new group, or have they been operating quietly for years?"*

Knownsec went backwards through malware samples and infrastructure.

They discovered activity stretching all the way back to:

### Flag

> **2022**

Although researchers only recently named the group, its operations had already been occurring for years.

---

# 🕵️ Clue 3 – Their Secret Weapon (ORPCBackdoor)

Investigators next recover a custom DLL called **ORPCBackdoor**.

Instead of looking suspicious, it pretends to be Microsoft's Version.dll by exporting many legitimate Windows functions.

Among the exports, one immediately stands out.

Instead of being a normal Windows API, it is actually where the malware begins execution.

### Question

What is the first malicious exported function?

### Flag

```
GetFileVersionInfoByHandleEx
```

This function acts like the hidden entrance into the malware.

---

# 🕵️ Clue 4 – Before Hiding Forever

Persistence is every malware author's priority.

But ORPCBackdoor doesn't immediately install itself.

First, it checks whether one tiny file already exists.

If the file is missing, persistence is created.

If present, installation is skipped.

That file is:

### Flag

```
ts.dat
```

Think of it as the malware asking:

> "Have I already been here?"

---

# 🕵️ Clue 5 – An Old Accomplice

Threat hunters notice something familiar.

The ORPCBackdoor isn't unique.

Another South Asian APT had already been using nearly identical malware.

This links the new actor with an older, well-known group.

### Flag

```
Bitter
```

This suggests either:

* shared developers,
* shared tooling,
* or cooperation.

---

# 🕵️ Clue 6 – Their Favourite Backdoor Evolves

Attackers constantly improve their malware.

Since 2023, Mysterious Elephant repeatedly deployed another custom implant.

Originally it talked to its Command & Control server using **TCP**.

Later versions upgraded to **HTTPS**, blending into normal web traffic.

The malware responsible is:

### Flag

```
AsyncShell-v2
```

Evolution:

```
TCP
   ↓
HTTPS
```

This makes detection much harder.

---

# 🕵️ Clue 7 – Outsmarting Sandboxes

Researchers now inspect another tool:

**MemLoader HidenDesk**

Before running, it performs an interesting check.

Virtual machines used by malware analysts usually have very few running processes.

Real computers have many more.

The malware simply counts them.

If there aren't enough...

```
Exit.
```

Minimum required:

### Flag

```
40
```

Less than 40 processes?

The malware assumes it's being analyzed.

---

# 🕵️ Clue 8 – The Invisible Office

Even after running, MemLoader HidenDesk doesn't want users seeing what it's doing.

Windows allows programs to create multiple desktops.

Instead of using the normal one, the malware secretly creates:

### Flag

```
MalwareTech_Hidden
```

Everything happens inside this invisible desktop.

Imagine opening a second monitor that only malware can see.

---

# 🕵️ Clue 9 – Surviving Reboots

To remain on the victim machine, MemLoader places a shortcut into Windows Startup.

This persistence method corresponds to MITRE ATT&CK:

### Flag

```
T1547.001
```

Technique:

```
Registry Run Keys / Startup Folder
```

Whenever Windows starts...

↓

Malware starts too.

---

# 🕵️ Clue 10 – Stealing WhatsApp Files

The campaign isn't interested in random files.

Researchers discover a custom exfiltration tool specifically hunting WhatsApp-related documents.

It recursively searches:

* Desktop
* Downloads
* removable drives
* almost every drive except C:

The tool is called:

### Flag

```
Stom Exfiltrator
```

Its mission:

```
Search
↓
Collect
↓
Upload
```

---

# 🕵️ Clue 11 – Scripts Everywhere

Kaspersky notices one consistent behaviour.

Instead of dropping executables directly, attackers rely heavily on PowerShell scripts.

MITRE classifies this as:

### Flag

```
T1059.001
```

Technique:

```
PowerShell
```

PowerShell is attractive because it's already installed on Windows and often trusted by defenders.

---

# 🕵️ Clue 12 – The First Downloader

Looking back at older campaigns reveals something unexpected.

Before ORPCBackdoor and AsyncShell existed, Mysterious Elephant used a downloader previously associated with another APT.

That downloader was:

### Flag

```
Vtyrei
```

This also creates links between different South Asian threat actors.

---

# 🕵️ Clue 13 – Initial Infection

One January 2024 campaign delivered AsyncShell using a malicious archive.

The archive abused a famous WinRAR vulnerability.

The exploited CVE:

### Flag

```
CVE-2023-38831
```

Victim opens archive

↓

WinRAR vulnerability

↓

Payload executes

↓

AsyncShell installed

---

# 🕵️ Clue 14 – Browser Theft

Researchers also recover another malware sample.

```
WhatsAppOB.exe
```

Its purpose?

Steal Chrome data.

The required MD5 fingerprint is:

### Flag

```
9e50adb6107067ff0bab73307f5499b6
```

Remember:

```
File
↓
WhatsAppOB.exe

MD5
↓
9e50adb6107067ff0bab73307f5499b6
```

---

# 🕵️ Clue 15 – Sending the Loot Home

Finally, researchers ask:

> "How does the stolen data leave the victim?"

The answer:

The malware uploads everything through its existing Command & Control channel.

MITRE ATT&CK calls this:

### Flag

```
T1041
```

Technique:

```
Exfiltration Over C2 Channel
```

Instead of opening another connection, the attackers quietly reuse their established communication channel.

---

# 🧠 Complete Attack Chain (Memory Flow)

```text
Hajj-themed phishing email
            │
            ▼
Victim opens malicious document
            │
            ▼
Vtyrei Downloader (early campaigns)
            │
            ▼
ORPCBackdoor
      │
      ├── Export: GetFileVersionInfoByHandleEx
      ├── Checks ts.dat
      └── Linked to Bitter
            │
            ▼
AsyncShell-v2
(TCP → HTTPS)
            │
            ▼
MemLoader HidenDesk
      │
      ├── Needs ≥40 processes
      ├── Creates MalwareTech_Hidden desktop
      └── Persistence (T1547.001)
            │
            ▼
Stom Exfiltrator
            │
            ▼
ChromeStealer (WhatsAppOB.exe)
MD5:
9e50adb6107067ff0bab73307f5499b6
            │
            ▼
PowerShell (T1059.001)
            │
            ▼
Data sent via C2
(T1041)
```

## Final Flag Summary

| Q  | Answer                               |
| -- | ------------------------------------ |
| 1  | **Mysterious Elephant**              |
| 2  | **2022**                             |
| 3  | **GetFileVersionInfoByHandleEx**     |
| 4  | **ts.dat**                           |
| 5  | **Bitter**                           |
| 6  | **AsyncShell-v2**                    |
| 7  | **40**                               |
| 8  | **MalwareTech_Hidden**               |
| 9  | **T1547.001**                        |
| 10 | **Stom Exfiltrator**                 |
| 11 | **T1059.001**                        |
| 12 | **Vtyrei**                           |
| 13 | **CVE-2023-38831**                   |
| 14 | **9e50adb6107067ff0bab73307f5499b6** |
| 15 | **T1041**                            |

By following the clues in sequence, you can reconstruct the entire lifecycle of Mysterious Elephant's operation—from the initial Hajj-themed phishing lure, through malware deployment and persistence, to WhatsApp-focused data theft and exfiltration over its command-and-control infrastructure.
