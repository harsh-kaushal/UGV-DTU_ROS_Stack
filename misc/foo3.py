import time

def dir(vel): return vel >= 0.0

def clamp(n,l_limit,u_limit): return max(min(u_limit, n), l_limit)

def vel2pwm(vel,min_vel,max_vel):
    if dir(vel):
        return vel*100/max_vel 
    else:
        return vel*100/min_vel

def run():
    max_vel = 1.5
    min_vel = -1.0

    global lw_vel
    global rw_vel
    lw_vel = 1.1
    rw_vel = 1.2
       
    lw_vel = clamp(lw_vel,min_vel,max_vel)
    rw_vel = clamp(rw_vel,min_vel,max_vel)

    # print(lw_vel)
    # print(rw_vel)  

    if (lw_vel == 0.0 and rw_vel== 0.0):
        # pwm1.ChangeDutyCycle(0.0)
        # pwm2.ChangeDutyCycle(0.0)  
        print(lw_vel)
        print(rw_vel)     
    else:

        # print(dir(lw_vel))
        # print(dir(rw_vel))
        # print(lw_vel)
        # print(rw_vel)  

        lw_vel = vel2pwm(lw_vel,min_vel,max_vel)
        rw_vel = vel2pwm(rw_vel,min_vel,max_vel)

        # print('Attempting to run at %d % & %d % Duty',lw_vel,rw_vel)

        # print(lw_vel)
        # print(rw_vel) 

if __name__ == '__main__':
    count =0
    try:

        st = time.time()
        while True:
            run()
            count +=1
            if (time.time()-st) > 1: 
                print(count)
                break
    except KeyboardInterrupt:
        print("OPPS")
