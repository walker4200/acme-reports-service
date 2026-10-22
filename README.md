# Acme Reports Service

> ⚠️ **INTENTIONALLY VULNERABLE.** Built for an Aikido Security demo. All secrets are fake.

Python / Flask service. Use it to show multi-language support and reachability in Python.

| Scanner | What's planted |
|---|---|
| SAST | SQLi (`/reports`), SSTI (`/greet`), `pickle.loads`, `shell=True`, SSRF + `verify=False`, MD5, `debug=True` |
| SCA – reachable | `PyYAML==5.3.1` (`yaml.load(FullLoader)`), `requests==2.19.1`, `Flask==1.0.2`, `Jinja2==2.10` |
| SCA – NOT reachable | `Pillow==8.0.0`, `cryptography==3.2` |
| Secrets | `app/main.py`, `Dockerfile` |
| Container | `python:3.8-buster` (EOL) |

## Run
```bash
docker build -t acme-reports-service .
docker run -p 5000:5000 acme-reports-service
```
