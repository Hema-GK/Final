import cv2
import numpy as np

def detect_spoof(image):


  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  variance = np.var(gray)

  if variance < 50:

      return True

  return False

