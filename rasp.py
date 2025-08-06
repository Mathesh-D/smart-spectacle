import RPi.GPIO import GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)

try:
    while True:
        GPIO.output(18,GPIO.HIGH)
        time.sleep(1)
        GPIO.output(18,GPIO.LOw)
except KeyboardInterrupt:
    print("Stopped")
finally:
    GPIO.cleanup()
    