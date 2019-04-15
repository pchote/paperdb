##### Notes for deploying on CentOS 7

Add the `epel` repository and install the `nginx`, `uwsgi`, `uwsgi-python36` packages.
Install the python dependencies `python36-bibtexparser`, `python36-biplist`, `python36-Flask`

Clone the repository to a useful location and edit `paperdb.service` to point to it
Copy `paperdb.service` to `/usr/lib/systemd/system/`

Create a directory `/srv/sockets` and `chown nginx:nginx` it.

Enable and start the `paperdb` service.

Add to the nginx config
```
location = /paperdb { rewrite ^ /paperdb/; }

location /paperdb/static {
    alias {{PROJECT_PATH}}/static;
}

location /paperdb/ {
    uwsgi_pass unix:/srv/sockets/paperdb.sock;
    uwsgi_param SCRIPT_NAME /paperdb;
    include uwsgi_params;
}
```

Enable and start the `nginx` service.
Open the firewall if needed `sudo firewall-cmd --permanent --zone=public --add-service=http && sudo firewall-cmd --reload`

If you see sqlite errors about failing to open the database change `DATABASE_PATH` in `config.py` to a location where `nginx` can write.
Note that the containing directory must be writable, not just the `.db` file itself.