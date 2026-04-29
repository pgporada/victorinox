# Overview

A VictorOps calendar filtering tool because what person decided that exporting the on-call calendar should show you the entire teams on-call schedule? You don't need to know when GuyDingus42 is on-call, just DudeBr0.

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

Give it a test! You can use it from curl or a browser, but most likely you're going to subscribe your calendar to it because that's the big brain wicked smaht thing to do. Assuming that your team calendar is `https://portal.victorops.com/api/v1/team/calendar/<redacted>.ics` you'd plug in
```
https://example.com/victorinox/api/v1/team/calendar/<redacted>.ics
```

If you wanted to filter by your own name, pass the `?user=` query parameter.
```
https://example.com/victorinox/api/v1/team/calendar/<redacted>.ics?user=Dude+Br0
```
