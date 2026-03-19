import cv2
import numpy as np
import base64

face_detector = cv2.CascadeClassifier(
cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def decode_base64_image(image_string):


  header, encoded = image_string.split(",")

  img_bytes = base64.b64decode(encoded)

  np_arr = np.frombuffer(img_bytes, np.uint8)

  image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

  return image


def extract_face_embedding(image):


  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  faces = face_detector.detectMultiScale(gray, 1.3, 5)

  if len(faces) == 0:
      return None

  x, y, w, h = faces[0]

  face = gray[y:y+h, x:x+w]

  face = cv2.resize(face, (64,64))

  embedding = face.flatten()

  embedding = embedding / np.linalg.norm(embedding)

  return embedding.tolist()

