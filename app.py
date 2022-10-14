from flask import Flask, render_template
import socketio

async_mode = None
sio = socketio.Server(logger = True, async_mode = async_mode)
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)
thread = None

def background_thread():
    count = 0
    while True:
        sio.sleep(2)
        count+= 1
        sio.emit("my_response", {"data": "server generated event"})
        
@app.route('/')
def index():
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)
    return render_template('index.html')

@sio.event
def connect(sid, environ):
    sio.emit("my_response", {'data': 'connected', 'count': 0})
    
@sio.event
def disconnected(sid):
    print("disconnected", sid)
    disc = "sid: " + str(sid)
    sio.emit("disconnect_broadcast", {'data': disc})

@sio.event()
def coba(sid, data):
    print("DINDDDD LIAT ", sid, data)
    sio.emit("response_coba", {'data': 'hae juga'})
    
if __name__ == '__main__':
    app.run()