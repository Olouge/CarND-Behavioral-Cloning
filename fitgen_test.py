import tensorflow as tf
tf.python.control_flow_ops = tf

from keras.models import Sequential, model_from_json, load_model
from keras.optimizers import Adam, SGD
from keras.layers.core import Dense, Activation, Flatten, Dropout
from keras.layers.convolutional import Convolution2D
from keras.layers.pooling import MaxPooling2D
from keras.preprocessing.image import *

from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split

import matplotlib.pyplot as plt
import tables
import sys
import cv2


# -------------------------------------
# Command line argument processing
# -------------------------------------
if len(sys.argv) < 2:
    print("Missing training data file.")
    print("python3 model.py <data.h5> <epoch_cnt>")

H5_FILE = str(sys.argv[1])

EPOCH = 1
if len(sys.argv) >2:
    EPOCH = int(sys.argv[2])

# ------------------
# Read data from preprocessed HDF5 file
# ------------------
f = tables.open_file(H5_FILE, 'r')

# -------------------------------------
# Data preparation
# -------------------------------------

X_train = np.array(f.root.img)
y_train = np.array(f.root.steer)
print(X_train.shape, y_train.shape)
print("Train data[3] mean = ", np.mean(X_train[3]))

X_train, X_valid, y_train, y_valid = train_test_split(
                X_train, y_train, test_size=0.2, random_state=88
                )
#X_train, y_train = shuffle(X_train, y_train)
print(X_train.shape, y_train.shape, X_valid.shape, y_valid.shape)

train_datagen = ImageDataGenerator(
            )
#train_datagen = ImageDataGenerator(
#            rotation_range=10,
#            height_shift_range=0.1,
#            shear_range= 0.2,
#            zoom_range = 0.1,
#            fill_mode = 'nearest'
#          )
train_datagen.fit(X_train)

val_datagen = ImageDataGenerator(
            )
val_datagen.fit(X_valid)


# -------------------------------------
# Compile and train the model
# -------------------------------------
model=load_model('model.h5')
#opt = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
opt = Adam(lr=0.00005)
model.compile(optimizer=opt, loss='mse', metrics=['accuracy'])
model.summary()

history = model.fit_generator(
                # ==== Unmask below line to dump image out to take snapshot of what's being fed into training process.
                train_datagen.flow(X_train, y_train, batch_size=16,save_to_dir="./", save_prefix="fitgen_", save_format="png"), 
                # ==== Use below line to do normal training
                #train_datagen.flow(X_train, y_train, batch_size=64), 
                samples_per_epoch=X_train.shape[0], 
                nb_epoch=EPOCH,
                validation_data=val_datagen.flow(X_valid, y_valid, batch_size=64), 
                nb_val_samples=X_valid.shape[0]
                )
# list all data in history
print(history.history.keys())

