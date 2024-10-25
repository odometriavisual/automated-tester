import numpy as np
import cv2
import random


def generate_random_num(t, res=10, max=1000):
    # The same seed is considered every 'res' seconds.
    random.seed(t // res)
    return int(random.random() * max)  # Between 0 and max


def calculate_teng_score(frame: np.ndarray) -> float:
    gaussianX = cv2.Sobel(frame, cv2.CV_64F, 1, 0)
    gaussianY = cv2.Sobel(frame, cv2.CV_64F, 1, 0)
    return np.mean(gaussianX * gaussianX + gaussianY * gaussianY)
