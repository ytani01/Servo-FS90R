#!/usr/bin/env python

# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import print_function

import sys
import socket

import argparse
import os.path
import json

import google.auth.transport.requests
import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file

import subprocess
#import RPi.GPIO as GPIO
from time import sleep
from pixels import pixels

ROBOT_HOST = 'localhost'
ROBOT_PORT = 12340

SOUND_DIR = '/home/pi/sound'
SOUND_ACK = [
	SOUND_DIR + '/computerbeep_43.mp3',
	SOUND_DIR + '/computerbeep_58.mp3',
	SOUND_DIR + '/computerbeep_12.mp3']

proc = None

PIN_LAMP = 12
PIN_BUTTON = [13, 17]
BOUNCE_MSEC = 500

endword = [
        ['ありがとう', True],
        ['またね', True],
        ['また後で', True],
        ['行ってきます', True],
        ['もういい', True],
        ['特にない',True],
        ['じゃあまた', True],
        ['じゃまた', True],
        ['さようなら', True],
        ['バイバイ', True],
        ['終了', False],
        ['ストップ', False],
        ['オーケー', False],
        ['OK', False],
        ['おやすみ', True],
        ['お休みなさい',True],
        ['null', False]]
continue_flag = True
timeout_count = 0

DEVICE_API_URL = 'https://embeddedassistant.googleapis.com/v1alpha2'

def robot_cmd(cmd):
    sock = socket.create_connection((ROBOT_HOST, ROBOT_PORT), 0.4)
    sock.settimeout(0.1)
    while True:
        try:
            data = sock.recv(1024)
            print(data)
        except socket.timeout:
            break
    sock.settimeout(0.7)
    sock.sendall(cmd.encode('utf-8'))
    sock.close()

def setContinueFlag(speech_str):
    global assistant
    global continue_flag
    global timeout_count

    print('> setContineFlag(', speech_str, ') ', end='')
    continue_flag = True

    for w in endword:
        if w[0] in speech_str:
            print(w[0], ' ', end='')
            continue_flag = False
            timeout_count = 0
            if not w[1]:
                assistant.stop_conversation()
    print(continue_flag)

def turnEnd():
    global assistant
    global continue_flag

    print('> turnEnd() continue_flag=', continue_flag)
    if continue_flag:
        assistant.start_conversation()
    else:
        continue_flag = True
        timeout_count = 0
        play_ack(0)
        print()

    # マイクが自然にミュートになってしまった場合に解除する
    cmd = ['amixer', 'sset', 'Mic', 'toggle']
    proc = subprocess.call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc = subprocess.call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
def procButton(pin):
    global assistant
    global continue_flag
    global timeout_count

    if pin in PIN_BUTTON:
            continue_flag = True
            timeout_count = 0
            assistant.start_conversation()
    print()

def play_ack(num):
    global proc

    if proc != None:
        proc.terminate()
    cmd = ['cvlc', '-q', '--play-and-exit', SOUND_ACK[num]]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    if num == 0:
        pixels.off()
    if num == 1:
        pixels.think()
#    if num == 2:
#        pixels.think()

#    sleep(0.5)

def process_device_actions(event, device_id):
    if 'inputs' in event.args:
        for i in event.args['inputs']:
            if i['intent'] == 'action.devices.EXECUTE':
                for c in i['payload']['commands']:
                    for device in c['devices']:
                        if device['id'] == device_id:
                            if 'execution' in c:
                                for e in c['execution']:
                                    if e['params']:
                                        yield e['command'], e['params']
                                    else:
                                        yield e['command'], None



