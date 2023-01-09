import json
import tensorflow as tf
import numpy as np

class Model:
    def __init__(self):
        self.interpreter = tf.lite.Interpreter(model_path="training/example_model.tflite")
        self.interpreter.allocate_tensors()

        with open("training/top.json") as file:
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

        probabilities = output_data[0]
        top_copy = self.top.copy()
        sorted_output = sorted(zip(probabilities, top_copy.keys()), reverse=True) # Sorts according to the first tuple value by default

        result = []
        while len(result) < num:
            show = sorted_output[i][1]
            if not watched[self.top[show]]:
                result.append(show)
                
        return result