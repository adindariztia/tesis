import time
import socketio
import random

thread = None
sio = socketio.Client(logger=False, engineio_logger=False)
start_timer = None

def background_thread():
    while True:
        b = random.randrange(10)
        if b > 5:
            print(b)
            send_coba()
            sio.sleep(5)


@sio.event
def connect():
    print('connected to server')
    # send_ping()
    global thread
    if thread is None:
        sio.start_background_task(background_thread)

@sio.event
def send_coba():
    sio.emit('cobadariclient', {'data': 'BISA GAKK'})

@sio.event
def coba_dari_server(data):
    print(data)


if __name__ == '__main__':
    sio.connect('http://localhost:5000')

    # sio.wait()