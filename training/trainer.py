import json
import numpy as np
import pandas as pd
import tensorflow as tf
import pathlib
import os

top_anime_csv = pd.read_csv("./anime.csv")
rating_csv = pd.read_csv("./rating.csv")

mal_ids = top_anime_csv["MAL_ID"]

INPUT_SIZE = 500

id_to_idx = {int(mal_ids[i]):i for i in range(INPUT_SIZE)}
if not os.path.exists("./top.json"):
    with open("./top.json", "w+") as file:
        json.dump(id_to_idx, file)

all_ratings = rating_csv.groupby("user_id")

def trainset_generator():
    row = 0
    for uid in all_ratings.groups.keys():
        user_rating = np.zeros(INPUT_SIZE)
        curr_group = all_ratings.get_group(uid)
        
        for _ in range(len(curr_group)):
            anime_id = curr_group["anime_id"][row]
            if anime_id in id_to_idx:
                idx = id_to_idx[anime_id]
                user_rating[idx] = curr_group["rating"][row]
            row += 1

        if not np.any(user_rating):
            continue

        for i in np.nonzero(user_rating)[0]:
            input_arr = np.copy(user_rating)
            target_arr = np.zeros(INPUT_SIZE)
            target_arr[i] = input_arr[i]
            input_arr[i] = 0
            yield (np.array([input_arr]), np.array([target_arr]))


model = tf.keras.Sequential([
    tf.keras.layers.InputLayer((INPUT_SIZE)),
    tf.keras.layers.Embedding(INPUT_SIZE, 20),
    tf.keras.layers.Dense(32, "relu"),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(INPUT_SIZE, "softmax")
])

model.compile(tf.keras.optimizers.Adam(), tf.keras.losses.CategoricalCrossentropy(), metrics=["accuracy"])

model.summary()

model.fit(x=trainset_generator(), use_multiprocessing=True)

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

tflite_models_dir = pathlib.Path("./")
tflite_models_dir.mkdir(exist_ok=True, parents=True)

tflite_model_file = tflite_models_dir/"model.tflite"
tflite_model_file.write_bytes(tflite_model)

converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_quant_model = converter.convert()
tflite_model_quant_file = tflite_models_dir/"optimised_model.tflite"
tflite_model_quant_file.write_bytes(tflite_quant_model)