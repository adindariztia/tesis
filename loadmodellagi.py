import numpy as np
from tensorflow import keras

sensor_data = np.asarray([12.3, 12, 12, 12])
sensor_data = sensor_data.reshape(4,1)

model = keras.models.load_model('modelMPL2.h5')

y = model.predict(sensor_data)

output = np.argmax(y)

print(output)