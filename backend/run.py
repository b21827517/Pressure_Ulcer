import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import cv2
import copy
import os
import numpy as np
import cv2
import json
from glob import glob
from metrics import *
import numpy as np
from tensorflow.keras.utils import CustomObjectScope
from tensorflow.keras.models import load_model
import tensorflow as tf
from sklearn.utils import shuffle

#from model import build_model, Upsample, ASPP

smooth = 1.
def dice_coef(y_true, y_pred):
    y_true_f = tf.keras.layers.Flatten()(y_true)
    y_pred_f = tf.keras.layers.Flatten()(y_pred)
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth)

def dice_loss(y_true, y_pred):
    return 1.0 - dice_coef(y_true, y_pred)

def load_model_weight(path):
    with CustomObjectScope({
    'dice_loss': dice_loss,
    'dice_coef': dice_coef,
    'bce_dice_loss': dice_loss,
    'focal_loss': dice_loss,
    'iou': dice_loss
        }):
        model = load_model(path)
        return model


def mask_to_3d(mask):
    mask = np.squeeze(mask)
    mask = [mask, mask, mask]
    mask = np.transpose(mask, (1, 2, 0))
    return mask

def read_image(x):
    image = cv2.imread(x, cv2.IMREAD_COLOR)
    image = cv2.resize(image, (512, 384))
    image = np.clip(image - np.median(image)+127, 0, 255)
    image = image/255.0
    image = image.astype(np.float32)
    image = np.expand_dims(image, axis=0)
    return image

def parse(y_pred):
    y_pred = np.expand_dims(y_pred, axis=-1)
    y_pred = y_pred[..., -1]
    y_pred = y_pred.astype(np.float32)
    y_pred = np.expand_dims(y_pred, axis=-1)
    return y_pred
def image_writer(file):
    
    model = load_model_weight("/Users/efekalayci/timing/backend/model_with_pretrained_model_v1.h5")
    x = read_image(file)

    
    _, h, w, _ = x.shape

    y_pred1 = parse(model.predict(x)[0][..., -2])
    y_pred2 = parse(model.predict(x)[0][..., -1])
    
    cv2.imwrite(f"original_image.png", x[0] * 255.0)
    image  = mpimg.imread("original_image.png")
    
    cv2.imwrite(f"predicted_mask_1.png", mask_to_3d(y_pred1) * 255.0)
    image0  = mpimg.imread("predicted_mask_1.png")

    cv2.imwrite(f"predicted_mask_2.png", mask_to_3d(y_pred2) * 255.0)
    image3  = mpimg.imread("predicted_mask_2.png")
    """
    fig, axs = plt.subplots(1, 4, figsize=(12, 4))
    axs[0].imshow(image)
    axs[0].set_title('Original Image: ')
    axs[1].imshow(image0)
    axs[1].set_title('Predicted Mask-1')
    axs[2].imshow(image3)
    axs[2].set_title('Predicted Mask-2')
    plt.show() """