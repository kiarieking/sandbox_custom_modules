whoami

sudo systemctl stop odoo15

cd /opt/odoo15

/home/kkiarie/.pyenv/versions/odoo15env/bin/python3 ./odoo-bin -c /etc/odoo15/odoo.conf -d odoo15sandbox -u quatrix_dispatch_module --stop-after-init

sudo systemctl start odoo15
