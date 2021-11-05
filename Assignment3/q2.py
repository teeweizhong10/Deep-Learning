# -*- coding: utf-8 -*-
"""CS491 Assignment3 Wei Zhong Tee, Question 2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SmfynIN5K0AxaAXoHkEdv9eIaaSF-nNG
"""
import numpy as np
import pandas as pd
import os
import random
import glob
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# !pip install tensorflow.io
from tensorflow.keras.layers import *
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.python.keras import layers
from tensorflow.keras import layers

EPOCHS = 50
BATCH_SIZE = 32
HEIGHT = 128
WIDTH = 128
CHANNELS = 3
N_CLASSES = 13
AUTO = tf.data.AUTOTUNE


def loadImage(path):
    img = Image.open(path)
    img = np.array(img)

    image = img[:, :256]
    image = image / 255.0
    mask = img[:, 256:]

    input_image = tf.image.resize(image, (128, 128))
    input_mask = tf.image.resize(mask, (128, 128))

    return input_image, input_mask


def bin_image(mask):
    bins = np.array([20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240])
    new_mask = np.digitize(mask, bins)
    return new_mask


def getSegmentationArr(image, classes, width=WIDTH, height=HEIGHT):
    seg_labels = np.zeros((height, width, classes))
    img = image[:, :, 0]

    for c in range(classes):
        seg_labels[:, :, c] = (img == c).astype(int)
    return seg_labels


def give_color_to_seg_img(seg, n_classes=N_CLASSES):
    seg_img = np.zeros((seg.shape[0], seg.shape[1], 3)).astype('float')
    colors = sns.color_palette("hls", n_classes)

    for c in range(n_classes):
        segc = (seg == c)
        seg_img[:, :, 0] += (segc * (colors[c][0]))
        seg_img[:, :, 1] += (segc * (colors[c][1]))
        seg_img[:, :, 2] += (segc * (colors[c][2]))

    return (seg_img)


train_folder = '/data/groups/gomesr/DeepL_CS491/Cityscapes/train'
valid_folder = '/data/groups/gomesr/DeepL_CS491/Cityscapes/val'

train_filenames = glob.glob(os.path.join(train_folder, "*.jpg"))
valid_filenames = glob.glob(os.path.join(valid_folder, "*.jpg"))

num_of_training_samples = len(train_filenames)
num_of_valid_samples = len(valid_filenames)


class DataGenerator(tf.keras.utils.Sequence):
    def __init__(self, filenames,
                 batch_size=BATCH_SIZE,
                 shuffle=True):

        self.filenames = filenames
        self.batch_size = BATCH_SIZE
        self.shuffle = shuffle
        self.n = len(self.filenames)

    def on_epoch_end(self):
        if self.shuffle:
            random.shuffle(self.filenames)

    def __get_data(self, batches):
        imgs = []
        segs = []
        for file in batches:
            image, mask = loadImage(file)
            mask_binned = bin_image(mask)
            labels = getSegmentationArr(mask_binned, N_CLASSES)
            labels = np.argmax(labels, axis=-1)

            imgs.append(image)
            segs.append(labels)

        return np.array(imgs), np.array(segs)

    def __getitem__(self, index):

        batches = self.filenames[index * self.batch_size:(index + 1) * self.batch_size]

        X, y = self.__get_data(batches)

        return (X, y)

    def __len__(self):

        return self.n // self.batch_size


train_gen = DataGenerator(train_filenames)
val_gen = DataGenerator(valid_filenames)

for imgs, segs in train_gen:
    break
print(imgs.shape, segs.shape)

image = imgs[0]
mask = give_color_to_seg_img(segs[0])
masked_image = image * 0.5 + mask * 0.5

fig, axs = plt.subplots(1, 3, figsize=(20, 20))
axs[0].imshow(image)
axs[0].set_title('Original Image')
axs[1].imshow(mask)
axs[1].set_title('Segmentation Mask')
# predimg = cv2.addWeighted(imgs[i]/255, 0.6, _p, 0.4, 0)
axs[2].imshow(masked_image)
axs[2].set_title('Masked Image')
plt.show()

resize_and_rescale = tf.keras.Sequential([
  tf.keras.layers.Resizing(HEIGHT, WIDTH),
  tf.keras.layers.layers.Rescaling(1./255)
])

