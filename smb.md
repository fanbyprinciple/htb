12. Enumerating smb

`crackmapexec smb 10.129.141.87 -u '' -p '' --shares`

`crackmapexec smb 10.129.141.87 -u 'guest' -p '' --shares`

```
# smbclient
smbclient -L //10.129.141.87/ -N
smbclient -L //10.129.141.87/ -U guest%   # guest with empty password

smbclient //10.129.141.87/SYSVOL -N

# Enum4linux (no-auth)
enum4linux-ng -A 10.129.141.87
enum4linux-ng -U 10.129.141.87
```

```
# Detailed share listing with permissions
smbmap -H 10.129.141.87 -u '' -p ''   # anonymous
smbmap -H 10.129.141.87 -u 'guest' -p ''

# Recursive listing of accessible shares (very noisy, use carefully)
smbmap -H 10.129.141.87 -u '' -p '' -R
```

Connecting to a share

```
smbclient //10.129.141.87/<share> -N
# Inside:
recurse; ls; prompt off; mget *
```

With credentials

```
# Validate creds & grab shares
crackmapexec smb 10.129.141.87 -u 'user' -p 'password' --shares
crackmapexec smb 10.129.141.87 -u 'user' -p 'password' --users

# Full enum with creds
enum4linux-ng -u 'user' -p 'password' -A 10.129.141.87

# RID cycling for user enumeration (with creds)
crackmapexec smb 10.129.141.87 -u 'user' -p 'password' --rid-brute
```

RPC client

```
rpcclient -U "" -N 10.129.141.87
# Useful commands inside:
#   enumdomusers
#   enumdomgroups
#   queryuser <RID>
#   querygroup <RID>
```

`GetNPUsers.py support.htb/ -no-pass -usersfile users.txt -dc-ip 10.129.141.87`