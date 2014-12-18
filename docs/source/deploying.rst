Deploying the Server
--------------------

First, decide if you want to run ``noted`` in a virtualenv or not.  If you using 
a virtualenv, first create it and start the::

    $ cd $venv_dir
    $ virtualenv .
    $ source bin/activate

Next, install note.  You may need to use ``sudo`` if you aren't using 
a virtualenv::

    $ pip install note


Deploying without any tools
---------------------------

Just run the note server in the background::

    $ noted -d

Deploying using Supervisord
---------------------------

To deploy with Supervisord first make an `.ini` file in `/etc/supervisor.d/`::

    $ touch /etc/supervisor.d/noted.ini

Next, add something like this to the file::

    [program:noted]
    command=/home/devin/.note_env/bin/noted
    directory = /home/devin/
    user = devin
    autostart = true
    autorestart = true
    stdout_logfile=/var/log/supervisor/noted.log
    stderr_logfile=/var/log/supervisor/noted_err.log
    environment = HOME="/home/devin",PWD="/home/devin/",USER="devin",DISPLAY=":0",LOGNAME="devin",PATH="/home/devin/bin:/usr/local/sbin:/usr/local/bin:/usr/bin",USERNAME="devin"

You'll probably want to change the username and some of the paths.

Deploying using systemD
---------------------------

Create a service directory in ``/etc/systemd/system``, ``/usr/lib/systemd/system``
is reserved for services installed by your package manager::

    $ touch /etc/systemd/system/noted.service

Edit the file::

    [Unit]
    Description=Note Server
    After=syslog.target
    After=mongod.service

    [Service]
    Type=forking
    User=devin
    PIDFile=/var/run/noted.pid
    ExecStart=/home/devin/.note_env/bin/noted -d -p /var/run/noted.pid
    Restart=on-abort

    [Install]
    WantedBy=multi-user.target

You'll probably want to change the ``User`` and the path to ``noted``.  Also, 
note that in systemd config scripts items are appended with each `=` so this
script depends on `syslog.target` and `mongod.service`

Next start the server for the firt time::

    $ sudo systemctl daemon-reload
    $ sudo systemctl start noted

For more details see the [systemd documentation](http://www.freedesktop.org/software/systemd/man/systemd.unit.html).
