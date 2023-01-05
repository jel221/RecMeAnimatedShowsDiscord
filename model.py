import json
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import pathlib
import copy

animecsv = pd.read_csv("./anime.csv")
ratingcsv = pd.read_csv("./rating_complete.csv")

ids = []

for i in range(len(animecsv["MAL_ID"])):
    if animecsv["Popularity"][i] < 1000 and animecsv["Popularity"][i] > 0:
        ids.append(animecsv["MAL_ID"][i])

id_to_num = {}

for i in range(len(ids)):
    id_to_num[ids[i]] = i


l=0
for i in id_to_num:
    print(str(i) + ":" + str(id_to_num[i]))
    l+=1
    if l == 5:
        break

with open('data.txt', 'w') as outfile:
    data = {}
    for i in id_to_num:
        for j in range(len(animecsv["MAL_ID"])):
            if animecsv["MAL_ID"][j] == i:
                if animecsv["English name"][j] != "Unknown":
                    if animecsv["English name"][j] in data.keys():
                        data[str(i)] = id_to_num[i]
                    else:
                        data[animecsv["English name"][j]] = id_to_num[i]
                else:
                    if animecsv["Name"][j] in data.keys():
                        data[str(i)] = id_to_num[i]
                    else:
                        data[animecsv["Name"][j]] = id_to_num[i]                
    json.dump([data], outfile)

animes1k = pd.DataFrame(columns=['anime_id', 'English name', 'Type', 'Source', 'Rating', 'Genres'])

for i in range(len(animecsv["MAL_ID"])):
    if animecsv["Popularity"][i] < 1000 and animecsv["Popularity"][i] > 0:
        
        id = animecsv["MAL_ID"][i]
        name = animecsv["English name"][i]
        type = animecsv["Type"][i]
        source = animecsv["Source"][i]
        rating = animecsv["Rating"][i]
        genres =  animecsv["Genres"][i].split(", ")
        
        row = [id, name, type, source, rating, genres]
                
        temp = pd.DataFrame([row], columns=['anime_id', 'English name','Type', 'Source', 'Rating', 'Genres'])
        animes1k = animes1k.append(temp, ignore_index=True)
        
print("1k")
        
# this is a generator that 
def ratings():
    user_current = -1
    xs = []
    ys = []
    x = [0 for i in range(len(ids))] # an array of zeros, this is 1000 long and will be filled in with ones if the referenced anime was watched
    nums = []
    for i in range(len(ratingcsv["user_id"])): # looping over the csv
        if ratingcsv["anime_id"][i] in ids: # if the anime is in the top 1000
            user = ratingcsv['user_id'][i] # what is the id of the user
            if user == user_current: # if the user is the same I will update their history
                x[id_to_num[ratingcsv['anime_id'][i]]] = 1
                nums.append(id_to_num[ratingcsv['anime_id'][i]])
            else: # if it is a new user I will yield the previous one and craete a new one
                user_current+=1
                for num in nums: # corrupt the users history, I take one out and that is the input. The target is the one that was removed
                    temp_y = [0 for i in range(len(ids))]
                    temp_x = copy.deepcopy(x) # shallow coppies do not work ):
                    
                    temp_y[num] = 1
                    temp_x[num] = 0
                                        
                    if temp_y.count(temp_y[0]) != len(temp_y) and temp_x.count(temp_x[0]) != len(temp_x):                                                                    
                        ys.append(temp_y)
                        xs.append(temp_x)
                        
                if bool(xs) == True and bool(ys) == True:
                    yield np.array([xs, ys]) # only yeild if they have seen 2 or more in the top 1000
                xs = [] # restart
                ys = []
                x = [0 for i in range(len(ids))]
                nums = []
                x[id_to_num[ratingcsv['anime_id'][i]]] = 1
                nums.append(id_to_num[ratingcsv['anime_id'][i]])

model = tf.keras.Sequential([ # create a model. It is simple as to have very fast inferance time
    tf.keras.layers.Input((1000)),
    tf.keras.layers.Embedding(1000, 10),
    tf.keras.layers.Dense(32, "relu"),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(1000, "softmax")
])

model.compile("adam", tf.keras.losses.CategoricalCrossentropy(), metrics=["categorical_accuracy"])

model.summary()

gen = ratings() 

# training, this prints the loss and accuracy every 2000 examples and logs it for plots every 250

scores = []
i = 0

for x, y in gen:
    if i % 100 == 0:
        score = model.train_on_batch(x,y)
        scores.append(score)
        if i % 2000 == 0:
            print(score)
    else:
        model.train_on_batch(x,y)
    if i == 10000: # limited to 10000 because of train time, the model uploaded was about 75000
        break
    i+=1

loss = []
acc = []

for i, j in scores:
    loss.append(i)
    acc.append(j)

plt.plot(loss)
plt.ylabel('loss (lower is better)')
plt.show()

plt.plot(acc)
plt.ylabel('accuracy (higher is better)')
plt.show()

# convert to tflite model
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