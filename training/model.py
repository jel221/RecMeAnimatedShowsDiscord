import json
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import pathlib
import copy

animecsv = pd.read_csv("./anime.csv")
ratingcsv = pd.read_csv("./rating_complete.csv")

def get_result(rows, num):
    pass