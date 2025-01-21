import os
import glob
import cv2
import warnings
warnings.simplefilter("ignore", UserWarning)
import numpy as np
import tensorflow as tf
import PIL as pw

from django.conf import settings


class LiverModel:
    def __init__(self):
        model_path = os.path.join(settings.BASE_DIR, "liver_tumor_seg.h5")
        self.unet_model = tf.keras.models.load_model(filepath=model_path)

        self.image_path = os.path.join(settings.MEDIA_ROOT, 'images/')
        self.output_path = os.path.join(settings.MEDIA_ROOT, 'imagesDetection/')
        self.output_path_overlay = os.path.join(settings.MEDIA_ROOT, 'imagesOverlay/')

    def detection(self):
        SIZE_Y = 256
        SIZE_X = 256

        test_images = {}

        for _ in sorted(glob.glob(self.image_path)):
            for img_path in sorted(glob.glob(os.path.join(self.image_path, "*.tif"))):
                img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
                img = img * 255
                img = img.astype(np.uint8)
                img = cv2.resize(img, (SIZE_Y, SIZE_X))

                img = cv2.medianBlur(img, ksize=5)

                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                img = clahe.apply(img)

                img = cv2.merge([img, img, img])
                test_images[os.path.basename(img_path)] = img

        for name in test_images:
            test_img = np.array([test_images[name]])[0]
            test_img_input = np.expand_dims(test_img, 0)
            test_pred = self.unet_model.predict(test_img_input)
            test_prediction = np.argmax(test_pred, axis=3)[0, :, :]

            liver_mask = pw.Image.fromarray((test_prediction * 255).astype(np.uint8))
            liver_mask.save(f"{self.output_path}/{name}")
            liver_mask.close()

            # Загрузка оригинального изображения
            original_img = cv2.imread(f"{self.image_path}/{name}")
            original_height, original_width = original_img.shape[:2]

            # Загрузка маски и масштабирование до размеров оригинального изображения
            mask = cv2.imread(f"{self.output_path}/{name}", cv2.IMREAD_GRAYSCALE)
            mask = cv2.resize(mask, (original_width, original_height))

            # Нахождение контуров на маске
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Рисование контуров на оригинальном изображении
            cv2.drawContours(original_img, contours, -1, (0, 255, 0), 2)  # Зелёный цвет для контуров

            cv2.imwrite(f"{self.output_path_overlay}/{name}", original_img)
