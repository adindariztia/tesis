import time
import socketio
import random
import time
import board
import adafruit_dht
import psutil

sensor_temp = 0
sensor_humidity = 0

#for proc in psutil.process_iter():
    #print(proc)
#    if proc.name() == 'libgpiod_pulsein' or proc_name() == 'libgpiod_pulsei':
#        proc.kill()

sensor = adafruit_dht.DHT11(board.D23)

thread = None
sio = socketio.Client(logger=False, engineio_logger=False)
start_timer = None

def background_thread():
    while True:
        b = random.randrange(10)
        if b > 5:
            print(b)
            send_sensorData()
            sio.sleep(5)


@sio.event
def connect():
    print('connected to server')
    # send_ping()
    global thread
    if thread is None:
        sio.start_background_task(background_thread)

@sio.event
def send_sensorData():
    try:
        temp = sensor.temperature
        humidity = sensor.humidity
        global sensor_temp
        global sensor_humidity
        
        sensor_temp = temp
        sensor_humidity = humidity
        print("temperature: {}C humidity: {}% ".format(temp, humidity))
    except RuntimeError as error:
        print(error.args[0])
        time.sleep(1.0)
        #continue
    except Exception as error:
        sensor.exit()
        raise error
    time.sleep(1.0)
    
    sio.emit('cobadariclient', {'data_temp': sensor_temp, 'data_humid': sensor_humidity})

@sio.event
def coba_dari_server(data):
    print(data)


if __name__ == '__main__':
    sio.connect('http://192.168.137.185:5000')

    # sio.wait()