#!/bin/sh

ENVDIR=${HOME}/env.pigpio

ACTIVATE_SCRIPT=${ENVDIR}/bin/activate

CMD=robocar.py

if [ ! -f ${ACTIVATE_SCRIPT} ]; then
    echo ${ACTIVATE_SCRIPT}: no such file
    exit 1
fi

. ${ENVDIR}/bin/activate

exec ${CMD}
