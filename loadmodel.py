import numpy as np
import tensorflow as tf

#load tflite model and allocate sensors
interpreter = tf.lite.Interpreter(model_path="ModelMLP2.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

sensor_data = [[22,  16.9, 22,  16.9]]



input_shape = input_details[0]['shape']
input_data = np.array(sensor_data, dtype=np.float32)
interpreter.set_tensor(input_details[0]['index'], input_data)

output_data = interpreter.get_tensor(output_details[0]['index'])
print(output_data)

# print(np.random.random_sample(input_shape))