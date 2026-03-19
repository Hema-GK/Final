import math

def distance(lat1, lon1, lat2, lon2):


  R = 6371

  dLat = math.radians(lat2 - lat1)
  dLon = math.radians(lon2 - lon1)

  a = (
      math.sin(dLat/2) * math.sin(dLat/2)
      + math.cos(math.radians(lat1))
      * math.cos(math.radians(lat2))
      * math.sin(dLon/2)
      * math.sin(dLon/2)
  )

  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

  return R * c


def is_inside_classroom(student_lat, student_lon, class_lat, class_lon):

  d = distance(student_lat, student_lon, class_lat, class_lon)

  return d < 0.05

