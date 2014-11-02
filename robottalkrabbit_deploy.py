#!/usr/bin/env python
import json
from subprocess import call
from time import sleep
import sys
import os
import pika
import logging
import subprocess
import signal

#configuraiton
leftServoId = 1
rightServoId = 2
servoMiddle = 150
leftStop = 152
rightStop = 151
maxSpeedLeft = 50
maxSpeedRight = 50
degreesPerSecond = 360/3.4
cmPerSecond = 100/4.5
json_data=open('/usr/local/sbin/config.json')
config = json.load(json_data)
json_data.close()
raspividSubProcess = None

print(config["amqp_pw"])

#functions
def call_command(servo, pulsewidth):
	command = 'echo ' + str(servo) + '=' + str(pulsewidth) + ' > /dev/servoblaster'
	os.system(command)
	print(command)

def move(cm, direction):
	call_command(leftServoId, leftStop - maxSpeedLeft * direction)
	call_command(rightServoId, rightStop + maxSpeedRight * direction)
	sleep(cm/cmPerSecond)
	call_command(leftServoId, leftStop)
	call_command(rightServoId, rightStop)
	print('move')

def turn(degrees, direction):
	print('degrees ' + str(degrees))
	print('dir ' + str(direction))
	call_command(leftServoId, leftStop - maxSpeedLeft * direction)
	call_command(rightServoId, rightStop -maxSpeedRight * direction)
	sleep(degrees/degreesPerSecond)
	call_command(leftServoId,leftStop)
	call_command(rightServoId, rightStop)
	print('turn')
def stream():
	print('starting stream...')
	global raspividSubProcess
        raspividSubProcess  = subprocess.Popen('/usr/local/sbin/raspi2ffmpeg.sh',stdout=subprocess.PIPE,shell=True,  preexec_fn=os.setsid)
        print(raspividSubProcess.pid)
	print('subprocess opened')
def streamoff():
	print('stream stopping...')
        print(raspividSubProcess.pid)
        os.killpg(raspividSubProcess.pid, signal.SIGTERM)
	print('subprocess stopped')
#read from queue
logging.basicConfig()
creds = pika.PlainCredentials('pmvpkimx',config["amqp_pw"])
connection = pika.BlockingConnection(pika.ConnectionParameters(host='turtle.rmq.cloudamqp.com',port=5672,credentials=creds,virtual_host='pmvpkimx'))
channel = connection.channel()
#channel.queue_declare(queue='tilt')
print 'Waiting for messages...'

def callback(ch,method,properties,body):
	print ' [x] Received %r' % (body,)
	args = body.split(' ', 3)
	print args
	command = args[0]
	if len(args) > 1:
        	movement = int(args[1])
		direction = int(args[2])
	if str(command) == 'turn':
		turn(movement,direction)
	elif str(command) == 'move':
		move(movement,direction)
        elif str(command) == 'stream':
	        print('***calling stream***')	
                stream()
  	elif str(command) == 'streamoff':
		print('***calling stream OFF***')
		streamoff()

channel.basic_consume(callback,queue='tilt',no_ack=True)
channel.start_consuming()

#print str(sys.argv)
#if str(sys.argv[1]) == 'turn':
#	turn(1,1)
#else:
#	move(int(sys.argv[1]),int(sys.argv[2]))

#move(sys.argv[1],sys.argv[2])
#main
#movement = 20
#direction = 1
#move(movement,direction)

#direction = -1
#move(movement,direction)
#movement = 100

#turn(movement, direction)
#turn(90,1)
#turn(360,1)
#turn(270,-1)
#turn(1,1)


 


	

