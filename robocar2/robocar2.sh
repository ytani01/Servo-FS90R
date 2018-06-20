#!/bin/sh

ENVDIR=${HOME}/env.pigpio

ACTIVATE_SCRIPT=${ENVDIR}/bin/activate

WORK_DIR=${HOME}/Servo-FS90R/robocar2
CMD=${WORK_DIR}/robocar2.py

if [ ! -f ${ACTIVATE_SCRIPT} ]; then
    echo ${ACTIVATE_SCRIPT}: no such file
    exit 1
fi

. ${ENVDIR}/bin/activate

cd ${WORK_DIR}
exec ${CMD}
