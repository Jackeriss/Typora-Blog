#!/bin/bash

function start()
{
    echo "start $app_name..."
    supervisorctl start ${app_name}:
    sleep 3
    echo "start done"
}

function stop()
{
    echo "stop $app_name..."
    supervisorctl stop ${app_name}:
    sleep 3
    echo "stop done"
}

function restart()
{
    echo "restart $app_name..."
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
    sudo git pull origin master
    restart
}

opt="$1"
app_name="$2"
if [ "$opt" == "" ]
then
    printf "usage: \n\tstart {app_name}\n\tstop {app_name}\n\trestart {app_name}\n\tupdate {app_name}\n"
    exit
else
    "$1"
fi