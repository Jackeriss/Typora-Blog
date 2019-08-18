#!/bin/bash
PROJECT_NAME="typora-blog"
LOG_DIR=/app/log/${PROJECT_NAME}

NOTICE_ENV="Can not load ${ENV} from system, only (dev, test, pre, prod) is available"
NOTICE_USAGE="Usage: `basename $0` cmd(start, stop, restart, log) env(dev, test, pre, prod, or load \${ENV} from system)"
NOTICE_PARAMS="You provided $# parameters, but 2 are required."

cmd=$1
if [ ! -n "$2" ] ;then
    env=${ENV}
    if [ ! -n "${env}" ] ;then
        echo ${NOTICE_ENV}
        echo ${USAGE}
        exit 1
    fi
else
    env=$2
fi

function get_num()
{
    num=$(ps -ef | grep -w "python app/main.py --name=${PROJECT_NAME} --env=${env}" | grep -v grep | wc -l)
    return ${num}
}

function init_env()
{
    pipenv install --deploy
    if ! test -d ${LOG_DIR}; then mkdir -p ${LOG_DIR}; fi
}

function start()
{
    init_env
    get_num
    num=$?
    if [ "${num}" -ge "1" ];then
        echo "${PROJECT_NAME} is running"
        return
    fi
    echo "${PROJECT_NAME} is starting..."
    gulp
    pipenv run serve --name=${PROJECT_NAME} --env=${env} >> $LOG_DIR/${PROJECT_NAME}.${env}.log 2>&1 &
    sleep 3
    get_num
    num=$?
    if [ "${num}" -ge "1" ];then
        echo "${PROJECT_NAME} is started"
    else
        echo "start ${PROJECT_NAME} failed"
        exit 1
    fi
}

function stop()
{
    echo "${PROJECT_NAME} is stopping..."
    ps -ef | grep "python app/main.py --name=${PROJECT_NAME} --env=${env}" | grep -v grep | awk '{print $2}' | xargs kill -9
    sleep 3
    get_num
    num=$?
    if [ "${num}" == "0" ];then
        echo "${PROJECT_NAME} is stopped"
        return 0
    else
        echo "stop ${PROJECT_NAME} failed"
        exit 1
    fi
}

function restart()
{
    stop
    ret=$?
        if [ "${num}" == "0" ];then
            start
            return $?
        else
            exit 1
    fi
}

function log()
{
    tail -f $LOG_DIR/${PROJECT_NAME}.${env}.log
}

if [ "$#" -le "2" ];then
    echo "cmd is ${cmd}"
    echo "env is ${env}"
    if [[ "${env}" =~ ^(dev|test|pre|prod)$ ]];then
        "$1"
    else
        echo ${NOTICE_ENV}
        echo ${NOTICE_USAGE}
        exit 1
    fi
else
    echo ${NOTICE_USAGE}
    echo ${NOTICE_PARAMS}
    exit 1
fi
