import json
import tensorflow as tf
import numpy as np

class Model:
    def __init__(self):
        self.interpreter = tf.lite.Interpreter(model_path="optimised_model.tflite")
        self.interpreter.allocate_tensors()

        with open("./top.json") as file:
            self.top = json.load(file)

    def get_result(self, rows, num):
        watched = np.zeros(2000, dtype='float32')
        for mal_id, rating in rows:
            if mal_id in self.top:
                idx = self.top[mal_id]
                input[idx] = rating

        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        self.interpreter.set_tensor(input_details[0]['index'], [watched])
        self.interpreter.invoke()

        output_data = self.interpreter.get_tensor(output_details[0]['index'])

        top_copy = self.top[:]
        sorted_output = sorted(zip(output_data, top_copy.keys()), reverse=True) # Sorts according to the first tuple value by default

        result = []
        i = 0
        while len(result) < 5:
            show = sorted_output[i]
            if not watched[self.top[show]]:
                result.append(show[1])
            i += 1
                
        return result