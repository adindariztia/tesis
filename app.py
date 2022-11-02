from flask import Flask, render_template
import socketio
from random import randint, random
import math
import numpy as np
import tensorflow as tf

async_mode = None
sio = socketio.Server(logger = True, async_mode = async_mode)
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)
thread = None

client_temp = 0
client_humid = 0
data_counter = 0

interpreter = tf.lite.Interpreter(model_path="ModelMLP2.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

inputSensorData = [[22,  16.9, 22,  16.9]]

input_shape = input_details[0]['shape']

def predict_data(inputSensorData):
    input_data = np.array(inputSensorData, dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    
    output_data = interpreter.get_tensor(output_details[0]['index'])
    
    return output_data

def preprocess_prediction():
    global inputSensorData
                 
    outputPred = predict_data(inputSensorData)
            
    resTemp = outputPred[0][0]
    resHumid = outputPred[0][1]
            
    if (resTemp < 1 or resHumid < 1):
        resTemp, resHumid = randint(19,22), randint(15,19)
        
    print(resTemp, resHumid)
        
    return resTemp, resHumid

#nanti ngejalanin predictionnya disini nih
def background_thread():
    count = 0
    while True:
        sio.sleep(1)
        count+= 1

        # temp = randint(1,100)
        global client_temp
        global client_humid      

        if (client_temp != 0 and client_humid!= 0):
            
            broadcast_temp, broadcast_humid = client_temp, client_humid
            
            
            client_temp, client_humid = 0, 0
            broadcastResult(broadcast_temp, broadcast_humid)
        else:
            resTemp, resHumid = preprocess_prediction()
            broadcast_temp = round(resTemp) #GANTI PAKE DATA HASIL PRED
            broadcast_humid = round(resHumid) #GANTI PAKE DATA HASIL PRED
            
            broadcastResult(broadcast_temp, broadcast_humid)
            
    
def broadcastResult(temp, humid):
    if (temp != 0 and humid != 0):
        sio.emit("my_response", {"data_temp": int(temp), "data_humid": int(humid)})
        preparenextpred(temp, humid)
        

def preparenextpred(temp, humid):
    global inputSensorData
    global data_counter
    

    del inputSensorData[0][0]
    inputSensorData[0].append(temp)
    del inputSensorData[0][0]
    inputSensorData[0].append(humid)
    data_counter +=1
    
    if data_counter >= 2:
        sensorDataRequest()

@sio.event
def sensorDataRequest():
    global client_temp
    sio.emit("data_request", {"data": 1})
    
      
        
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
def client_sensor_data(sid, data):
    print('DAPET DATA DARI CLIENT NIHH ', data)
    global client_temp
    global client_humid
    client_temp = data['data_temp']
    client_humid = data['data_humid']
    
    server_res = 0
    
    if (not math.isnan(client_temp) and not math.isnan(client_humid)):
        server_res = 1
    sio.emit('server_respond', {'data': server_res}, to=sid)


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