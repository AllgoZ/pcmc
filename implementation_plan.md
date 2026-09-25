# Implementation Plan: Host Static Site (tepros.in) via Nginx Reverse Proxy

This plan outlines how to run a static HTML website for the domain `tepros.in` alongside the existing Python (Django) website on this server.

---

## Current Server Status & Constraints
1. **Port 80 Conflict**: The Python application is running via Django's development server (`./newenv/bin/python manage.py runserver 0.0.0.0:80`) directly on port 80.
2. **Nginx Service**: Nginx is installed but inactive, and the default configuration file (`/etc/nginx/nginx.conf`) is missing or corrupted. 
3. **Requirement**: To run both sites on the same server on port 80, we must run Nginx as a reverse proxy on port 80, move the Python site to a different port (like 8000), and let Nginx route traffic to uwsgi/gunicorn (or the routed django development server) or serve the static `tepros.in` files based on the requested domain.

---

## User Review Required
> [!IMPORTANT]
> The change requires Nginx setup and moving Django to a background port (`8000`). We need to stop the current python process listening on port 80 to start Nginx.
> 
> We strongly recommend setting up Django with a production server (Gunicorn or uWSGI) managed via `systemd` rather than running `runserver` as root. This plan includes commands for both `runserver` and a production configuration.

---

## Proposed Changes

### 1. Re-install Nginx to Restore Configurations
We will reinstall the Nginx core configuration files if they are corrupted or missing:
```bash
sudo apt-get update
sudo apt-get install --reinstall nginx nginx-common -y
```

### 2. Move the Python Site to Port 8000
1. Identify and stop the current Django instance:
   ```bash
   sudo kill 54297
   ```
2. Relaunch Django on port 8000 in uWSGI/Gunicorn or as a development server:
   * **Development Server Option**:
     ```bash
     nohup /home/ubuntu/build/PCMC_site/newenv/bin/python /home/ubuntu/build/PCMC_site/manage.py runserver 127.0.0.1:8000 > /home/ubuntu/build/PCMC_site/django.log 2>&1 &
     ```
   * **Production Option (Recommended)**: Set up uWSGI/Gunicorn systemd service.

### 3. Deploy the Static HTML files for `tepros.in`
1. Create a root directory for the static website:
   ```bash
   sudo mkdir -p /var/www/tepros.in
   sudo chown -R ubuntu:ubuntu /var/www/tepros.in
   ```
2. Upload/copy the static HTML files (e.g. [index.html](file:///home/ubuntu/build/PCMC_site/pcmc_app/templates/assessment/index.html), style sheets, etc.) into `/var/www/tepros.in/`.

### 4. Configure Nginx Virtual Hosts
Create server blocks to handle both domains on port 80:

#### A. PCMC Python Site configuration (`/etc/nginx/sites-available/pcmc`)
```nginx
server {
    listen 80;
    server_name localhost pcmc.tepros.in; # Change to your actual PCMC domain

    # Proxy traffic to Python/Django running on 8000
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Serve static assets directly via Nginx
    location /static/ {
        alias /home/ubuntu/build/PCMC_site/static/;
    }

    # Serve media assets directly via Nginx
    location /media/ {
        alias /home/ubuntu/build/PCMC_site/media/;
    }
}
```

#### B. Tepros Static Site configuration (`/etc/nginx/sites-available/tepros.in`)
```nginx
server {
    listen 80;
    server_name tepros.in www.tepros.in;

    root /var/www/tepros.in;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

### 5. Enable Sites and Restart Nginx
1. Create symlinks to enable the virtual hosts:
   ```bash
   sudo ln -sf /etc/nginx/sites-available/pcmc /etc/nginx/sites-enabled/
   sudo ln -sf /etc/nginx/sites-available/tepros.in /etc/nginx/sites-enabled/
   # Remove default if present
   sudo rm -f /etc/nginx/sites-enabled/default
   ```
2. Verify configuration and start Nginx:
   ```bash
   sudo nginx -t
   sudo systemctl enable nginx
   sudo systemctl restart nginx
   ```

---

## Verification Plan
1. **Nginx Health**: Confirm `sudo systemctl status nginx` is `active (running)`.
2. **Dynamic Site**: Access the PCMC site via IP or domain and verify Django responds normally.
3. **Static Site**: Access `http://tepros.in` and confirm it serves the root custom HTML page.
