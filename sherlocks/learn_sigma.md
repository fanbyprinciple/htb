Your organization has detected a ransomware infection on one of its critical systems, and it is imperative that you address this issue immediately. This type of malware searches for valuable files, such as sensitive documents and configuration files, and encrypts them using a strong encryption algorithm.

The investigation has revealed that the ransomware may have used the Windows utility bitsadmin.exe to download additional malicious payloads or communicate with its command-and-control (C2) server.

Your task is to carefully review the Sigma rule, answer the related questions, and understand how different rule sections (selection, condition, fields, tags, logsource) work together to detect malicious activity.

Connect to the VM with the credential provided using RDP. 
From pwnbox use the command 

xfreerdp /v:10.129.245.167/u:letsdefend /p:'' /cert:ignore /dynamic-resolution 

File Location: C:\Users\LetsDefend\Desktop\ChallengeFile\proc_creation_win_bitsadmin_download.yml

bitsadmin.exe