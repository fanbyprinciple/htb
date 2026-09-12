ow open http://10.129.75.234/login.php in browser and we can try login using username:admin and password:rKXM59ESxesUFHAd

rKXM59ESxesUFHAd

curl -v -X POST -d "username=admin&password=rKXM59ESxesUFHAd" http://10.129.205.211/login.php

curl -v -L -c cookies.txt -b cookies.txt -d "username=admin&password=rKXM59ESxesUFHAd" http://10.129.205.211/login.php