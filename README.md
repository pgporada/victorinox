# Overview

```
git clone https://github.com/pgporada/victornox /opt/victorinox
python3 -m venv /opt/victorinox/venv
source /opt/victorinox/venv/bin/activate
cd /opt/victorninox
pip install -r requirements.txt
```

Install the nginx vhost, editting it accordingly for useful things like TLS. Install the systemd service file and start it up.
```
systemctl daemon-reload
systemctl start victorinox
systemctl status victorinox
systemctl reload nginx
systemctl status nginx
```
