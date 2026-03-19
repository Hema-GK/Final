import cv2
import base64
import numpy as np
import pickle
import os

EMBEDDING_FILE = "models/face_embeddings.pkl"

def decode_image(image_string):

  header, encoded = image_string.split(",")

  data = base64.b64decode(encoded)

  np_arr = np.frombuffer(data, np.uint8)

  img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

  return img


def extract_face_embedding(image):

  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  resized = cv2.resize(gray, (100,100))

  embedding = resized.flatten()

  return embedding


def load_embeddings():

  if os.path.exists(EMBEDDING_FILE):

      with open(EMBEDDING_FILE,"rb") as f:

          return pickle.load(f)

  return {}


def save_embeddings(data):

  with open(EMBEDDING_FILE,"wb") as f:

      pickle.dump(data,f)


def recognize_face(image):

  embedding = extract_face_embedding(image)

  database = load_embeddings()

  best_match = None

  min_distance = 999999

  for usn, stored_embedding in database.items():

      dist = np.linalg.norm(embedding - stored_embedding)

      if dist < min_distance:

          min_distance = dist

          best_match = usn

  if min_distance < 5000:

      return best_match

  return None

def register_face(usn, image):

  embedding = extract_face_embedding(image)

  database = load_embeddings()

  database[usn] = embedding

  save_embeddings(database)

