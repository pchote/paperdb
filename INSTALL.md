##### Notes for deploying on CentOS 8

1. Install dependencies: `nginx`, `uwsgi` (python), `flask` (python), `github-flask` (python), `bibtexparser` (python), `biplist` (python)

2. Clone the repository to a useful location
3. Edit `paperdb.ini` to set `uid = ` your username
4. Edit `paperdb.service` to point to set
   * `User=` your username
   * `WorkingDirectory=` project location

5. Copy `paperdb.service` to `/usr/lib/systemd/system/`
6. Add user to the `nginx` group: `sudo usermod -a -G <user> nginx`
7. `chmod g+x` each directory in the path to the project
8. Enable and start the service
   ```
   sudo systemctl start paperdb
   sudo systemctl enable paperdb
   ```
9. Create / update nginx config to include:
   ```
    location /paperdb/static {
        alias <project path>/static;
    }

    location /paperdb/ {
        uwsgi_pass unix:<project path>/paperdb.sock;
        uwsgi_param SCRIPT_NAME /paperdb;
        include uwsgi_params;
    }
   ```
10. Enable and start the `nginx` service.
11. Open the firewall if needed
   ```
   sudo firewall-cmd --permanent --zone=public --add-service=http
   sudo firewall-cmd --reload`
   ```