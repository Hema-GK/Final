# import os

# # DATABASE_URL = "mysql+pymysql://root:1974Kvch8@localhost/smart_attendance"
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://root:AakYN2ogdHC9KQO8jN7XVqobecID3OqT@dpg-d6s05k9j16oc73efbpkg-a.oregon-postgres.render.com/attendance_db_g5y9?sslmode=require")
# SECRET_KEY = os.getenv("SECRET_KEY", "smartattendancekey")

# ALGORITHM = "HS256"

# ACCESS_TOKEN_EXPIRE_MINUTES = 60

import os

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "smartattendancekey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60