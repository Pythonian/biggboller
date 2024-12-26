# Deploying a Django project on Linode

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [1. Create a Linode Account and Deploy a Server](#1-create-a-linode-account-and-deploy-a-server)
3. [2. Configure Your Server](#2-configure-your-server)
4. [3. Set Up the Server Environment](#3-set-up-the-server-environment)
5. [4. Clone Your Django Project from GitHub](#4-clone-your-django-project-from-github)
6. [5. Configure Django Settings](#5-configure-django-settings)
7. [6. Set Up the Database](#6-set-up-the-database)
8. [7. Collect Static Files](#7-collect-static-files)
9. [8. Configure Gunicorn](#8-configure-gunicorn)
10. [9. Configure Nginx](#9-configure-nginx)
11. [10. Secure Your Application with SSL](#10-secure-your-application-with-ssl)
12. [11. Set Up Firewall](#11-set-up-firewall)
13. [12. Finalize and Test](#12-finalize-and-test)
14. [13. Optional: Configure Domain Name](#13-optional-configure-domain-name)
15. [Troubleshooting Tips](#troubleshooting-tips)

## Prerequisites

Before you begin, ensure you have the following:

- **Linode Account**: Sign up for a [Linode account](https://www.linode.com/).
- **Django Project on GitHub**: Your Django project should be pushed to a GitHub repository.
- **Domain Name (Optional)**: A registered domain name if you wish to use a custom domain.
- **Basic Knowledge**: Familiarity with SSH, Linux commands, and Django.

## 1. Create a Linode Account and Deploy a Server

### a. Sign Up and Log In

1. **Sign Up**: If you don’t have a Linode account, [sign up here](https://www.linode.com/).
2. **Log In**: Access the [Linode Cloud Manager](https://cloud.linode.com/).

### b. Create a New Linode

1. **Create Linode**: Click on the **"Create Linode"** button.
2. **Select Distribution**: Choose an operating system. **Ubuntu 22.04 LTS** is recommended.
3. **Choose a Plan**: Select a plan that suits your project's needs. For small projects, a **Nanode** (1 GB RAM) is sufficient.
4. **Region**: Choose a data center region closest to your target audience.
5. **Label**: Give your Linode a recognizable label.
6. **Root Password**: Set a strong root password or add SSH keys for authentication.
7. **Create**: Click **"Create Linode"** to deploy your server.

### c. Access Your Linode

Once the Linode is running, note its **Public IP Address**. You’ll use this to SSH into your server.

```bash
ssh root@your_server_ip
```

Replace `your_server_ip` with your Linode’s IP address.

---

## 2. Configure Your Server

### a. Update and Upgrade Packages

After logging in via SSH, update your package list and upgrade existing packages:

```bash
sudo apt update && sudo apt upgrade -y
```

### b. Create a New User

For security, it's best not to use the root account for regular operations.

```bash
adduser yourusername
```

Follow the prompts to set a password and provide user details.

### c. Grant Sudo Privileges

Add your new user to the `sudo` group:

```bash
usermod -aG sudo yourusername
```

### d. Set Up SSH Key Authentication (Recommended)

1. **Generate SSH Keys on Your Local Machine**:

   ```bash
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```

2. **Copy the Public Key to the Server**:

   ```bash
   ssh-copy-id yourusername@your_server_ip
   ```

   Save and exit, then restart SSH:

   ```bash
   sudo systemctl restart ssh
   ```

---

## 3. Set Up the Server Environment

### a. Install Essential Packages

```bash
sudo apt install -y python3-pip python3-dev libpq-dev nginx curl python3-venv
```

---

## 4. Clone Your Django Project from GitHub

### a. Navigate to the Home Directory

```bash
cd /home/yourusername
```

### b. Clone the Repository

```bash
git clone https://github.com/yourusername/your-django-repo.git
```

Replace `https://github.com/yourusername/your-django-repo.git` with your repository URL.

### c. Navigate to the Project Directory

```bash
cd your-django-repo
```

---

## 5. Configure Django Settings

### a. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### b. Install Project Dependencies

Assuming you have a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### c. Set Up Environment Variables

It's recommended to use environment variables for sensitive settings.

1. **Create a `.env` File**:

   ```bash
   nano .env
   ```

2. **Add Your Variables**:

   ```env
   SECRET_KEY=your_secret_key
   DEBUG=False
   ALLOWED_HOSTS=your_server_ip, your_domain.com
   DATABASE_URL=postgres://user:password@localhost:5432/dbname
   ```

3. **Load Environment Variables**:

   You can use packages like `python-dotenv` or configure them in your `systemd` service later.

### d. Update `settings.py`

Ensure `settings.py` reads from environment variables. For example:

```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')
```

---

## 6. Set Up the Database

Assuming you are using PostgreSQL.

### a. Install PostgreSQL

```bash
sudo apt install -y postgresql postgresql-contrib
```

### b. Create a Database and User

1. **Switch to PostgreSQL User**:

   ```bash
   sudo -i -u postgres
   ```

2. **Create Database**:

   ```bash
   createdb yourdbname
   ```

3. **Create User**:

   ```bash
   createuser yourdbuser --pwprompt
   ```

4. **Grant Privileges**:

   ```bash
   psql
   GRANT ALL PRIVILEGES ON DATABASE yourdbname TO yourdbuser;
   \q
   ```

5. **Exit PostgreSQL User**:

   ```bash
   exit
   ```

### c. Update `DATABASE_URL` in `.env`

```env
DATABASE_URL=postgres://yourdbuser:yourdbpassword@localhost:5432/yourdbname
```

### d. Apply Migrations

```bash
python manage.py migrate
```

---

## 7. Collect Static Files

```bash
python manage.py collectstatic
```

Ensure your `settings.py` has the correct `STATIC_ROOT` defined:

```python
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
```

---

## 8. Configure Gunicorn

Gunicorn will serve your Django application.

### a. Install Gunicorn

```bash
pip install gunicorn
```

### b. Test Gunicorn

From your project directory:

```bash
gunicorn your_project_name.wsgi
```

Replace `your_project_name` with your Django project’s name. If it runs without errors, stop it (Ctrl+C).

### c. Create a Systemd Service File

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Add the following content:

```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=yourusername
Group=www-data
WorkingDirectory=/home/yourusername/your-django-repo
ExecStart=/home/yourusername/your-django-repo/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/home/yourusername/your-django-repo.sock \
          your_project_name.wsgi:application

[Install]
WantedBy=multi-user.target
```

### d. Start and Enable Gunicorn

```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### e. Check Gunicorn Status

```bash
sudo systemctl status gunicorn
```

Ensure it’s active and running. If not, check logs for errors:

```bash
journalctl -u gunicorn
```

---

## 9. Configure Nginx

Nginx will serve as a reverse proxy to Gunicorn and handle static files.

### a. Remove Default Nginx Configuration

```bash
sudo rm /etc/nginx/sites-enabled/default
```

### b. Create Nginx Server Block

```bash
sudo nano /etc/nginx/sites-available/your_project
```

Add the following content:

```nginx
server {
    listen 80;
    server_name your_server_ip your_domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias /home/yourusername/your-django-repo;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/yourusername/your-django-repo.sock;
    }
}
```

### c. Enable the Server Block

```bash
sudo ln -s /etc/nginx/sites-available/your_project /etc/nginx/sites-enabled
```

### d. Test Nginx Configuration

```bash
sudo nginx -t
```

If the test is successful, reload Nginx:

```bash
sudo systemctl restart nginx
```

---

## 10. Secure Your Application with SSL

Use Let's Encrypt to obtain a free SSL certificate.

### a. Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### b. Obtain and Install SSL Certificate

```bash
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

Follow the prompts to complete the SSL setup. Certbot will automatically modify your Nginx configuration to use SSL.

### c. Verify Auto-Renewal

Certbot sets up a cron job for auto-renewal. To test it:

```bash
sudo certbot renew --dry-run
```

## 11. Set Up Firewall

Use UFW (Uncomplicated Firewall) to secure your server.

### a. Allow SSH

```bash
sudo ufw allow OpenSSH
```

### b. Allow Nginx Traffic

```bash
sudo ufw allow 'Nginx Full'
```

### c. Enable UFW

```bash
sudo ufw enable
```

### d. Check UFW Status

```bash
sudo ufw status
```

---

## 12. Finalize and Test

### a. Test Your Application

- Navigate to `http://your_server_ip` or `https://your_domain.com` in your web browser.
- Ensure your Django application is running correctly.

### b. Debugging

- **Gunicorn Logs**: `journalctl -u gunicorn`
- **Nginx Logs**: `/var/log/nginx/error.log` and `/var/log/nginx/access.log`
- **Django Logs**: Configure logging in `settings.py` if needed.

---

## 13. Optional: Configure Domain Name

If you have a domain name, point it to your Linode server.

### a. Update DNS Records

1. **Log In to Your Domain Registrar**: Access the DNS management section.
2. **Add an A Record**:
   - **Name**: `@` (or your desired subdomain)
   - **Type**: `A`
   - **Value**: Your Linode’s IP address
   - **TTL**: Default or 3600 seconds

3. **Add a CNAME Record** (Optional for `www`):

   - **Name**: `www`
   - **Type**: `CNAME`
   - **Value**: `your_domain.com`
   - **TTL**: Default or 3600 seconds

### b. Verify DNS Propagation

Use tools like [DNS Checker](https://dnschecker.org/) to verify that your domain points to your Linode’s IP.

---

## Troubleshooting Tips

- **Gunicorn Not Starting**:
  - Check the service status: `sudo systemctl status gunicorn`
  - Review logs: `journalctl -u gunicorn`
  - Ensure the virtual environment path and project name are correct in the service file.

- **Nginx Errors**:
  - Test configuration: `sudo nginx -t`
  - Check logs: `/var/log/nginx/error.log`

- **Database Connection Issues**:
  - Verify `DATABASE_URL` in `.env`.
  - Ensure PostgreSQL is running: `sudo systemctl status postgresql`
  - Test connection manually using `psql`.

- **Static Files Not Loading**:
  - Ensure `STATIC_ROOT` is correctly set.
  - Run `python manage.py collectstatic`.
  - Verify Nginx `location /static/` path.

- **SSL Certificate Issues**:
  - Ensure DNS is correctly pointing to your server.
  - Re-run Certbot if necessary: `sudo certbot --nginx`

----------------------------

I'm sorry to hear you're encountering a **502 Bad Gateway** error after setting up Nginx and Gunicorn. The error message indicates that Nginx is unable to communicate with Gunicorn due to a **permission issue** when trying to access the Unix socket at `/home/seyi/betbay.sock`. Let's systematically troubleshoot and resolve this issue.

---

## **Understanding the 502 Bad Gateway Error**

A **502 Bad Gateway** error occurs when a server acting as a gateway or proxy (Nginx) receives an invalid response from an upstream server (Gunicorn). In your case, the error message:

```plaintext
connect() to unix:/home/seyi/betbay.sock failed (13: Permission denied) while connecting to upstream
```

indicates that Nginx cannot access the Gunicorn socket due to permission restrictions.

---

## **Root Cause Analysis**

Even though your socket file `/home/seyi/betbay.sock` has `srwxrwxrwx` permissions, Nginx is still unable to connect. This is likely because of **restrictive permissions on the parent directory** `/home/seyi`. For Nginx (running under the `www-data` user) to access the socket, it must have execute (`x`) permissions on all parent directories leading to the socket.

---

## **Solution Overview**

To resolve the permission issue, you have two primary options:

1. **Adjust Directory Permissions:** Modify the permissions of the `/home/seyi` directory to allow `www-data` to traverse it.
2. **Relocate the Socket File:** Move the Gunicorn socket to a directory that Nginx can access without changing home directory permissions.

**Option 2** is the recommended and more secure approach as it avoids exposing your home directory. Here's how to implement it:

---

## **Step-by-Step Resolution**

### **1. Create a Dedicated Directory for the Gunicorn Socket**

It's best to place the socket in a location accessible to Nginx without altering your home directory's permissions.

1. **Create the Directory:**

   ```bash
   sudo mkdir /run/gunicorn
   ```

2. **Set Ownership and Permissions:**

   Assign ownership to your user (`seyi`) and the `www-data` group, and set appropriate permissions.

   ```bash
   sudo chown seyi:www-data /run/gunicorn
   sudo chmod 775 /run/gunicorn
   ```

   - **`chown seyi:www-data`**: Sets the owner to `seyi` and the group to `www-data`.
   - **`chmod 775`**: Grants read, write, and execute permissions to the owner and group, and read and execute permissions to others.

### **2. Update the Gunicorn Service Configuration**

Modify the Gunicorn service file to bind the socket to the new directory.

1. **Open the Service File:**

   ```bash
   sudo nano /etc/systemd/system/gunicorn.service
   ```

2. **Modify the `ExecStart` Line:**

   Change the socket path from `/home/seyi/betbay.sock` to `/run/gunicorn/betbay.sock`.

   ```ini
   [Unit]
   Description=gunicorn daemon
   After=network.target

   [Service]
   User=seyi
   Group=www-data
   WorkingDirectory=/home/seyi/betbay
   EnvironmentFile=/home/seyi/betbay/.env
   ExecStart=/home/seyi/betbay/venv/bin/gunicorn \
             --access-logfile - \
             --workers 3 \
             --bind unix:/run/gunicorn/betbay.sock \
             config.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

   **Key Changes:**

   - **`--bind unix:/run/gunicorn/betbay.sock`**: Updates the socket path.

3. **Reload Systemd and Restart Gunicorn:**

   Apply the changes and restart the Gunicorn service.

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart gunicorn
   ```

4. **Enable Gunicorn to Start on Boot (if not already enabled):**

   ```bash
   sudo systemctl enable gunicorn
   ```

### **3. Update Nginx Configuration to Point to the New Socket Location**

Ensure Nginx is configured to communicate with Gunicorn via the new socket path.

1. **Open Your Nginx Site Configuration:**

   ```bash
   sudo nano /etc/nginx/sites-available/betbay
   ```

2. **Modify the `proxy_pass` Directive:**

   Update the socket path in the `proxy_pass` directive.

   ```nginx
   server {
      server_name 45.56.116.77 bigg-boller.com www.bigg-boller.com;

      location = /favicon.ico { access_log off; log_not_found off; }
      location /static/ {
         alias /home/seyi/betbay/assets/;
      }

      location / {
         include proxy_params;
         proxy_pass http://unix:/run/gunicorn/betbay.sock;
      }
   }
   ```

   **Key Change:**

   - **`proxy_pass http://unix:/run/gunicorn/betbay.sock;`**: Updates the socket path.

3. **Test Nginx Configuration:**

   Ensure there are no syntax errors in the configuration.

   ```bash
   sudo nginx -t
   ```

   **Expected Output:**

   ```plaintext
   nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
   nginx: configuration file /etc/nginx/nginx.conf test is successful
   ```

4. **Reload Nginx:**

   Apply the configuration changes.

   ```bash
   sudo systemctl reload nginx
   ```

### **4. Verify Gunicorn and Nginx are Communicating Properly**

1. **Check Gunicorn Service Status:**

   ```bash
   sudo systemctl status gunicorn
   ```

   **Expected Output:**

   ```plaintext
   ● gunicorn.service - gunicorn daemon
      Loaded: loaded (/etc/systemd/system/gunicorn.service; enabled; vendor preset: enabled)
      Active: active (running) since Mon 2024-10-04 21:35:00 UTC; 5s ago
    Main PID: 1234 (gunicorn)
       Tasks: 3 (limit: 1152)
      CGroup: /system.slice/gunicorn.service
              ├─1234 /home/seyi/betbay/venv/bin/python3 /home/seyi/betbay/venv/bin/gunicorn ...
              ├─1235 /home/seyi/betbay/venv/bin/python3 /home/seyi/betbay/venv/bin/gunicorn ...
              └─1236 /home/seyi/betbay/venv/bin/python3 /home/seyi/betbay/venv/bin/gunicorn ...
   ```

   - **`Active: active (running)`**: Indicates Gunicorn is running correctly.

2. **Check Socket File Permissions:**

   Ensure the socket has the correct ownership and permissions.

   ```bash
   ls -l /run/gunicorn/betbay.sock
   ```

   **Expected Output:**

   ```plaintext
   srw-rw---- 1 seyi www-data 0 Oct  4 21:35 /run/gunicorn/betbay.sock
   ```

   - **Owner:** `seyi`
   - **Group:** `www-data`
   - **Permissions:** `srw-rw----` (read and write for owner and group)

3. **Inspect Nginx Error Logs:**

   Ensure there are no lingering permission issues.

   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

   **Look for Errors:**

   - If you no longer see the `Permission denied` error, the issue is resolved.
   - If errors persist, proceed to the next troubleshooting steps.

4. **Access Your Application:**

   Open your browser and navigate to `http://45.56.116.77/`. Your Django application should now load without the 502 error.

### **5. Additional Troubleshooting (If Necessary)**

If you still encounter issues, consider the following:

#### **a. Verify Gunicorn is Listening on the Correct Socket**

Ensure Gunicorn is bound to the new socket location.

```bash
sudo ss -l | grep gunicorn
```

**Expected Output:**

```plaintext
u_str  LISTEN  0      128          /run/gunicorn/betbay.sock
```

#### **b. Check for Application Errors**

Gunicorn might fail to start your Django application due to application-specific issues.

1. **Review Gunicorn Logs:**

   ```bash
   sudo journalctl -u gunicorn -b
   ```

   Look for any errors related to your Django application.

2. **Run Gunicorn Manually:**

   Activate your virtual environment and run Gunicorn manually to see real-time errors.

   ```bash
   source /home/seyi/betbay/venv/bin/activate
   gunicorn betbay.wsgi:application --bind unix:/run/gunicorn/betbay.sock
   ```

   Access your application in the browser to see if it loads correctly. Press `Ctrl+C` to stop Gunicorn after testing.

#### **c. Ensure Django is Properly Configured**

1. **`ALLOWED_HOSTS`:**

   Ensure your `ALLOWED_HOSTS` in `settings.py` includes your server's IP and domain.

   ```python
   ALLOWED_HOSTS = ['45.56.116.77', 'yourdomain.com']
   ```

2. **Static Files:**

   Ensure you've collected static files.

   ```bash
   python manage.py collectstatic
   ```

#### **d. Check Firewall Settings**

Ensure that your firewall allows HTTP and HTTPS traffic.

1. **Using UFW:**

   ```bash
   sudo ufw allow 'Nginx Full'
   sudo ufw enable
   sudo ufw status
   ```

2. **Verify Ports:**

   Ensure ports `80` and `443` are open.

   ```bash
   sudo ufw status | grep '80\|443'
   ```

#### **e. SELinux/AppArmor (Advanced)**

If you're using SELinux or AppArmor, ensure they're not restricting access to the socket.

1. **Check AppArmor Status:**

   ```bash
   sudo aa-status
   ```

2. **Adjust AppArmor Profiles:**

   If AppArmor is enforcing policies on Nginx, you might need to modify its profile to allow access to the new socket location.

   **Example for AppArmor:**

   - Edit the Nginx AppArmor profile.

     ```bash
     sudo nano /etc/apparmor.d/usr.sbin.nginx
     ```

   - Add the socket path to the allowed locations.

     ```plaintext
     /run/gunicorn/betbay.sock rw,
     ```

   - Reload AppArmor profiles.

     ```bash
     sudo systemctl reload apparmor
     ```

   **Note:** Adjusting security profiles should be done cautiously. Refer to [AppArmor documentation](https://gitlab.com/apparmor/apparmor/-/wikis/Home) for detailed guidance.

# Generating SSH key for git pulls

---

### **1. Generate an SSH Key (if you don’t already have one):**

If you don’t have an SSH key pair, create one using the following command:

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

- Press **Enter** to save the key in the default location (`~/.ssh/id_rsa`).
- You can optionally set a passphrase for added security.

---

### **2. Add the SSH Key to Your SSH Agent:**

Ensure the SSH agent is running and add your private key to it.

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
```

---

### **3. Add the SSH Key to Your Git Hosting Service:**

#### **GitHub:**

1. Copy the public key:

   ```bash
   cat ~/.ssh/id_rsa.pub
   ```

2. Go to **GitHub Settings** > **SSH and GPG keys** > **New SSH Key**.
3. Paste your public key and save.

### **4. Update Your Git Remote URL to Use SSH:**

Check your current remote URL with:

```bash
git remote -v
```

If the URL is HTTPS, change it to SSH. Replace the current URL with the SSH equivalent:

#### **Example:**

For GitHub:

```bash
git remote set-url origin git@github.com:username/repo.git
```

### **5. Test the SSH Connection:**

Run the following command to verify the connection:

```bash
ssh -T git@github.com  # For GitHub
```

You should see a success message indicating the connection is authenticated.

---

### **6. Pull Using SSH:**

Once the SSH setup is complete and the remote URL is updated, you can use `git pull` as usual:

```bash
git pull
```
