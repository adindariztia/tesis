from flask import Flask, render_template
import socketio
from random import randint, random

async_mode = None
sio = socketio.Server(logger = True, async_mode = async_mode)
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)
thread = None

data_dari_client = 0

#nanti ngejalanin predictionnya disini nih
def background_thread():
    count = 0
    while True:
        sio.sleep(1)
        count+= 1

        temp = randint(1,100)
        broadcast_to_all = temp #"server_generated_event"
        global data_dari_client

        if data_dari_client != 0:
            broadcast_to_all = data_dari_client
            data_dari_client = 0
        sio.emit("my_response", {"data": broadcast_to_all})
        
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
def disconnect(sid):
    print("disconnected", sid)
    disc = "sid: " + str(sid)
    sio.emit("disconnect_broadcast", {'data': disc})

@sio.event
def coba(sid, data):
    print("DINDDDD LIAT ", sid, data)
    sio.emit("response_coba", {'data': 'hae juga'})

@sio.event
def cobadariclient(sid, data):
    print('DAPET DATA DARI CLIENT NIHH ', data)
    global data_dari_client
    data_dari_client = data['data']
    sio.emit('coba_dari_server', {'data': 'DARI SERVER NIHHH'}, to=sid)


if __name__ == '__main__':
    if sio.async_mode == 'threading':
        # deploy with Werkzeug
        app.run(host='0.0.0.0',threaded=True)
    elif sio.async_mode == 'eventlet':
        # deploy with eventlet
        import eventlet
        import eventlet.wsgi
        eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
    elif sio.async_mode == 'gevent':
        # deploy with gevent
        from gevent import pywsgi
        try:
            from geventwebsocket.handler import WebSocketHandler
            websocket = True
        except ImportError:
            websocket = False
        if websocket:
            pywsgi.WSGIServer(('', 5000), app,
                              handler_class=WebSocketHandler).serve_forever()
        else:
            pywsgi.WSGIServer(('', 5000), app).serve_forever()
    elif sio.async_mode == 'gevent_uwsgi':
        print('Start the application through the uwsgi server. Example:')
        print('uwsgi --http :5000 --gevent 1000 --http-websockets --master '
              '--wsgi-file app.py --callable app')
    else:
        print('Unknown async_mode: ' + sio.async_mode)