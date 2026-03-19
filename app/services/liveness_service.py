import cv2
import numpy as np
import face_recognition


def detect_liveness(image):

    try:

        # convert to gray
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # basic brightness check
        brightness = np.mean(gray)

        if brightness < 40:
            return False

        # detect faces
        faces = face_recognition.face_locations(image)

        if len(faces) != 1:
            return False

        # check face size (photo attack often small)
        top, right, bottom, left = faces[0]

        width = right - left
        height = bottom - top

        if width < 80 or height < 80:
            return False

        return True

    except:
        return False