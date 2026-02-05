#!/usr/bin/bash

set -e

deploy_changes(){

    sudo systemctl stop odoo15

    cd /opt/odoo15

    /home/kkiarie/.pyenv/versions/odoo15env/bin/python3 ./odoo-bin -c /etc/odoo15/odoo.conf -d odoo15sandbox -u quatrix_dispatch_module --stop-after-init

    sudo systemctl start odoo15

}

merge_changes_to_main(){

    cd /opt/custom_modules/quatrix-odoo

    git remote -v

    git branch

    git fetch origin

    git checkout Main

    git merge origin/Work-pc --no-ff -m "JENKINS: Merge Work-pc into Main"

    git push origin Main
                                

}

case "$1" in
    stage_deploy_changes)
        deploy_changes

    ;;

    stage_merge_changes)
        merge_changes_to_main

    ;;

esac
