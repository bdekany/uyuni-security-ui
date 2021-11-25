# uyuni-security-ui

Unofficial WebUI to get a nice view on Security information through the Uyuni API

## Installation
Install Python 3 and Flask

```bash
zypper -n in python3 python3-Flask
```

## Start
Start Flask (Port 5000 by default)

```bash
export FLASK_APP=app.py
flask run --host=0.0.0.0
```

## Use SUMA certificates
```bash
export FLASK_APP=app.py
flask run --host=0.0.0.0 --cert=/root/ssl-build/RHN-ORG-TRUSTED-SSL-CERT --key=/root/ssl-build/RHN-ORG-PRIVATE-SSL-KEY
```
