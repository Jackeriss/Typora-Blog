#!/bin/bash
function deploy()
{
    echo "deploying $app_name..."
    echo "creating venv..."
    python3 -m venv venv
    source venv/bin/activate
    echo "installing requirements..."
    python3 -m pip install -r requirements.txt
    echo "copying config..."
    cp deploy/*.ini /etc/supervisord.d/
    cp deploy/*.conf /etc/nginx/conf.d/
    echo "reloading supervisor..."
    supervisorctl reload
    echo "reloading nginx..."
    nginx -s reload
    echo "deploy done"
}

function start()
{
    echo "starting $app_name..."
    supervisorctl start ${app_name}:
    sleep 3
    echo "start done"
}

function stop()
{
    echo "stopping $app_name..."
    supervisorctl stop ${app_name}:
    sleep 3
    echo "stop done"
}

function restart()
{
    echo "restarting $app_name..."
    for port in $( seq 8101 8102 )
    do
        supervisorctl restart ${app_name}:${port}
        sleep 1
    done
    sleep 1
    echo "restart done"
}

function update()
{
    echo "updating $app_name..."
    echo "pulling..."
    git pull
    restart
    echo "update done"
}

opt="$1"
app_name="$2"
if [ "$opt" == "" ]
then
    printf "usage: \n\tdeploy {app_name}\n\tstart {app_name}\n\tstop {app_name}\n\trestart {app_name}\n\tupdate {app_name}\n"
    exit
else
    "$1"
fi