data_augmentation = tf.keras.Sequential([
  tf.keras.layers.layers.RandomFlip("horizontal_and_vertical"),
  tf.keras.layers.layers.RandomRotation(0.2),
])


def normalize(input_image, input_mask):
    input_image = tf.cast(input_image, tf.float32) / 255.0
    input_mask -= 1
    return input_image, input_mask


def unet_model(output_channels: int):
    # The encoder
    resize_and_rescale
    data_augmentation
    encoder_inputs = tf.keras.layers.Input(shape=[128, 128, 3])
    f = [32, 64, 128, 256, 512]
    kernel_size = (3, 3)
    strides = 1
    padding = "same"
    ## Encoder

    e1 = layers.Conv2D(f[0], kernel_size, padding=padding, strides=strides)(encoder_inputs)
    e1 = layers.BatchNormalization()(e1)
    e1 = layers.Activation("relu")(e1)
    m1 = layers.MaxPool2D(pool_size=(2, 2))(e1)

    e2 = layers.Conv2D(f[1], kernel_size, padding=padding, strides=strides)(m1)
    e2 = layers.BatchNormalization()(e2)
    e2 = layers.Activation("relu")(e2)
    m2 = layers.MaxPool2D(pool_size=(2, 2))(e2)

    e3 = layers.Conv2D(f[2], kernel_size, padding=padding, strides=strides)(m2)
    e3 = layers.BatchNormalization()(e3)
    e3 = layers.Activation("relu")(e3)
    m3 = layers.MaxPool2D(pool_size=(2, 2))(e3)

    e4 = layers.Conv2D(f[3], kernel_size, padding=padding, strides=strides)(m3)
    e4 = layers.BatchNormalization()(e4)
    e4 = layers.Activation("relu")(e4)
    m4 = layers.MaxPool2D(pool_size=(2, 2))(e4)

    ## Bridge

    b0 = layers.Conv2D(f[4], kernel_size, padding=padding, strides=strides)(m4)
    b0 = layers.BatchNormalization()(b0)
    b0 = layers.Activation("relu")(b0)

    b1 = layers.Conv2D(f[4], kernel_size, padding=padding, strides=strides)(b0)
    b1 = layers.BatchNormalization()(b1)
    b1 = layers.Activation("relu")(b1)

    ##Decoder

    u1 = layers.UpSampling2D((2, 2))(b1)
    u1 = layers.Conv2D(f[3], kernel_size, padding=padding, strides=strides)(u1)
    u1 = layers.BatchNormalization()(u1)
    u1 = layers.Activation("relu")(u1)
    u1 = layers.Concatenate()([u1, e4])

    c1 = layers.Conv2D(f[3], kernel_size, padding=padding, strides=strides)(u1)
    c1 = layers.BatchNormalization()(c1)
    c1 = layers.Activation("relu")(c1)

    c1 = layers.Conv2D(f[3], kernel_size, padding=padding, strides=strides)(c1)
    c1 = layers.BatchNormalization()(c1)
    c1 = layers.Activation("relu")(c1)

    #############################################

    u2 = layers.UpSampling2D((2, 2))(c1)
    u2 = layers.Conv2D(f[2], kernel_size, padding=padding, strides=strides)(u2)
    u2 = layers.BatchNormalization()(u2)
    u2 = layers.Activation("relu")(u2)
    u2 = layers.Concatenate()([u2, e3])

    c2 = layers.Conv2D(f[2], kernel_size, padding=padding, strides=strides)(u2)
    c2 = layers.BatchNormalization()(c2)
    c2 = layers.Activation("relu")(c2)

    c2 = layers.Conv2D(f[2], kernel_size, padding=padding, strides=strides)(c2)
    c2 = layers.BatchNormalization()(c2)
    c2 = layers.Activation("relu")(c2)

    #############################################

    u3 = layers.UpSampling2D((2, 2))(c2)
    u3 = layers.Conv2D(f[1], kernel_size, padding=padding, strides=strides)(u3)
    u3 = layers.BatchNormalization()(u3)
    u3 = layers.Activation("relu")(u3)
    u3 = layers.Concatenate()([u3, e2])

    c3 = layers.Conv2D(f[1], kernel_size, padding=padding, strides=strides)(u3)
    c3 = layers.BatchNormalization()(c3)
    c3 = layers.Activation("relu")(c3)

    c3 = layers.Conv2D(f[1], kernel_size, padding=padding, strides=strides)(c3)
    c3 = layers.BatchNormalization()(c3)
    c3 = layers.Activation("relu")(c3)

    ###############################################

    u4 = layers.UpSampling2D((2, 2))(c3)
    u4 = layers.Conv2D(f[0], kernel_size, padding=padding, strides=strides)(u4)
    u4 = layers.BatchNormalization()(u4)
    u4 = layers.Activation("relu")(u4)
    u4 = layers.Concatenate()([u4, e1])

    c4 = layers.Conv2D(f[0], kernel_size, padding=padding, strides=strides)(u4)
    c4 = layers.BatchNormalization()(c4)
    c4 = layers.Activation("relu")(c4)

    c4 = layers.Conv2D(f[0], kernel_size, padding=padding, strides=strides)(c4)
    c4 = layers.BatchNormalization()(c4)
    c4 = layers.Activation("relu")(c4)

    #####################################################

    encoder_outputs = layers.Conv2D(output_channels, (1, 1), padding="same")(c4)
    encoder = tf.keras.Model(inputs=encoder_inputs, outputs=c4, name="encoder")
    return encoder


