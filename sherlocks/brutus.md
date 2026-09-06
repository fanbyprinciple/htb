# Sherlocks

## Brutus

1. The first two answers from auth.log

2. Using wtmp to get UTC

>utmpdump wtmp

> ─$ last wtmp

`wtmpdb begins Fri Sep 27 15:42:09 2024`

wtmp is one of three files that tracks login and logout events on a Linux system. /var/run/utmp tracks the currently logged in users. /var/log/wtmp keeps a historical log of login and logout activity. And /var/log/btmp keeps a record of invalid login attempts.

from iipsec

https://www.youtube.com/watch?v=bv08UcIL1po

> TZ=utc last -f wtmp -F

> head -l auth.log

> awk {print $5} auth.log


