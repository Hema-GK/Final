# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models.student import Student
# import face_recognition
# import numpy as np
# import base64
# import cv2
# import json

# router = APIRouter(prefix="/face", tags=["Face Recognition"])


# @router.post("/recognize")
# def recognize_face(data: dict, db: Session = Depends(get_db)):

#     try:

#         # Decode captured image
#         image_data = data["image"].split(",")[1]
#         image_bytes = base64.b64decode(image_data)

#         np_arr = np.frombuffer(image_bytes, np.uint8)
#         img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

#         rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#         # Detect face
#         face_locations = face_recognition.face_locations(rgb)
#         encodings = face_recognition.face_encodings(rgb, face_locations)

#         if len(encodings) == 0:
#             return {"status": "No face detected"}

#         captured_encoding = encodings[0]

#         students = db.query(Student).all()

#         best_match = None
#         best_distance = 1.0

#         for student in students:

#             if not student.face_encoding:
#                 continue

#             stored_encoding = np.array(json.loads(student.face_encoding))

#             distance = face_recognition.face_distance(
#                 [stored_encoding], captured_encoding
#             )[0]

#             print("Checking:", student.name, "Distance:", distance)

#             if distance < best_distance:
#                 best_distance = distance
#                 best_match = student

#         # strict threshold for accuracy
#         if best_match and best_distance < 0.50:

#             return {
#                 "status": "Face recognized",
#                 "student": {
#                     "id": best_match.id,
#                     "name": best_match.name,
#                     "usn": best_match.usn,
#                     "section": best_match.section
#                 }
#             }

#         return {"status": "Face not recognized"}

#     except Exception as e:
#         print("FACE ERROR:", e)
#         return {"status": "Recognition error"}


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.student import Student
from app.services.liveness_service import detect_liveness

import face_recognition
import numpy as np
import base64
import cv2
import json

router = APIRouter(prefix="/face", tags=["Face Recognition"])


@router.post("/recognize")
def recognize_face(data: dict, db: Session = Depends(get_db)):

    try:

        # -----------------------------
        # Decode captured image
        # -----------------------------
        image_data = data["image"].split(",")[1]
        image_bytes = base64.b64decode(image_data)

        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # -----------------------------
        # LIVENESS CHECK
        # -----------------------------
        live = detect_liveness(img)

        if not live:
            return {"status": "Fake face detected"}

        # -----------------------------
        # FACE DETECTION
        # -----------------------------
        face_locations = face_recognition.face_locations(rgb)

        if len(face_locations) != 1:
            return {"status": "Please show exactly one face"}

        encodings = face_recognition.face_encodings(rgb, face_locations)

        if len(encodings) == 0:
            return {"status": "No face detected"}

        captured_encoding = encodings[0]

        # -----------------------------
        # COMPARE WITH DATABASE
        # -----------------------------
        students = db.query(Student).all()

        best_match = None
        best_distance = 1.0

        for student in students:

            if not student.face_encoding:
                continue

            stored_encoding = np.array(json.loads(student.face_encoding))

            distance = face_recognition.face_distance(
                [stored_encoding], captured_encoding
            )[0]

            print("Checking:", student.name, "Distance:", distance)

            if distance < best_distance:
                best_distance = distance
                best_match = student

        # -----------------------------
        # MATCH THRESHOLD
        # -----------------------------
        if best_match and best_distance < 0.50:

            return {
                "status": "Face recognized",
                "student": {
                    "id": best_match.id,
                    "name": best_match.name,
                    "usn": best_match.usn,
                    "section": best_match.section
                }
            }

        return {"status": "Face not recognized"}

    except Exception as e:

        print("FACE ERROR:", e)

        return {"status": "Recognition error"}