model = unet_model(output_channels=N_CLASSES)
model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])


# tf.keras.utils.plot_model(model, show_shapes=True)


TRAIN_STEPS = len(train_gen)
VAL_STEPS = len(val_gen)

checkpoint = ModelCheckpoint('seg_model.h5', monitor='val_loss', verbose=1, save_best_only=True, save_weights_only=True)

model.compile(optimizer="adam", loss='sparse_categorical_crossentropy', metrics=["acc"])
history = model.fit(train_gen, validation_data=val_gen, steps_per_epoch=TRAIN_STEPS,
                    validation_steps=VAL_STEPS, epochs=EPOCHS, callbacks=[checkpoint])

# summarize history for accuracy
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.savefig('U_Training_Accuracy.png')
plt.clf()

# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.savefig('U_Training_Loss.png')
plt.clf()


# ResUNet structure

def resunet_model(output_channels: int):
    # The encoder
    resize_and_rescale
    data_augmentation
    encoder_inputs = tf.keras.layers.Input(shape=[128, 128, 3])
    f = [32, 64, 128, 256, 512]
    kernel_size = (3, 3)
    strides = 1
    padding = "same"
    ## Encoder

    e1 = layers.Conv2D(f[0], kernel_size, padding=padding, strides=strides)(encoder_inputs)
    e1 = layers.BatchNormalization()(e1)
    e1 = layers.Activation("relu")(e1)
    e1 = layers.Conv2D(f[0], kernel_size, padding=padding, strides=strides)(e1)
    m1 = layers.MaxPool2D(pool_size=(2, 2))(e1)

    e2 = layers.Conv2D(f[1], kernel_size, padding=padding, strides=strides)(m1)
    e2 = layers.BatchNormalization()(e2)
    e2 = layers.Activation("relu")(e2)
    e2 = layers.Conv2D(f[1], kernel_size, padding=padding, strides=strides)(e2)
    m2 = layers.MaxPool2D(pool_size=(2, 2))(e2)

    e3 = layers.Conv2D(f[2], kernel_size, padding=padding, strides=strides)(m2)
    e3 = layers.BatchNormalization()(e3)
    e3 = layers.Activation("relu")(e3)
    e3 = layers.Conv2D(f[2], kernel_size, padding=padding, strides=strides)(e3)
    m3 = layers.MaxPool2D(pool_size=(2, 2))(e3)

    e4 = layers.Conv2D(f[3], kernel_size, padding=padding, strides=strides)(m3)
    e4 = layers.BatchNormalization()(e4)
    e4 = layers.Activation("relu")(e4)
    e4 = layers.Conv2D(f[3], kernel_size, padding=padding, strides=strides)(e4)
    m4 = layers.MaxPool2D(pool_size=(2, 2))(e4)

    ## Bridge

    b0 = layers.Conv2D(f[4], kernel_size, padding=padding, strides=strides)(m4)
    b0 = layers.BatchNormalization()(b0)
    b0 = layers.Activation("relu")(b0)

    b1 = layers.Conv2D(f[4], kernel_size, padding=padding, strides=strides)(b0)
    b1 = layers.BatchNormalization()(b1)
    b1 = layers.Activation("relu")(b1)

    ##Decoder

    u1 = layers.UpSampling2D((2, 2))(b1)
    u1 = layers.Conv2D(f[3], kernel_size, padding=padding, strides=strides)(u1)
    u1 = layers.BatchNormalization()(u1)
    u1 = layers.Activation("relu")(u1)
    u1 = layers.Conv2D(f[3], kernel_size, padding=padding, strides=strides)(u1)
    u1 = layers.Concatenate()([u1, e4])

    c1 = layers.Conv2D(f[3], kernel_size, padding=padding, strides=strides)(u1)
    c1 = layers.BatchNormalization()(c1)
    c1 = layers.Activation("relu")(c1)

    c1 = layers.Conv2D(f[3], kernel_size, padding=padding, strides=strides)(c1)
    c1 = layers.BatchNormalization()(c1)
    c1 = layers.Activation("relu")(c1)

    #############################################

    u2 = layers.UpSampling2D((2, 2))(c1)
    u2 = layers.Conv2D(f[2], kernel_size, padding=padding, strides=strides)(u2)
    u2 = layers.BatchNormalization()(u2)
    u2 = layers.Activation("relu")(u2)
    u2 = layers.Conv2D(f[2], kernel_size, padding=padding, strides=strides)(u2)
    u2 = layers.Concatenate()([u2, e3])

    c2 = layers.Conv2D(f[2], kernel_size, padding=padding, strides=strides)(u2)
    c2 = layers.BatchNormalization()(c2)
    c2 = layers.Activation("relu")(c2)

    c2 = layers.Conv2D(f[2], kernel_size, padding=padding, strides=strides)(c2)
    c2 = layers.BatchNormalization()(c2)
    c2 = layers.Activation("relu")(c2)

    #############################################

    u3 = layers.UpSampling2D((2, 2))(c2)
    u3 = layers.Conv2D(f[1], kernel_size, padding=padding, strides=strides)(u3)
    u3 = layers.BatchNormalization()(u3)
    u3 = layers.Activation("relu")(u3)
    u3 = layers.Conv2D(f[1], kernel_size, padding=padding, strides=strides)(u3)
    u3 = layers.Concatenate()([u3, e2])

    c3 = layers.Conv2D(f[1], kernel_size, padding=padding, strides=strides)(u3)
    c3 = layers.BatchNormalization()(c3)
    c3 = layers.Activation("relu")(c3)

    c3 = layers.Conv2D(f[1], kernel_size, padding=padding, strides=strides)(c3)
    c3 = layers.BatchNormalization()(c3)
    c3 = layers.Activation("relu")(c3)

    ###############################################

    u4 = layers.UpSampling2D((2, 2))(c3)
    u4 = layers.Conv2D(f[0], kernel_size, padding=padding, strides=strides)(u4)
    u4 = layers.BatchNormalization()(u4)
    u4 = layers.Activation("relu")(u4)
    u4 = layers.Conv2D(f[0], kernel_size, padding=padding, strides=strides)(u4)
    u4 = layers.Concatenate()([u4, e1])

    c4 = layers.Conv2D(f[0], kernel_size, padding=padding, strides=strides)(u4)
    c4 = layers.BatchNormalization()(c4)
    c4 = layers.Activation("relu")(c4)

    c4 = layers.Conv2D(f[0], kernel_size, padding=padding, strides=strides)(c4)
    c4 = layers.BatchNormalization()(c4)
    c4 = layers.Activation("relu")(c4)

    #####################################################

    encoder_outputs = layers.Conv2D(output_channels, (1, 1), padding="same")(c4)
    encoder = tf.keras.Model(inputs=encoder_inputs, outputs=c4, name="encoder")
    return encoder


model = resunet_model(output_channels=N_CLASSES)
model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

TRAIN_STEPS = len(train_gen)
VAL_STEPS = len(val_gen)

checkpoint = ModelCheckpoint('seg_model.h5', monitor='val_loss', verbose=1, save_best_only=True, save_weights_only=True)

model.compile(optimizer="adam", loss='sparse_categorical_crossentropy', metrics=["acc"])
history = model.fit(train_gen, validation_data=val_gen, steps_per_epoch=TRAIN_STEPS,
                    validation_steps=VAL_STEPS, epochs=EPOCHS, callbacks=[checkpoint])

# summarize history for accuracy
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.savefig('Res_Training_Accuracy.png')
plt.clf()

# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.savefig('Res_Training_Loss.png')
plt.clf()