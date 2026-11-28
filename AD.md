When you are enumerating ADS start with smb enumeratiuon

Ensure that clocks are in sync

get the krb file from the smb and add it to the local env

try list shares if there are nay other shares than what is there in the smb then that is sure shot sign of somthing amiss.

└─$ ldapsearch -x -H ldap://10.129.141.87 \
  -D 'ldap@support.htb' \
  -w 'nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz' \
  -b 'DC=support,DC=htb' \
  -s sub '(objectClass=*)'

For AD 

netexec smb 10.129.128.220 --generate-hosts-file hosts

netexec smb 10.129.4.239 --generate-krb5-file krb5.conf

’ll also add dns_canonicalize_hostname = false to the [libdefaults] section of /etc/krb5.conf. By default, the system Kerberos library canonicalizes the hostname through DNS before building the service principal name, and that can produce a name that doesn’t match. With this set, it uses the hostname exactly as I give it.
  
nmap notes a clock skew, so I’ll want to make sure to run sudo ntpdate DC1.ping.htb before any actions that use Kerberos auth

netexec smb dc1.ping.htb -u c.roberts -p AssumedBreach123

┌──(ajp㉿kali)-[~/codeplay/htb/machines/pingpong]
└─$ sudo timedatectl set-ntp false
                                                                                                                        
┌──(ajp㉿kali)-[~/codeplay/htb/machines/pingpong]
└─$ sudo ntpdate dc1.ping.htb
2026-11-27 21:26:32.268485 (-0500) +28799.911137 +/- 0.163387 dc1.ping.htb 10.129.4.239 s1 no-leap
CLOCK: time stepped by 28799.911137
                                                                                                                        
┌──(ajp㉿kali)-[~/codeplay/htb/machines/pingpong]
└─$ netexec ldap dc1.ping.htb -u c.roberts -p AssumedBreach123 -k
LDAP        dc1.ping.htb    389    DC1              [*] None (name:DC1) (domain:ping.htb) (signing:None) (channel binding:Never) (NTLM:False)                                                                                                   
LDAP        dc1.ping.htb    389    DC1              [+] ping.htb\c.roberts:AssumedBreach123 