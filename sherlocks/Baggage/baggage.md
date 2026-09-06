grep -aEio '[A-Za-z0-9_./\\ -]+\.(zip|rar|7z|tar|gz|bz2)' \
  C/Users/steve/NTUSER.DAT \
  C/Users/steve/AppData/Local/Microsoft/Windows/UsrClass.dat

  1.zip

strings -el C/Users/steve/NTUSER.DAT | grep -Ei \
'Everything|Agent Ransack|WinDirStat|grep|findstr|search|portable|exe'