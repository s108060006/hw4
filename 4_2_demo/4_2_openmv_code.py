import pyb, sensor, image, time, math

THRESHOLD = (0,100) # Grayscale threshold for dark things...
BINARY_VISIBLE = True

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
clock = time.clock()

uart = pyb.UART(3,9600,timeout_char=1000)
uart.init(9600,bits=8,parity = None, stop=1, timeout_char=1000)

while(True):
    clock.tick()
    img = sensor.snapshot().binary([THRESHOLD]) if BINARY_VISIBLE else sensor.snapshot()
    line = img.get_regression([(255,255) if BINARY_VISIBLE else THRESHOLD], False, (20, 0, 120, 20))

    if (line): img.draw_line(line.line(), color = 127)
    theta = line.theta() if(line) else 0
    rho = line.rho() if(line) else 0
    if (rho < 0) :
        theta = abs(theta - 180)

    mid_approx = abs(rho) / math.cos(math.radians(theta))
    if (line) :
        diff_dis = mid_approx - 80
        if (abs(diff_dis) <= 30 and diff_dis < 0 and theta > 60) :  # turn right
            uart.write(("/turn/run 80 -0.5 \n").encode())
            print("right")
        elif(abs(diff_dis) <= 30 and diff_dis > 0 and theta > 60) : # turn left
            uart.write(("/turn/run 80 0.5 \n").encode())
            print("left")
        elif (abs(diff_dis) <= 30) :                             # go straight
            uart.write(("/goStraight/run 80 \n").encode())
            print("straight")
        elif (diff_dis > 0) :                                   # turn left
            uart.write(("/turn/run 80 0.5 \n").encode())
            print("left")
        elif (diff_dis < 0) :                                    # turn right
            uart.write(("/turn/run 80 -0.5 \n").encode())
            print("right")
        else :
            uart.write(("/stop/run \n").encode())
            #print("stop\n")
        time.sleep(0.05)
        print("FPS %f, theta = %f, diff_dis = %f, mid_approx = %f\n" % (clock.fps(), theta, diff_dis, mid_approx))
    else :
        uart.write(("/stop/run \n").encode())
        print("stop\n")
        time.sleep(0.05)
