# **Understanding NTDS.dit: Active Directory's Database and How Attackers Extract It**

To understand the CrownJewel-2 Sherlock properly, you need to understand three things:

1. What Active Directory (AD) is and how it stores user and computer accounts.
2. What `NTDS.dit` contains and why it is such a valuable target.
3. How attackers use `ntdsutil.exe`, Volume Shadow Copy Service (VSS), and Windows event logs to extract the database.

Let's work through this from the fundamentals, then connect everything to the Sherlock investigation.

# **1. What is Active Directory?**

[Active Directory for Pentesters — Part 1: Understanding the Basics | by Azzam Mohammed (WHHacker) | Mar, 2026 | Medium](https://images.openai.com/static-rsc-4/Drl6dKKW9eAVfZS4oZXZcZq8C7wJhSAOHdNm2qKOqq4sl_VGPiHvi19FLbvs9kjNVh5B0l3qd4TbS_xxvgbAindHogKrZ4LRdg_OOcwA2cNit0tD3B3-2BtXy_sQrrLyXJbzUCSYV94Ew43_9IcFgkO3QlYSoPqFC9a9FhPPW18?purpose=inline)

[medium.com](https://medium.com/%40WHHacker/active-directory-for-pentesters-part-1-understanding-the-basics-608ac28ebe7d?utm_source=chatgpt.com)

**Active Directory (AD)** is Microsoft's directory service used in Windows domain environments. It provides centralised authentication, authorisation, and management of users, computers, groups, and other network resources.

Imagine an organisation with 5,000 employees and 2,000 computers.

Without Active Directory, administrators would have to manage user accounts, passwords, permissions, and access individually on each machine.

Active Directory centralises this management.

For example:

| Object              | Example             |
| ------------------- | ------------------- |
| Domain              | `forela.local`      |
| Domain Controller   | `DC01.forela.local` |
| User                | `ash.forela.local`  |
| Group               | Domain Admins       |
| Computer            | `WORKSTATION01`     |
| Organisational Unit | Finance, HR, IT     |

### **What is a Domain Controller?**

A Domain Controller (DC) is a Windows server running Active Directory Domain Services (AD DS).

It performs several important functions:

- Authenticates domain users.
- Validates credentials.
- Issues Kerberos authentication tickets.
- Maintains user and computer account information.
- Enforces access policies.
- Manages domain security groups.

Think of a Domain Controller as the central authority responsible for deciding who can access what within an organisation's Windows domain.

And this brings us to the most important file in this investigation.

# **2. What exactly is NTDS.dit?**

[Active Directory for Pentesters — Part 1: Understanding the Basics | by Azzam Mohammed (WHHacker) | Mar, 2026 | Medium](https://images.openai.com/static-rsc-4/wzbILXyAFQGB5giIQZSrh2fqumckAOh1hvhXxRB-FbsdaJMu7pXyaK8M4O-vXnnogsAiJmYftjymgEsjE-Y2aBGP1d7-PA990QrQ6o1aG14x8eUKOJqrd8pWCsSKBRVesv2Fg3KO-MI1QwLuhBZuFgnDgOlP1IjDEp1jTTxwbFY?purpose=inline)

[medium.com](https://medium.com/%40WHHacker/active-directory-for-pentesters-part-1-understanding-the-basics-608ac28ebe7d?utm_source=chatgpt.com)

`NTDS.dit` stands for **NT Directory Services Directory Information Tree**.

It is the primary database file used by Active Directory Domain Services to store directory information.

On a typical Domain Controller, its default location is:

```
C:\Windows\NTDS\ntds.dit
```

The file is essentially the database containing the information that makes Active Directory work.

### **What does NTDS.dit contain?**

It contains several categories of information:

| Information              | Description                                     |
| ------------------------ | ----------------------------------------------- |
| User accounts            | Domain usernames and account attributes         |
| Computer accounts        | Domain-joined computer identities               |
| Security groups          | Group membership and associated information     |
| Password-related data    | Password hashes and credential-related secrets  |
| Domain information       | Domain configuration and directory objects      |
| Group memberships        | Relationships between users and security groups |
| Kerberos-related secrets | Information used in domain authentication       |

One particularly important aspect is that `NTDS.dit` contains password hashes for domain accounts.

These include NT password hashes, which attackers can extract and potentially use for offline password cracking or authentication attacks.

**Why is this dangerous?**

Imagine an organisation has 10,000 domain users.

If an attacker obtains a usable copy of `NTDS.dit`, they may be able to extract password hashes for a large proportion of those accounts.

Instead of compromising accounts one by one, the attacker potentially obtains credential material for the entire domain in a single operation.

This is why NTDS database extraction is considered a high-impact Active Directory attack.

# **3. How are passwords stored in NTDS.dit?**

This is worth understanding because it explains why attackers want the database.

When a user creates a password, Windows does not simply store the password as readable text.

Instead, Windows uses cryptographic mechanisms to derive password hashes.

For example, consider:

```
Username: ash
Password: MyPassword123
```

The password is processed using the NT hashing mechanism.

The resulting NT hash is stored as part of the account's credential data.

An example of an NT hash format is:

```
8846f7eaee8fb117ad06bdd830b7586c
```

This is an illustrative hash, not a hash from the Sherlock.

An important distinction:

- A password is the original secret.
- A password hash is a derived representation of that secret.
- A hash is not normally reversible through decryption.
- However, attackers can perform offline password cracking by testing candidate passwords against the hash.

### **What can an attacker do with these hashes?**

There are several possibilities:

**1. Offline password cracking**

The attacker extracts hashes and uses tools such as Hashcat or John the Ripper to attempt to recover the original passwords.

**2. Pass-the-Hash**

In certain Windows authentication scenarios, an attacker can authenticate using an NT hash without knowing the original plaintext password.

**3. Privileged account compromise**

If the attacker obtains the hash of a Domain Administrator account, they may be able to gain extensive control over the domain.

**4. Lateral movement**

Compromised credentials can be used to access other domain-joined systems, depending on permissions and authentication controls.

This is why an NTDS dump is much more serious than simply stealing a list of usernames.

# **4. What is ntdsutil.exe?**

[Obtaining NTDS.Dit Using In-Built Windows Commands | Cyberis Limited](https://images.openai.com/static-rsc-4/ymQSm-XFsZUTnlm9gQm6mRo6ee_y1jSmjq6O_inc8ZN-mE44o77oR9YfptZurW5hE_wcgJ0-iouk6Ys0cviLRduEkU3-B4SdG5_cZ5Qkao2-qp8kIYxKb8wTnvR_-8gXz7ZWkoFSZznASathb1ccRsUV-UjbovWHGOrBRuPP6X0?purpose=inline)

[cyberis.com](https://www.cyberis.com/article/obtaining-ntdsdit-using-built-windows-commands?utm_source=chatgpt.com)

Now let's connect this to CrownJewel-2.

`ntdsutil.exe` is a legitimate Microsoft Windows command-line utility used to perform Active Directory database maintenance and administrative operations.

It is normally located at:

```
C:\Windows\System32\ntdsutil.exe
```

Administrators use it for tasks such as:

- Active Directory database maintenance.
- Database integrity checks.
- Metadata cleanup.
- Domain controller maintenance.
- Managing certain directory service operations.
- Creating installation media and database snapshots.

However, attackers can abuse its legitimate functionality to create a copy of the Active Directory database.

This is an example of **Living off the Land (LotL)**.

Living off the Land means using legitimate tools already present in an operating system to perform malicious activities.

Instead of uploading an unfamiliar executable, an attacker uses a trusted Windows utility.

This can make malicious activity harder to distinguish from legitimate administrative operations.

### **How does ntdsutil dump NTDS.dit?**

At a conceptual level, the attacker uses the Active Directory database maintenance functionality to create a snapshot or copy of the database.

The database is normally in use by the Domain Controller, so simply copying the live file is problematic.

This is where Volume Shadow Copy Service becomes important.

# **5. What is Volume Shadow Copy Service (VSS)?**

[Microsoft VSS Framework: Recap and Troubleshooting | Veeam Community Resource Hub](https://images.openai.com/static-rsc-4/e4bJbVsqHYtsEpIf0liF3zcfNLhLPiuOmgIzWkLoVWXjo1VsTN1yunKflXyBQcWuc0GJuUvf-iA0raBoJXaOdN44Turk9XhlRIpixYcCwsH7zOpucB9Sqnl3Fi9uIFBZEzHiZD0zNRNVVIYADIWidauS4mKF9m6wmSQxemWxVnM?purpose=inline)

[community.veeam.com](https://community.veeam.com/blogs-and-podcasts-57/microsoft-vss-framework-recap-and-troubleshooting-8634?utm_source=chatgpt.com)

**Volume Shadow Copy Service (VSS)** is a Windows service that allows applications and backup software to create snapshots of volumes while the system is running.

Consider a Domain Controller:

- Windows is running.
- Active Directory is running.
- Users are authenticating.
- The `NTDS.dit` database is actively being accessed and modified.

If someone attempts to copy the database directly while it is being used, the resulting copy might be inconsistent or incomplete.

VSS helps address this problem.

It coordinates snapshot creation so that applications and backup software can access a consistent point-in-time representation of the volume.

### **How does VSS work?**

There are three important components:

| Component     | Function                                                     |
| ------------- | ------------------------------------------------------------ |
| VSS Service   | Coordinates the shadow-copy operation                        |
| VSS Requester | Requests a snapshot, such as backup software                 |
| VSS Writer    | Prepares an application or service for a consistent snapshot |

In an Active Directory environment, the NTDS VSS Writer participates in preparing the database for snapshot operations.

The resulting snapshot can provide access to the database files without directly interfering with the live database.

### **Why does this matter to attackers?**

An attacker can abuse VSS functionality to obtain a copy of files that are otherwise locked or actively being used.

This includes:

- `NTDS.dit`
- Registry hives containing credential-related material
- Other application databases

This is why defenders monitor VSS activity on Domain Controllers.

In CrownJewel-2, the Sherlock specifically asks you to identify when the Microsoft Shadow Copy Service entered the running state.

That event is an important indicator of possible NTDS extraction activity.

However, remember: VSS activity alone does not prove malicious behaviour. Legitimate backup operations also use VSS.

# **6. How the NTDS dumping attack works**

Let's combine the components.

**NTDS.dit extraction – conceptual attack sequence**

1. **Initial access to Domain Controller**

   The attacker obtains access to a Domain Controller, potentially using compromised domain administrator credentials.
2. **Execute ntdsutil.exe**

   The attacker invokes the legitimate Windows Active Directory maintenance utility.
3. **Initiate shadow-copy activity**

   The Volume Shadow Copy Service is used to facilitate access to a consistent database copy.
4. **Create NTDS database copy**

   A copy of `NTDS.dit` is created at an attacker-selected location.
5. **Detach the database**

   The database operation completes and the newly created database is detached.
6. **Extract credentials**

   The attacker obtains the database and extracts password hashes and other credential material.
7. **Further exploitation**

   Extracted credentials may facilitate privilege escalation, lateral movement and domain-wide compromise.

The important point is that the attacker does not necessarily need to exploit a vulnerability in Active Directory itself.

They can abuse legitimate administrative functionality after obtaining sufficient privileges.

# **7. Understanding the Windows Event Logs in CrownJewel-2**

This is arguably the most important part from a blue-team and DFIR perspective.

The Sherlock gives you three event logs:

- APPLICATION
- SECURITY
- SYSTEM

Each records different types of activity.

Let's examine the events you encountered.

## **A. SYSTEM log – Event ID 7036**

Service activity

Event ID 7036 is associated with the Service Control Manager.

It records when a Windows service enters a particular state.

For example:

```
The Volume Shadow Copy service entered
the running state.
```

In CrownJewel-2:

```
2024-05-15 05:39:55
```

This was the most recent timestamp at which the VSS service entered the running state.

**Why is it useful?**

It provides a timeline indicator for possible snapshot activity.

Note: Your write-up refers to Event ID 7086, but the standard Windows Service Control Manager event for a service entering the running or stopped state is Event ID **7036**. Verify the event ID against the supplied EVTX record.

## **B. APPLICATION log – Event ID 325**

Database creation

Event ID 325 from ESENT indicates that the database engine created a new database.

ESENT stands for:

**Extensible Storage Engine**

It is Microsoft's database storage technology, used by Active Directory and other Windows components.

In your investigation, this event recorded the creation of the dumped database.

The recorded location was:

```
C:\Windows\Temp\dump_tmp\Active Directory\ntds.dit
```

This is significant because it establishes where the attacker created the database copy.

## **C. APPLICATION log – Event ID 327**

Database detachment

Event ID 327 from ESENT indicates that the database engine detached a database.

In the context of this investigation, it indicates that the newly created database was detached from the database engine.

The distinction is:

| Event | Meaning           |
| ----- | ----------------- |
| 325   | Database created  |
| 327   | Database detached |

Your investigation established:

- Database creation: `05:39:56`
- Database detachment: `05:39:58`

The two-second difference provides a useful timeline of the database extraction process.

## **D. SECURITY log – Event ID 4799**

Security group enumeration

Event ID 4799 records:

```
A security-enabled local group membership was enumerated.
```

This event is useful because it identifies processes querying security group membership.

In CrownJewel-2, `ntdsutil.exe` enumerated:

1. Administrators
2. Backup Operators

Why these groups?

**Administrators**

This group provides extensive administrative privileges on the Domain Controller.

**Backup Operators**

This group has specific backup and restore privileges, which can be particularly relevant to accessing files that would otherwise be restricted.

The process enumeration helps establish what privileges or group memberships the utility was checking.

Your investigation also identified:

```
Logon ID: 0x8DE3D
```

This is particularly important because it provides a correlation identifier for the associated logon session.

## **E. SECURITY log – Event ID 4768 and 4769**

These events relate to Kerberos authentication.

| Event ID | Description                                     |
| -------- | ----------------------------------------------- |
| 4768     | Kerberos Ticket Granting Ticket (TGT) requested |
| 4769     | Kerberos service ticket requested               |

A TGT is issued by the Kerberos Key Distribution Center (KDC) after successful authentication.

The TGT is subsequently used to request service tickets for accessing network resources.

These events help investigators understand authentication activity within the domain.

One technical distinction: Event ID 4768 and 4769 are not the definitive events for identifying the beginning of a Windows logon session. Event ID 4624 is generally more directly useful for identifying a successful logon and correlating its Logon ID.

Also, Event ID 5379 records Credential Manager credential reads; it should not be confused with the initial logon event.

# **8. Reconstructing the CrownJewel-2 attack timeline**

Now let's put your Sherlock findings together.

**CrownJewel-2 – reconstructed timeline**

1. **05:36:31**

   Initial session

   The malicious user session started. FORELA's Logon ID was subsequently correlated as `0x8DE3D`.
2. **05:39:55**

   Volume Shadow Copy Service entered the running state.
3. **05:39:56**

   ESENT Event ID 325 recorded the creation of the new NTDS database.
4. **05:39:58**

   ESENT Event ID 327 recorded the database detachment.
5. **After database creation**

   `ntdsutil.exe` enumerated Administrators and Backup Operators groups, recorded through Security Event ID 4799.

The database was created at:

```
C:\Windows\Temp\dump_tmp\Active Directory\ntds.dit
```

The important investigative insight is that you can correlate multiple independent Windows event sources to reconstruct the attack.

Instead of relying on a single alert, you establish a sequence of events:

- Authentication activity.
- Service activity.
- Database creation.
- Database detachment.
- Security group enumeration.

That is the essence of timeline-based digital forensics.

# **9. How would you detect this attack in a real SOC?**

This is where the Sherlock becomes particularly useful for your practical SOC knowledge.

You should not depend on a single Event ID to identify NTDS dumping.

Instead, correlate several indicators.

| Data source | Event / indicator | What to investigate                      |
| ----------- | ----------------- | ---------------------------------------- |
| SYSTEM      | 7036              | VSS service state changes                |
| APPLICATION | ESENT 325         | Database creation                        |
| APPLICATION | ESENT 327         | Database detachment                      |
| SECURITY    | 4799              | Security group enumeration               |
| SECURITY    | 4624              | Successful logon                         |
| SECURITY    | 4688              | Process creation, if auditing is enabled |
| SECURITY    | 4768              | Kerberos TGT requests                    |
| SECURITY    | 4769              | Kerberos service ticket requests         |

### **Other indicators worth monitoring**

Beyond event logs, monitor:

- Execution of `ntdsutil.exe` on Domain Controllers.
- Unexpected VSS snapshot creation.
- Creation of `ntds.dit` outside its normal directory.
- Unusual access to the NTDS database.
- Unexpected access to SYSTEM and SECURITY registry hives.
- Unusual outbound network transfers from Domain Controllers.
- Creation of suspicious archives containing database files.

### **Useful MITRE ATT&CK mapping**

**MITRE ATT&CK**

Credential Access

| Technique                    | ID        | Relevance                               |
| ---------------------------- | --------- | --------------------------------------- |
| OS Credential Dumping        | T1003     | Credential extraction                   |
| NTDS                         | T1003.003 | Extraction of Active Directory database |
| Archive Collected Data       | T1560     | Packaging collected data                |
| Exfiltration Over C2 Channel | T1041     | Possible subsequent data transfer       |

The most directly relevant technique is **T1003.003 – OS Credential Dumping: NTDS**.

Reference: [MITRE ATT&CK – NTDS](https://attack.mitre.org/techniques/T1003/003/?utm_source=chatgpt.com).

# **10. What you should remember from this Sherlock**

There are five concepts worth retaining.

1\. **NTDS.dit is the heart of Active Directory.** It stores directory objects and credential-related information, including password hashes. Compromising it can expose credentials across an entire domain.

2\. **ntdsutil.exe is a legitimate Windows utility.** Its abuse demonstrates Living off the Land techniques, where attackers use trusted native tools rather than introducing unfamiliar binaries.

3\. **VSS facilitates access to consistent copies of active files.** This is useful for backups but can also be abused for credential dumping.

4\. **ESENT events provide database-level forensic evidence.** Event ID 325 and 327 help identify database creation and detachment.

5\. **Event correlation is more valuable than isolated alerts.** Combining authentication, service, database and security events allows investigators to reconstruct the attack.

## **Further practical learning**

I would suggest exploring these three areas next:

- **NTDS.dit extraction and offline analysis:** Understand how tools such as Impacket's `secretsdump.py` extract NTLM hashes from an acquired database and its corresponding SYSTEM hive.
- **Kerberos authentication:** Understand TGTs, service tickets, Pass-the-Hash and Pass-the-Ticket. This explains what attackers can do after obtaining domain credentials.
- **Active Directory attack paths:** Explore DCSync, Kerberoasting, Golden Tickets and DCShadow. These are related AD attack techniques, although they exploit different mechanisms.

The central lesson from CrownJewel-2 is that an attacker who compromises a Domain Controller does not necessarily need to exploit Active Directory itself. Legitimate administrative utilities and backup mechanisms can provide the functionality needed to obtain the organisation's credential database.