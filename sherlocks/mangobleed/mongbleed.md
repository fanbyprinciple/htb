16  tree | clip
 1917  ls
 1918  tree | grep 'mongo'
 1919  find ./* | grep 'mongo'
 1920  cat ./[root]/etc/mongod.conf\n
 1921  cat ./[root]/var/log/mongodb/mongod.log\n
 1924  cat [root]/var/lib/dpkg/status | grep 'mongo'
 1925  cat [root]/var/lib/dpkg/status
 1926  cat ./[root]/var/log/mongodb/mongod.log | grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' 
 1927  cat ./[root]/var/log/mongodb/mongod.log | grep -F -m1 -B10 -A10 '65.0.76.43' 
 1928  cat ./[root]/var/log/mongodb/mongod.log | clip
 1929  cat ./\[root\]/home/mongoadmin/.bash_history
                                                       