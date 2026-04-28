# Overview

A VictorOps calendar filtering tool because what person decided that exporting the on-call calendar should show you the entire teams on-call schedule? You and I don't need to know when GuyDingus42 is on-call, just DudeBr09.

```
git clone https://github.com/pgporada/victornox.git /opt/victorinox
python3 -m venv /opt/victorinox/venv
source /opt/victorinox/venv/bin/activate
cd /opt/victorninox
pip install -r requirements.txt
useradd -r -s /sbin/nologin victorinox
chown -R victorinox:victorinox /opt/victorinox
```

Install the nginx vhost, editting it accordingly for useful things like TLS. Install the systemd service file and start it up.
```
systemctl daemon-reload
systemctl start victorinox
systemctl status victorinox
systemctl reload nginx
systemctl status nginx
```

Give it a test!
```
curl https://example.com/victorinox
firefox https://example.com/victorinox
```