def process_event(event, device_id):
    global assistant
    global continue_flag
    global timeout_count

    """Pretty prints events.

    Prints all events that occur with two spaces between each new
    conversation and a single space between turns of a conversation.

    Args:
        event(event.Event): The current event to process.
    """
    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        print()

    print(event)

    if event.type == EventType.ON_START_FINISHED:
        play_ack(0)

    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        play_ack(1)

    if event.type == EventType.ON_END_OF_UTTERANCE:
        play_ack(2)

    if event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
        speech_str = event.args['text']
        if '照明' in speech_str:
            if 'つけて' in speech_str:
                #GPIO.output(PIN_LAMP, GPIO.HIGH)
                assistant.stop_conversation()
            if '消して' in speech_str:
                #GPIO.output(PIN_LAMP, GPIO.LOW)
                assistant.stop_conversation()
        if 'ikea ライト' in speech_str:
            #GPIO.output(PIN_LAMP, GPIO.LOW)
            sleep(0.5)
            #GPIO.output(PIN_LAMP, GPIO.HIGH)
        if '回転' in speech_str:
            if '右' in speech_str:
                assistant.stop_conversation()
                robot_cmd('D')
            if '左' in speech_str:
                assistant.stop_conversation()
                robot_cmd('A')
        if '前進' in speech_str:
            assistant.stop_conversation()
            robot_cmd('A')
        if 'バック' in speech_str:
            assistant.stop_conversation()
            robot_cmd('X')


        setContinueFlag(speech_str)

    if event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT:
        timeout_count += 1
        if timeout_count >= 2:
            timeout_count = 0
            continue_flag = False
        turnEnd()

    if event.type == EventType.ON_NO_RESPONSE:
        turnEnd()

    if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and
            event.args and not event.args['with_follow_on_turn']):
        turnEnd()

    if event.type == EventType.ON_DEVICE_ACTION:
        for command, params in process_device_actions(event, device_id):
            print('Do command', command, 'with params', str(params))


def register_device(project_id, credentials, device_model_id, device_id):
    """Register the device if needed.

    Registers a new assistant device if an instance with the given id
    does not already exists for this model.

    Args:
       project_id(str): The project ID used to register device instance.
       credentials(google.oauth2.credentials.Credentials): The Google
                OAuth2 credentials of the user to associate the device
                instance with.
       device_model_id: The registered device model ID.
       device_id: The device ID of the new instance.
    """
    base_url = '/'.join([DEVICE_API_URL, 'projects', project_id, 'devices'])
    device_url = '/'.join([base_url, device_id])
    session = google.auth.transport.requests.AuthorizedSession(credentials)
    r = session.get(device_url)
    print(device_url, r.status_code)
    if r.status_code == 404:
        print('Registering....', end='', flush=True)
        r = session.post(base_url, data=json.dumps({
            'id': device_id,
            'model_id': device_model_id,
            'client_type': 'SDK_LIBRARY'
        }))
        if r.status_code != 200:
            raise Exception('failed to register device: ' + r.text)
        print('\rDevice registered.')


def main():
    global assistant

    pixels.wakeup()

#    GPIO.setmode(GPIO.BCM)
#    GPIO.setup(PIN_LAMP, GPIO.OUT)
#    for p in PIN_BUTTON:
#        GPIO.setup(p, GPIO.IN, GPIO.PUD_UP)
#        if p == 13: # toggle button
#            GPIO.add_event_detect(p, GPIO.BOTH, callback=procButton, \
#                    bouncetime=BOUNCE_MSEC)
#        else:
#            GPIO.add_event_detect(p, GPIO.FALLING, callback=procButton, \
#                    bouncetime=BOUNCE_MSEC)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--credentials', type=existing_file,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'google-oauthlib-tool',
                            'credentials.json'
                        ),
                        help='Path to store and read OAuth2 credentials')
    parser.add_argument('--device_model_id', type=str,
                        metavar='DEVICE_MODEL_ID', required=True,
                        help='The device model ID registered with Google')
    parser.add_argument(
        '--project_id',
        type=str,
        metavar='PROJECT_ID',
        required=False,
        help='The project ID used to register device instances.')
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s ' +
        Assistant.__version_str__())

    args = parser.parse_args()
    with open(args.credentials, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))

    with Assistant(credentials, args.device_model_id) as assistant:
        events = assistant.start()

        print('device_model_id:', args.device_model_id + '\n' +
              'device_id:', assistant.device_id + '\n')

        if args.project_id:
            register_device(args.project_id, credentials,
                            args.device_model_id, assistant.device_id)

        for event in events:
            process_event(event, assistant.device_id)


if __name__ == '__main__':
  try:
    main()
  finally:
    pixels.off()
#    print('GPIO.cleanup()')
#    GPIO.cleanup()
