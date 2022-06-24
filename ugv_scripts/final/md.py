#!/usr/bin/env python
import rospy
from std_msgs.msg import Float32

import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

in1 = 10
an1 = 12

in2 = 16
an2 = 36

lw_vel = 0.0
rw_vel = 0.0

def init():

    global pwm1
    global pwm2	

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(in1,GPIO.OUT)
    GPIO.setup(an1,GPIO.OUT)

    GPIO.setup(in2,GPIO.OUT)
    GPIO.setup(an2,GPIO.OUT)

    pwm1 = GPIO.PWM(an1,490)
    pwm2 = GPIO.PWM(an2,490)

    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.LOW)
    pwm1.start(0)
    pwm2.start(0)

def stop():

    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup((in1,in2))

def dir(vel): return vel >= 0.0

def clamp(n,l_limit,u_limit): return max(min(u_limit, n), l_limit)

def vel2pwm(vel,min_vel,max_vel):
    if dir(vel):
        return abs(vel*100/max_vel)
    else:
        return abs(vel*100/min_vel)

def run():
    #max_vel = 1.5
    max_vel = 2.5/0.16 # ros hardware interface uses angular velocities so 2.5(m/s)/0.16(m) = 15.625 rad/sec
    min_vel = -2.5/0.16

    global lw_vel
    global rw_vel

    print('Recieved %d & %d',lw_vel,rw_vel)

    lw_vel = clamp(lw_vel,min_vel,max_vel)
    rw_vel = clamp(rw_vel,min_vel,max_vel)

    if (lw_vel == 0.0 and rw_vel== 0.0):
        pwm1.ChangeDutyCycle(0.0)
        pwm2.ChangeDutyCycle(0.0)       
    else:

        GPIO.output(in1,dir(lw_vel)) # Setting the Direction of motors
        GPIO.output(in2,dir(rw_vel))

        lw_vel = vel2pwm(lw_vel,min_vel,max_vel)
        rw_vel = vel2pwm(rw_vel,min_vel,max_vel)

        print('Attempting to run at %d % & %d % Duty',round(lw_vel,3),round(rw_vel,3))

        pwm1.ChangeDutyCycle(lw_vel)
        pwm2.ChangeDutyCycle(rw_vel)
        print('Ran: %d & %d',lw_vel,rw_vel)

def lw_sub(msg):
    global lw_vel
    lw_vel = msg.data

def rw_sub(msg):
    global rw_vel
    rw_vel = msg.data

if __name__ == '__main__':
    try:
        GPIO.cleanup()
        init()
        rospy.init_node('cmd_vel_executioner', anonymous=False)
        rate = rospy.Rate(10)    
        while not rospy.is_shutdown():
            rospy.Subscriber("/diffbot/motor_left", Float32, lw_sub)
            rospy.Subscriber("/diffbot/motor_right", Float32, rw_sub)
            run()

            rate.sleep()

    except rospy.ROSInterruptException:
        stop()
        print('Stopped At: %d,%d',lw_vel,rw_vel)
        print('Old Moter Driver had a Shit, E-I-E-I-O')
