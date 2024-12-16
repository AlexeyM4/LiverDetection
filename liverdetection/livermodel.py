# import os
# import glob
# import cv2
# import warnings
# warnings.simplefilter("ignore", UserWarning)
# import numpy as np
# import tensorflow as tf
# from matplotlib import pyplot as plt
# import PIL as pw
# import gdown
# from pathlib import Path
#
# root_path = Path(__file__).resolve().parents[1]
# print(root_path)
#
# if not os.path.isfile("liver_tumor_seg.h5"):
#     url = ""
#     output = "liver_tumor_seg.h5"
#     gdown.download(url, fuzzy=True)
#
# model_path = str(root_path) + "/liver_tumor_seg.h5"
# unet_model = tf.keras.models.load_model(filepath=model_path)
#
# image_path = input("путь к файлу: ")
# output_path = input("путь для сохранения файла: ")
#
# def generateMask(image_path, output_path, unet_model):
#     SIZE_Y = 256
#     SIZE_X = 256
#
#     test_images = []
#
#     for directory_path in sorted(glob.glob(image_path)):
#         for img_path in sorted(glob.glob(os.path.join(image_path, "*.tif"))):
#             img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
#             img = img * 255
#             img = img.astype(np.uint8)
#             img = cv2.resize(img, (SIZE_Y, SIZE_X))
#
#             img = cv2.medianBlur(img, ksize = 5)
#
#             clahe = cv2.createCLAHE(clipLimit = 2.0, tileGridSize = (8,8))
#             img = clahe.apply(img)
#
#             img = cv2.merge([img, img, img])
#             test_images.append(img)
#
#     test_images = np.array(test_images)
#
#     for i in range(len(test_images)):
#         test_img = test_images[i]
#         test_img_input = np.expand_dims(test_img, 0)
#         test_pred1 = unet_model.predict(test_img_input)
#         test_prediction1 = np.argmax(test_pred1, axis = 3)[0, :, :]
#
#         liver_mask = pw.Image.fromarray((test_prediction1 * 255).astype(np.uint8))
#         liver_mask.save(output_path + "/output_image" + str(i) + ".png")
#         liver_mask.close()
#
# generateMask(image_path, output_path, unet_model)
import os
import shutil
from django.conf import settings

class LiverModel:
    def __init__(self):
        pass

    def detection(self):
        images_path = os.path.join(settings.MEDIA_ROOT, 'images/')
        images = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]

        destination_directory = os.path.join(settings.MEDIA_ROOT, 'imagesDetection/')

        for image in images:
            image_path = os.path.join(images_path, image)
            destination_file = os.path.join(destination_directory, image)

            shutil.copy2(image_path, destination_file)



