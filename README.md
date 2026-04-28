# Overview

```
pip install -r requirements.txt --user
```

Install the nginx vhost, editting it accordingly for useful things like TLS. Install the systemd service file and start it up.
```
systemctl daemon-reload
systemctl start victorinox
systemctl status victorinox
systemctl reload nginx
systemctl status nginx
```
