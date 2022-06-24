import RPi.GPIO as GPIO
import time

#Defining Pins for Reading
sine = 35 # White 37
cosine = 37 # Green 35
revPin = 33 # Yellow 33

dir = 0

count = 0
rev_count = 0

current_rev_ind = 0
previous_rev_ind = 0

current_sine = 0
previous_sine = 0
current_cosine = 0
previous_cosine = 0

def init():

	GPIO.setmode(GPIO.BOARD)

	GPIO.setup(sine,GPIO.IN)
	GPIO.setup(cosine,GPIO.IN)	
	GPIO.setup(revPin,GPIO.IN)

def stop():
	GPIO.cleanup((sine,cosine,revPin))

def read():
	global rev_count
	global count
	global current_sine
	global previous_sine
	global current_cosine
	global previous_cosine
	global current_rev_ind
	global previous_rev_ind
	global dir

	current_sine = GPIO.input(sine)
	current_cosine = GPIO.input(cosine)
	current_rev_ind = GPIO.input(revPin)
	#--------------------Rev Counter------------------
	if current_rev_ind!=previous_rev_ind and current_rev_ind > previous_rev_ind:
		rev_count +=1
		count = 0

		print("RevCount = ",rev_count)
		print("=====================")

	previous_rev_ind = current_rev_ind
	#-------------------Pulse Counter-----------------
	if(current_sine > current_cosine):	dir = 1
	if(current_sine < current_cosine):  dir = -1
	
	if(current_sine!= previous_sine and current_sine > previous_sine):
		
		count += dir

		print("count = ",count)
	
	previous_sine = current_sine


if __name__ == '__main__':
	try:
		GPIO.cleanup()
		init()
		while True:
			read()
	except KeyboardInterrupt:
		stop()
		print('stopped')
				
