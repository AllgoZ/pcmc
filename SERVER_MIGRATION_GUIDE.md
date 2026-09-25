# PCMC Site — New Server Migration Guide

This document lists **every config, file, and step** needed to stand up the PCMC site (`pcmc.tepros.in`) on a new server. The code, media, and databases are backed up in GitHub (`https://github.com/AllgoZ/pcmc`); everything else described here lives **outside** that repo on the current server and must be set up manually.

Current server reference: Ubuntu 22.04.3 LTS, Python 3.10.12, project at `/home/ubuntu/build/PCMC_site`.

---

## 1. What's already covered by git

Pulling the repo gets you all of this — no manual copying needed:
- All Django app code (`pcmc/`, `pcmc_app/`, `goi/`, `hp/`)
- All three SQLite databases: `pcmcdb.sqlite3`, `hp_db.sqlite3`, `goi_db.sqlite3`
- `media/` (study material PDFs, images) and `default_media/`
- `static/`, `templates/`, `assets/` (collected static files)
- `requirements.txt` (regenerated from the real running venv — see §3)

## 2. What is NOT in git — server-level setup

| Item | Location on old server | What to do on new server |
|---|---|---|
| Nginx site config (PCMC) | `/etc/nginx/sites-available/pcmc` | Recreate — see §6 |
| Nginx site config (tepros.in root domain) | `/etc/nginx/sites-available/tepros.in` | Recreate if this domain also moves |
| SSL certificates | `/etc/letsencrypt/live/pcmc.tepros.in/`, `/etc/letsencrypt/live/tepros.in/` | Re-issue with certbot, don't copy — see §7 |
| Static HTML site for bare `tepros.in` | `/var/www/tepros.in` | Copy this directory separately if that site is moving too — it's unrelated to this git repo |
| Python virtualenv | `myenv/`, `newenv/`, `pcmc/Lib` (gitignored / not usable cross-platform) | Rebuild fresh — see §3 |
| Cron jobs | none configured (`crontab -l` is empty) | N/A |
| Process manager | none — currently run via `nohup python manage.py runserver` | Replace with gunicorn + systemd — see §5 |

---

## 3. Set up the project on the new server

```bash
# System packages
sudo apt update
sudo apt install -y python3-venv python3-pip nginx certbot python3-certbot-nginx git

# Clone the backup
git clone https://github.com/AllgoZ/pcmc.git /home/ubuntu/build/PCMC_site
cd /home/ubuntu/build/PCMC_site

# Virtualenv + real dependencies
python3 -m venv newenv
source newenv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` was regenerated from the actual running environment, so it includes everything really needed: Django 5.0.2, djangorestframework, djangorestframework-simplejwt, django-admin-interface, django-ckeditor, django-colorfield, django-pwa, pillow, openpyxl, etc.

## 4. Django settings to review (`pcmc/settings.py`)

These are things you should deliberately check/change for the new server, not just copy blindly:

- **`SECRET_KEY`** (line 23) — currently a hardcoded, already-public value (`django-insecure-...`). Generate a fresh one for the new server:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
  Then set it as an environment variable rather than hardcoding it again, e.g. in the systemd unit (§5) or a `.env` loaded via `python-decouple`/`os.environ`.
- **`DEBUG`** — currently `True`. Set to `False` for production once everything is verified working, to avoid leaking stack traces/paths.
- **`ALLOWED_HOSTS`** — currently `['*', 'https://pcmc.tepros.in/']` (the URL scheme there is actually invalid for this setting — `ALLOWED_HOSTS` wants bare hostnames). Update to the new server's actual hostname/IP plus the domain, e.g. `['pcmc.tepros.in', 'NEW_SERVER_IP']`.
- **`CSRF_TRUSTED_ORIGINS`** — currently `['https://pcmc.tepros.in']`. Keep as-is if the domain doesn't change.
- **`STATIC_ROOT`** / **`MEDIA_ROOT`** — hardcoded via `BASE_DIR`, so they'll automatically point at wherever you clone the repo on the new server. Just make sure the nginx config (§6) matches the actual clone path.

## 5. Run migrations, collect static, and set up gunicorn

```bash
# Databases already come populated via git, but run this to be safe
# in case app code has newer migrations than the committed DB state:
python manage.py migrate

# Static files
python manage.py collectstatic --noinput
```

Install gunicorn and create a systemd service (the old server never had a real one — it was just running `manage.py runserver` under `nohup`):

```bash
pip install gunicorn
```

`/etc/systemd/system/gunicorn.service`:
```ini
[Unit]
Description=gunicorn daemon for PCMC site
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/build/PCMC_site
ExecStart=/home/ubuntu/build/PCMC_site/newenv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    pcmc.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn
sudo systemctl status gunicorn
```

## 6. Nginx config

Create `/etc/nginx/sites-available/pcmc` (adjust the path if you clone somewhere other than `/home/ubuntu/build/PCMC_site`):

```nginx
server {
    listen 80;
    server_name pcmc.tepros.in;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/ubuntu/build/PCMC_site/assets/;
    }

    location /media/ {
        alias /home/ubuntu/build/PCMC_site/media/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/pcmc /etc/nginx/sites-enabled/pcmc
sudo nginx -t
sudo systemctl reload nginx
```

(certbot will add the `listen 443 ssl` blocks automatically in the next step — no need to write them by hand.)

## 7. SSL via certbot

Don't copy the old certificates — re-issue fresh ones once DNS points at the new server:

```bash
sudo certbot --nginx -d pcmc.tepros.in
```

If the bare `tepros.in` static site is moving too:
```bash
sudo certbot --nginx -d tepros.in -d www.tepros.in
```

## 8. DNS cutover

Point the DNS A/AAAA record(s) for `pcmc.tepros.in` (and `tepros.in`/`www.tepros.in` if applicable) to the new server's IP. Do this **after** nginx + gunicorn are confirmed working on the new server (test by hitting the new server's IP directly with a `Host:` header, or temporarily editing your local `/etc/hosts`), to minimize downtime.

## 9. Post-migration checklist

- [ ] `python manage.py migrate` ran cleanly on all three databases
- [ ] `python manage.py collectstatic` ran, `assets/` populated
- [ ] gunicorn service is `active (running)`: `systemctl status gunicorn`
- [ ] `curl -I http://127.0.0.1:8000` returns 200 from the server itself
- [ ] nginx serves the site over the new server's IP
- [ ] SSL cert issued and auto-renewal timer active: `systemctl status certbot.timer`
- [ ] Admin login works (`/admin/`) with an existing account from `auth_user`
- [ ] Assessment flow (question images, AJAX modal) works end-to-end
- [ ] Study material PDF downloads work (`media/study_materials/`)
- [ ] DNS switched and old server can be decommissioned

## 10. Notes / things worth fixing while you're at it

- `SECRET_KEY` for this project has been public on GitHub since the repo backup — regenerating it (§4) is a good opportunity to close that out, since old sessions/tokens signed with it become invalid once it changes (expected side effect, not a bug).
- The repo currently also has full Windows virtualenvs committed inside `pcmc/Lib` and `pcmc/Scripts` (leftover from a previous environment) — these aren't used by anything and are safe to delete from the repo in a future cleanup; they don't need to be recreated on the new server.
