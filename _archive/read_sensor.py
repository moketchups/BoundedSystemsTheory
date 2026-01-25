import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600)
f = open('sensor_data.csv', 'a')

while True:
    line = ser.readline().decode().strip()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    f.write(f'{timestamp},{line}\n')
    f.flush()
