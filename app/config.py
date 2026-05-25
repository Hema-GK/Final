import os
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "smartattendancekey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
